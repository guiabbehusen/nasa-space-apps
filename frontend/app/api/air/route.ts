import { type NextRequest, NextResponse } from "next/server"

const BACKEND_URL = "http://api.tempo11.earth:8000"

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
}

export async function OPTIONS() {
  return NextResponse.json({}, { status: 200, headers: corsHeaders })
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const lat = searchParams.get("lat")
  const lng = searchParams.get("lng")

  if (!lat || !lng) {
    return NextResponse.json(
      { error: "Missing required parameters: lat and lng" },
      { status: 400, headers: corsHeaders }
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
      return NextResponse.json(
        {
          error: errorData.detail || "Failed to fetch air quality data",
        },
        { status: response.status, headers: corsHeaders }
      )
    }

    const data = await response.json()
    return NextResponse.json(data, { headers: corsHeaders })
  } catch (error) {
    return NextResponse.json(
      {
        error: "Failed to connect to air quality service",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 503, headers: corsHeaders }
    )
  }
}
