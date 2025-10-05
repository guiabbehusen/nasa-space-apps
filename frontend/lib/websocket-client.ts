"use client"

import type { AirQualityData } from "./air-quality-data"
import type { WeatherData } from "./weather-data"

export type WebSocketMessage =
  | {
      type: "air-quality-update"
      data: AirQualityData & { timestamp: string }
    }
  | {
      type: "weather-update"
      data: WeatherData & { timestamp: string }
    }
  | {
      type: "alert"
      data: {
        severity: "low" | "moderate" | "high" | "very-high"
        message: string
        location: string
        timestamp: string
      }
    }

export class AirQualityWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private listeners: Map<string, Set<(data: WebSocketMessage) => void>> = new Map()

  constructor(private url: string) {}

  connect() {
    try {
      // Convert http/https to ws/wss
      const wsUrl = this.url.replace(/^http/, "ws")
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log("[v0] WebSocket connected")
        this.reconnectAttempts = 0
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.notifyListeners(message.type, message)
        } catch (error) {
          console.error("[v0] Failed to parse WebSocket message:", error)
        }
      }

      this.ws.onerror = (error) => {
        console.error("[v0] WebSocket error:", error)
      }

      this.ws.onclose = () => {
        console.log("[v0] WebSocket disconnected")
        this.attemptReconnect()
      }
    } catch (error) {
      console.error("[v0] Failed to create WebSocket:", error)
      this.attemptReconnect()
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
      console.log(`[v0] Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`)

      setTimeout(() => {
        this.connect()
      }, delay)
    } else {
      console.error("[v0] Max reconnection attempts reached")
    }
  }

  subscribe(type: string, callback: (data: WebSocketMessage) => void) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set())
    }
    this.listeners.get(type)?.add(callback)

    // Return unsubscribe function
    return () => {
      this.listeners.get(type)?.delete(callback)
    }
  }

  private notifyListeners(type: string, message: WebSocketMessage) {
    const callbacks = this.listeners.get(type)
    if (callbacks) {
      callbacks.forEach((callback) => callback(message))
    }

    // Also notify wildcard listeners
    const wildcardCallbacks = this.listeners.get("*")
    if (wildcardCallbacks) {
      wildcardCallbacks.forEach((callback) => callback(message))
    }
  }

  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn("[v0] WebSocket is not connected")
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners.clear()
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Singleton instance
let wsInstance: AirQualityWebSocket | null = null

export function getWebSocketClient(): AirQualityWebSocket {
  if (!wsInstance) {
    // In production, this would be your actual WebSocket server URL
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `${window.location.origin}/api/ws`
    wsInstance = new AirQualityWebSocket(wsUrl)
  }
  return wsInstance
}
