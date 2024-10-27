from dbconfig import Database
from model.share import Error
from model.s3 import S3

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import bcrypt
import jwt
import datetime
import os
import re
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# ---------- schema ----------
class User(BaseModel):
    id: int
    name: str
class UserProfile(User):
    photo: Optional[str] = None
    avg_rating: Optional[float] = None
    pocket_No: int
    comment_No: int 
class Token(BaseModel):
    token: str = Field(description="包含JWT加密字串")

class Gender(Enum):
    male = "male"
    female = "female"
class UserSignUpInput(BaseModel):
    name: str
    email: str
    password: str
    gender: Optional[Gender] = None
    age: Optional[int] = None
    profile_picture: Optional[str]= None

    @field_validator("email")
    def email_match(cls, v: str):
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError("Email格式不正確")
        return v
class UserSignInInput(BaseModel):
    email: str
    password: str

# ---------- Core user behavior model  ----------
class UserModel:
    def check_email_exist(email: str) -> bool:
        if (Database.read_one("SELECT 1 FROM users WHERE email = %s", (email,))):
            return True
        else:
            return False
    
    def signup(name:str, email: str, password: str, gender: Gender, age: Optional[int] , photo: Optional[str]) -> bool:
        hash_password = make_hash_password(password)
        gender = gender.value if gender is not None else None
        result = Database.create("INSERT INTO users (username, email, password, gender, age, profile_picture) VALUES (%s, %s, %s, %s, %s, %s)", (name, email, hash_password, gender, age, photo))
        if (result > 0):
            return True
        else:
            return False
        
    def signin(email: str, password: str) -> Token | Error:
        current_user = Database.read_one("SELECT * FROM users WHERE email = %s", (email,))
        if current_user is None:
            return Error(message="此email沒有註冊過")

        
        verification = bcrypt.checkpw(password.encode(), current_user["password"].encode())
        if not verification:
            return Error(message="密碼輸入錯誤")

        token = make_JWT(id=current_user["id"], name=current_user["username"])
        return Token(token=token)

    def get_user_profile(id: int):
        sql = """
        SELECT u.username, u.avg_rating, u.profile_picture, 
        (SELECT COUNT(*) FROM pockets WHERE user_id = u.id AND attitude = 'like') AS pockets_count, 
        (SELECT COUNT(*) FROM comments WHERE user_id = u.id) AS comments_count 
        FROM users u 
        WHERE u.id = %s ;
        """
        val = (id,)
        current_user = Database.read_one(sql, val)
        return UserProfile(id=id, name=current_user["username"], photo=current_user["profile_picture"], avg_rating=current_user["avg_rating"], pocket_No=current_user["pockets_count"], comment_No=current_user["comments_count"])

    def update_avg_rating(id:int):
        sql = """
        UPDATE users
        SET avg_rating = (
            SELECT AVG(rating)
            FROM comments
            WHERE user_id = %s
        )
        WHERE id = %s;
        """
        val = (id, id)
        result = Database.update(sql, val)
        if (result > 0):
            return True
        else:
            return False

    def update_user_profile(image_file, id):
        # 刪除舊的
        delete_sql = "SELECT profile_picture FROM users WHERE id = %s "
        delete_val = (id,)
        user = Database.read_one(delete_sql, delete_val)
        if user["profile_picture"] is not None:
            S3.delete(user["profile_picture"])
        # 更新
        img_url = S3.upload(image_file)
        update_sql = "UPDATE users SET profile_picture = %s WHERE id = %s";
        update_val = (img_url, id)
        result = Database.update(update_sql,update_val)
        if(result>0):
            return True
        else:
            return False


# ---------- JWT ----------
SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"

class CustomizeRaise(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise CustomizeRaise(status_code=403, message="錯誤的authentication scheme.")
            payload = self.decode_JWT(credentials.credentials)
            if not payload:
                raise CustomizeRaise(status_code=403, message="無效token或是過期")
            return payload
        else:
            raise CustomizeRaise(status_code=403, message="未登入系統或是授權碼無效")

    def decode_JWT(self, token):
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
            return decoded_token 
        except jwt.ExpiredSignatureError:
            return {}
        except jwt.InvalidTokenError:
            return {}       

# ---------- something else  ----------

def make_hash_password(password: str):
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

def make_JWT(id, name) -> str:
    expire = datetime.datetime.now() + datetime.timedelta(days=90)
    payload={"id" : id, "name": name, "exp": expire}
    token = jwt.encode(payload=payload, key= SECRET_KEY, algorithm = ALGORITHM)
    return token