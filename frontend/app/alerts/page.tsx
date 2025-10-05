"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Bell, AlertTriangle, CheckCircle, Info, Mail, User, Settings } from "lucide-react"
import { mockAirQualityData, getCategoryColor, getCategoryBgColor } from "@/lib/air-quality-data"
import { Slider } from "@/components/ui/slider"
import LocationSearch from "@/components/location-search"
import type { AirQualityData } from "@/lib/air-quality-data"

type UserProfile = "general" | "pregnant" | "child" | "elderly" | "asthmatic"

interface ProfileOption {
  id: UserProfile
  label: string
  icon: string
  description: string
}

const profiles: ProfileOption[] = [
  { id: "general", label: "General Public", icon: "👤", description: "Standard air quality monitoring" },
  { id: "pregnant", label: "Pregnant", icon: "🤰", description: "Enhanced protection for pregnancy" },
  { id: "child", label: "Child", icon: "👶", description: "Extra care for young children" },
  { id: "elderly", label: "Elderly", icon: "👴", description: "Senior health monitoring" },
  { id: "asthmatic", label: "Asthmatic", icon: "🫁", description: "Respiratory condition alerts" },
]

function getRecommendations(aqi: number, profile: UserProfile) {
  const recommendations = []

  if (aqi <= 50) {
    recommendations.push({
      type: "success",
      title: "Excellent Air Quality",
      message: "Air quality is excellent! Perfect day for outdoor activities.",
      icon: CheckCircle,
    })
  } else if (aqi <= 100) {
    recommendations.push({
      type: "info",
      title: "Moderate Air Quality",
      message: "Air quality is acceptable for most people.",
      icon: Info,
    })

    if (profile === "asthmatic" || profile === "child") {
      recommendations.push({
        type: "warning",
        title: "Sensitive Groups: Take Precautions",
        message: "Consider reducing prolonged outdoor exertion if you experience symptoms.",
        icon: AlertTriangle,
      })
    }
  } else if (aqi <= 150) {
    recommendations.push({
      type: "warning",
      title: "Unhealthy for Sensitive Groups",
      message: "General public is less likely to be affected.",
      icon: AlertTriangle,
    })

    if (profile === "pregnant") {
      recommendations.push({
        type: "warning",
        title: "Pregnant Women: Limit Outdoor Activities",
        message: "High PM2.5 levels may affect fetal development. Stay indoors when possible.",
        icon: AlertTriangle,
      })
    }

    if (profile === "child") {
      recommendations.push({
        type: "warning",
        title: "Children: Reduce Outdoor Play",
        message: "Children are more vulnerable to air pollution. Limit outdoor activities.",
        icon: AlertTriangle,
      })
    }

    if (profile === "elderly") {
      recommendations.push({
        type: "warning",
        title: "Elderly: Take It Easy",
        message: "Avoid strenuous outdoor activities. Monitor for respiratory symptoms.",
        icon: AlertTriangle,
      })
    }

    if (profile === "asthmatic") {
      recommendations.push({
        type: "warning",
        title: "Asthmatic: High Alert",
        message: "Keep rescue inhaler nearby. Avoid outdoor exercise. Monitor symptoms closely.",
        icon: AlertTriangle,
      })
    }
  } else {
    recommendations.push({
      type: "danger",
      title: "Unhealthy Air Quality",
      message: "Everyone may begin to experience health effects.",
      icon: AlertTriangle,
    })

    recommendations.push({
      type: "danger",
      title: "Stay Indoors",
      message: "Keep windows closed. Use air purifiers if available. Avoid all outdoor activities.",
      icon: AlertTriangle,
    })

    if (profile === "pregnant" || profile === "child" || profile === "elderly" || profile === "asthmatic") {
      recommendations.push({
        type: "danger",
        title: "High Risk: Seek Medical Advice",
        message: "Contact your healthcare provider if you experience any symptoms. Stay indoors with air filtration.",
        icon: AlertTriangle,
      })
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

  // Use first location's data for demo
  const airData = mockAirQualityData[0]
  const recommendations = getRecommendations(airData.aqi, selectedProfile)

  const handleLocationSelect = (location: { lat: number; lng: number; name: string; data: AirQualityData }) => {
    setSelectedLocation({
      lat: location.lat,
      lng: location.lng,
      name: location.name,
    })
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
          location: selectedLocation.name,
          profile: selectedProfile,
          thresholds: { aqi: aqiThreshold[0] },
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setSubscriptionStatus("success")
      } else {
        setSubscriptionStatus("error")
      }
    } catch (error) {
      setSubscriptionStatus("error")
      console.error("[v0] Subscription error:", error)
    } finally {
      setIsSubscribing(false)
    }
  }

  return (
    <div className="container mx-auto py-6 md:py-12 px-4 md:px-6 space-y-6 md:space-y-8">
      {/* Header */}
      <div className="space-y-3 md:space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold text-balance">Health Alerts & Recommendations</h1>
        <p className="text-base md:text-lg text-muted-foreground text-pretty">
          Get personalized air quality alerts delivered to your email based on your health profile and location
        </p>
      </div>

      {/* Current AQI Status */}
      <Card className={`border-2 ${getCategoryBgColor(airData.category)}`}>
        <CardContent className="pt-4 md:pt-6 px-4 md:px-6">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <p className="text-xs md:text-sm font-medium text-muted-foreground">Current Air Quality</p>
              <div className="flex items-baseline gap-2 md:gap-3">
                <span className="text-3xl md:text-4xl font-bold">{airData.aqi}</span>
                <Badge
                  variant="outline"
                  className={`${getCategoryColor(airData.category)} border-current text-sm md:text-base`}
                >
                  {airData.category}
                </Badge>
              </div>
              <p className="text-xs md:text-sm text-muted-foreground">{airData.location.name}</p>
            </div>
            <Bell className={`h-10 w-10 md:h-12 md:w-12 ${getCategoryColor(airData.category)}`} />
          </div>
        </CardContent>
      </Card>

      {/* Email Alert Subscription */}
      <Card className="border-2 border-primary/20">
        <CardHeader className="px-4 md:px-6">
          <CardTitle className="flex items-center gap-2 text-xl md:text-2xl">
            <Mail className="h-5 w-5 text-primary" />
            Subscribe to Email Alerts
          </CardTitle>
          <CardDescription className="text-sm md:text-base">
            Receive personalized air quality alerts when conditions match your preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5 md:space-y-6 px-4 md:px-6">
          {/* Email Input */}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm md:text-base">
              Email Address
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="your.email@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-11 md:h-12"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm md:text-base">Location</Label>
            <LocationSearch onLocationSelect={handleLocationSelect} />
            {selectedLocation && (
              <p className="text-xs md:text-sm text-muted-foreground mt-2">Selected: {selectedLocation.name}</p>
            )}
          </div>

          {/* Profile Selection */}
          <div className="space-y-3">
            <Label className="flex items-center gap-2 text-sm md:text-base">
              <User className="h-4 w-4" />
              Health Profile
            </Label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 md:gap-3">
              {profiles.map((profile) => (
                <button
                  key={profile.id}
                  onClick={() => setSelectedProfile(profile.id)}
                  className={`p-3 md:p-4 rounded-lg border-2 transition-all text-left space-y-1.5 md:space-y-2 hover:border-primary/50 ${
                    selectedProfile === profile.id ? "border-primary bg-primary/5" : "border-border bg-card"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xl md:text-2xl">{profile.icon}</span>
                    <span className="font-medium text-sm md:text-base">{profile.label}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">{profile.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* AQI Threshold */}
          <div className="space-y-3">
            <Label className="flex items-center gap-2 text-sm md:text-base">
              <Settings className="h-4 w-4" />
              Alert Threshold (AQI)
            </Label>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs md:text-sm text-muted-foreground">Send alert when AQI exceeds:</span>
                <span className="text-lg md:text-xl font-bold">{aqiThreshold[0]}</span>
              </div>
              <Slider
                value={aqiThreshold}
                onValueChange={setAqiThreshold}
                min={0}
                max={300}
                step={10}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0 (Good)</span>
                <span className="hidden sm:inline">150 (Unhealthy)</span>
                <span>300 (Hazardous)</span>
              </div>
            </div>
          </div>

          {/* Subscribe Button */}
          <Button onClick={handleSubscribe} disabled={isSubscribing} className="w-full h-11 md:h-12" size="lg">
            <Mail className="mr-2 h-4 w-4" />
            {isSubscribing ? "Subscribing..." : "Subscribe to Alerts"}
          </Button>

          {/* Status Messages */}
          {subscriptionStatus === "success" && (
            <div className="p-3 md:p-4 rounded-lg bg-accent/10 border border-accent/20 text-accent">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 flex-shrink-0" />
                <span className="font-medium text-sm md:text-base">Successfully subscribed to air quality alerts!</span>
              </div>
            </div>
          )}

          {subscriptionStatus === "error" && (
            <div className="p-3 md:p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 flex-shrink-0" />
                <span className="font-medium text-sm md:text-base">Failed to subscribe. Please try again.</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recommendations */}
      <div className="space-y-4">
        <h2 className="text-2xl md:text-3xl font-bold">Your Recommendations</h2>

        <div className="grid gap-3 md:gap-4">
          {recommendations.map((rec, index) => {
            const Icon = rec.icon
            const colorClass =
              rec.type === "success"
                ? "text-accent border-accent/20 bg-accent/5"
                : rec.type === "warning"
                  ? "text-chart-4 border-chart-4/20 bg-chart-4/5"
                  : rec.type === "danger"
                    ? "text-destructive border-destructive/20 bg-destructive/5"
                    : "text-primary border-primary/20 bg-primary/5"

            return (
              <Card key={index} className={`border-2 ${colorClass}`}>
                <CardContent className="pt-4 md:pt-6 px-4 md:px-6">
                  <div className="flex gap-3 md:gap-4">
                    <Icon className={`h-5 w-5 md:h-6 md:w-6 mt-0.5 flex-shrink-0`} />
                    <div className="space-y-1 flex-1">
                      <h3 className="font-semibold text-base md:text-lg">{rec.title}</h3>
                      <p className="text-sm md:text-base text-muted-foreground text-pretty">{rec.message}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* General Tips */}
      <Card>
        <CardHeader className="px-4 md:px-6">
          <CardTitle className="text-xl md:text-2xl">General Air Quality Tips</CardTitle>
        </CardHeader>
        <CardContent className="px-4 md:px-6">
          <ul className="space-y-2.5 md:space-y-3 text-sm text-muted-foreground">
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span className="text-pretty">Check air quality before planning outdoor activities</span>
            </li>
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span className="text-pretty">Keep windows closed during high pollution days</span>
            </li>
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span className="text-pretty">Use air purifiers indoors when AQI is elevated</span>
            </li>
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span className="text-pretty">Avoid exercising near busy roads during rush hour</span>
            </li>
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span className="text-pretty">Stay hydrated to help your body process pollutants</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
