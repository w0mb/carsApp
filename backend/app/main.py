import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from app.api.router import api_router
from routers.router import front_router
from mongodb import connect, close
from app.init import redis_manager


logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    try:
        await redis_manager.connect()
    except Exception as e:
        logging.warning(f"Redis недоступен, продолжаю без кеша: {e}")
    yield
    try:
        await redis_manager.close()
    except Exception:
        pass
    await close()

app = FastAPI(docs_url=None, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/openapi.json", include_in_schema=False)
async def get_openapi():
    return JSONResponse(app.openapi())

@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve Swagger UI"""
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json", 
        title=app.title + " - Swagger UI",  
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,  
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

app.include_router(api_router, prefix="/api")

frontend_path = Path(__file__).parent.parent.parent / "frontend"
print(f"путь  {frontend_path}")

app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")

app.include_router(front_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)