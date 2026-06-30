from datetime import datetime, time
from typing import Any


def parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def is_now_within_window(start: str | None, end: str | None) -> bool:
    if not start or not end:
        return True

    now = datetime.now().time()
    start_time = parse_time(start)
    end_time = parse_time(end)

    if start_time <= end_time:
        return start_time <= now <= end_time

    return now >= start_time or now <= end_time


def evaluate_access_rule(
    student: dict[str, Any] | None,
    geofence: dict[str, Any],
) -> dict[str, str]:
    rules = geofence.get("rules") or {}

    if not student:
        return {
            "decision": "alert",
            "severity": "high",
            "reason": "Unknown RFID tag detected",
            "alert_type": "UNKNOWN_RFID_TAG",
        }

    allowed_roles = rules.get("allow_roles") or rules.get("allowed_roles") or []
    start_time = rules.get("time_start")
    end_time = rules.get("time_end")

    student_role = student.get("role") or student.get("student_status") or "student"

    if allowed_roles and student_role not in allowed_roles:
        return {
            "decision": "denied",
            "severity": "high",
            "reason": f"Role '{student_role}' is not allowed in {geofence.get('name')}",
            "alert_type": "ROLE_RESTRICTED_ACCESS",
        }

    if not is_now_within_window(start_time, end_time):
        return {
            "decision": "denied",
            "severity": "medium",
            "reason": f"Access outside allowed time window {start_time} - {end_time}",
            "alert_type": "TIME_RESTRICTED_ACCESS",
        }

    return {
        "decision": "allowed",
        "severity": "low",
        "reason": "Access allowed by geofence rule",
        "alert_type": "ACCESS_ALLOWED",
    }