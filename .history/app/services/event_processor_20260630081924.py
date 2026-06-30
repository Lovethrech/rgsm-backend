from datetime import datetime, timezone
from typing import Any

from app.core.database import get_db_cursor
from app.services.rule_engine import evaluate_access_rule


def row_to_dict(cursor, row) -> dict[str, Any] | None:
    if row is None:
        return None

    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def get_reader_by_code(reader_code: str) -> dict[str, Any] | None:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            select *
            from public.rfid_readers
            where reader_code = %s
            limit 1
            """,
            (reader_code,),
        )
        return row_to_dict(cursor, cursor.fetchone())


def get_student_by_tag_uid(tag_uid: str) -> dict[str, Any] | None:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            select *
            from public.students
            where rfid_uid = %s
            limit 1
            """,
            (tag_uid,),
        )
        return row_to_dict(cursor, cursor.fetchone())


def get_geofences_for_reader(reader_id: str) -> list[dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            select gz.*
            from public.geofence_zones gz
            join public.geofence_reader_map grm
              on grm.geofence_id = gz.id
            where grm.reader_id = %s
            """,
            (reader_id,),
        )

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]


def insert_detection_event(
    organization_id: str | None,
    reader_id: str | None,
    tag_uid: str,
    event_type: str,
    payload: dict[str, Any],
) -> str:
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            insert into public.detection_events (
              organization_id,
              reader_id,
              tag_uid,
              event_type,
              occurred_at,
              payload
            )
            values (%s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                organization_id,
                reader_id,
                tag_uid,
                event_type,
                datetime.now(timezone.utc),
                __import__("json").dumps(payload),
            ),
        )
        return str(cursor.fetchone()[0])


def insert_access_log(
    detection_event_id: str,
    organization_id: str | None,
    student_id: str | None,
    reader_id: str | None,
    geofence_id: str | None,
    decision: str,
    reason: str,
) -> str:
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            insert into public.access_logs (
              detection_event_id,
              organization_id,
              student_id,
              reader_id,
              geofence_id,
              decision,
              reason,
              created_at
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                detection_event_id,
                organization_id,
                student_id,
                reader_id,
                geofence_id,
                decision,
                reason,
                datetime.now(timezone.utc),
            ),
        )
        return str(cursor.fetchone()[0])


def insert_alert(
    organization_id: str | None,
    hostel_id: str | None,
    access_log_id: str,
    severity: str,
    alert_type: str,
    message: str,
) -> str:
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            insert into public.alerts (
                organization_id,
                hostel_id,
                access_log_id,
                severity,
                alert_type,
                message,
                status,
                created_at
            )
            values (%s, %s, %s, %s, %s, %s, 'open', %s)
            returning id
            """,
            (
                organization_id,
                hostel_id,
                access_log_id,
                severity,
                alert_type,
                message,
                datetime.now(timezone.utc),
            ),
        )
        return str(cursor.fetchone()[0])


def process_rfid_event(event: dict[str, Any]) -> dict[str, Any]:
    reader_code = event["reader_code"]
    tag_uid = event["tag_uid"]
    event_type = event.get("event_type", "scan")

    reader = get_reader_by_code(reader_code)
    student = get_student_by_tag_uid(tag_uid)

    if not reader:
        detection_event_id = insert_detection_event(
            organization_id=None,
            reader_id=None,
            tag_uid=tag_uid,
            event_type=event_type,
            payload=event,
        )

        access_log_id = insert_access_log(
            detection_event_id=detection_event_id,
            organization_id=None,
            student_id=None,
            reader_id=None,
            geofence_id=None,
            decision="alert",
            reason=f"Unknown reader code: {reader_code}",
        )

        alert_id = insert_alert(
            organization_id=None,
            hostel_id=None,
            access_log_id=access_log_id,
            severity="critical",
            alert_type="UNKNOWN_READER",
            message=f"RFID event received from unknown reader '{reader_code}'",
        )

        return {
            "ok": False,
            "decision": "alert",
            "message": "Unknown reader",
            "detection_event_id": detection_event_id,
            "access_log_id": access_log_id,
            "alert_id": alert_id,
        }

    organization_id = str(reader["organization_id"]) if reader.get("organization_id") else None
    reader_id = str(reader["id"])
    hostel_id = str(reader["hostel_id"]) if reader.get("hostel_id") else None

    detection_event_id = insert_detection_event(
        organization_id=organization_id,
        reader_id=reader_id,
        tag_uid=tag_uid,
        event_type=event_type,
        payload=event,
    )

    geofences = get_geofences_for_reader(reader_id)

    if not geofences:
        access_log_id = insert_access_log(
            detection_event_id=detection_event_id,
            organization_id=organization_id,
            student_id=str(student["id"]) if student else None,
            reader_id=reader_id,
            geofence_id=None,
            decision="alert",
            reason="Reader is not mapped to any geofence",
        )

        alert_id = insert_alert(
            organization_id=organization_id,
            hostel_id=hostel_id,
            access_log_id=access_log_id,
            severity="medium",
            alert_type="UNMAPPED_READER",
            message=f"Reader '{reader_code}' is active but not mapped to a geofence",
        )

        return {
            "ok": True,
            "decision": "alert",
            "message": "Reader not mapped to geofence",
            "detection_event_id": detection_event_id,
            "access_log_id": access_log_id,
            "alert_id": alert_id,
        }

    decisions = []

    for geofence in geofences:
        result = evaluate_access_rule(student, geofence)

        access_log_id = insert_access_log(
            detection_event_id=detection_event_id,
            organization_id=organization_id,
            student_id=str(student["id"]) if student else None,
            reader_id=reader_id,
            geofence_id=str(geofence["id"]),
            decision=result["decision"],
            reason=result["reason"],
        )

        alert_id = None

        if result["decision"] in ["denied", "alert"]:
            alert_id = insert_alert(
                organization_id=organization_id,
                hostel_id=str(geofence["hostel_id"]) if geofence.get("hostel_id") else hostel_id,
                access_log_id=access_log_id,
                severity=result["severity"],
                alert_type=result["alert_type"],
                message=result["reason"],
            )

        decisions.append(
            {
                "geofence_id": str(geofence["id"]),
                "geofence_name": geofence["name"],
                "decision": result["decision"],
                "reason": result["reason"],
                "access_log_id": access_log_id,
                "alert_id": alert_id,
            }
        )

    return {
        "ok": True,
        "detection_event_id": detection_event_id,
        "reader_code": reader_code,
        "tag_uid": tag_uid,
        "decisions": decisions,
    }