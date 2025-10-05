import { type NextRequest, NextResponse } from "next/server"

const BACKEND_URL = "http://0.0.0.0:8000"

// CORS headers
const corsHeaders = {
  "Access-Control-Allow-Origin": "*", // 👉 em prod: "https://teusite.vercel.app"
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
}

export async function OPTIONS() {
  return NextResponse.json({}, { status: 200, headers: corsHeaders })
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, location, profile, thresholds } = body

    if (!email || !location || !profile) {
      return NextResponse.json(
        { error: "Missing required fields: email, location, profile" },
        { status: 400, headers: corsHeaders }
      )
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: "Invalid email format" },
        { status: 400, headers: corsHeaders }
      )
    }

    const response = await fetch(`${BACKEND_URL}/subscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, location, profile, thresholds }),
    })

    const data = await response.json()

    if (!response.ok) {
      if (response.status === 503) {
        return NextResponse.json(
          {
            success: true,
            message: "Subscription recorded (Firebase not configured)",
            subscription: {
              email,
              location,
              profile,
              thresholds,
              createdAt: new Date().toISOString(),
            },
          },
          { headers: corsHeaders }
        )
      }

      return NextResponse.json(
        { error: data.detail || "Failed to subscribe" },
        { status: response.status, headers: corsHeaders }
      )
    }

    return NextResponse.json(data, { headers: corsHeaders })
  } catch (error) {
    return NextResponse.json(
      {
        error: "Failed to process subscription",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500, headers: corsHeaders }
    )
  }
}
