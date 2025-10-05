import { type NextRequest, NextResponse } from "next/server"
import { generateMockWeather } from "@/lib/weather-data"

// This route will be ready to integrate with real weather APIs
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const lat = Number.parseFloat(searchParams.get("lat") || "0")
  const lng = Number.parseFloat(searchParams.get("lng") || "0")

  // TODO: Replace with real API call
  // Example: OpenWeatherMap, WeatherAPI, or NOAA
  // const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lng}&appid=${API_KEY}`)

  const data = generateMockWeather(20)

  return NextResponse.json(data)
}
