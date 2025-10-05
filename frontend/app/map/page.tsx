"use client"

import { useState, useEffect } from "react"
import dynamic from "next/dynamic"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Bell, Activity, TrendingUp, TrendingDown } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { getCategoryColor, getCategoryBgColor } from "@/lib/air-quality-data"
// 👇 remove os mocks generateTimelineData/getMockDataForLocation
import TimelineScrubber from "@/components/timeline-scrubber"
import LocationSearch from "@/components/location-search"
import type { AirQualityData } from "@/lib/air-quality-data"
import type { TimelineData } from "@/lib/weather-data"

const WindMap = dynamic(() => import("@/components/wind-map"), {
  ssr: false,
  loading: () => (
    <div className="h-[500px] bg-muted rounded-lg flex items-center justify-center">
      <p className="text-muted-foreground">Loading map...</p>
    </div>
  ),
})

export default function MapPage() {
  const [timelineData, setTimelineData] = useState<TimelineData[] | null>(null)
  const [currentIndex, setCurrentIndex] = useState<number>(0)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationName, setLocationName] = useState<string>("")

  // 👇 nova função para buscar das rotas internas e montar a timeline no mesmo formato usado pela UI
  const fetchAirQualityAndWeather = async (lat: number, lng: number) => {
    const [airRes, weatherRes] = await Promise.all([
      fetch(`/api/air?lat=${lat}&lng=${lng}`),
      fetch(`/api/weather?lat=${lat}&lng=${lng}`),
    ])
    if (!airRes.ok) throw new Error(`/api/air ${airRes.status}`)
    if (!weatherRes.ok) throw new Error(`/api/weather ${weatherRes.status}`)

    const airData = await airRes.json()
    const weatherData = await weatherRes.json()

    const merged: TimelineData[] =
      (airData.timeline || []).map((a: any, i: number) => {
        const w = weatherData.timeline?.[i] || {}
        return {
          timestamp: a.timestamp,
          airQuality: {
            aqi: a.aqi,
            category: a.category,
            pollutants: a.pollutants, // { pm25, pm10, o3, ... }
          },
          weather: {
            temperature: w.t_2m,
            feelsLike: w.t_apparent ?? w.t_2m,
            windSpeed: w.wind_speed_10m,
            windDirection: w.wind_dir_10m,
            humidity: w.relative_humidity_2m,
            pressure: w.msl_pressure,
            cloudCover: w.total_cloud_cover,
          },
        } as TimelineData
      }) || []

    setTimelineData(merged)
    setCurrentIndex(Math.floor((merged.length ?? 0) / 2))
    setLocationName(airData.location?.name || weatherData.location?.name || "Current location")
  }

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = { lat: position.coords.latitude, lng: position.coords.longitude }
          setUserLocation(location)
          fetchAirQualityAndWeather(location.lat, location.lng).catch((e) => console.error("[map] fetch err", e))
        },
        () => {
          const defaultLocation = { lat: 40.7128, lng: -74.006 }
          setUserLocation(defaultLocation)
          fetchAirQualityAndWeather(defaultLocation.lat, defaultLocation.lng).catch((e) => console.error("[map] fetch err", e))
        },
      )
    }
  }

  useEffect(() => {
    getUserLocation()
  }, [])

  const handleLocationSelect = (location: { lat: number; lng: number; name: string; data: AirQualityData }) => {
    setUserLocation({ lat: location.lat, lng: location.lng })
    setLocationName(location.name)
    fetchAirQualityAndWeather(location.lat, location.lng).catch((e) => console.error("[map] fetch err", e))
    setCurrentIndex(24)
  }

  if (!timelineData || !userLocation) {
      return (
        <div className="min-h-screen bg-nasa-midnight-blue nasa-pattern-orbits flex flex-col items-center justify-center text-center space-y-6">
          <div className="w-24 h-24 border-4 border-nasa-electric-blue border-t-transparent rounded-full animate-spin" />
          <div className="space-y-2">
            <h2 className="text-white text-2xl font-semibold font-heading">Initializing Systems...</h2>
            <p className="text-white/70 text-sm md:text-base">
              Syncing air quality sensors and wind data...
            </p>
          </div>
        </div>
      )
    }


  const currentData = timelineData[currentIndex]
  const { airQuality } = currentData

  const previousData = timelineData[Math.max(0, currentIndex - 6)]
  const aqiTrend = currentData.airQuality.aqi - previousData.airQuality.aqi
  const isTrendingUp = aqiTrend > 5
  const isTrendingDown = aqiTrend < -5

  return (
    <div className="min-h-screen bg-nasa-midnight-blue nasa-pattern-orbits">
      <div className="container mx-auto py-6 md:py-12 px-4 md:px-6 space-y-6 md:space-y-8">
        {/* Header */}
        <div className="space-y-3 md:space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl md:text-4xl font-bold text-balance text-white font-heading">Air Quality Map</h1>
              <p className="text-sm md:text-lg text-white/80 text-pretty mt-1 md:mt-0">
                Real-time air quality monitoring with wind visualization and timeline analysis
              </p>
            </div>
            <Image
              src="/logos/nasa-worm-white.svg"
              alt="NASA"
              width={80}
              height={80}
              className="hidden md:block opacity-60"
            />
          </div>
        </div>

        <div className="max-w-2xl">
          <LocationSearch onLocationSelect={handleLocationSelect} />
        </div>

        {/* Timeline Scrubber */}
        <TimelineScrubber data={timelineData} currentIndex={currentIndex} onIndexChange={setCurrentIndex} />

        {/* Air Health Index Card */}
        <Card className={`border-2 ${getCategoryBgColor(airQuality.category)}`}>
          <CardContent className="pt-4 md:pt-6 px-4 md:px-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-6">
              <div className="space-y-2">
                <p className="text-xs md:text-sm font-medium text-muted-foreground">Air Health Index</p>
                <div className="flex items-baseline gap-2 md:gap-3">
                  <span className="text-3xl md:text-5xl font-bold">{airQuality.aqi}</span>
                  <Badge
                    variant="outline"
                    className={`${getCategoryColor(airQuality.category)} border-current text-xs md:text-sm`}
                  >
                    {airQuality.category}
                  </Badge>
                  {isTrendingUp && (
                    <div className="flex items-center gap-1 text-destructive">
                      <TrendingUp className="h-4 w-4 md:h-5 md:w-5" />
                      <span className="text-xs md:text-sm font-medium">+{aqiTrend}</span>
                    </div>
                  )}
                  {isTrendingDown && (
                    <div className="flex items-center gap-1 text-accent">
                      <TrendingDown className="h-4 w-4 md:h-5 md:w-5" />
                      <span className="text-xs md:text-sm font-medium">{aqiTrend}</span>
                    </div>
                  )}
                </div>
              </div>
              <Button asChild size="default" className="w-full md:w-auto">
                <Link href="/alerts">
                  <Bell className="mr-2 h-4 w-4 md:h-5 md:w-5" />
                  <span className="text-sm md:text-base">View Health Recommendations</span>
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Map and Pollutants Grid */}
        <div className="grid lg:grid-cols-3 gap-4 md:gap-6">
          <div className="lg:col-span-2">
            <WindMap
              center={userLocation}
              timelineData={currentData}
              locationName={locationName}
              onRecenterLocation={getUserLocation}
            />
          </div>

          {/* Pollutant Levels */}
          <div className="space-y-4 md:space-y-6">
            <Card className="relative overflow-hidden border-2 border-nasa-electric-blue/30 bg-nasa-deep-space/50 backdrop-blur shadow-xl">
              <div className="absolute inset-0 bg-[url('/patterns/orbits.png')] opacity-25 bg-repeat" />
              <CardHeader className="relative pb-4">
                <CardTitle className="flex items-center gap-2 text-white text-lg md:text-xl">
                  <Activity className="h-5 w-5 md:h-6 md:w-6 text-nasa-electric-blue" />
                  Pollutant Levels
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 md:space-y-6 relative">
                {/* PM2.5 */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">PM2.5</span>
                    <span className="text-xl md:text-2xl font-bold text-white">{airQuality.pollutants.pm25}</span>
                  </div>
                  <div className="text-xs text-white/60">μg/m³</div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-nasa-electric-blue transition-all"
                      style={{ width: `${Math.min((airQuality.pollutants.pm25 / 100) * 100, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-white/70 text-pretty">
                    Fine particulate matter that can penetrate deep into lungs
                  </p>
                </div>

                {/* NO₂ */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">NO₂</span>
                    <span className="text-xl md:text-2xl font-bold text-white">{airQuality.pollutants.no2}</span>
                  </div>
                  <div className="text-xs text-white/60">ppb</div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-nasa-bright-blue transition-all"
                      style={{ width: `${Math.min((airQuality.pollutants.no2 / 100) * 100, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-white/70 text-pretty">
                    Nitrogen dioxide from vehicle emissions and industrial sources
                  </p>
                </div>

                {/* O₃ */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">O₃</span>
                    <span className="text-xl md:text-2xl font-bold text-white">{airQuality.pollutants.o3}</span>
                  </div>
                  <div className="text-xs text-white/60">ppb</div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-nasa-neon-yellow transition-all"
                      style={{ width: `${Math.min((airQuality.pollutants.o3 / 100) * 100, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-white/70 text-pretty">
                    Ground-level ozone that can irritate respiratory system
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
