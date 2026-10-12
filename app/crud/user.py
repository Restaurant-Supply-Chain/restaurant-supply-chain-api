from app.models.user import User


def get_user_by_email(db, email):
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db, phone):
    return db.query(User).filter(User.phone == phone).first()


def create_user(db, data, password_hash):
    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        password_hash=password_hash,
        role=data.role,
    )
    db.add(user)
    db.commit()
    # Load database-generated values such as the user ID.
    db.refresh(user)
    return user
