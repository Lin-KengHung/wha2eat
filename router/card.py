from fastapi import *
from fastapi.responses import JSONResponse
from model.card_model import RestaurantOut, CardModel
from model.user_model import JWTBearer
from typing import Optional



router = APIRouter(
     prefix="/api", 
)
security = JWTBearer()


@router.get("/cards/suggest", response_model=RestaurantOut, summary="訪客取得推薦餐廳卡片", tags=["Card"])
async def suggest_restaurant_card(
     min_google_rating:Optional[float] | None = None, 
     min_rating_count:Optional[int] | None = None, 
     lat:Optional[float] | None = None, 
     lng:Optional[float] | None = None,
     restaurant_type:Optional[str] | None = None, 
     distance_limit:Optional[int] | None = None,
     ):
     result = CardModel.get_suggest_restaurants_info(
          min_google_rating=min_google_rating, 
          min_rating_count=min_rating_count, 
          user_lat=lat, 
          user_lng=lng, 
          restaurant_type=restaurant_type, 
          distance_limit=distance_limit, 
          user_id=None)
     return result

@router.get("/cards/suggest/login", response_model=RestaurantOut, summary="用戶取得推薦餐廳卡片", tags=["Card"])
async def suggest_restaurant_card(
     min_google_rating:Optional[float] | None = None, 
     min_rating_count:Optional[int] | None = None, 
     lat:Optional[float] | None = None, 
     lng:Optional[float] | None = None,
     restaurant_type:Optional[str] | None = None, 
     distance_limit:Optional[int] | None = None,
     payload =  Depends(security)
     ):
     result = CardModel.get_suggest_restaurants_info(
          min_google_rating=min_google_rating, 
          min_rating_count=min_rating_count, 
          user_lat=lat, 
          user_lng=lng, 
          restaurant_type=restaurant_type, 
          distance_limit=distance_limit, 
          user_id=payload["id"])
     return result

@router.get("/card/{id}", summary="根據id取得餐廳卡片", tags=["Card"])
async def get_restaurant_by_id(id:int):
     result = CardModel.get_restaurant_by_id(id)
     return result

@router.get("/cards/search", summary="訪客搜尋餐廳卡片", tags=["Card"])
async def search_restaurant_card(keyword:str, page:int, lat:Optional[float] | None = None, lng:Optional[float] | None = None,):
     result = CardModel.get_search_restaurants_info(keyword=keyword, page=page, user_lat=lat, user_lng=lng, user_id=None)
     return result

@router.get("/cards/search/login", summary="用戶搜尋餐廳卡片", tags=["Card"])
async def search_restaurant_card(keyword:str, page:int, lat:Optional[float] | None = None, lng:Optional[float] | None = None, payload =  Depends(security)):
     result = CardModel.get_search_restaurants_info(keyword=keyword, page=page, user_lat=lat, user_lng=lng, user_id=payload["id"])
     return result

@router.get("/cards/suggest/user-base", summary="推薦演算法，user-base，窮舉", tags=["Card"])
async def test(user_id:int):
     result = CardModel.get_suggest_restaurant_list(user_id)
     return result

@router.get("/cards/suggest/item-base", summary="推薦演算法，item-base，KNN", tags=["Card"])