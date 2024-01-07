from pydantic import BaseModel
from datetime import datetime

# Modelo de datos para usuarios
class User(BaseModel):
    name: str
    password: str

class UserAccount(BaseModel):
    name: str
    aboutMe: str
    profilePicture: str

# Modelo de datos para posts
class Post(BaseModel):
    id: str
    name: str
    species: str
    age: int
    size: str
    breed: str
    image: str
    color: str
    characteristics: str
    date: datetime
    user: str