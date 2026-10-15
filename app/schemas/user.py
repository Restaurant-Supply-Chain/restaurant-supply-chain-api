from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.constants import UserRole, UserStatus
from app.utils.validators import validate_password


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr = Field(max_length=254)
    phone: str | None = Field(default=None, pattern=r"^\+?[1-9]\d{7,14}$", max_length=20)
    password: str = Field(min_length=8)
    # All six roles can be selected in this practice project's signup.
    role: UserRole = UserRole.RESTAURANT_ADMIN

    @field_validator("email", "full_name", mode="before")
    @classmethod
    def clean_text(cls, value, info):
        # Normalize email before validation and duplicate checks.
        if isinstance(value, str):
            value = value.strip()
            if info.field_name == "email":
                value = value.lower()
        return value

    # Check allowed characters after the name has been trimmed.
    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value):
        if not any(character.isalpha() for character in value):
            raise ValueError("Full name must contain letters")
        for character in value:
            if not character.isalpha() and character not in " .'-":
                raise ValueError("Full name may contain letters, spaces, dots, apostrophes, and hyphens")
        return value

    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        return validate_password(value)


class UserResponse(BaseModel):
    # Read fields from a SQLAlchemy User; omit password fields from the response.
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    full_name: str
    email: EmailStr
    phone: str | None
    role: UserRole
    status: UserStatus
