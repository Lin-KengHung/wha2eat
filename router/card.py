from fastapi import *
from fastapi.responses import JSONResponse
from model.card_model import Restaurant, CardModel



router = APIRouter(
     prefix="/api", 
)



@router.get("/card")
async def get_restaurant_card():
     result = CardModel.get_restaurants_info()
     return result