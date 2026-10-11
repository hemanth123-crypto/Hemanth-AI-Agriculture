"""Submission-layout launcher; implementation remains in the canonical app package."""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.config.settings import settings

    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
