from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from backend.config import get_settings

from backend.routes import router


settings = get_settings()


app = FastAPI(

    title=settings.app_name,

    description=(
        "AI-assisted legal document "
        "drafting and export API."
    ),

    version="1.0.0",
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(
    router
)


@app.get("/")
def root():

    return {

        "app": settings.app_name,

        "status": "running",

        "message": (
            "LegalEase API is ready."
        ),

        "docs": "/docs",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }