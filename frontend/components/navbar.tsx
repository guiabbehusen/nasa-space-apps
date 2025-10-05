import Link from "next/link"
import { Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import Image from "next/image"

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-nasa-midnight-blue backdrop-blur supports-[backdrop-filter]:bg-nasa-midnight-blue/95">
      <div className="container mx-auto flex h-16 md:h-20 items-center justify-between px-4 md:px-6">
        <Link href="/" className="flex items-center gap-3 md:gap-4 font-bold">
          <div className="flex items-center gap-2 md:gap-3">
            <Image
              src="/logos/nasa-icon-simple.png"
              alt="NASA"
              width={24}
              height={24}
              className="w-5 h-5 md:w-7 md:h-7 opacity-90"
            />
            <span className="text-white font-heading text-base md:text-xl">BREATHSAFE</span>
          </div>
          <div className="hidden sm:block h-8 w-px bg-white/20" />
          <span className="hidden sm:block text-sm text-white/60 font-mono">Powered by NASA</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          <Link href="/" className="text-base font-medium text-white/70 hover:text-white transition-colors">
            Home
          </Link>
          <Link href="/map" className="text-base font-medium text-white/70 hover:text-white transition-colors">
            Map
          </Link>
          <Link href="/alerts" className="text-base font-medium text-white/70 hover:text-white transition-colors">
            Alerts
          </Link>
          <Link href="/about" className="text-base font-medium text-white/70 hover:text-white transition-colors">
            About
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <Button
            asChild
            size="default"
            className="hidden sm:flex bg-nasa-rocket-red hover:bg-nasa-rocket-red/90 text-white font-bold"
          >
            <Link href="/map">Check Air Quality</Link>
          </Button>

          <Button
            asChild
            size="sm"
            className="sm:hidden bg-nasa-rocket-red hover:bg-nasa-rocket-red/90 text-white font-bold"
          >
            <Link href="/map">Check AQ</Link>
          </Button>

          {/* Mobile Menu */}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
                <Menu className="h-6 w-6" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="bg-nasa-midnight-blue border-white/10 w-[280px] sm:w-[320px]">
              <nav className="flex flex-col gap-8 mt-12">
                <Link
                  href="/"
                  className="text-lg font-medium text-white hover:text-nasa-electric-blue transition-colors py-2"
                >
                  Home
                </Link>
                <Link
                  href="/map"
                  className="text-lg font-medium text-white hover:text-nasa-electric-blue transition-colors py-2"
                >
                  Map
                </Link>
                <Link
                  href="/alerts"
                  className="text-lg font-medium text-white hover:text-nasa-electric-blue transition-colors py-2"
                >
                  Alerts
                </Link>
                <Link
                  href="/about"
                  className="text-lg font-medium text-white hover:text-nasa-electric-blue transition-colors py-2"
                >
                  About
                </Link>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </nav>
  )
}
