from datetime import datetime, time
from typing import Any


def parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def is_now_within_window(start: str | None, end: str | None) -> bool:
    """
    Checks whether current local time falls within the allowed window.
    Supports normal windows like 08:00-18:00 and overnight windows like 22:00-05:00.
    """
    if not start or not end:
        return True

    now = datetime.now().time()
    start_time = parse_time(start)
    end_time = parse_time(end)

    if start_time <= end_time:
        return start_time <= now <= end_time

    return now >= start_time or now <= end_time


def normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def get_student_role(student: dict[str, Any]) -> str:
    """
    Your students table currently uses student_status='student'.
    Later, you can add a proper role column if needed.
    """
    return normalize(
        student.get("role")
        or student.get("student_status")
        or "student"
    )


def evaluate_access_rule(
    student: dict[str, Any] | None,
    geofence: dict[str, Any],
    lockdown: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Evaluates whether a scanned RFID tag is allowed inside a geofence.

    Expected geofence rules JSON examples:

    {
      "allow_roles": ["student", "security", "university_admin"],
      "allowed_gender": "male",
      "time_start": "05:00",
      "time_end": "23:00"
    }

    Returns:
    {
      "decision": "allowed" | "denied" | "alert",
      "severity": "low" | "medium" | "high" | "critical",
      "reason": "...",
      "alert_type": "..."
    }
    """

    zone_name = geofence.get("name") or "Unknown Zone"
    zone_type = normalize(geofence.get("zone_type"))
    rules = geofence.get("rules") or {}
    lockdown = lockdown or {}
    lockdown_enabled = bool(lockdown.get("enabled"))
    lockdown_reason = lockdown.get("reason") or "Emergency lockdown is active"

    # 1. Unknown RFID tag
    if not student:
        return {
            "decision": "alert",
            "severity": "high",
            "reason": f"Unknown RFID tag attempted access to {zone_name}.",
            "alert_type": "UNKNOWN_RFID_TAG",
        }

    student_name = student.get("full_name") or "Unknown Student"
    student_role = get_student_role(student)
    student_gender = normalize(student.get("gender"))
    student_hostel_id = str(student.get("hostel_id")) if student.get("hostel_id") else None

    geofence_hostel_id = str(geofence.get("hostel_id")) if geofence.get("hostel_id") else None

    allowed_roles = [
        normalize(role)
        for role in (
            rules.get("allow_roles")
            or rules.get("allowed_roles")
            or []
        )
    ]

    allowed_gender = normalize(rules.get("allowed_gender"))
    start_time = rules.get("time_start")
    end_time = rules.get("time_end")

        # Emergency lockdown restriction
    if lockdown_enabled:
        allowed_during_lockdown = [
            "security",
            "university_admin",
            "global_admin",
        ]

        if not student:
            return {
                "decision": "alert",
                "severity": "critical",
                "reason": f"Unknown RFID tag detected during emergency lockdown at {zone_name}.",
                "alert_type": "LOCKDOWN_UNKNOWN_RFID_TAG",
            }

        student_role = get_student_role(student)
        student_name = student.get("full_name") or "Unknown Student"

        if student_role not in allowed_during_lockdown:
            return {
                "decision": "denied",
                "severity": "critical",
                "reason": (
                    f"{student_name} attempted access to {zone_name} during emergency lockdown. "
                    f"Reason: {lockdown_reason}."
                ),
                "alert_type": "EMERGENCY_LOCKDOWN_ACCESS_DENIED",
            }

    # 2. Time-based restriction
    if not is_now_within_window(start_time, end_time):
        return {
            "decision": "denied",
            "severity": "medium",
            "reason": (
                f"{student_name} attempted access to {zone_name} outside the allowed "
                f"time window ({start_time} - {end_time})."
            ),
            "alert_type": "TIME_RESTRICTED_ACCESS",
        }

    # 3. Role-based restriction
    if allowed_roles and student_role not in allowed_roles:
        severity = "high" if zone_type in ["restricted_lab", "admin_block"] else "medium"

        return {
            "decision": "denied",
            "severity": severity,
            "reason": (
                f"{student_name} with role '{student_role}' is not permitted to access "
                f"{zone_name}."
            ),
            "alert_type": "ROLE_RESTRICTED_ACCESS",
        }

    # 4. Gender restriction for hostel zones
    if allowed_gender and student_gender and student_gender != allowed_gender:
        return {
            "decision": "denied",
            "severity": "high",
            "reason": (
                f"{student_name} ({student_gender}) attempted access to {zone_name}, "
                f"which is restricted to {allowed_gender} students."
            ),
            "alert_type": "GENDER_RESTRICTED_HOSTEL_ACCESS",
        }

    # 5. Hostel mismatch restriction
    # If a student is entering a hostel geofence that is not their assigned hostel,
    # flag it as a security concern even if gender is valid.
    if zone_type == "hostel" and geofence_hostel_id and student_hostel_id:
        if student_hostel_id != geofence_hostel_id:
            return {
                "decision": "denied",
                "severity": "medium",
                "reason": (
                    f"{student_name} attempted access to {zone_name}, but is not assigned "
                    f"to this hostel."
                ),
                "alert_type": "HOSTEL_MISMATCH_ACCESS",
            }

    # 6. Restricted lab extra caution
    # If students are not in allow_roles for restricted labs, role check already catches them.
    # This section gives a clear alert type for restricted zones if needed later.
    if zone_type == "restricted_lab" and student_role == "student":
        return {
            "decision": "denied",
            "severity": "high",
            "reason": (
                f"{student_name} attempted access to restricted laboratory zone: {zone_name}."
            ),
            "alert_type": "RESTRICTED_LAB_ACCESS",
        }

    # 7. Allowed
    return {
        "decision": "allowed",
        "severity": "low",
        "reason": f"{student_name} was allowed access to {zone_name}.",
        "alert_type": "ACCESS_ALLOWED",
    }