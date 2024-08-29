from fastapi import *
from fastapi.responses import JSONResponse
from model.card_model import CollaborativeFiltering
from model.user_model import JWTBearer
from model.share import Success, Error
import json


router = APIRouter(
     prefix="/api", 
)
security = JWTBearer()

@router.get("/collaborative_filtering/user-base", summary="推薦演算法: User-base 協同過濾", tags=["Recommendation"])
async def user_base_recommend(response: Response, payload =  Depends(security)):
    user_id = payload["id"]
    result = CollaborativeFiltering.user_base_suggest(user_id)
    if result:
          response.set_cookie(
            key="UBCF",
            value=json.dumps(result),
            expires=8 * 60 * 60,
          )
          return Success(ok=True)
    else:
        return Error(error=True, message="目前沒有推薦的餐廳")
    
@router.get("/collaborative_filtering/item-base", summary="推薦演算法，Item-base 協同過濾", tags=["Recommendation"])
async def item_base_recommend(response: Response, payload =  Depends(security)):
    user_id = payload["id"]
    result = CollaborativeFiltering.item_base_suggest(user_id)
    if result:
          response.set_cookie(
            key="IBCF",
            value=json.dumps(result),
            expires=8 * 60 * 60,
          )
          return Success(ok=True)
    else:
        return Error(error=True, message="目前沒有推薦的餐廳")
