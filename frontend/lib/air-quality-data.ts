// Mock NASA air quality data
export interface AirQualityData {
  location: {
    lat: number
    lng: number
    name: string
  }
  pollutants: {
    pm25: number // PM2.5 in μg/m³
    no2: number // NO₂ in ppb
    o3: number // O₃ in ppb
  }
  aqi: number // Air Quality Index (0-500)
  category: "Good" | "Moderate" | "Unhealthy for Sensitive Groups" | "Unhealthy" | "Very Unhealthy" | "Hazardous"
  timestamp: string
}

export function getAQICategory(aqi: number): AirQualityData["category"] {
  if (aqi <= 50) return "Good"
  if (aqi <= 100) return "Moderate"
  if (aqi <= 150) return "Unhealthy for Sensitive Groups"
  if (aqi <= 200) return "Unhealthy"
  if (aqi <= 300) return "Very Unhealthy"
  return "Hazardous"
}

export function getCategoryColor(category: AirQualityData["category"]): string {
  switch (category) {
    case "Good":
      return "text-accent"
    case "Moderate":
      return "text-chart-4"
    case "Unhealthy for Sensitive Groups":
      return "text-orange-500"
    case "Unhealthy":
      return "text-destructive"
    case "Very Unhealthy":
      return "text-purple-500"
    case "Hazardous":
      return "text-red-700"
  }
}

export function getCategoryBgColor(category: AirQualityData["category"]): string {
  switch (category) {
    case "Good":
      return "bg-accent/10 border-accent/20"
    case "Moderate":
      return "bg-chart-4/10 border-chart-4/20"
    case "Unhealthy for Sensitive Groups":
      return "bg-orange-500/10 border-orange-500/20"
    case "Unhealthy":
      return "bg-destructive/10 border-destructive/20"
    case "Very Unhealthy":
      return "bg-purple-500/10 border-purple-500/20"
    case "Hazardous":
      return "bg-red-700/10 border-red-700/20"
  }
}

// Mock data for different locations
export const mockAirQualityData: AirQualityData[] = [
  {
    location: { lat: 40.7128, lng: -74.006, name: "New York, NY" },
    pollutants: { pm25: 12, no2: 25, o3: 45 },
    aqi: 48,
    category: "Good",
    timestamp: new Date().toISOString(),
  },
  {
    location: { lat: 34.0522, lng: -118.2437, name: "Los Angeles, CA" },
    pollutants: { pm25: 35, no2: 45, o3: 65 },
    aqi: 95,
    category: "Moderate",
    timestamp: new Date().toISOString(),
  },
  {
    location: { lat: 41.8781, lng: -87.6298, name: "Chicago, IL" },
    pollutants: { pm25: 55, no2: 38, o3: 72 },
    aqi: 152,
    category: "Unhealthy for Sensitive Groups",
    timestamp: new Date().toISOString(),
  },
  {
    location: { lat: 29.7604, lng: -95.3698, name: "Houston, TX" },
    pollutants: { pm25: 28, no2: 32, o3: 58 },
    aqi: 78,
    category: "Moderate",
    timestamp: new Date().toISOString(),
  },
  {
    location: { lat: 37.7749, lng: -122.4194, name: "San Francisco, CA" },
    pollutants: { pm25: 18, no2: 22, o3: 42 },
    aqi: 62,
    category: "Moderate",
    timestamp: new Date().toISOString(),
  },
]

export function getMockDataForLocation(lat: number, lng: number): AirQualityData {
  // Find closest location or return default
  const closest = mockAirQualityData.reduce((prev, curr) => {
    const prevDist = Math.sqrt(Math.pow(prev.location.lat - lat, 2) + Math.pow(prev.location.lng - lng, 2))
    const currDist = Math.sqrt(Math.pow(curr.location.lat - lat, 2) + Math.pow(curr.location.lng - lng, 2))
    return currDist < prevDist ? curr : prev
  })

  return closest
}
