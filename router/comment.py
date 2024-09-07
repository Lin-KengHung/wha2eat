from fastapi import *
from fastapi.responses import JSONResponse
from model.comment_model import Comment, CommentModel
from model.user_model import JWTBearer, UserModel
from model.s3 import S3
from model.share import Success, Error
from typing import Optional



router = APIRouter(
     prefix="/api", 
)
security = JWTBearer()

@router.post("/comment", summary="新增留言", response_model=Success, responses={400:{"model":Error}}, tags=["Comment"])
async def add_comment(    
     user_id: int = Form(...),
     restaurant_id: int = Form(...),
     place_id: str = Form(...),
     rating: int = Form(...),
     context: str = Form(...),
     checkin: bool = Form(),
     image: Optional[UploadFile] = File(None),
     payload=Depends(security)
     ):

     comment = Comment(
        user_id=user_id,
        restaurant_id=restaurant_id,
        place_id=place_id,
        rating=rating,
        context=context,
        checkin=checkin,
        image=None
    )
     
     if (image):
          url = S3.upload(image)
          comment.image = url

     print(comment)
     result = CommentModel.record_comment(comment)
     
     if result is True:
          # 更新打分
          UserModel.update_avg_rating(payload["id"])
          return Success(ok=True)
     else:
          return Error(error=True, message="新增留言有錯")
     
@router.get("/comment/restaurant", summary="獲取餐廳的留言", tags=["Comment"])
async def get_restaurant_comment(restaurant_id: int):
     result = CommentModel.get_restaurant_comment(restaurant_id)
     return result

@router.get("/comment/member", summary="獲取使用者的留言", tags=["Comment"])
async def get_user_comment(payload=Depends(security)):
     result = CommentModel.get_user_comment(payload["id"])
     return result

@router.delete("/comment", summary="刪除使用者的留言", tags=["Comment"], responses={400:{"model":Error}})
async def delete_comment(comment_id:int, payload=Depends(security)):
     # 刪除資料庫資料
     photo_url = CommentModel.delete(comment_id=comment_id, user_id=payload["id"])
     if photo_url == "error":
          return JSONResponse(status_code=400, content=Error(error=True, message="無法刪除留言，抓不到資料").model_dump())
     elif photo_url == "no image":
          # 更新使用者平均打分
          UserModel.update_avg_rating(payload["id"])
          return Success(ok=True)
     else:
          # 更新使用者平均打分
          UserModel.update_avg_rating(payload["id"])
          # 刪除s3資料
          result = S3.delete(photo_url)
          if result:
               return Success(ok=True)
          else:
               return JSONResponse(status_code=400, content=Error(error=True, message="S3刪除失敗").model_dump())