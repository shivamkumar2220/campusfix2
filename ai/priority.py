# Priority engine: gives each complaint a score from 4 questions, then a priority.
#   score = students affected (1-4) + severity (1-3) + academic impact (1-3) + duration (1-3)
#   11-13 = Critical, 8-10 = High, 5-7 = Medium, 4 = Low
# Staff can still change the priority later (staff override).
SEVERITY = {"minor": 1, "moderate": 2, "severe": 3}
IMPACT = {"low": 1, "medium": 2, "high": 3}


def recommend_priority(affected_students, severity, academic_impact, duration_hours):
    students = 4 if affected_students >= 100 else 3 if affected_students >= 50 else 2 if affected_students >= 10 else 1
    duration = 3 if duration_hours >= 24 else 2 if duration_hours >= 8 else 1
    score = students + SEVERITY[severity] + IMPACT[academic_impact] + duration
    priority = "Critical" if score >= 11 else "High" if score >= 8 else "Medium" if score >= 5 else "Low"
    return score, priority


if __name__ == "__main__":
    print(recommend_priority(100, "severe", "high", 12))  # (12, 'Critical')
    print(recommend_priority(1, "minor", "low", 1))       # (4, 'Low')
