from fastapi import *
from fastapi.responses import JSONResponse
from model.card_model import RestaurantOut, CardModel, CollaborativeFiltering
from model.user_model import JWTBearer
from model.share import Error
from typing import Optional, List
import json



router = APIRouter(
     prefix="/api", 
)
security = JWTBearer()


@router.get("/cards/suggest", response_model=RestaurantOut, summary="訪客取得推薦餐廳卡片", tags=["Card"])
async def suggest_restaurant_card(
     algorithm:Optional[str] | None = None,
     lat:Optional[float] | None = None, 
     lng:Optional[float] | None = None,
     restaurant_type:Optional[str] | None = None, 
     distance_limit:Optional[int] | None = None,
     is_open:Optional[bool] | None = None
     ):

     min_google_rating = None 
     min_rating_count = None

     if algorithm == "high_google_rating":
          min_google_rating = 4.0
     elif algorithm == "high_google_rating_count":
          min_rating_count = 1000

     result = CardModel.get_suggest_restaurants_info(
          min_google_rating=min_google_rating, 
          min_rating_count=min_rating_count, 
          user_lat=lat, 
          user_lng=lng, 
          restaurant_type=restaurant_type, 
          distance_limit=distance_limit, 
          user_id=None,
          have_seen=None,
          is_open=is_open,
          restaurant_id_list=None
          )
     return result

@router.get("/cards/suggest/login", response_model=RestaurantOut, summary="用戶取得推薦餐廳卡片", tags=["Card"])
async def suggest_restaurant_card(
     request: Request,
     response: Response,
     algorithm:Optional[str] | None = None,
     lat:Optional[float] | None = None, 
     lng:Optional[float] | None = None,
     restaurant_type:Optional[str] | None = None, 
     distance_limit:Optional[int] | None = None,
     have_seen:Optional[bool] | None = None,
     is_open:Optional[bool] | None = None,
     payload =  Depends(security)
     ):

     # 判斷推薦規則
     min_google_rating = None 
     min_rating_count = None
     restaurant_id_list = None

     if algorithm == "high_google_rating":
          min_google_rating = 4.0
     elif algorithm == "high_google_rating_count":
          min_rating_count = 1000
     elif algorithm == "UBCF":
          array_str = request.cookies.get("UBCF")
          if array_str:
               print("收到UBCF cookie")
               restaurant_id_list = json.loads(array_str)
          else:
               restaurant_id_list = CollaborativeFiltering.user_base_suggest(payload["id"])
               if restaurant_id_list:
                    response.set_cookie(
                    key="UBCF",
                    value=json.dumps(restaurant_id_list),
                    expires=8 * 60 * 60,
                    )
               else:
                    return JSONResponse(status_code=400, content=Error(error=True, message="UBCF沒有推薦的餐廳").model_dump())
     elif algorithm == "IBCF":
          array_str = request.cookies.get("IBCF")
          if array_str:
               print("收到IBCF cookie")
               restaurant_id_list = json.loads(array_str)
          else:
               restaurant_id_list = CollaborativeFiltering.item_base_suggest(payload["id"])
               if restaurant_id_list:
                    response.set_cookie(
                    key="IBCF",
                    value=json.dumps(restaurant_id_list),
                    expires=8 * 60 * 60,
                    )
               else:
                    return JSONResponse(status_code=400, content=Error(error=True, message="IBCF沒有推薦的餐廳").model_dump())

     result = CardModel.get_suggest_restaurants_info(
          min_google_rating=min_google_rating, 
          min_rating_count=min_rating_count, 
          user_lat=lat, 
          user_lng=lng, 
          restaurant_type=restaurant_type, 
          distance_limit=distance_limit, 
          user_id=payload["id"],
          have_seen=have_seen,
          is_open=is_open,
          restaurant_id_list=restaurant_id_list
          )
     return result

@router.get("/card/{id}", summary="訪客根據id取得餐廳卡片", tags=["Card"])
async def get_restaurant_by_id(id:int):
     result = CardModel.get_restaurant_by_id(restaurant_id=id, user_id=None)
     return result

@router.get("/card/{id}/login", summary="用戶根據id取得餐廳卡片", tags=["Card"])
async def get_restaurant_by_id(id:int, payload = Depends(security) ):
     result = CardModel.get_restaurant_by_id(restaurant_id=id, user_id=payload["id"])
     return result

@router.get("/cards/search", summary="訪客搜尋餐廳卡片", tags=["Card"])
async def search_restaurant_card(keyword:str, page:int, lat:Optional[float] | None = None, lng:Optional[float] | None = None,):
     result = CardModel.get_search_restaurants_info(keyword=keyword, page=page, user_lat=lat, user_lng=lng, user_id=None)
     return result

@router.get("/cards/search/login", summary="用戶搜尋餐廳卡片", tags=["Card"])
async def search_restaurant_card(keyword:str, page:int, lat:Optional[float] | None = None, lng:Optional[float] | None = None, payload =  Depends(security)):
     result = CardModel.get_search_restaurants_info(keyword=keyword, page=page, user_lat=lat, user_lng=lng, user_id=payload["id"])
     return result
