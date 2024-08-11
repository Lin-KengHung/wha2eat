from fastapi import *
from fastapi.responses import JSONResponse
from model.share import Success, Error
from model.pocket_model import Match, PocketModel


router = APIRouter(
     prefix="/api", 
)



@router.put("/pocket", summary="使用者把餐廳加入口袋", tags=["Pocket"])
async def put_card_to_pocket(match:Match):
    result = PocketModel.record_match(match.user_id, match.restaurant_id, match.attitude)
    if (result):
        return  Success(ok=True)
    else:
        return Error(message="資料庫操作有錯誤")
    
    

