"use client"

import { useState, useEffect } from "react"
import dynamic from "next/dynamic"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Bell, Activity, TrendingUp, TrendingDown } from "lucide-react"
import Link from "next/link"
import {
  getMockDataForLocation,
  getCategoryColor,
  getCategoryBgColor,
  type AirQualityData,
} from "@/lib/air-quality-data"
import { generateTimelineData, type TimelineData } from "@/lib/weather-data"
import TimelineScrubber from "@/components/timeline-scrubber"
import LocationSearch from "@/components/location-search"

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
  const [currentIndex, setCurrentIndex] = useState<number>(24)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationName, setLocationName] = useState<string>("")

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          }
          setUserLocation(location)

          const currentData = getMockDataForLocation(location.lat, location.lng)
          setLocationName(currentData.location.name)

          const timeline = generateTimelineData(currentData.aqi, currentData.pollutants, 24, 48)
          setTimelineData(timeline)
        },
        () => {
          const defaultLocation = { lat: 40.7128, lng: -74.006 }
          setUserLocation(defaultLocation)

          const currentData = getMockDataForLocation(defaultLocation.lat, defaultLocation.lng)
          setLocationName(currentData.location.name)

          const timeline = generateTimelineData(currentData.aqi, currentData.pollutants, 24, 48)
          setTimelineData(timeline)
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

    const timeline = generateTimelineData(location.data.aqi, location.data.pollutants, 24, 48)
    setTimelineData(timeline)
    setCurrentIndex(24)
  }

  if (!timelineData || !userLocation) {
    return (
      <div className="container mx-auto py-12">
        <div className="flex items-center justify-center min-h-[60vh]">
          <p className="text-muted-foreground">Loading air quality data...</p>
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
    <div className="container mx-auto py-12 space-y-8">
      {/* Header */}
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-balance">Air Quality Map</h1>
        <p className="text-lg text-muted-foreground text-pretty">
          Real-time air quality monitoring with wind visualization and timeline analysis
        </p>
      </div>

      <div className="max-w-2xl">
        <LocationSearch onLocationSelect={handleLocationSelect} />
      </div>

      {/* Timeline Scrubber */}
      <TimelineScrubber data={timelineData} currentIndex={currentIndex} onIndexChange={setCurrentIndex} />

      {/* Air Health Index Card */}
      <Card className={`border-2 ${getCategoryBgColor(airQuality.category)}`}>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Air Health Index</p>
              <div className="flex items-baseline gap-3">
                <span className="text-5xl font-bold">{airQuality.aqi}</span>
                <Badge variant="outline" className={`${getCategoryColor(airQuality.category)} border-current`}>
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
        </CardContent>
      </Card>

      {/* Map and Pollutants Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <WindMap
            center={userLocation}
            timelineData={currentData}
            locationName={locationName}
            onRecenterLocation={getUserLocation}
          />
        </div>

        {/* Pollutant Levels */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-secondary" />
                Pollutant Levels
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* PM2.5 */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">PM2.5</span>
                  <span className="text-2xl font-bold">{airQuality.pollutants.pm25}</span>
                </div>
                <div className="text-xs text-muted-foreground">μg/m³</div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all"
                    style={{ width: `${Math.min((airQuality.pollutants.pm25 / 100) * 100, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground text-pretty">
                  Fine particulate matter that can penetrate deep into lungs
                </p>
              </div>

              {/* NO₂ */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">NO₂</span>
                  <span className="text-2xl font-bold">{airQuality.pollutants.no2}</span>
                </div>
                <div className="text-xs text-muted-foreground">ppb</div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-secondary transition-all"
                    style={{ width: `${Math.min((airQuality.pollutants.no2 / 100) * 100, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground text-pretty">
                  Nitrogen dioxide from vehicle emissions and industrial sources
                </p>
              </div>

              {/* O₃ */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">O₃</span>
                  <span className="text-2xl font-bold">{airQuality.pollutants.o3}</span>
                </div>
                <div className="text-xs text-muted-foreground">ppb</div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent transition-all"
                    style={{ width: `${Math.min((airQuality.pollutants.o3 / 100) * 100, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground text-pretty">
                  Ground-level ozone that can irritate respiratory system
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
