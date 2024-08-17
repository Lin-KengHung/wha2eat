from fastapi import *
from fastapi.responses import JSONResponse
from model.card_model import RestaurantOut, CardModel



router = APIRouter(
     prefix="/api", 
)



@router.get("/cards/suggest", response_model=RestaurantOut, summary="取得推薦餐廳卡片", tags=["Card"])
async def suggest_restaurant_card():
     result = CardModel.get_suggest_restaurants_info()
     return result

@router.get("/card/{id}", summary="根據id取得餐廳卡片", tags=["Card"])
async def get_restaurant_by_id(id:int):
     result = CardModel.get_restaurant_by_id(id)
     return result

@router.get("/cards/search",  summary="搜尋餐廳卡片", tags=["Card"])
async def search_restaurant_card():

     return "ok"