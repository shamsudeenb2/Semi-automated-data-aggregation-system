from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    phone_number: int
    email: str
    role: str
