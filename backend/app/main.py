"""FastAPI application entry point.

负责装配应用基础结构：
- 结构化日志（structlog，按 ``settings.DEBUG`` 切换 console/JSON）
- CORS 中间件（来源由 ``settings.CORS_ORIGINS`` 控制）
- 全局异常处理（业务异常 / 请求校验失败 / 兜底 500）
- OpenAPI 文档（``/docs``、``/redoc``、``${API_PREFIX}/openapi.json``）

业务路由的注册保持原有结构，每个 router 自行声明前缀。
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin_dictionaries import router as admin_dictionaries_router
from app.api.admin_monitoring import router as admin_monitoring_router
from app.api.admin_profiles import router as admin_profiles_router
from app.api.admin_reviews import router as admin_reviews_router
from app.api.admin_universal_parser import router as admin_universal_parser_router
from app.api.admin_users import router as admin_users_router
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.feedback import router as feedback_router
from app.api.health import router as health_router
from app.api.ik_dict import router as ik_dict_router
from app.api.permissions import router as permissions_router
from app.api.qa import router as qa_router
from app.api.rag import router as rag_router
from app.api.search import router as search_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    # 必须在创建 FastAPI 之前配置日志，确保启动期间的日志也走 structlog
    configure_logging()
    logger = get_logger(__name__)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "企业级知识库系统：文档导入、解析、清洗、向量化、复合搜索（BM25 + Dense + "
            "Sparse + RRF）与 RAG 问答。"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        debug=settings.DEBUG,
    )

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- 全局异常处理 ----
    register_exception_handlers(app)

    # ---- 业务路由 ----
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(permissions_router)
    app.include_router(documents_router)
    app.include_router(search_router)
    app.include_router(rag_router)
    app.include_router(qa_router)
    app.include_router(admin_profiles_router)
    app.include_router(admin_reviews_router)
    app.include_router(admin_dictionaries_router)
    app.include_router(admin_universal_parser_router)
    app.include_router(admin_users_router)
    app.include_router(admin_monitoring_router)
    app.include_router(feedback_router)
    app.include_router(ik_dict_router)

    logger.info(
        "app_initialized",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        api_prefix=settings.API_PREFIX,
        cors_origins=settings.CORS_ORIGINS,
    )
    return app


app = create_app()
