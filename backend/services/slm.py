import asyncio
import logging
from textwrap import dedent
from core.config import SLM_PROVIDER, OLLAMA_MODEL
from core.utils import get_aqi_category

logger = logging.getLogger("air-api")
from pathlib import Path
from typing import Union, Sequence, Dict, Any
import math
import numpy as np
import pandas as pd

def render_rule_based_message(name: str, location_name: str, aqi: int, category: str, timestamp: str) -> str:
    """Generate a simple rule-based email message."""
    recommendations = {
        "Good": "Enjoy outdoor activities as normal.",
        "Moderate": "Sensitive groups should reduce prolonged exposure.",
        "Unhealthy for Sensitive Groups": "People with sensitivities should limit intense activities.",
        "Unhealthy": "Avoid outdoor activities; use a mask if necessary.",
        "Very Unhealthy": "Stay indoors with air filtration if possible.",
        "Hazardous": "Emergency: avoid leaving home."
    }

    tip = recommendations.get(category, "Follow local guidance and advisories.")
    greeting = f"Hello {name or ''},".strip()
    return (
        f"{greeting}\n\nAir Quality Alert for {location_name} ({timestamp}).\n"
        f"Category: {category}\nAQI: {aqi}\n\nRecommendation: {tip}\n\n"
        "You can adjust your alert preferences in your settings."
    )

async def generate_air_quality_email(name, location_name, aqi, category, timestamp):
    """Tenta usar Ollama; se falhar, gera mensagem rule-based."""
    if SLM_PROVIDER != "ollama":
        return render_rule_based_message(name, location_name, aqi, category, timestamp)

    prompt = dedent(f"""
        You are an assistant that writes short, clear, and empathetic emails.
        Generate a friendly air quality alert email for:
        - Name: {name or 'user'}
        - Location: {location_name}
        - AQI: {aqi}
        - Category: {category}
        - Timestamp: {timestamp}
        Include emojis and practical recommendations.
    """)

    try:
        import ollama
        def sync_call():
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7},
            )
            return (response.get("message", {}).get("content", "") or "").strip()

        return await asyncio.to_thread(sync_call)
    except Exception as e:
        logger.warning("Erro ao chamar Ollama: %s", e)
        return render_rule_based_message(name, location_name, aqi, category, timestamp)


def _haversine_km(lat1: float, lon1: float, lat2_arr: np.ndarray, lon2_arr: np.ndarray) -> np.ndarray:
    """Compute haversine distance (km) from one point to arrays of points."""
    R = 6371.0
    lat1r = math.radians(lat1)
    lon1r = math.radians(lon1)
    lat2r = np.radians(lat2_arr)
    lon2r = np.radians(lon2_arr)
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    a = np.sin(dlat/2.0)**2 + np.cos(lat1r) * np.cos(lat2r) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def get_slm_history_and_summary(
    fuzzy_source: Union[str, Path, pd.DataFrame],
    user_lat: float,
    user_lon: float,
    years: Sequence[int] = (2000, 2010, 2020, 2030),
) -> Dict[str, Any]:
    """
    Return the nearest 1°×1° grid cell to the given coordinates, the historical
    fuzzy labels (final_label) for the requested years, and a short English
    summary describing the local pollution trend.

    Context:
      • Labels are derived from ANNUAL emissions (kg/km²·yr) under the SRES B2MESSAGE
        scenario — not from atmospheric concentrations.
      • For each cell and year, 'final_label' is the fuzzy class (Good→Hazardous)
        computed from CO, NMVOC, NOx, and CH4; the final decision is the worst
        (most severe) among the gases available.
      • Because the data are annual, they do not capture seasonal or daily variability.

    Parameters:
      - fuzzy_source: path to a CSV OR a DataFrame with at least these columns:
          lon, lat, year, final_label
        (Optionally may include CO_label, NMVOC_label, NOx_label, CH4_label.)
      - user_lat, user_lon: user coordinates (decimal degrees).
      - years: sequence of target years (e.g., (2000, 2010, 2020, 2030)).

    Returns:
      dict with:
        - 'nearest': {'lon', 'lat'} of the closest grid cell to the input point;
        - 'history': {year -> final_label} for the requested years
                     (uses 'No data' when a year is missing);
        - 'summary': a short text describing stability/worsening/improvement
                     based on the available historical labels.
    """

    # load
    if isinstance(fuzzy_source, pd.DataFrame):
        df = fuzzy_source.copy()
    else:
        p = Path(fuzzy_source)
        if not p.exists():
            raise FileNotFoundError(f"Fuzzy labels CSV not found: {p}")
        df = pd.read_csv(p)

    # ensure columns exist
    for c in ("lon", "lat", "year", "final_label"):
        if c not in df.columns:
            raise KeyError(f"Expected column '{c}' in fuzzy labels CSV")

    pts = df[["lon", "lat"]].drop_duplicates().reset_index(drop=True)
    if pts.empty:
        raise RuntimeError("No grid points in fuzzy labels CSV")

    dists = _haversine_km(user_lat, user_lon, pts["lat"].to_numpy(), pts["lon"].to_numpy())
    idx = int(dists.argmin())
    nearest_lon = float(pts.loc[idx, "lon"])
    nearest_lat = float(pts.loc[idx, "lat"])

    history: Dict[int, str] = {}
    for y in years:
        row = df[(df["lon"] == nearest_lon) & (df["lat"] == nearest_lat) & (df["year"] == y)]
        history[y] = str(row.iloc[0]["final_label"]) if not row.empty else "No data"

    # build summary (simple rule-based)
    severity = {"Good": 1, "Moderate": 2, "USG": 3, "Unhealthy": 4, "Very Unhealthy": 5, "Hazardous": 6}
    available = [(y, history[y]) for y in years if history[y] != "No data"]
    if not available:
        summary = "No historical data available for this location."
    else:
        first_y, first_lab = available[0]
        last_y, last_lab = available[-1]
        if all(lab == first_lab for _, lab in available):
            summary = f"Stable: category '{first_lab}' between {first_y} and {last_y}."
        else:
            s_first = severity.get(first_lab, 0)
            s_last = severity.get(last_lab, 0)
            if s_last > s_first:
                summary = f"Trend of worsening: from '{first_lab}' in {first_y} to '{last_lab}' in {last_y}."
            elif s_last < s_first:
                summary = f"Trend of improvement: from '{first_lab}' in {first_y} to '{last_lab}' in {last_y}."
            else:
                summary = "Observed variations: " + ", ".join([f"{y}:{lab}" for y, lab in available])

    return {"nearest": {"lon": nearest_lon, "lat": nearest_lat}, "history": history, "summary": summary}
