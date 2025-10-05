"use client"

import { useState, useEffect } from "react"
import { Search, MapPin, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import type { AirQualityData } from "@/lib/air-quality-data"

interface LocationSearchProps {
  onLocationSelect: (location: { lat: number; lng: number; name: string; data: AirQualityData }) => void
}

interface GeocodingResult {
  display_name: string
  lat: string
  lon: string
  type: string
  address: {
    road?: string
    suburb?: string
    city?: string
    state?: string
    country?: string
  }
}

export default function LocationSearch({ onLocationSelect }: LocationSearchProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<GeocodingResult[]>([])
  const [showResults, setShowResults] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (searchQuery.trim().length < 3) {
        setSearchResults([])
        setShowResults(false)
        return
      }

      handleGeocodingSearch(searchQuery)
    }, 500)

    return () => clearTimeout(delayDebounce)
  }, [searchQuery])

  const handleGeocodingSearch = async (query: string) => {
    setIsLoading(true)
    try {
      // Using Nominatim (OpenStreetMap) for free geocoding
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?` +
          `q=${encodeURIComponent(query)}` +
          `&format=json` +
          `&addressdetails=1` +
          `&limit=10`,
        {
          headers: {
            "Accept-Language": "en",
          },
        },
      )

      if (response.ok) {
        const data: GeocodingResult[] = await response.json()
        setSearchResults(data)
        setShowResults(data.length > 0)
      }
    } catch (error) {
      console.error("[v0] Geocoding error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectLocation = (location: GeocodingResult) => {
    const lat = Number.parseFloat(location.lat)
    const lng = Number.parseFloat(location.lon)

    const mockData: AirQualityData = {
      location: {
        name: location.display_name,
        lat,
        lng,
      },
      aqi: Math.floor(Math.random() * 150) + 20,
      category: "Moderate",
      pollutants: {
        pm25: Math.floor(Math.random() * 50) + 10,
        pm10: Math.floor(Math.random() * 80) + 20,
        no2: Math.floor(Math.random() * 40) + 10,
        o3: Math.floor(Math.random() * 60) + 20,
        so2: Math.floor(Math.random() * 20) + 5,
        co: Math.random() * 2 + 0.5,
      },
      timestamp: new Date().toISOString(),
    }

    onLocationSelect({
      lat,
      lng,
      name: location.display_name,
      data: mockData,
    })

    setSearchQuery(location.display_name)
    setShowResults(false)
  }

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return "text-green-500"
    if (aqi <= 100) return "text-yellow-500"
    if (aqi <= 150) return "text-orange-500"
    if (aqi <= 200) return "text-red-500"
    if (aqi <= 300) return "text-purple-500"
    return "text-red-900"
  }

  return (
    <div className="relative w-full">
      <div className="relative">
        {isLoading ? (
          <Loader2 className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground animate-spin" />
        ) : (
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        )}
        <Input
          type="text"
          placeholder="Search any location: city, street, neighborhood..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => searchQuery.length >= 3 && setShowResults(true)}
          className="pl-10 pr-4 h-12 text-base bg-background/50 backdrop-blur border-border"
        />
      </div>

      {/* Search Results Dropdown */}
      {showResults && searchResults.length > 0 && (
        <Card className="absolute top-full mt-2 w-full z-50 bg-background/95 backdrop-blur border-border shadow-lg max-h-[400px] overflow-y-auto">
          <CardContent className="p-2">
            <div className="space-y-1">
              {searchResults.map((location, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  className="w-full justify-start h-auto py-3 px-3 hover:bg-accent/50"
                  onClick={() => handleSelectLocation(location)}
                >
                  <div className="flex items-start gap-3 w-full">
                    <MapPin className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div className="flex-1 text-left">
                      <div className="font-medium text-sm">{location.display_name}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {location.type && <span className="capitalize">{location.type}</span>}
                      </div>
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Results */}
      {showResults && searchQuery.length >= 3 && searchResults.length === 0 && !isLoading && (
        <Card className="absolute top-full mt-2 w-full z-50 bg-background/95 backdrop-blur border-border">
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground text-center">No locations found for "{searchQuery}"</p>
            <p className="text-xs text-muted-foreground text-center mt-2">
              Try searching for cities, streets, or neighborhoods
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
