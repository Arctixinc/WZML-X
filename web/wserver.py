# ruff: noqa: E402
from uvloop import install

install()

from contextlib import asynccontextmanager
from logging import INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

getLogger("httpx").setLevel(WARNING)
getLogger("aiohttp").setLevel(WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # No external services to initialize for yt-dlp only
    yield

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="web/templates/")

basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",  #  [%(filename)s:%(lineno)d]
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

LOGGER = getLogger(__name__)


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.exception_handler(Exception)
async def page_not_found(_, exc):
    return HTMLResponse(
        f"<h1>404: Page not found! <br><br>Error: {exc}</h1>",
        status_code=404,
    )
