"use client"

import { useEffect, useRef } from "react"
import type { AirQualityData } from "@/lib/air-quality-data"

interface MapComponentProps {
  center: { lat: number; lng: number }
  airData: AirQualityData
}

export default function MapComponent({ center, airData }: MapComponentProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)

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
        const map = L.map(mapRef.current).setView([center.lat, center.lng], 10)

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenStreetMap contributors",
        }).addTo(map)

        // Add marker for user location
        const getMarkerColor = (aqi: number) => {
          if (aqi <= 50) return "#4ade80" // green
          if (aqi <= 100) return "#facc15" // yellow
          if (aqi <= 150) return "#fb923c" // orange
          if (aqi <= 200) return "#ef4444" // red
          if (aqi <= 300) return "#a855f7" // purple
          return "#991b1b" // dark red
        }

        const markerHtml = `
          <div style="
            background-color: ${getMarkerColor(airData.aqi)};
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 12px;
          ">
            ${airData.aqi}
          </div>
        `

        const customIcon = L.divIcon({
          html: markerHtml,
          className: "custom-marker",
          iconSize: [40, 40],
          iconAnchor: [20, 20],
        })

        L.marker([center.lat, center.lng], { icon: customIcon })
          .addTo(map)
          .bindPopup(`
            <div style="font-family: system-ui; padding: 4px;">
              <strong>${airData.location.name}</strong><br/>
              AQI: ${airData.aqi} (${airData.category})<br/>
              PM2.5: ${airData.pollutants.pm25} μg/m³<br/>
              NO₂: ${airData.pollutants.no2} ppb<br/>
              O₃: ${airData.pollutants.o3} ppb
            </div>
          `)

        mapInstanceRef.current = map
      }
    })

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [center, airData])

  return <div ref={mapRef} className="h-[500px] rounded-lg overflow-hidden" />
}
