from fastapi import *
from fastapi.responses import JSONResponse
from model.card_model import RestaurantOut, CardModel



router = APIRouter(
     prefix="/api", 
)



@router.get("/suggest_cards", response_model=RestaurantOut, summary="取得推薦餐廳卡片", tags=["Card"])
async def get_restaurant_card():
     result = CardModel.get_restaurants_info()
     return result

