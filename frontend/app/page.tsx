import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Wind, MapPin, Bell, Shield, Activity, Heart } from "lucide-react"

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-secondary/10 to-background pointer-events-none" />
        <div className="container mx-auto relative py-24 md:py-32 lg:py-40">
          <div className="mx-auto max-w-3xl text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium text-primary">
              <Wind className="h-4 w-4" />
              Powered by NASA Open Data
            </div>

            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight text-balance">
              BREATHSAFE
              <span className="block text-primary mt-2">Personal Air Health Assistant</span>
            </h1>

            <p className="text-xl md:text-2xl text-muted-foreground text-balance">
              Know your air. Protect your health.
            </p>

            <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">
              We use NASA open data to help you stay safe from invisible air pollution. Get real-time air quality
              insights and personalized health recommendations.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Button asChild size="lg" className="text-lg">
                <Link href="/map">
                  <MapPin className="mr-2 h-5 w-5" />
                  Check Air Quality Now
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="text-lg bg-transparent">
                <Link href="/about">Learn More</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center mb-16 space-y-4">
            <h2 className="text-3xl md:text-4xl font-bold text-balance">Breathe Easier with Real-Time Insights</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">
              Monitor air quality levels and receive personalized health alerts based on your profile.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="border-border/50 bg-card/50 backdrop-blur">
              <CardContent className="pt-6 space-y-4">
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <MapPin className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">Interactive Map</h3>
                <p className="text-muted-foreground text-pretty">
                  Visualize air quality data on an interactive map with real-time pollutant levels for your location.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-card/50 backdrop-blur">
              <CardContent className="pt-6 space-y-4">
                <div className="h-12 w-12 rounded-lg bg-secondary/10 flex items-center justify-center">
                  <Activity className="h-6 w-6 text-secondary" />
                </div>
                <h3 className="text-xl font-semibold">Pollutant Tracking</h3>
                <p className="text-muted-foreground text-pretty">
                  Monitor PM2.5, NO₂, and O₃ levels with easy-to-understand health risk categories.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-card/50 backdrop-blur">
              <CardContent className="pt-6 space-y-4">
                <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
                  <Bell className="h-6 w-6 text-accent" />
                </div>
                <h3 className="text-xl font-semibold">Health Alerts</h3>
                <p className="text-muted-foreground text-pretty">
                  Get personalized recommendations based on current air quality and your health profile.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-card/50 backdrop-blur">
              <CardContent className="pt-6 space-y-4">
                <div className="h-12 w-12 rounded-lg bg-chart-4/10 flex items-center justify-center">
                  <Heart className="h-6 w-6 text-chart-4" />
                </div>
                <h3 className="text-xl font-semibold">Profile-Based</h3>
                <p className="text-muted-foreground text-pretty">
                  Tailored alerts for pregnant women, children, elderly, and people with respiratory conditions.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-card/50 backdrop-blur">
              <CardContent className="pt-6 space-y-4">
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">NASA Data</h3>
                <p className="text-muted-foreground text-pretty">
                  Powered by reliable NASA Earth observation data and scientific research.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-card/50 backdrop-blur">
              <CardContent className="pt-6 space-y-4">
                <div className="h-12 w-12 rounded-lg bg-secondary/10 flex items-center justify-center">
                  <Wind className="h-6 w-6 text-secondary" />
                </div>
                <h3 className="text-xl font-semibold">Easy to Use</h3>
                <p className="text-muted-foreground text-pretty">
                  Clean, intuitive interface designed for everyone to understand air quality at a glance.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="container mx-auto">
          <Card className="border-primary/20 bg-gradient-to-br from-primary/10 via-secondary/5 to-background">
            <CardContent className="py-16 text-center space-y-6">
              <h2 className="text-3xl md:text-4xl font-bold text-balance">Ready to Breathe Safer?</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">
                Start monitoring the air quality in your area and get personalized health recommendations today.
              </p>
              <Button asChild size="lg" className="text-lg">
                <Link href="/map">
                  <MapPin className="mr-2 h-5 w-5" />
                  Check Air Quality Now
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}
