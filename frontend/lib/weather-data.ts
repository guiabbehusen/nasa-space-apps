// Weather data types and utilities
export interface WeatherData {
  temperature: number // in Celsius
  feelsLike: number
  humidity: number // percentage
  windSpeed: number // km/h
  windDirection: number // degrees
  windGust?: number // km/h
  pressure: number // hPa
  visibility: number // km
  cloudCover: number // percentage
  uvIndex: number
  timestamp: string
}

export interface TimelineData {
  airQuality: {
    aqi: number
    category: string
    pollutants: {
      pm25: number
      no2: number
      o3: number
    }
  }
  weather: WeatherData
  timestamp: string
}

// Generate mock weather data
export function generateMockWeather(baseTemp = 20): WeatherData {
  const variation = Math.random() * 10 - 5
  const temp = baseTemp + variation

  return {
    temperature: Math.round(temp * 10) / 10,
    feelsLike: Math.round((temp + (Math.random() * 4 - 2)) * 10) / 10,
    humidity: Math.round(40 + Math.random() * 40),
    windSpeed: Math.round((5 + Math.random() * 20) * 10) / 10,
    windDirection: Math.round(Math.random() * 360),
    windGust: Math.round((10 + Math.random() * 30) * 10) / 10,
    pressure: Math.round(1000 + Math.random() * 30),
    visibility: Math.round((5 + Math.random() * 15) * 10) / 10,
    cloudCover: Math.round(Math.random() * 100),
    uvIndex: Math.round(Math.random() * 11),
    timestamp: new Date().toISOString(),
  }
}

// Generate historical and forecast data
export function generateTimelineData(
  currentAqi: number,
  currentPollutants: { pm25: number; no2: number; o3: number },
  hoursBack = 24,
  hoursForward = 48,
): TimelineData[] {
  const data: TimelineData[] = []
  const now = new Date()

  // Generate historical data
  for (let i = hoursBack; i > 0; i--) {
    const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000)
    const aqiVariation = Math.random() * 20 - 10
    const aqi = Math.max(0, Math.round(currentAqi + aqiVariation))

    data.push({
      airQuality: {
        aqi,
        category: getAQICategory(aqi),
        pollutants: {
          pm25: Math.max(0, Math.round(currentPollutants.pm25 + (Math.random() * 10 - 5))),
          no2: Math.max(0, Math.round(currentPollutants.no2 + (Math.random() * 10 - 5))),
          o3: Math.max(0, Math.round(currentPollutants.o3 + (Math.random() * 10 - 5))),
        },
      },
      weather: generateMockWeather(18 + Math.random() * 8),
      timestamp: timestamp.toISOString(),
    })
  }

  // Add current data
  data.push({
    airQuality: {
      aqi: currentAqi,
      category: getAQICategory(currentAqi),
      pollutants: currentPollutants,
    },
    weather: generateMockWeather(22),
    timestamp: now.toISOString(),
  })

  // Generate forecast data
  for (let i = 1; i <= hoursForward; i++) {
    const timestamp = new Date(now.getTime() + i * 60 * 60 * 1000)
    const aqiVariation = Math.random() * 15 - 7
    const aqi = Math.max(0, Math.round(currentAqi + aqiVariation))

    data.push({
      airQuality: {
        aqi,
        category: getAQICategory(aqi),
        pollutants: {
          pm25: Math.max(0, Math.round(currentPollutants.pm25 + (Math.random() * 8 - 4))),
          no2: Math.max(0, Math.round(currentPollutants.no2 + (Math.random() * 8 - 4))),
          o3: Math.max(0, Math.round(currentPollutants.o3 + (Math.random() * 8 - 4))),
        },
      },
      weather: generateMockWeather(20 + Math.random() * 6),
      timestamp: timestamp.toISOString(),
    })
  }

  return data
}

function getAQICategory(aqi: number): string {
  if (aqi <= 50) return "Good"
  if (aqi <= 100) return "Moderate"
  if (aqi <= 150) return "Unhealthy for Sensitive Groups"
  if (aqi <= 200) return "Unhealthy"
  if (aqi <= 300) return "Very Unhealthy"
  return "Hazardous"
}

// Get wind direction as compass direction
export function getWindDirection(degrees: number): string {
  const directions = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
  ]
  const index = Math.round(degrees / 22.5) % 16
  return directions[index]
}

// Get UV Index description
export function getUVIndexDescription(uvIndex: number): string {
  if (uvIndex <= 2) return "Low"
  if (uvIndex <= 5) return "Moderate"
  if (uvIndex <= 7) return "High"
  if (uvIndex <= 10) return "Very High"
  return "Extreme"
}
