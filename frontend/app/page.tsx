import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Wind, MapPin, Bell, Shield, Activity, Heart } from "lucide-react"
import Image from "next/image"

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden nasa-gradient nasa-pattern-orbits">
        <div className="container mx-auto relative py-12 md:py-20 lg:py-24 px-4">
          <div className="mx-auto max-w-3xl text-center space-y-6 md:space-y-8">
            <div className="flex items-center justify-center gap-4 md:gap-6 mb-4 md:mb-6">
              <Image
                src="/logos/nasa-logo.png"
                alt="NASA"
                width={320}
                height={80}
                className="opacity-90 w-[200px] h-auto md:w-[320px]"
              />
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-black tracking-tight text-balance text-white font-heading">
                BREATHSAFE
              </h1>
            </div>

            <div className="inline-flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 rounded-full bg-white/10 border border-white/20 text-xs md:text-sm font-medium text-white backdrop-blur">
              <Image
                src="/logos/nasa-icon-simple.png"
                alt="NASA"
                width={16}
                height={16}
                className="w-3 h-3 md:w-4 md:h-4 opacity-90"
              />
              Powered by NASA Open Data
            </div>

            <h2 className="text-2xl md:text-4xl lg:text-5xl font-black tracking-tight text-balance text-nasa-neon-yellow font-heading">
              Personal Air Health Assistant
            </h2>

            <p className="text-lg md:text-2xl text-white/90 text-balance font-bold">
              Know your air. Protect your health.
            </p>

            <p className="text-base md:text-lg text-white/80 max-w-2xl mx-auto text-pretty">
              We use NASA open data to help you stay safe from invisible air pollution. Get real-time air quality
              insights and personalized health recommendations.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 md:gap-4 justify-center pt-2 md:pt-4">
              <Button
                asChild
                size="lg"
                className="text-base md:text-xl bg-nasa-neon-yellow text-black hover:bg-nasa-neon-yellow/90 font-bold px-6 py-3 md:px-8 md:py-4 h-auto uppercase"
              >
                <Link href="/map">
                  <MapPin className="mr-2 md:mr-3 h-5 w-5 md:h-6 md:w-6" />
                  Check Air Quality Now
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="text-sm md:text-lg bg-transparent border-white text-white hover:bg-white/10 px-6 py-3 md:px-8 md:py-4 h-auto uppercase"
              >
                <Link href="/about">Learn More</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24 bg-white nasa-pattern-waves-light">
        <div className="container mx-auto space-y-16 md:space-y-24 px-4">
          {/* Health Profiles */}
          <div>
            <div className="text-center mb-12 md:mb-16 space-y-3 md:space-y-4">
              <h2 className="text-2xl md:text-4xl font-black text-balance text-black font-heading">
                Personalized for Your Health Profile
              </h2>
              <p className="text-base md:text-lg text-black/80 max-w-2xl mx-auto text-pretty font-heading">
                Get tailored air quality recommendations based on your specific health needs and vulnerabilities.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 md:gap-6">
              <Card className="border-nasa-neon-yellow/30 bg-white/80 backdrop-blur hover:border-nasa-neon-yellow hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4 text-center">
                  <div className="text-5xl mb-2">🤰</div>
                  <h3 className="text-xl font-bold text-black font-heading">Pregnant Women</h3>
                  <p className="text-black/70 text-pretty text-sm font-heading">
                    Enhanced protection for maternal and fetal health during pregnancy.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-electric-blue/30 bg-white/80 backdrop-blur hover:border-nasa-electric-blue hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4 text-center">
                  <div className="text-5xl mb-2">👶</div>
                  <h3 className="text-xl font-bold text-black font-heading">Children</h3>
                  <p className="text-black/70 text-pretty text-sm font-heading">
                    Extra care for developing lungs and immune systems.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-bright-blue/30 bg-white/80 backdrop-blur hover:border-nasa-bright-blue hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4 text-center">
                  <div className="text-5xl mb-2">👴</div>
                  <h3 className="text-xl font-bold text-black font-heading">Elderly</h3>
                  <p className="text-black/70 text-pretty text-sm font-heading">
                    Senior health monitoring with age-specific recommendations.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-rocket-red/30 bg-white/80 backdrop-blur hover:border-nasa-rocket-red hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4 text-center">
                  <div className="text-5xl mb-2">🫁</div>
                  <h3 className="text-xl font-bold text-black font-heading">Asthmatics</h3>
                  <p className="text-black/70 text-pretty text-sm font-heading">
                    Respiratory condition alerts and breathing safety guidance.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-deep-blue/30 bg-white/80 backdrop-blur hover:border-nasa-deep-blue hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4 text-center">
                  <div className="text-5xl mb-2">👤</div>
                  <h3 className="text-xl font-bold text-black font-heading">General Public</h3>
                  <p className="text-black/70 text-pretty text-sm font-heading">
                    Standard air quality monitoring for everyone.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>

          <div>
            <div className="text-center mb-12 md:mb-16 space-y-3 md:space-y-4">
              <h2 className="text-2xl md:text-4xl font-black text-balance text-black font-heading">
                Breathe Easier with Real-Time Insights
              </h2>
              <p className="text-base md:text-lg text-black/80 max-w-2xl mx-auto text-pretty font-heading">
                Monitor air quality levels and receive personalized health alerts based on your profile.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
              <Card className="border-nasa-electric-blue/30 bg-white/80 backdrop-blur hover:border-nasa-electric-blue hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4">
                  <div className="h-16 w-16 rounded-lg bg-nasa-electric-blue/20 flex items-center justify-center">
                    <MapPin className="h-10 w-10 text-nasa-electric-blue" />
                  </div>
                  <h3 className="text-2xl font-bold text-black font-heading">Interactive Map</h3>
                  <p className="text-base text-black/70 text-pretty font-heading">
                    Visualize air quality data on an interactive map with real-time pollutant levels for your location.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-bright-blue/30 bg-white/80 backdrop-blur hover:border-nasa-bright-blue hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4">
                  <div className="h-16 w-16 rounded-lg bg-nasa-bright-blue/20 flex items-center justify-center">
                    <Activity className="h-10 w-10 text-nasa-bright-blue" />
                  </div>
                  <h3 className="text-2xl font-bold text-black font-heading">Pollutant Tracking</h3>
                  <p className="text-base text-black/70 text-pretty font-heading">
                    Monitor PM2.5, NO₂, and O₃ levels with easy-to-understand health risk categories.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-electric-blue/30 bg-white/80 backdrop-blur hover:border-nasa-electric-blue hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4">
                  <div className="h-16 w-16 rounded-lg bg-nasa-electric-blue/20 flex items-center justify-center">
                    <Bell className="h-10 w-10 text-nasa-electric-blue" />
                  </div>
                  <h3 className="text-2xl font-bold text-black font-heading">Health Alerts</h3>
                  <p className="text-base text-black/70 text-pretty font-heading">
                    Get personalized recommendations based on current air quality and your health profile.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-rocket-red/30 bg-white/80 backdrop-blur hover:border-nasa-rocket-red hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4">
                  <div className="h-16 w-16 rounded-lg bg-nasa-rocket-red/20 flex items-center justify-center">
                    <Heart className="h-10 w-10 text-nasa-rocket-red" />
                  </div>
                  <h3 className="text-2xl font-bold text-black font-heading">Profile-Based</h3>
                  <p className="text-base text-black/70 text-pretty font-heading">
                    Tailored alerts for pregnant women, children, elderly, and people with respiratory conditions.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-electric-blue/30 bg-white/80 backdrop-blur hover:border-nasa-electric-blue hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4">
                  <div className="h-16 w-16 rounded-lg bg-nasa-electric-blue/20 flex items-center justify-center">
                    <Shield className="h-10 w-10 text-nasa-electric-blue" />
                  </div>
                  <h3 className="text-2xl font-bold text-black font-heading">NASA Data</h3>
                  <p className="text-base text-black/70 text-pretty font-heading">
                    Powered by reliable NASA Earth observation data and scientific research.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-nasa-bright-blue/30 bg-white/80 backdrop-blur hover:border-nasa-bright-blue hover:shadow-lg transition-all">
                <CardContent className="pt-6 space-y-4">
                  <div className="h-16 w-16 rounded-lg bg-nasa-bright-blue/20 flex items-center justify-center">
                    <Wind className="h-10 w-10 text-nasa-bright-blue" />
                  </div>
                  <h3 className="text-2xl font-bold text-black font-heading">Easy to Use</h3>
                  <p className="text-base text-black/70 text-pretty font-heading">
                    Clean, intuitive interface designed for everyone to understand air quality at a glance.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24 bg-nasa-deep-blue nasa-pattern-fiduciaries">
        <div className="container mx-auto px-4">
          <Card className="border-nasa-rocket-red/30 nasa-gradient-red overflow-hidden">
            <CardContent className="py-12 md:py-16 text-center space-y-4 md:space-y-6 px-4">
              <h2 className="text-2xl md:text-4xl lg:text-5xl font-black tracking-tight text-balance text-white font-heading">
                Ready to Breathe Safer?
              </h2>
              <p className="text-base md:text-lg text-white/90 max-w-2xl mx-auto text-pretty">
                Start monitoring the air quality in your area and get personalized health recommendations today.
              </p>
              <Button
                asChild
                size="lg"
                className="text-base md:text-xl bg-nasa-neon-yellow text-black hover:bg-nasa-neon-yellow/90 font-bold px-6 py-3 md:px-8 md:py-4 h-auto uppercase"
              >
                <Link href="/map">
                  <MapPin className="mr-2 md:mr-3 h-5 w-5 md:h-6 md:w-6" />
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
