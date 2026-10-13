from getpass import getpass

from app.core.constants import UserRole, UserStatus
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import UserRegister


def create_platform_admin(email, password):
    # Reuse signup validation, then assign the admin role through this local script.
    data = UserRegister(full_name="Platform Admin", email=email, password=password)
    with SessionLocal() as db:
        if db.query(User).filter(User.email == data.email).first():
            raise ValueError("This email already exists. Choose a different admin email.")

        admin = User(
            full_name=data.full_name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=UserRole.PLATFORM_ADMIN,
            status=UserStatus.ACTIVE,
        )
        db.add(admin)
        db.commit()
        print("Platform admin created:", data.email)


if __name__ == "__main__":
    email = input("Admin email [platform.admin@example.com]: ").strip()
    password = getpass("Admin password: ")
    create_platform_admin(email or "platform.admin@example.com", password)
