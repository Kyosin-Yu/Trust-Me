from fastapi import FastAPI

#Create Trust Me backend appllicatrion
app = FastAPI(
    title = "Trust Me API",
    description = "AI-powered Product Trust Analysis and Decision Support Platform",
    version = "0.1.0"
)

#Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Trust Me Backend"
    }


