"""
Groq-powered demand forecasting / anomaly detection (stub).

v0: sends a compact summary of a user's recent readings to a Groq-hosted
LLM and asks for (a) a next-day production/consumption estimate and
(b) a flag if today's reading looks anomalous vs. their recent pattern.

This is a stub — swap in a real numeric forecasting model later if time
allows; the LLM call is a fast way to get something plausible for a demo.
"""
import os
import json
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama-3.1-8b-instant"  # fast + cheap, good enough for demo-time forecasting

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY must be set in the environment (.env)")
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def forecast_next_day(recent_readings: list[dict]) -> dict:
    """
    recent_readings: list of dicts with date, energy_produced_kwh,
    energy_consumed_kwh (most recent last), e.g. last 7 days.
    Returns a dict with predicted_produced_kwh, predicted_consumed_kwh,
    is_anomalous (bool), and a short note.
    """
    client = _get_client()

    prompt = f"""
You are a forecasting assistant for a household solar energy system.
Given the last several days of readings (JSON below), predict tomorrow's
energy_produced_kwh and energy_consumed_kwh, and flag if the most recent
day looks anomalous compared to the trend (e.g. sudden spike/drop that
could indicate a fault or meter issue).

Readings: {json.dumps(recent_readings)}

Respond ONLY with JSON in this exact shape, no other text:
{{"predicted_produced_kwh": <number>, "predicted_consumed_kwh": <number>, "is_anomalous": <true/false>, "note": "<short reason>"}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=200,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "predicted_produced_kwh": None,
            "predicted_consumed_kwh": None,
            "is_anomalous": False,
            "note": "forecast_unavailable",
        }
