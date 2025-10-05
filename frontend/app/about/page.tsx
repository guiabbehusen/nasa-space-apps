import { Card, CardContent } from "@/components/ui/card"
import { Satellite, BookOpen, Heart, Shield } from "lucide-react"

export default function AboutPage() {
  return (
    <div className="container mx-auto py-12 space-y-12">
      {/* Header */}
      <div className="max-w-3xl mx-auto text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold text-balance">About BREATHSAFE</h1>
        <p className="text-xl text-muted-foreground text-balance">
          Empowering communities with NASA data to make informed decisions about air quality and health
        </p>
      </div>

      {/* Mission */}
      <div className="max-w-4xl mx-auto">
        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-background">
          <CardContent className="pt-8 space-y-4">
            <div className="flex items-center gap-3 mb-4">
              <Heart className="h-8 w-8 text-primary" />
              <h2 className="text-2xl font-bold">Our Mission</h2>
            </div>
            <p className="text-lg text-muted-foreground leading-relaxed text-pretty">
              BREATHSAFE was created to bridge the gap between complex NASA Earth observation data and everyday health
              decisions. We believe everyone deserves to understand the air they breathe and receive personalized
              guidance to protect their health and their loved ones.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* How It Works */}
      <div className="max-w-4xl mx-auto space-y-6">
        <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Satellite className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">NASA Data Collection</h3>
              <p className="text-muted-foreground leading-relaxed text-pretty">
                We utilize NASA's Earth observation satellites and ground monitoring stations to collect real-time data
                on key air pollutants including PM2.5, NO₂, and O₃.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 space-y-4">
              <div className="h-12 w-12 rounded-lg bg-secondary/10 flex items-center justify-center">
                <BookOpen className="h-6 w-6 text-secondary" />
              </div>
              <h3 className="text-xl font-semibold">Scientific Analysis</h3>
              <p className="text-muted-foreground leading-relaxed text-pretty">
                Our algorithms process the data and calculate Air Quality Index (AQI) values, categorizing air quality
                from Good to Hazardous based on EPA standards.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 space-y-4">
              <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <Heart className="h-6 w-6 text-accent" />
              </div>
              <h3 className="text-xl font-semibold">Personalized Insights</h3>
              <p className="text-muted-foreground leading-relaxed text-pretty">
                Based on your health profile (pregnant, child, elderly, asthmatic, or general), we provide tailored
                recommendations to protect your specific health needs.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 space-y-4">
              <div className="h-12 w-12 rounded-lg bg-chart-4/10 flex items-center justify-center">
                <Shield className="h-6 w-6 text-chart-4" />
              </div>
              <h3 className="text-xl font-semibold">Actionable Alerts</h3>
              <p className="text-muted-foreground leading-relaxed text-pretty">
                Receive clear, actionable health alerts that help you make informed decisions about outdoor activities,
                exercise, and daily routines.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Health Impact */}
      <div className="max-w-4xl mx-auto space-y-6">
        <h2 className="text-3xl font-bold text-center mb-8">Understanding Air Pollution & Health</h2>

        <Card>
          <CardContent className="pt-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">PM2.5 (Fine Particulate Matter)</h3>
              <p className="text-muted-foreground leading-relaxed text-pretty">
                Particles smaller than 2.5 micrometers can penetrate deep into lungs and enter the bloodstream.
                Long-term exposure is linked to cardiovascular disease, respiratory issues, and adverse pregnancy
                outcomes. Particularly dangerous for pregnant women and developing fetuses.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">NO₂ (Nitrogen Dioxide)</h3>
              <p className="text-muted-foreground leading-relaxed text-pretty">
                Primarily from vehicle emissions and industrial sources, NO₂ irritates airways and can worsen asthma.
                Children exposed to high levels show increased respiratory infections and reduced lung function
                development.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">O₃ (Ground-Level Ozone)</h3>
              <p className="text-muted-foreground leading-relaxed text-pretty">
                Forms when pollutants react with sunlight. Can trigger asthma attacks, reduce lung function, and cause
                respiratory inflammation. Elderly individuals are at higher risk for ozone-related health effects.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* References */}
      <div className="max-w-4xl mx-auto">
        <Card className="bg-muted/30">
          <CardContent className="pt-6 space-y-4">
            <h3 className="text-xl font-semibold">Scientific References</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="text-pretty">
                • World Health Organization (WHO). "Air Quality Guidelines" - Global standards for air pollutant
                concentrations
              </li>
              <li className="text-pretty">
                • EPA. "Integrated Science Assessment for Particulate Matter" - Comprehensive review of PM2.5 health
                effects
              </li>
              <li className="text-pretty">
                • NASA Earth Observatory - Real-time satellite monitoring of global air quality
              </li>
              <li className="text-pretty">
                • American Lung Association. "State of the Air" - Annual report on air quality and health impacts
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* NASA Attribution */}
      <div className="max-w-4xl mx-auto text-center">
        <Card className="border-primary/20">
          <CardContent className="pt-6 space-y-4">
            <Satellite className="h-12 w-12 text-primary mx-auto" />
            <h3 className="text-xl font-semibold">Built for NASA Space Apps Challenge</h3>
            <p className="text-muted-foreground text-pretty">
              This application was developed as part of the NASA Space Apps Challenge, utilizing NASA's open Earth
              observation data to create solutions that benefit humanity.
            </p>
            <p className="text-sm text-muted-foreground">Data sources: NASA MODIS, Sentinel-5P, and EPA AirNow</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
