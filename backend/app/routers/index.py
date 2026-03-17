from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

front_router = APIRouter(tags=["frontend"])

# Путь к папке frontend
FRONTEND_PATH = Path(__file__).parent.parent.parent.parent / "frontend"

# Список путей, которые НЕ должны обрабатываться frontend роутером
# Все API пути начинаются с /api, поэтому исключаем их
EXCLUDED_PREFIXES = ['/api/', '/docs', '/openapi.json', '/redoc']
print("путь ", FRONTEND_PATH)
@front_router.get("/")
async def serve_index():
    """Serve the main index.html"""
    index_file = FRONTEND_PATH / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"error": "index.html not found"}

@front_router.get("/cars/new")
async def serve_cars_new():
    """Serve the new car page"""
    cars_new_file = FRONTEND_PATH / "new_car.html"
    if cars_new_file.exists():
        return FileResponse(cars_new_file)
    return {"error": "cars_new.html not found"}

@front_router.get("/search")
async def serve_search():
    """Serve the search page"""
    search_file = FRONTEND_PATH / "search.html"
    if search_file.exists():
        return FileResponse(search_file)
    return {"error": "search.html not found"}

@front_router.get("/popular")
async def serve_popular():
    """Serve the popular cars page"""
    popular_file = FRONTEND_PATH / "popular.html"
    if popular_file.exists():
        return FileResponse(popular_file)
    return {"error": "popular.html not found"}

@front_router.get("/cars/{car_id}")
async def serve_car_detail(car_id: int):
    """Serve the car detail page (SPA)"""
    return FileResponse(FRONTEND_PATH / "car.html")

# Статические файлы уже обслуживаются через app.mount в main.py
# Поэтому эти маршруты не нужны, но если хотите оставить:
@front_router.get("/css/{file_path:path}")
async def serve_css(file_path: str):
    """Serve CSS files"""
    css_file = FRONTEND_PATH / "css" / file_path
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    return {"error": "CSS file not found"}

@front_router.get("/js/{file_path:path}")
async def serve_js(file_path: str):
    """Serve JavaScript files"""
    js_file = FRONTEND_PATH / "js" / file_path
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    return {"error": "JS file not found"}

# ВАЖНО: Этот маршрут должен быть последним
# И он НЕ должен обрабатывать пути, начинающиеся с /api/
@front_router.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve index.html for all other routes (SPA support)"""
    
    # Проверяем, не является ли путь API или системным
    if any(full_path.startswith(prefix.lstrip('/')) for prefix in EXCLUDED_PREFIXES):
        # Возвращаем 404 для API путей
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    
    # Проверяем, существует ли запрошенный HTML файл
    html_file = FRONTEND_PATH / f"{full_path}.html"
    if html_file.exists():
        return FileResponse(html_file)
    
    # Для всего остального возвращаем index.html
    return FileResponse(FRONTEND_PATH / "index.html")