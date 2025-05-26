from datetime import datetime, timezone

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models import Base


def _serialize_value(val):
    if isinstance(val, (datetime,)):
        return val.isoformat()
    return val


def _create_audit_log_obj(target, action):
    from app.models import AuditLog

    # Avoid recursion for AuditLog itself
    if getattr(target, "__tablename__", None) == "audit_log":
        return None
    diff = {
        c.name: _serialize_value(getattr(target, c.name))
        for c in target.__table__.columns
    }
    return AuditLog(
        user_id=getattr(target, "user_id", None),
        table_name=target.__tablename__,
        row_id=getattr(target, "id", None),
        action=action,
        diff=diff,
        timestamp=datetime.now(timezone.utc),
    )


def after_insert_listener(mapper, connection, target):
    session = Session.object_session(target)
    if session is not None:
        if not hasattr(session, "_audit_logs"):
            session._audit_logs = []
        audit_log = _create_audit_log_obj(target, "CREATE")
        if audit_log:
            session._audit_logs.append(audit_log)


def after_update_listener(mapper, connection, target):
    session = Session.object_session(target)
    if session is not None:
        if not hasattr(session, "_audit_logs"):
            session._audit_logs = []
        audit_log = _create_audit_log_obj(target, "UPDATE")
        if audit_log:
            session._audit_logs.append(audit_log)


def after_delete_listener(mapper, connection, target):
    session = Session.object_session(target)
    if session is not None:
        if not hasattr(session, "_audit_logs"):
            session._audit_logs = []
        audit_log = _create_audit_log_obj(target, "DELETE")
        if audit_log:
            session._audit_logs.append(audit_log)


def after_flush(session, flush_context):
    if hasattr(session, "_audit_logs"):
        for audit_log in session._audit_logs:
            session.add(audit_log)
        session._audit_logs.clear()


def register_audit_listeners():
    for cls in Base.__subclasses__():
        if getattr(cls, "__tablename__", None) != "audit_log":
            event.listen(cls, "after_insert", after_insert_listener)
            event.listen(cls, "after_update", after_update_listener)
            event.listen(cls, "after_delete", after_delete_listener)
    event.listen(Session, "after_flush", after_flush)
