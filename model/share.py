from pydantic import BaseModel

class Error(BaseModel):
    error : bool = True
    message : str

class Success(BaseModel):
    ok: bool = True