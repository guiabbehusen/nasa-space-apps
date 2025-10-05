"use client"

import { useEffect, useState } from "react"
import { getWebSocketClient, type WebSocketMessage } from "@/lib/websocket-client"
import type { AirQualityData } from "@/lib/air-quality-data"

export function useAirQualityRealtime(location?: { lat: number; lng: number }) {
  const [data, setData] = useState<AirQualityData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const ws = getWebSocketClient()

    // Connect to WebSocket
    if (!ws.isConnected()) {
      ws.connect()
    }

    // Subscribe to air quality updates
    const unsubscribe = ws.subscribe("air-quality-update", (message: WebSocketMessage) => {
      if (message.type === "air-quality-update") {
        setData(message.data as AirQualityData)
        setIsConnected(true)
        setError(null)
      }
    })

    // Request data for specific location if provided
    if (location) {
      ws.send({
        type: "subscribe-location",
        location,
      })
    }

    // Cleanup
    return () => {
      unsubscribe()
      if (location) {
        ws.send({
          type: "unsubscribe-location",
          location,
        })
      }
    }
  }, [location])

  return { data, isConnected, error }
}
