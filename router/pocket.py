from fastapi import *
from fastapi.responses import JSONResponse
from model.share import Success, Error
from model.pocket_model import Match, PocketModel
from model.user_model import JWTBearer

router = APIRouter(
     prefix="/api", 
)
security = JWTBearer()


@router.put("/pocket", summary="使用者把餐廳加入口袋", tags=["Pocket"])
async def put_card_to_pocket(match:Match, payload=Depends(security)):
    result = PocketModel.record_match(match.user_id, match.restaurant_id, match.attitude)
    if (result):
        return  Success(ok=True)
    else:
        return Error(error=True, message="資料庫操作有錯誤")
    
@router.get("/pocket", summary="取得使用者口袋喜歡的餐廳", tags=["Pocket"])
async def get_favor_restaurant(page:int, payload=Depends(security)):
    result = PocketModel.get_my_pocket(id=payload["id"], page=page)
    return result