from app.models import AuditLog

def log_audit(
    db,
    *,
    user_id: int | None,
    table_name: str,
    row_id: int,
    action: str,
    diff: dict
):
    audit = AuditLog(
        user_id=user_id,
        table_name=table_name,
        row_id=row_id,
        action=action,
        diff=diff
    )
    db.add(audit)
    db.commit()