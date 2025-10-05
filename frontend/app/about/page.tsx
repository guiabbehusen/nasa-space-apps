import { Card, CardContent } from "@/components/ui/card"
import { Satellite, BookOpen, Heart, Shield } from "lucide-react"
import Image from "next/image"

export default function AboutPage() {
  return (
    <div className="flex flex-col">
      <section className="relative overflow-hidden nasa-gradient-blue nasa-pattern-waves py-8 md:py-16 border-b-2 border-nasa-neon-yellow/30">
        <div className="container mx-auto px-4 md:px-6">
          <div className="max-w-3xl mx-auto text-center space-y-4 md:space-y-6 relative">
            <div className="flex justify-center mb-4">
              <Image
                src="/logos/nasa-space-apps-white.svg"
                alt="NASA Space Apps Challenge"
                width={100}
                height={100}
                className="opacity-90 md:w-[120px] md:h-[120px]"
              />
            </div>
            <h1 className="text-3xl md:text-5xl font-black text-balance text-white font-heading">About BREATHSAFE</h1>
            <p className="text-base md:text-xl text-nasa-neon-yellow text-balance font-bold">
              Empowering communities with NASA data to make informed decisions about air quality and health
            </p>
          </div>
        </div>
      </section>

      <section className="py-8 md:py-12 bg-white nasa-pattern-waves-light">
        <div className="container mx-auto px-4 md:px-6 space-y-8 md:space-y-12">
          <div className="max-w-4xl mx-auto">
            <Card className="relative overflow-hidden border-2 border-nasa-electric-blue/30 bg-white/80 backdrop-blur shadow-xl">
              <CardContent className="pt-6 md:pt-8 px-4 md:px-6 space-y-3 md:space-y-4 relative">
                <div className="flex items-center gap-3 mb-3 md:mb-4">
                  <Heart className="h-7 w-7 md:h-8 md:w-8 text-nasa-rocket-red" />
                  <h2 className="text-xl md:text-2xl font-black text-black font-heading">Our Mission</h2>
                </div>
                <p className="text-base md:text-lg text-black/90 leading-relaxed text-pretty font-heading">
                  BREATHSAFE was created to bridge the gap between complex NASA Earth observation data and everyday
                  health decisions. We believe everyone deserves to understand the air they breathe and receive
                  personalized guidance to protect their health and their loved ones.
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="max-w-4xl mx-auto space-y-4 md:space-y-6">
            <h2 className="text-2xl md:text-3xl font-black text-center mb-6 md:mb-8 text-black font-heading">
              How It Works
            </h2>

            <div className="grid md:grid-cols-2 gap-4 md:gap-6">
              <Card className="relative overflow-hidden border-2 border-nasa-electric-blue/30 bg-white/80 backdrop-blur hover:border-nasa-electric-blue hover:shadow-lg transition-all">
                <CardContent className="pt-5 md:pt-6 px-4 md:px-6 space-y-3 md:space-y-4 relative">
                  <div className="h-12 w-12 rounded-lg bg-nasa-electric-blue/20 flex items-center justify-center">
                    <Satellite className="h-6 w-6 text-nasa-electric-blue" />
                  </div>
                  <h3 className="text-lg md:text-xl font-bold text-black font-heading">NASA Data Collection</h3>
                  <p className="text-sm md:text-base text-black/80 leading-relaxed text-pretty font-heading">
                    We utilize NASA's Earth observation satellites and ground monitoring stations to collect real-time
                    data on key air pollutants including PM2.5, NO₂, and O₃.
                  </p>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-2 border-nasa-bright-blue/30 bg-white/80 backdrop-blur hover:border-nasa-bright-blue hover:shadow-lg transition-all">
                <CardContent className="pt-5 md:pt-6 px-4 md:px-6 space-y-3 md:space-y-4 relative">
                  <div className="h-12 w-12 rounded-lg bg-nasa-bright-blue/20 flex items-center justify-center">
                    <BookOpen className="h-6 w-6 text-nasa-bright-blue" />
                  </div>
                  <h3 className="text-lg md:text-xl font-bold text-black font-heading">Scientific Analysis</h3>
                  <p className="text-sm md:text-base text-black/80 leading-relaxed text-pretty font-heading">
                    Our algorithms process the data and calculate Air Quality Index (AQI) values, categorizing air
                    quality from Good to Hazardous based on EPA standards.
                  </p>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-2 border-nasa-electric-blue/30 bg-white/80 backdrop-blur hover:border-nasa-electric-blue hover:shadow-lg transition-all">
                <CardContent className="pt-5 md:pt-6 px-4 md:px-6 space-y-3 md:space-y-4 relative">
                  <div className="h-12 w-12 rounded-lg bg-nasa-electric-blue/20 flex items-center justify-center">
                    <Heart className="h-6 w-6 text-nasa-electric-blue" />
                  </div>
                  <h3 className="text-lg md:text-xl font-bold text-black font-heading">Personalized Insights</h3>
                  <p className="text-sm md:text-base text-black/80 leading-relaxed text-pretty font-heading">
                    Based on your health profile (pregnant, child, elderly, asthmatic, or general), we provide tailored
                    recommendations to protect your specific health needs.
                  </p>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-2 border-nasa-rocket-red/30 bg-white/80 backdrop-blur hover:border-nasa-rocket-red hover:shadow-lg transition-all">
                <CardContent className="pt-5 md:pt-6 px-4 md:px-6 space-y-3 md:space-y-4 relative">
                  <div className="h-12 w-12 rounded-lg bg-nasa-rocket-red/20 flex items-center justify-center">
                    <Shield className="h-6 w-6 text-nasa-rocket-red" />
                  </div>
                  <h3 className="text-lg md:text-xl font-bold text-black font-heading">Actionable Alerts</h3>
                  <p className="text-sm md:text-base text-black/80 leading-relaxed text-pretty font-heading">
                    Receive clear, actionable health alerts that help you make informed decisions about outdoor
                    activities, exercise, and daily routines.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      <section className="py-8 md:py-12 bg-nasa-midnight-blue nasa-pattern-code">
        <div className="container mx-auto px-4 md:px-6 space-y-8 md:space-y-12">
          <div className="max-w-4xl mx-auto space-y-4 md:space-y-6">
            <h2 className="text-2xl md:text-4xl font-black text-center mb-6 md:mb-8 text-white font-heading">
              Understanding Air Pollution & <span className="text-nasa-neon-yellow">Health</span>
            </h2>

            <Card className="relative overflow-hidden border-2 border-nasa-neon-yellow/30 bg-nasa-deep-space/50 backdrop-blur shadow-xl">
              <div className="absolute inset-0 bg-[url('/patterns/waves.png')] opacity-25 bg-repeat" />
              <CardContent className="pt-6 md:pt-8 px-4 md:px-6 space-y-6 md:space-y-8 relative">
                <div>
                  <h3 className="text-lg md:text-xl font-bold mb-2 md:mb-3 text-nasa-neon-yellow flex items-center gap-3 md:gap-4">
                    <Satellite className="h-8 w-8 md:h-10 md:w-10" />
                    PM2.5 (Fine Particulate Matter)
                  </h3>
                  <p className="text-sm md:text-lg text-white/80 leading-relaxed text-pretty">
                    Particles smaller than 2.5 micrometers can penetrate deep into lungs and enter the bloodstream.
                    Long-term exposure is linked to cardiovascular disease, respiratory issues, and adverse pregnancy
                    outcomes. Particularly dangerous for pregnant women and developing fetuses.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg md:text-xl font-bold mb-2 md:mb-3 text-nasa-neon-yellow flex items-center gap-3 md:gap-4">
                    <Shield className="h-8 w-8 md:h-10 md:w-10" />
                    NO₂ (Nitrogen Dioxide)
                  </h3>
                  <p className="text-sm md:text-lg text-white/80 leading-relaxed text-pretty">
                    Primarily from vehicle emissions and industrial sources, NO₂ irritates airways and can worsen
                    asthma. Children exposed to high levels show increased respiratory infections and reduced lung
                    function development.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg md:text-xl font-bold mb-2 md:mb-3 text-nasa-neon-yellow flex items-center gap-3 md:gap-4">
                    <Heart className="h-8 w-8 md:h-10 md:w-10" />
                    O₃ (Ground-Level Ozone)
                  </h3>
                  <p className="text-sm md:text-lg text-white/80 leading-relaxed text-pretty">
                    Forms when pollutants react with sunlight. Can trigger asthma attacks, reduce lung function, and
                    cause respiratory inflammation. Elderly individuals are at higher risk for ozone-related health
                    effects.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="max-w-4xl mx-auto">
            <Card className="bg-nasa-deep-space/30 backdrop-blur border-2 border-white/10">
              <CardContent className="pt-5 md:pt-6 px-4 md:px-6 space-y-3 md:space-y-4">
                <h3 className="text-lg md:text-xl font-bold text-white">Scientific References</h3>
                <ul className="space-y-2 text-xs md:text-sm text-white/70">
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

          <div className="max-w-4xl mx-auto text-center">
            <Card className="relative overflow-hidden border-2 border-nasa-electric-blue/30 nasa-gradient-blue shadow-xl">
              <div className="absolute inset-0 bg-[url('/patterns/rosette.png')] opacity-25 bg-repeat" />
              <CardContent className="pt-5 md:pt-6 px-4 md:px-6 space-y-3 md:space-y-4 relative">
                <Image
                  src="/logos/nasa-logo-white.svg"
                  alt="NASA"
                  width={60}
                  height={60}
                  className="mx-auto opacity-90 md:w-[80px] md:h-[80px]"
                />
                <h3 className="text-lg md:text-xl font-bold text-white">Built for NASA Space Apps Challenge</h3>
                <p className="text-sm md:text-base text-white/90 text-pretty">
                  This application was developed as part of the NASA Space Apps Challenge, utilizing NASA's open Earth
                  observation data to create solutions that benefit humanity.
                </p>
                <p className="text-xs md:text-sm text-white/70">
                  Data sources: NASA MODIS, Sentinel-5P, and EPA AirNow
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  )
}
