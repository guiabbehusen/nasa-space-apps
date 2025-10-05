"use client"

import { useEffect, useRef, useState } from "react"
import type { TimelineData } from "@/lib/weather-data"
import { getWindDirection } from "@/lib/weather-data"
import { Card, CardContent } from "@/components/ui/card"
import { Wind, Thermometer, Droplets, Eye, Gauge } from "lucide-react"

interface EnhancedMapProps {
  center: { lat: number; lng: number }
  timelineData: TimelineData
  locationName: string
}

export default function EnhancedMap({ center, timelineData, locationName }: EnhancedMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const [mapLoaded, setMapLoaded] = useState(false)

  useEffect(() => {
    if (typeof window === "undefined" || !mapRef.current) return

    // Dynamically import Leaflet
    import("leaflet").then((L) => {
      // Import Leaflet CSS
      if (!document.querySelector('link[href*="leaflet.css"]')) {
        const link = document.createElement("link")
        link.rel = "stylesheet"
        link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        document.head.appendChild(link)
      }

      // Initialize map
      if (!mapInstanceRef.current && mapRef.current) {
        const map = L.map(mapRef.current).setView([center.lat, center.lng], 11)

        // Use a more modern map style
        L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
          attribution: "© OpenStreetMap contributors © CARTO",
          maxZoom: 19,
        }).addTo(map)

        mapInstanceRef.current = map
        setMapLoaded(true)
      }
    })

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
        setMapLoaded(false)
      }
    }
  }, [center])

  // Update marker when data changes
  useEffect(() => {
    if (!mapInstanceRef.current || !mapLoaded) return

    import("leaflet").then((L) => {
      const map = mapInstanceRef.current

      // Clear existing markers
      map.eachLayer((layer: any) => {
        if (layer instanceof L.Marker || layer instanceof L.Circle) {
          map.removeLayer(layer)
        }
      })

      const { airQuality, weather } = timelineData

      // Get marker color based on AQI
      const getMarkerColor = (aqi: number) => {
        if (aqi <= 50) return "#4ade80"
        if (aqi <= 100) return "#facc15"
        if (aqi <= 150) return "#fb923c"
        if (aqi <= 200) return "#ef4444"
        if (aqi <= 300) return "#a855f7"
        return "#991b1b"
      }

      const color = getMarkerColor(airQuality.aqi)

      // Add air quality circle overlay
      L.circle([center.lat, center.lng], {
        color: color,
        fillColor: color,
        fillOpacity: 0.15,
        radius: 5000,
        weight: 2,
      }).addTo(map)

      // Add main marker with AQI
      const markerHtml = `
        <div style="
          background-color: ${color};
          width: 50px;
          height: 50px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          color: white;
          font-size: 16px;
        ">
          ${airQuality.aqi}
        </div>
      `

      const customIcon = L.divIcon({
        html: markerHtml,
        className: "custom-marker",
        iconSize: [50, 50],
        iconAnchor: [25, 25],
      })

      L.marker([center.lat, center.lng], { icon: customIcon })
        .addTo(map)
        .bindPopup(
          `
          <div style="font-family: system-ui; padding: 8px; min-width: 200px;">
            <strong style="font-size: 16px;">${locationName}</strong><br/><br/>
            <div style="margin: 8px 0;">
              <strong>Air Quality</strong><br/>
              AQI: ${airQuality.aqi} (${airQuality.category})<br/>
              PM2.5: ${airQuality.pollutants.pm25} μg/m³<br/>
              NO₂: ${airQuality.pollutants.no2} ppb<br/>
              O₃: ${airQuality.pollutants.o3} ppb
            </div>
            <div style="margin: 8px 0; padding-top: 8px; border-top: 1px solid #e5e7eb;">
              <strong>Weather</strong><br/>
              Temperature: ${weather.temperature}°C<br/>
              Wind: ${weather.windSpeed} km/h ${getWindDirection(weather.windDirection)}<br/>
              Humidity: ${weather.humidity}%
            </div>
          </div>
        `,
          { maxWidth: 300 },
        )

      // Add wind direction indicator
      const windArrowHtml = `
        <div style="
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          transform: rotate(${weather.windDirection}deg);
        ">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M12 5l-4 4M12 5l4 4"/>
          </svg>
        </div>
      `

      const windIcon = L.divIcon({
        html: windArrowHtml,
        className: "wind-arrow",
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      })

      // Offset wind indicator slightly
      L.marker([center.lat + 0.02, center.lng + 0.02], { icon: windIcon }).addTo(map)
    })
  }, [timelineData, center, locationName, mapLoaded])

  const { weather } = timelineData

  return (
    <div className="space-y-4">
      {/* Map */}
      <div ref={mapRef} className="h-[500px] rounded-lg overflow-hidden border-2" />

      {/* Weather Info Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Card>
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Thermometer className="h-4 w-4" />
              <span className="text-xs font-medium">Temperature</span>
            </div>
            <div className="text-2xl font-bold">{weather.temperature}°C</div>
            <div className="text-xs text-muted-foreground">Feels like {weather.feelsLike}°C</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Wind className="h-4 w-4" />
              <span className="text-xs font-medium">Wind</span>
            </div>
            <div className="text-2xl font-bold">{weather.windSpeed}</div>
            <div className="text-xs text-muted-foreground">km/h {getWindDirection(weather.windDirection)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Droplets className="h-4 w-4" />
              <span className="text-xs font-medium">Humidity</span>
            </div>
            <div className="text-2xl font-bold">{weather.humidity}%</div>
            <div className="text-xs text-muted-foreground">Relative</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Eye className="h-4 w-4" />
              <span className="text-xs font-medium">Visibility</span>
            </div>
            <div className="text-2xl font-bold">{weather.visibility}</div>
            <div className="text-xs text-muted-foreground">km</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Gauge className="h-4 w-4" />
              <span className="text-xs font-medium">Pressure</span>
            </div>
            <div className="text-2xl font-bold">{weather.pressure}</div>
            <div className="text-xs text-muted-foreground">hPa</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
