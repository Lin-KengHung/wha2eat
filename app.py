from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from router import card
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError


app = FastAPI()

app.include_router(card.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")

@app.get("/user", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/user.html", media_type="text/html")
