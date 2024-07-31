import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from uuid import uuid4

import uvicorn
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.dependencies import get_token_header
from app.docs.main import description
from app.log import setup_logging
from app.routers import prompt
from app.src.exception.service import SampleServiceError
from app.version import GIT_REVISION, GIT_BRANCH, BUILD_DATE, GIT_SHORT_REVISION, VERSION, get_current_datetime

# 앱 구동 성공 여부와 상관없이 앱 정보 출력
print(json.dumps(
    {"SERVICE NAME": settings.SERVICE_NAME, "SERVICE CODE": settings.SERVICE_CODE, "SERVICE VERSION": VERSION,
     "HOME_PATH": os.getcwd(), "COMMAND": ' '.join(sys.argv),
     "Usage": "uvicorn app.main:app --host 0.0.0.0 --port <port number>"}, ensure_ascii=False))


@asynccontextmanager
async def lifespan(lifespan_app: FastAPI):
    # startup event
    logging.info(f"uptime: {get_current_datetime()}")
    logging.debug(f"Working Directory: {repr(os.getcwd())}")
    logging.info(f"Start {settings.SERVICE_NAME} {VERSION}")
    yield
    # shutdown event
    logging.info(f"Shut down {settings.SERVICE_NAME} Service")


app = FastAPI(
    lifespan=lifespan,
    title=f"{settings.SERVICE_NAME}",
    summary="AI플랫폼팀 Prompt Engineering 🚀",
    description=description,
    version=VERSION,
    license_info={
        "name": "Wisenut"
    },
    docs_url=None, redoc_url=None  # Serve the static files
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.logger = setup_logging()  # type: ignore

app.include_router(prompt.router, dependencies=[Depends(get_token_header)])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.6f} sec"
    return response


async def get_request_id(request: Request):
    """요청 ID 생성

    클라이언트가 헤더로 요청한 request id가 따로 있을 경우, 해당 값을 사용하고 없을 경우, uuid 생성
    Args:
        request:

    Returns:

    """
    x_request_id = request.headers.get('X-Request-ID')
    request_id = x_request_id if x_request_id else uuid4().hex
    return request_id


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = await get_request_id(request)
    with logger.contextualize(request_id=request_id):
        # extra[request_id]가 uuid 로 부여됨
        # logging.debug(f"Start Request")   # 요청 로직 시작: 필요할 경우 사용
        response = await call_next(request)  # 응답까지 로그에 생성
        response.headers['X-Request-ID'] = request_id  # response.header 에 추가 --> client 가 로그 추적 가능
        # logging.debug(f"End Request") # 요청 로직 종료: 필요할 경우 사용
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    status_code = int(f"{settings.SERVICE_CODE}{exc.status_code}")
    if exc.status_code == 404:
        return JSONResponse(
            status_code=200, content={
                "code": status_code, "message": "Invalid URL. see api-doc `/docs` or `/openapi.json`",
                "result": {"detail": exc.detail},
            }
        )
    return JSONResponse(
        status_code=200, content={
            "code": status_code, "message": f"{exc.detail}", "result": {"headers": exc.headers}
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200, content={
            "code": int(f"{settings.SERVICE_CODE}{status.HTTP_422_UNPROCESSABLE_ENTITY}"),
            "message": f"Invalid Request: {exc.errors()[0]['msg']} (type: {exc.errors()[0]['type']}), "
                       f"Check {(exc.errors()[0]['loc'])}",
            "result": {"body": exc.body}
        }
    )


@app.exception_handler(ValidationError)
async def request_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=200, content={
            "code": int(f"{settings.SERVICE_CODE}{status.HTTP_422_UNPROCESSABLE_ENTITY}"),
            "message": "pydantic model ValidationError 발생",
            "result": {"body": exc.errors()}
        }
    )


@app.exception_handler(SampleServiceError)
async def custom_exception_handler(request: Request, exc: SampleServiceError):
    logging.error(f"{request.client} {request.method} {request.url} → {repr(exc)}")
    return JSONResponse(
        status_code=200, content={"code": int(exc.code), "message": f"{exc.message}", "result": exc.result}
    )


@app.get('/')
def index():
    return RedirectResponse('/docs')


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # pyright: ignore
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # pyright: ignore
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,  # pyright: ignore
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.get("/health")
def health():
    return {
        "status": "UP", "service": settings.SERVICE_NAME, "version": VERSION, "home_path": os.getcwd(),
        "command": f"{' '.join(sys.argv)}", "build_date": BUILD_DATE, "uptime": get_current_datetime()
    }


@app.get("/info")
async def info():
    version: str = VERSION
    if 'Unknown' in version:
        version = version.split('.')[0]
    return {
        "service": settings.SERVICE_NAME, "version": version, "git_branch": GIT_BRANCH, "git_revision": GIT_REVISION,
        "git_short_revision": GIT_SHORT_REVISION, "build_date": BUILD_DATE, "uptime": get_current_datetime()
    }


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=['X-Request-ID']
    )

if __name__ == '__main__':
    uvicorn.run(app="main:app", host="0.0.0.0", port=settings.PORT, log_level=settings.log_level)
