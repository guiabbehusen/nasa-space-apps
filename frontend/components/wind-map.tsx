"use client"

import { useEffect, useRef, useState } from "react"
import type { TimelineData } from "@/lib/weather-data"
import { getWindDirection } from "@/lib/weather-data"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Wind, Thermometer, Droplets, Eye, Gauge, Navigation, Sun, Moon } from "lucide-react"

interface WindMapProps {
  center: { lat: number; lng: number }
  timelineData: TimelineData
  locationName: string
  onRecenterLocation?: () => void
}

// Wind particle for animation
interface WindParticle {
  x: number
  y: number
  vx: number
  vy: number
  life: number
  maxLife: number
}

export default function WindMap({ center, timelineData, locationName, onRecenterLocation }: WindMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const [mapLoaded, setMapLoaded] = useState(false)
  const particlesRef = useRef<WindParticle[]>([])
  const animationFrameRef = useRef<number>()
  const [isDarkMode, setIsDarkMode] = useState(true)

  // Initialize map
  useEffect(() => {
    if (typeof window === "undefined" || !mapRef.current) return

    import("leaflet").then((L) => {
      if (!document.querySelector('link[href*="leaflet.css"]')) {
        const link = document.createElement("link")
        link.rel = "stylesheet"
        link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        document.head.appendChild(link)
      }

      if (!mapInstanceRef.current && mapRef.current) {
        const map = L.map(mapRef.current, {
          zoomControl: true,
          attributionControl: false,
        }).setView([center.lat, center.lng], 11)

        const tileUrl = isDarkMode
          ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          : "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"

        L.tileLayer(tileUrl, {
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
  }, [center, isDarkMode])

  useEffect(() => {
    if (!mapInstanceRef.current || !mapLoaded) return

    import("leaflet").then((L) => {
      const map = mapInstanceRef.current

      // Remove existing tile layers
      map.eachLayer((layer: any) => {
        if (layer instanceof L.TileLayer) {
          map.removeLayer(layer)
        }
      })

      // Add new tile layer based on theme
      const tileUrl = isDarkMode
        ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        : "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"

      L.tileLayer(tileUrl, {
        maxZoom: 19,
      }).addTo(map)
    })
  }, [isDarkMode, mapLoaded])

  // Update markers and zones
  useEffect(() => {
    if (!mapInstanceRef.current || !mapLoaded) return

    import("leaflet").then((L) => {
      const map = mapInstanceRef.current

      map.eachLayer((layer: any) => {
        if (layer instanceof L.Marker || layer instanceof L.Circle) {
          map.removeLayer(layer)
        }
      })

      const { airQuality, weather } = timelineData

      const getMarkerColor = (aqi: number) => {
        if (aqi <= 50) return "#10b981"
        if (aqi <= 100) return "#eab308"
        if (aqi <= 150) return "#f97316"
        if (aqi <= 200) return "#ef4444"
        if (aqi <= 300) return "#a855f7"
        return "#7f1d1d"
      }

      const color = getMarkerColor(airQuality.aqi)

      const zones = [
        { lat: center.lat, lng: center.lng, radius: 8000, opacity: 0.2 },
        { lat: center.lat + 0.03, lng: center.lng + 0.02, radius: 6000, opacity: 0.15 },
        { lat: center.lat - 0.02, lng: center.lng + 0.03, radius: 5000, opacity: 0.12 },
        { lat: center.lat + 0.02, lng: center.lng - 0.03, radius: 5500, opacity: 0.13 },
      ]

      zones.forEach((zone) => {
        L.circle([zone.lat, zone.lng], {
          color: color,
          fillColor: color,
          fillOpacity: zone.opacity,
          radius: zone.radius,
          weight: 1,
        }).addTo(map)
      })

      // Main marker
      const markerHtml = `
        <div style="
          background: linear-gradient(135deg, ${color} 0%, ${color}dd 100%);
          width: 60px;
          height: 60px;
          border-radius: 50%;
          border: 3px solid rgba(255,255,255,0.9);
          box-shadow: 0 4px 20px rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          color: white;
          font-size: 18px;
        ">
          ${airQuality.aqi}
        </div>
      `

      const customIcon = L.divIcon({
        html: markerHtml,
        className: "custom-marker",
        iconSize: [60, 60],
        iconAnchor: [30, 30],
      })

      const popupBg = isDarkMode ? "#1a1a1a" : "#ffffff"
      const popupText = isDarkMode ? "#fff" : "#000"
      const popupBorder = isDarkMode ? "#333" : "#e5e5e5"

      L.marker([center.lat, center.lng], { icon: customIcon })
        .addTo(map)
        .bindPopup(
          `
          <div style="font-family: system-ui; padding: 12px; min-width: 220px; background: ${popupBg}; color: ${popupText}; border-radius: 8px;">
            <strong style="font-size: 18px;">${locationName}</strong><br/><br/>
            <div style="margin: 10px 0;">
              <strong style="color: #10b981;">Air Quality</strong><br/>
              AQI: ${airQuality.aqi} (${airQuality.category})<br/>
              PM2.5: ${airQuality.pollutants.pm25} μg/m³<br/>
              NO₂: ${airQuality.pollutants.no2} ppb<br/>
              O₃: ${airQuality.pollutants.o3} ppb
            </div>
            <div style="margin: 10px 0; padding-top: 10px; border-top: 1px solid ${popupBorder};">
              <strong style="color: #3b82f6;">Weather</strong><br/>
              Temperature: ${weather.temperature}°C<br/>
              Wind: ${weather.windSpeed} km/h ${getWindDirection(weather.windDirection)}<br/>
              Humidity: ${weather.humidity}%
            </div>
          </div>
        `,
          { maxWidth: 300 },
        )

      const windIndicators = [
        { lat: center.lat + 0.04, lng: center.lng, size: 50 },
        { lat: center.lat - 0.04, lng: center.lng, size: 45 },
        { lat: center.lat, lng: center.lng + 0.05, size: 48 },
        { lat: center.lat, lng: center.lng - 0.05, size: 46 },
      ]

      windIndicators.forEach((indicator, idx) => {
        const windArrowHtml = `
          <div style="
            width: ${indicator.size}px;
            height: ${indicator.size}px;
            display: flex;
            align-items: center;
            justify-content: center;
            transform: rotate(${weather.windDirection + idx * 15}deg);
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
          ">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2.5">
              <path d="M12 5v14M12 5l-4 4M12 5l4 4"/>
            </svg>
          </div>
        `

        const windIcon = L.divIcon({
          html: windArrowHtml,
          className: "wind-arrow",
          iconSize: [indicator.size, indicator.size],
          iconAnchor: [indicator.size / 2, indicator.size / 2],
        })

        L.marker([indicator.lat, indicator.lng], { icon: windIcon }).addTo(map)
      })
    })
  }, [timelineData, center, locationName, mapLoaded, isDarkMode])

  useEffect(() => {
    const canvas = canvasRef.current
    const mapDiv = mapRef.current
    if (!canvas || !mapDiv) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const resizeCanvas = () => {
      const rect = mapDiv.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = rect.height
      canvas.style.width = `${rect.width}px`
      canvas.style.height = `${rect.height}px`
    }

    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    const { weather } = timelineData
    const windAngle = (weather.windDirection * Math.PI) / 180
    const windSpeed = weather.windSpeed / 10

    const initParticles = () => {
      particlesRef.current = []
      for (let i = 0; i < 300; i++) {
        particlesRef.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: Math.cos(windAngle) * windSpeed,
          vy: Math.sin(windAngle) * windSpeed,
          life: Math.random() * 100,
          maxLife: 100,
        })
      }
    }
    initParticles()

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      particlesRef.current.forEach((particle) => {
        particle.x += particle.vx
        particle.y += particle.vy
        particle.life -= 1

        if (
          particle.x < 0 ||
          particle.x > canvas.width ||
          particle.y < 0 ||
          particle.y > canvas.height ||
          particle.life <= 0
        ) {
          particle.x = Math.random() * canvas.width
          particle.y = Math.random() * canvas.height
          particle.life = particle.maxLife
        }

        const alpha = particle.life / particle.maxLife
        ctx.fillStyle = `rgba(59, 130, 246, ${alpha * 0.5})`
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, 2, 0, Math.PI * 2)
        ctx.fill()
      })

      animationFrameRef.current = requestAnimationFrame(animate)
    }
    animate()

    return () => {
      window.removeEventListener("resize", resizeCanvas)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [timelineData])

  const { weather } = timelineData

  return (
    <div className="space-y-4">
      {/* Map with wind overlay */}
      <div className="relative h-[500px] rounded-lg overflow-hidden border border-border shadow-lg">
        <div ref={mapRef} className="absolute inset-0 z-0" />
        <canvas ref={canvasRef} className="absolute inset-0 z-10 pointer-events-none w-full h-full" />

        <div className="absolute top-4 right-4 z-20 flex flex-col gap-2">
          <Button
            size="icon"
            variant="secondary"
            className="shadow-lg"
            onClick={onRecenterLocation}
            title="Return to my location"
          >
            <Navigation className="h-4 w-4" />
          </Button>
          <Button
            size="icon"
            variant="secondary"
            className="shadow-lg"
            onClick={() => setIsDarkMode(!isDarkMode)}
            title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Weather Info Cards - Dark Theme */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Card className="bg-card/50 backdrop-blur border-border">
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Thermometer className="h-4 w-4" />
              <span className="text-xs font-medium">Temperature</span>
            </div>
            <div className="text-2xl font-bold">{weather.temperature}°C</div>
            <div className="text-xs text-muted-foreground">Feels like {weather.feelsLike}°C</div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur border-border">
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Wind className="h-4 w-4" />
              <span className="text-xs font-medium">Wind</span>
            </div>
            <div className="text-2xl font-bold">{weather.windSpeed}</div>
            <div className="text-xs text-muted-foreground">km/h {getWindDirection(weather.windDirection)}</div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur border-border">
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Droplets className="h-4 w-4" />
              <span className="text-xs font-medium">Humidity</span>
            </div>
            <div className="text-2xl font-bold">{weather.humidity}%</div>
            <div className="text-xs text-muted-foreground">Relative</div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur border-border">
          <CardContent className="pt-4 pb-4 space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Eye className="h-4 w-4" />
              <span className="text-xs font-medium">Visibility</span>
            </div>
            <div className="text-2xl font-bold">{weather.visibility}</div>
            <div className="text-xs text-muted-foreground">km</div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur border-border">
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
