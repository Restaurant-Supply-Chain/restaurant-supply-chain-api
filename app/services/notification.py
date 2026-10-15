from datetime import datetime, timezone

from app.models.notification import Notification


def create_notification(db, user_id, notification_type, title, body, payload=None):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        body=body,
        payload_json=payload,
        channel="IN_APP",
        sent_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(notification)
    # Store the in-app message without sending email or SMS.
    return notification
