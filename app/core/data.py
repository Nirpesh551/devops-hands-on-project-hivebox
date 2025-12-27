import httpx
from datetime import datetime, timedelta, timezone
from typing import List

SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
]

async def get_latest_temperatures() -> List[float]:
    temperatures = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

    async with httpx.AsyncClient(timeout=10.0) as client:
        for box_id in SENSEBOX_IDS:
            try:
                r = await client.get(f"https://api.opensensemap.org/boxes/{box_id}")
                r.raise_for_status()
                box = r.json()

                for sensor in box.get("sensors", []):
                    title = sensor.get("title", "")
                    if "Temperatur" in title:  # German spelling is standard here
                        last = sensor.get("lastMeasurement", {})
                        value_str = last.get("value")
                        created_at = last.get("createdAt")

                        if value_str and created_at:
                            try:
                                ts = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                                if ts >= cutoff:
                                    temperatures.append(float(value_str))
                            except (ValueError, TypeError):
                                continue
                        break  # one temp sensor per box
            except Exception as e:
                print(f"Failed to fetch box {box_id}: {e}")

    return temperatures
