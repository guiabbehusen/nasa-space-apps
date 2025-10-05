import { type NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const lat = searchParams.get("lat")
  const lng = searchParams.get("lng")

  if (!lat || !lng) {
    return NextResponse.json(
      { error: "Missing required parameters: lat and lng" },
      { status: 400 }
    )
  }

  try {
    const response = await fetch(`${BACKEND_URL}/air?lat=${lat}&lon=${lng}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      next: { revalidate: 300 },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error("[air-quality] Backend error:", response.status, errorData)

      return NextResponse.json(
        {
          error: errorData.detail || "Failed to fetch air quality data",
          status: response.status,
        },
        { status: response.status }
      )
    }

    const data = await response.json()

    console.log("[air-quality] Success:", {
      lat,
      lng,
      aqi: data.aqi,
      category: data.category,
    })

    return NextResponse.json(data)
  } catch (error) {
    console.error("[air-quality] Error:", error)

    return NextResponse.json(
      {
        error: "Failed to connect to air quality service",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 503 }
    )
  }
}
