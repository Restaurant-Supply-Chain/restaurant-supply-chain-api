from passlib.context import CryptContext


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return password_context.hash(password)


def verify_password(password, password_hash):
    return password_context.verify(password, password_hash)
