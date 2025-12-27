from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from random import uniform
from app.core.data import get_latest_temperatures

app = FastAPI(
    title="HiveBox API",
    description="Beekeeping sensor data aggregator (work in progress)",
    version="0.0.1"
)

Instrumentator().instrument(app).expose(app)

class SensorReading(BaseModel):
    temperature_c: float
    humidity_percent: float
    status: str

@app.get("/version")
async def get_version():
    return {"version": "v0.0.1"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "v0.0.1"}

@app.get("/sensors", response_model=SensorReading)
async def get_sensor_data():
    temp = round(uniform(15.0, 38.0), 1)
    humidity = round(uniform(40.0, 90.0), 1)

    if temp < 20:
        status = "Too Cold"
    elif temp > 35:
        status = "Too Hot"
    else:
        status = "Good"
    return SensorReading(
        temperature_c=temp,
        humidity_percent=humidity,
        status=status
    )

@app.get("/temperature")
async def get_average_temperature():
    """
    Returns the average temperature from all senseBoxes (only data ≤ 1h old)
    """
    temps = await get_latest_temperatures()

    if not temps:
        raise HTTPException(status_code=503, detail="No recent temperature data available")

    avg_temp = round(sum(temps) / len(temps), 1)
    return {"average_temperature_c": avg_temp, "number_of_boxes_used": len(temps)}
