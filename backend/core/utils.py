def calculate_aqi_from_pm25(pm25: float) -> int:
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500)
    ]
    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= pm25 <= bp_hi:
            return round(((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo)
    return 500 if pm25 > 500.4 else 50

def get_aqi_category(aqi: int) -> str:
    if aqi <= 50: return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups"
    elif aqi <= 200: return "Unhealthy"
    elif aqi <= 300: return "Very Unhealthy"
    else: return "Hazardous"

def get_location_name(lat: float, lon: float) -> str:
    known = {
        (-23.55, -46.63): "São Paulo, Brazil",
        (40.71, -74.00): "New York, USA",
        (51.50, -0.12): "London, UK",
        (35.67, 139.65): "Tokyo, Japan",
        (-33.86, 151.20): "Sydney, Australia"
    }
    for (k_lat, k_lon), name in known.items():
        if abs(lat - k_lat) < 0.1 and abs(lon - k_lon) < 0.1:
            return name
    return f"{lat:.4f}, {lon:.4f}"
