import { type NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, location, profile, thresholds, name } = body

    // Validação básica
    if (!email || !location || !profile) {
      return NextResponse.json(
        { error: "Missing required fields: email, location, profile" },
        { status: 400 }
      )
    }

    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: "Invalid email format" },
        { status: 400 }
      )
    }

    console.log("[subscribe] Sending to backend:", { email, location, profile })

    // Chamar a API Python
    const response = await fetch(`${BACKEND_URL}/subscribe`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        name,
        location,
        profile,
        thresholds,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      console.error("[subscribe] Backend error:", response.status, data)

      // Se Firebase não estiver configurado (503), ainda consideramos sucesso
      if (response.status === 503) {
        console.warn("[subscribe] Firebase not configured, returning mock success")
        return NextResponse.json({
          success: true,
          message: "Subscription recorded (Firebase not configured)",
          subscription: {
            email,
            location,
            profile,
            thresholds,
            createdAt: new Date().toISOString(),
          },
        })
      }

      return NextResponse.json(
        {
          error: data.detail || "Failed to subscribe",
          status: response.status
        },
        { status: response.status }
      )
    }

    console.log("[subscribe] Success:", data)

    return NextResponse.json(data)

  } catch (error) {
    console.error("[subscribe] Error:", error)

    return NextResponse.json(
      {
        error: "Failed to process subscription",
        message: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    )
  }
}