"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Bell, AlertTriangle, CheckCircle, Info, Mail, MapPin, Gauge, Activity } from "lucide-react"
import { getCategoryColor } from "@/lib/air-quality-data" // 👈 removei mockAirQualityData
import { Slider } from "@/components/ui/slider"
import LocationSearch from "@/components/location-search"
import type { AirQualityData } from "@/lib/air-quality-data"
import Image from "next/image"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

type UserProfile = "general" | "pregnant" | "child" | "elderly" | "asthmatic"

interface ProfileOption {
  id: UserProfile
  label: string
  icon: string
  description: string
}

const profiles: ProfileOption[] = [
  { id: "general", label: "General Public", icon: "👤", description: "Standard monitoring" },
  { id: "pregnant", label: "Pregnant", icon: "🤰", description: "Enhanced protection" },
  { id: "child", label: "Child", icon: "👶", description: "Extra care for children" },
  { id: "elderly", label: "Elderly", icon: "👴", description: "Senior health monitoring" },
  { id: "asthmatic", label: "Asthmatic", icon: "🫁", description: "Respiratory alerts" },
]

function getRecommendations(aqi: number, profile: UserProfile) {
  const recommendations = []

  if (aqi <= 50) {
    recommendations.push({ type: "success", title: "Excellent Air Quality", message: "Perfect day for outdoor activities.", icon: CheckCircle })
  } else if (aqi <= 100) {
    recommendations.push({ type: "info", title: "Moderate Air Quality", message: "Air quality is acceptable for most people.", icon: Info })
    if (profile === "asthmatic" || profile === "child") {
      recommendations.push({ type: "warning", title: "Sensitive Groups: Take Precautions", message: "Consider reducing prolonged outdoor exertion if you experience symptoms.", icon: AlertTriangle })
    }
  } else if (aqi <= 150) {
    recommendations.push({ type: "warning", title: "Unhealthy for Sensitive Groups", message: "General public is less likely to be affected.", icon: AlertTriangle })
    if (profile === "pregnant") {
      recommendations.push({ type: "warning", title: "Limit Outdoor Activities", message: "High PM2.5 levels may affect fetal development. Stay indoors when possible.", icon: AlertTriangle })
    }
    if (profile === "child") {
      recommendations.push({ type: "warning", title: "Reduce Outdoor Play", message: "Children are more vulnerable to air pollution. Limit outdoor activities.", icon: AlertTriangle })
    }
    if (profile === "elderly") {
      recommendations.push({ type: "warning", title: "Take It Easy", message: "Avoid strenuous outdoor activities. Monitor for respiratory symptoms.", icon: AlertTriangle })
    }
    if (profile === "asthmatic") {
      recommendations.push({ type: "warning", title: "High Alert", message: "Keep rescue inhaler nearby. Avoid outdoor exercise.", icon: AlertTriangle })
    }
  } else {
    recommendations.push({ type: "danger", title: "Unhealthy Air Quality", message: "Everyone may experience health effects.", icon: AlertTriangle })
    recommendations.push({ type: "danger", title: "Stay Indoors", message: "Keep windows closed. Use air purifiers if available.", icon: AlertTriangle })
    if (profile === "pregnant" || profile === "child" || profile === "elderly" || profile === "asthmatic") {
      recommendations.push({ type: "danger", title: "High Risk: Seek Medical Advice", message: "Contact your healthcare provider if you experience symptoms.", icon: AlertTriangle })
    }
  }

  return recommendations
}

export default function AlertsPage() {
  const [selectedProfile, setSelectedProfile] = useState<UserProfile>("general")
  const [email, setEmail] = useState("")
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number; name: string } | null>(null)
  const [aqiThreshold, setAqiThreshold] = useState([100])
  const [isSubscribing, setIsSubscribing] = useState(false)
  const [subscriptionStatus, setSubscriptionStatus] = useState<"idle" | "success" | "error">("idle")

      // 👇 Estado inicial do ar
    const [airData, setAirData] = useState({
      aqi: 0,
      category: "—",
      location: { name: "Select a location" },
      pm25: 0,
      pm10: 0,
      o3: 0,
    })

    // ✅ busca real da API quando o usuário escolher uma localização
    useEffect(() => {
      if (!selectedLocation) return

      const fetchAir = async () => {
        try {
          const res = await fetch(`/api/air?lat=${selectedLocation.lat}&lng=${selectedLocation.lng}`)
          if (!res.ok) throw new Error(`Erro na API /api/air (${res.status})`)

          const raw = await res.json()
          console.log("Air API data:", raw) // opcional — ajuda a ver o formato real da resposta

          // timeline vem com 48h passadas + "now" + 48h futuras
            const timeline = Array.isArray(raw.timeline) ? raw.timeline : []

            // índice central (ponto atual)
            const midIndex = Math.floor(timeline.length / 2)
            const current = timeline[midIndex] || raw.current || raw

            const pollutants = current?.pollutants || raw?.pollutants || {}

            setAirData({
              aqi: current?.aqi ?? raw?.aqi ?? 0,
              category: current?.category ?? raw?.category ?? "—",
              location: raw?.location || { name: selectedLocation.name },
              pm25: pollutants.pm25 ?? pollutants.pm_25 ?? pollutants["pm2_5"] ?? 0,
              pm10: pollutants.pm10 ?? pollutants.pm_10 ?? 0,
              o3: pollutants.o3 ?? pollutants.ozone ?? 0,
            })

        } catch (error) {
          console.error("[AlertsPage] Failed to fetch air data:", error)
        }
      }

      fetchAir()
    }, [selectedLocation])


  const recommendations = getRecommendations(airData.aqi, selectedProfile)

  const handleLocationSelect = (location: { lat: number; lng: number; name: string; data: AirQualityData }) => {
    setSelectedLocation({ lat: location.lat, lng: location.lng, name: location.name })
  }

  const handleSubscribe = async () => {
    if (!email || !selectedLocation) {
      alert("Please fill in all required fields")
      return
    }

    setIsSubscribing(true)
    setSubscriptionStatus("idle")

    try {
      const response = await fetch("/api/alerts/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          lat: selectedLocation.lat,
          lng: selectedLocation.lng,
          profile: selectedProfile,
          thresholds: { aqi: aqiThreshold[0] },
        }),

      })

      await response.json().catch(() => null)
      setSubscriptionStatus(response.ok ? "success" : "error")
    } catch (error) {
      setSubscriptionStatus("error")
      console.error("[v0] Subscription error:", error)
    } finally {
      setIsSubscribing(false)
    }
  }

  return (
    <div
      className="min-h-screen bg-gradient-to-br from-[#0042a6] via-[#07173F] to-black nasa-pattern-fiduciaries"
      style={{ backgroundImage: "linear-gradient(45deg, #0042a6, #07173F)" }}
    >
      <div className="container mx-auto py-8 md:py-12 px-4 md:px-6 space-y-8 relative">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <h1 className="text-3xl md:text-5xl font-black text-balance text-white font-heading">Air Quality Alerts</h1>
            <p className="text-base md:text-lg text-white/80 text-pretty max-w-2xl">
              Get personalized notifications when air quality affects your health
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

        <div className="grid lg:grid-cols-2 gap-6 md:gap-8">
          {/* Left Column: Subscription Form */}
          <div className="space-y-6">
            <Card className="border-2 border-nasa-neon-yellow/60 bg-gradient-to-br from-nasa-deep-blue/90 to-nasa-bright-blue/80 backdrop-blur-sm shadow-2xl shadow-nasa-neon-yellow/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl text-white font-heading">
                  <Bell className="h-6 w-6 text-nasa-neon-yellow" />
                  Subscribe to Alerts
                </CardTitle>
                <CardDescription className="text-white/90">
                  Receive email notifications based on your preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-5">
                {/* Email Input */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-white font-semibold flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    Email Address
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="your.email@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-11 bg-nasa-midnight-blue/80 border-nasa-electric-blue/40 focus:border-nasa-electric-blue text-white placeholder:text-white/50"
                  />
                </div>

                {/* Location */}
                <div className="space-y-2">
                  <Label className="text-white font-semibold flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    Location
                  </Label>
                  <LocationSearch onLocationSelect={handleLocationSelect} />
                  {selectedLocation && (
                    <p className="text-sm text-nasa-neon-yellow font-medium">✓ {selectedLocation.name}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label className="text-white font-semibold flex items-center gap-2">
                    <Activity className="h-4 w-4" />
                    Health Profile
                  </Label>
                  <Select value={selectedProfile} onValueChange={(value) => setSelectedProfile(value as UserProfile)}>
                    <SelectTrigger className="h-11 bg-nasa-midnight-blue/80 border-nasa-electric-blue/40 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {profiles.map((profile) => (
                        <SelectItem key={profile.id} value={profile.id}>
                          <div className="flex items-center gap-2">
                            <span>{profile.icon}</span>
                            <div>
                              <div className="font-semibold">{profile.label}</div>
                              <div className="text-xs text-muted-foreground">{profile.description}</div>
                            </div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-3">
                  <Label className="text-white font-semibold flex items-center gap-2">
                    <Gauge className="h-4 w-4" />
                    Alert Threshold
                  </Label>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-white/80">Notify when AQI exceeds:</span>
                      <span className="text-xl font-bold text-nasa-neon-yellow">{aqiThreshold[0]}</span>
                    </div>
                    <Slider
                      value={aqiThreshold}
                      onValueChange={setAqiThreshold}
                      min={0}
                      max={300}
                      step={10}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-white/60">
                      <span>0</span>
                      <span>150</span>
                      <span>300</span>
                    </div>
                  </div>
                </div>

                <Button
                  onClick={handleSubscribe}
                  disabled={isSubscribing}
                  className="w-full h-14 bg-nasa-neon-yellow text-black hover:bg-nasa-neon-yellow/90 font-bold text-xl"
                  size="lg"
                >
                  <Bell className="mr-2 h-6 w-6" />
                  {isSubscribing ? "Subscribing..." : "Subscribe to Alerts"}
                </Button>

                {/* Status Messages */}
                {subscriptionStatus === "success" && (
                  <div className="p-4 rounded-lg bg-green-500/20 border-2 border-green-400/50 backdrop-blur">
                    <div className="flex items-center gap-2 text-white">
                      <CheckCircle className="h-5 w-5 flex-shrink-0" />
                      <span className="font-semibold text-sm">Successfully subscribed!</span>
                    </div>
                  </div>
                )}

                {subscriptionStatus === "error" && (
                  <div className="p-4 rounded-lg bg-red-500/20 border-2 border-red-400/50 backdrop-blur">
                    <div className="flex items-center gap-2 text-white">
                      <AlertTriangle className="h-5 w-5 flex-shrink-0" />
                      <span className="font-semibold text-sm">Failed to subscribe. Please try again.</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            {/* Current AQI Card */}
            <Card className="border-2 border-nasa-bright-blue/60 bg-gradient-to-br from-nasa-bright-blue/30 to-nasa-electric-blue/20 backdrop-blur-sm shadow-lg">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-white/80 mb-2">Current Air Quality</p>
                      <div className="flex items-baseline gap-3">
                        <span className="text-5xl font-black text-white">{airData.aqi}</span>
                        <Badge
                          variant="outline"
                          className={`${getCategoryColor(airData.category)} border-2 border-current text-base font-bold px-3 py-1`}
                        >
                          {airData.category}
                        </Badge>
                      </div>
                      <p className="text-sm text-white/70 font-medium mt-2">{airData.location.name}</p>
                    </div>
                    <Bell className="h-12 w-12 text-white/80" />
                  </div>

                  {/* Quick Stats */}
                  <div className="grid grid-cols-3 gap-3 pt-4 border-t border-white/20">
                    <div>
                      <p className="text-xs text-white/60">PM2.5</p>
                      <p className="text-lg font-bold text-white">{airData.pm25}</p>
                    </div>
                    <div>
                      <p className="text-xs text-white/60">PM10</p>
                      <p className="text-lg font-bold text-white">{airData.pm10}</p>
                    </div>
                    <div>
                      <p className="text-xs text-white/60">O₃</p>
                      <p className="text-lg font-bold text-white">{airData.o3}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2 border-nasa-electric-blue/60 bg-nasa-midnight-blue/60 backdrop-blur-sm shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl text-white font-heading">
                  Recommendations for {profiles.find((p) => p.id === selectedProfile)?.label}
                </CardTitle>
                <CardDescription className="text-white/80">
                  Based on current air quality and your health profile
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {recommendations.map((rec, index) => {
                  const Icon = rec.icon
                  const colorClass =
                    rec.type === "success"
                      ? "border-nasa-neon-yellow/50 bg-nasa-neon-yellow/10"
                      : rec.type === "warning"
                        ? "border-yellow-400/50 bg-yellow-500/10"
                        : rec.type === "danger"
                          ? "border-nasa-rocket-red/50 bg-nasa-rocket-red/10"
                          : "border-nasa-electric-blue/50 bg-nasa-electric-blue/10"

                  const iconColor =
                    rec.type === "success"
                      ? "text-nasa-neon-yellow"
                      : rec.type === "warning"
                        ? "text-yellow-300"
                        : rec.type === "danger"
                          ? "text-nasa-rocket-red"
                          : "text-nasa-electric-blue"

                  return (
                    <div key={index} className={`p-4 rounded-lg border-2 ${colorClass} backdrop-blur`}>
                      <div className="flex gap-3">
                        <Icon className={`h-5 w-5 mt-0.5 flex-shrink-0 ${iconColor}`} />
                        <div className="space-y-1 flex-1">
                          <h3 className="font-bold text-sm text-white">{rec.title}</h3>
                          <p className="text-sm text-white/80 text-pretty">{rec.message}</p>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </CardContent>
            </Card>
          </div>
        </div>

        <Card className="border-2 border-nasa-rocket-red/60 bg-nasa-rocket-red/20 backdrop-blur-sm shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl text-white font-heading">General Air Quality Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-2 gap-x-6 gap-y-2">
              <div className="flex gap-2 text-sm text-white/90">
                <span className="text-nasa-neon-yellow font-bold">•</span>
                <span>Check air quality before outdoor activities</span>
              </div>
              <div className="flex gap-2 text-sm text-white/90">
                <span className="text-nasa-neon-yellow font-bold">•</span>
                <span>Keep windows closed during high pollution</span>
              </div>
              <div className="flex gap-2 text-sm text-white/90">
                <span className="text-nasa-neon-yellow font-bold">•</span>
                <span>Use air purifiers when AQI is elevated</span>
              </div>
              <div className="flex gap-2 text-sm text-white/90">
                <span className="text-nasa-neon-yellow font-bold">•</span>
                <span>Avoid exercising near busy roads</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
