import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Body, Response, Depends
from fastapi.responses import RedirectResponse
from shorter.service import UrlService
from shorter.repository import UrlRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Сервис для сокращения ссылок",
              description="Простой сервис для сокращения длинных URL.",
              version="1.0.0")

def get_service():
    db_path = Path(__file__).parent.parent.parent / "data" / "shorter.db"
    db_path.parent.mkdir(exist_ok=True)
    repository = UrlRepository(str(db_path))
    return UrlService(repository)

@app.post("/shorten/",
          summary="Сократить URL",
          description="Преобразует длинный URL в короткий и возвращает сокращённую ссылку.",
          tags=["URL"])
def shorten_url(long_url: str = Body(..., embed=True),
                service: UrlService = Depends(get_service)):
    logger.info(f"Request received to shorten URL: {long_url}")
    try:
        short_code = service.shorten_url(long_url)
        return {"shortened_url": f"/{short_code}"}
    except ValueError as e:
        logger.error(f"Error occurred during URL shortening: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/{short_code}/",
         summary="Редирект по короткому коду",
         description="Производит редирект на оригинальный URL по заданному короткому коду.",
         responses={301: {"description": "Редирект осуществлён"},
                    404: {"description": "Короткий код не найден"}},
         tags=["URL"])
def redirect_to_long_url(short_code: str, service: UrlService = Depends(get_service)):
    logger.info(f"Redirect requested for short code: {short_code}")
    try:
        original_url = service.handle_redirect(short_code)
        if original_url is None:
            raise HTTPException(status_code=404, detail="Короткий код не найден")
        return RedirectResponse(url=original_url, status_code=301)
    except ValueError as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.get("/qr_code/{short_code}/", response_class=Response,
         summary="Генерирует QR код по короткой ссылке",
         description="Генерирует QR код по короткой ссылке.",
         responses={404: {"description": "Короткий код не найден"}},
         tags=["URL"])
def qr_code_generator(short_code: str, service: UrlService = Depends(get_service)):
    """
    Генерирует QR-код для заданного короткого кода.
    """
    try:
        image_bytes = service.generate_qr_code(short_code)
        return Response(content=image_bytes, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Короткий код не найден")
