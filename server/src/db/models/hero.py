from sqlmodel import Field, SQLModel


class HeroModel(SQLModel, table=True):

    __tablename__ = "hero"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str
