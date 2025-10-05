"use client"

import { useState, useEffect } from "react"
import dynamic from "next/dynamic"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Bell, Activity, TrendingUp, TrendingDown, Loader2 } from "lucide-react"
import Link from "next/link"
import { getCategoryColor, getCategoryBgColor, type AirQualityData } from "@/lib/air-quality-data"
import { generateTimelineData, type TimelineData } from "@/lib/weather-data"
import TimelineScrubber from "@/components/timeline-scrubber"
import LocationSearch from "@/components/location-search"

const WindMap = dynamic(() => import("@/components/wind-map"), {
  ssr: false,
  loading: () => (
    <div className="h-[500px] bg-muted rounded-lg flex items-center justify-center animate-pulse">
      <p className="text-muted-foreground">Carregando mapa...</p>
    </div>
  ),
})

export default function MapPage() {
  const [timelineData, setTimelineData] = useState<TimelineData[] | null>(null)
  const [currentIndex, setCurrentIndex] = useState<number>(24)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationName, setLocationName] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [isUpdating, setIsUpdating] = useState(false)

  /** Busca dados do backend Python via Next.js API routes */
  const fetchAirQualityAndWeather = async (lat: number, lng: number, showLoading = true) => {
    try {
      if (showLoading) setLoading(true)
      const [airRes, weatherRes] = await Promise.all([
        fetch(`/api/air?lat=${lat}&lng=${lng}`),
        fetch(`/api/weather?lat=${lat}&lng=${lng}`),
      ])

      if (!airRes.ok || !weatherRes.ok) {
        throw new Error("Erro ao buscar dados do backend")
      }

      const airData: AirQualityData = await airRes.json()
      const weatherData = await weatherRes.json()

      // Cria timeline fake baseada em dados reais
      const timeline = generateTimelineData(airData.aqi, airData.pollutants, 24, 48)

      setTimelineData(timeline)
      setLocationName(airData.location?.name || "Local atual")
    } catch (err) {
      console.error("[MapPage] Erro ao buscar dados:", err)
    } finally {
      if (showLoading) setLoading(false)
      setIsUpdating(false)
    }
  }

  /** Obter geolocalização inicial */
  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          }
          setUserLocation(location)
          fetchAirQualityAndWeather(location.lat, location.lng)
        },
        () => {
          const defaultLocation = { lat: 40.7128, lng: -74.006 } // fallback NYC
          setUserLocation(defaultLocation)
          fetchAirQualityAndWeather(defaultLocation.lat, defaultLocation.lng)
        }
      )
    }
  }

  /** Quando carregar a página */
  useEffect(() => {
    getUserLocation()
  }, [])

  /** Quando o usuário muda manualmente o local */
  const handleLocationSelect = (location: { lat: number; lng: number; name: string }) => {
    setUserLocation({ lat: location.lat, lng: location.lng })
    setLocationName(location.name)
    fetchAirQualityAndWeather(location.lat, location.lng)
    setCurrentIndex(24)
  }

  /** Quando o usuário muda o horário no timeline */
  const handleTimelineChange = async (index: number) => {
    setCurrentIndex(index)
    if (!userLocation) return
    setIsUpdating(true)
    await fetchAirQualityAndWeather(userLocation.lat, userLocation.lng, false)
  }

  /** Loader inicial */
  if (!userLocation && loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-muted-foreground">
        <Loader2 className="h-8 w-8 animate-spin mb-3" />
        <p>Carregando localização e dados do ar...</p>
      </div>
    )
  }

  // Proteção contra dados indefinidos
  const currentData = timelineData?.[currentIndex]
  const airQuality = currentData?.airQuality

  const previousData =
    timelineData && currentIndex > 0 ? timelineData[Math.max(0, currentIndex - 6)] : null

  const aqiTrend =
    airQuality && previousData ? airQuality.aqi - previousData.airQuality.aqi : 0

  const isTrendingUp = aqiTrend > 5
  const isTrendingDown = aqiTrend < -5

  return (
    <div className="container mx-auto py-12 space-y-8">
      {/* Header */}
      <div className="space-y-4">
        <h1 className="text-4xl font-bold">Air Quality Map</h1>
        <p className="text-lg text-muted-foreground">
          Real-time air quality monitoring with wind visualization and timeline analysis
        </p>
      </div>

      {/* Busca por local */}
      <div className="max-w-2xl">
        <LocationSearch onLocationSelect={handleLocationSelect} />
      </div>

      {/* Timeline */}
      {timelineData ? (
        <TimelineScrubber
          data={timelineData}
          currentIndex={currentIndex}
          onIndexChange={handleTimelineChange}
        />
      ) : (
        <div className="h-8 w-full bg-muted animate-pulse rounded-lg" />
      )}

      {/* Air Health Index */}
      <Card
        className={`border-2 transition-all ${
          airQuality ? getCategoryBgColor(airQuality.category) : "opacity-50"
        }`}
      >
        <CardContent className="pt-6">
          {loading ? (
            <div className="flex items-center justify-center py-12 text-muted-foreground animate-pulse">
              <Loader2 className="h-6 w-6 mr-2 animate-spin" /> Carregando dados do ar...
            </div>
          ) : airQuality ? (
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Air Health Index</p>
                <div className="flex items-baseline gap-3">
                  <span className="text-5xl font-bold">{airQuality.aqi}</span>
                  <Badge
                    variant="outline"
                    className={`${getCategoryColor(airQuality.category)} border-current`}
                  >
                    {airQuality.category}
                  </Badge>
                  {isTrendingUp && (
                    <div className="flex items-center gap-1 text-destructive">
                      <TrendingUp className="h-5 w-5" />
                      <span className="text-sm font-medium">+{aqiTrend}</span>
                    </div>
                  )}
                  {isTrendingDown && (
                    <div className="flex items-center gap-1 text-accent">
                      <TrendingDown className="h-5 w-5" />
                      <span className="text-sm font-medium">{aqiTrend}</span>
                    </div>
                  )}
                </div>
              </div>
              <Button asChild size="lg">
                <Link href="/alerts">
                  <Bell className="mr-2 h-5 w-5" />
                  View Health Recommendations
                </Link>
              </Button>
            </div>
          ) : (
            <p className="text-muted-foreground text-center">Sem dados disponíveis.</p>
          )}
        </CardContent>
      </Card>

      {/* Map and Pollutants */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 relative">
          {isUpdating && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/70 z-10">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}
          {currentData ? (
            <WindMap
              center={userLocation}
              timelineData={currentData}
              locationName={locationName}
              onRecenterLocation={getUserLocation}
            />
          ) : (
            <div className="h-[500px] bg-muted animate-pulse rounded-lg flex items-center justify-center">
              <p className="text-muted-foreground">Carregando mapa...</p>
            </div>
          )}
        </div>

        {/* Pollutants */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-secondary" />
                Pollutant Levels
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {airQuality
                ? Object.entries(airQuality.pollutants).map(([key, value]) => (
                    <div key={key} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium uppercase">{key}</span>
                        <span className="text-2xl font-bold">{value}</span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary transition-all"
                          style={{ width: `${Math.min((Number(value) / 100) * 100, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))
                : (
                  <div className="h-24 w-full bg-muted animate-pulse rounded-lg" />
                )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
