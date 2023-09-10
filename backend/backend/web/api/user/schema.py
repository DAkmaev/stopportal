from pydantic import BaseModel, ConfigDict


class UserModelDTO(BaseModel):
    """
    DTO for user models.

    It returned when accessing user models from the API.
    """

    id: int
    name: str
    email: str
    is_superuser: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserModelInputDTO(BaseModel):
    """DTO for creating new user model."""

    name: str
    email: str
    is_superuser: bool
    is_active: bool
    password: str
