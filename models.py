from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    username: str
    password: str
    custom_token: str

class FavoriteItem(BaseModel):
    surah_number: int
    ayah_number: Optional[int] = 0  # 0 کا مطلب ہوگا کہ یہ پوری سورۃ ہے
    note: str
    custom_token: str

class TokenRequest(BaseModel):
    custom_token: str