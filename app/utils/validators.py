import re


def validate_password(value):
    # Signup and password reset must use the same password rules.
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^A-Za-z0-9\s]).{8,}$"
    if not re.fullmatch(pattern, value):
        raise ValueError("Password needs an uppercase letter, lowercase letter, digit, and special character")
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password must not exceed 72 bytes for bcrypt")
    return value
