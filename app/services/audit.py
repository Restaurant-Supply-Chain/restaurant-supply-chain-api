from app.models.audit_log import AuditLog


def record_audit(db, action, entity, entity_id=None, actor_id=None,
                 before=None, after=None, ip_address=None):
    # Pass only non-secret fields in snapshots; never include passwords or tokens.
    log = AuditLog(
        actor_id=actor_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        before_json=before,
        after_json=after,
        ip_address=ip_address,
    )
    db.add(log)
    # The calling service commits the event with its business change.
    return log
