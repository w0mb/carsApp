
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn

from app.api.router import api_router
from mongodb import connect, close


logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    yield
    await close()

app = FastAPI(docs_url=None, lifespan=lifespan)

app.include_router(api_router)



@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # type: ignore
        title=app.title + " - Swagger UI",  # type: ignore
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,  # type: ignore
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)