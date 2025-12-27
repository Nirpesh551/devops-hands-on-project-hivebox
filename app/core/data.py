import httpx
from datetime import datetime, timedelta, timezone
from typing import List

SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
]

async def get_latest_temperatures() -> List[float]:
    """
    Fetch the most recent temperature (°C) from each senseBox.
    Only include values not older than 1 hour.
    """
    temperatures = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

    async with httpx.AsyncClient() as client:
        for box_id in SENSEBOX_IDS:
            try:
                response = await client.get(f"https://api.opensensemap.org/boxes/{box_id}")
                response.raise_for_status()
                data = response.json()

                for sensor in data.get("sensors", []):
                    if "Temperatur" in sensor.get("title", ""):  # German spelling
                        last = sensor.get("lastMeasurement", {})
                        value_str = last.get("value")
                        timestamp_str = last.get("createdAt")

                        if value_str and timestamp_str:
                            try:
                                ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                                if ts >= cutoff:
                                    temperatures.append(float(value_str))
                            except (ValueError, TypeError):
                                pass  # skip invalid values/timestamps
                        break  # assume only one temp sensor per box

            except Exception as e:
                print(f"Error fetching box {box_id}: {e}")

    return temperatures
