from fastapi import FastAPI
from app.api.review_routes import router as review_router


# Create Trust Me backend application
app = FastAPI(
    title="Trust Me API",
    description="AI-powered Product Trust Analysis and Decision Support Platform",
    version="0.1.0",
)


# Register Review Intelligence API routes
app.include_router(review_router)


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Trust Me Backend",
    }
