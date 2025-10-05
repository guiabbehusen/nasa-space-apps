import Link from "next/link"
import { Wind, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 md:px-6">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg md:text-xl">
          <Wind className="h-5 w-5 md:h-6 md:w-6 text-primary" />
          <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">BREATHSAFE</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-6">
          <Link href="/" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Home
          </Link>
          <Link
            href="/map"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Map
          </Link>
          <Link
            href="/alerts"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Alerts
          </Link>
          <Link
            href="/about"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            About
          </Link>
        </div>

        <div className="flex items-center gap-2">
          <Button asChild size="sm" className="hidden sm:flex">
            <Link href="/map">Check Air Quality</Link>
          </Button>

          <Button asChild size="sm" className="sm:hidden">
            <Link href="/map">Check</Link>
          </Button>

          {/* Mobile Menu */}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right">
              <nav className="flex flex-col gap-4 mt-8">
                <Link href="/" className="text-lg font-medium hover:text-primary transition-colors">
                  Home
                </Link>
                <Link href="/map" className="text-lg font-medium hover:text-primary transition-colors">
                  Map
                </Link>
                <Link href="/alerts" className="text-lg font-medium hover:text-primary transition-colors">
                  Alerts
                </Link>
                <Link href="/about" className="text-lg font-medium hover:text-primary transition-colors">
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
