from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from router import card, user, pocket, comment, recommend
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from model.user_model import CustomizeRaise
from model.share import Error


app = FastAPI()

app.include_router(card.router)
app.include_router(recommend.router)
app.include_router(user.router)
app.include_router(pocket.router)
app.include_router(comment.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(CustomizeRaise)
async def error_raise(requset: Request, exc: CustomizeRaise):
	return JSONResponse(status_code=exc.status_code, content=Error(message=exc.message).model_dump())

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	error = exc.errors()[0]
	message = f'錯誤欄位:{error["loc"]}, 錯誤訊息: {error["msg"]}, 錯誤類型: {error["type"]}'
	return JSONResponse(status_code=400,content=Error(message=message).model_dump())

@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")

@app.get("/member", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/member.html", media_type="text/html")

@app.get("/restaurant/{id}", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/restaurants.html", media_type="text/html")