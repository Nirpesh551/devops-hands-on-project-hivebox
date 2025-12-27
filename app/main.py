from fastapi import FastAPI

app = FastAPI(
    title="HiveBox API",
    description="Beekeeping sensor data aggregator (work in progress)",
    version="0.0.1"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "v0.0.1"}
