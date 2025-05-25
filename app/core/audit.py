from sqlalchemy import event
from sqlalchemy.orm import Session
from app.models import AuditLog, Base
from datetime import datetime

def _create_audit_log(session, target, action):
    # Avoid recursion for AuditLog itself
    if getattr(target, "__tablename__", None) == "audit_log":
        return
    audit = AuditLog(
        user_id=getattr(target, "user_id", None),
        table_name=target.__tablename__,
        row_id=getattr(target, "id", None),
        action=action,
        diff={c.name: getattr(target, c.name) for c in target.__table__.columns},
        timestamp=datetime.now(datetime.timezone.utc),
    )
    session.add(audit)

def after_insert_listener(mapper, connection, target):
    session = Session.object_session(target)
    if session:
        _create_audit_log(session, target, "CREATE")

def after_update_listener(mapper, connection, target):
    session = Session.object_session(target)
    if session:
        _create_audit_log(session, target, "UPDATE")

def after_delete_listener(mapper, connection, target):
    session = Session.object_session(target)
    if session:
        _create_audit_log(session, target, "DELETE")

def register_audit_listeners():
    for cls in Base.__subclasses__():
        if getattr(cls, "__tablename__", None) != "audit_log":
            event.listen(cls, "after_insert", after_insert_listener)
            event.listen(cls, "after_update", after_update_listener)
            event.listen(cls, "after_delete", after_delete_listener)