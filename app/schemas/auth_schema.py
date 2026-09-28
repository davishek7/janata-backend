from pydantic import EmailStr, BaseModel


class LoginSchema(BaseModel):
    username: EmailStr | str

    password: str
