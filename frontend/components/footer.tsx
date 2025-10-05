import Link from "next/link"
import { Wind } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-card">
      <div className="container mx-auto py-8 md:py-12 px-4 md:px-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
          <div className="space-y-3 sm:col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 font-bold text-lg">
              <Wind className="h-5 w-5 text-primary" />
              <span>BREATHSAFE</span>
            </Link>
            <p className="text-sm text-muted-foreground max-w-xs">
              Personal Air Health Assistant powered by NASA open data.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-3 text-sm md:text-base">Product</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="/map" className="hover:text-foreground transition-colors">
                  Air Quality Map
                </Link>
              </li>
              <li>
                <Link href="/alerts" className="hover:text-foreground transition-colors">
                  Health Alerts
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-foreground transition-colors">
                  About
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-3 text-sm md:text-base">Resources</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a
                  href="https://earthdata.nasa.gov/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-foreground transition-colors"
                >
                  NASA Earth Data
                </a>
              </li>
              <li>
                <a
                  href="https://www.epa.gov/air-quality"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-foreground transition-colors"
                >
                  EPA Air Quality
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-3 text-sm md:text-base">Legal</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="#" className="hover:text-foreground transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-foreground transition-colors">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-6 md:mt-8 pt-6 md:pt-8 border-t border-border/40 text-center text-xs md:text-sm text-muted-foreground">
          <p>© 2025 BREATHSAFE. Built with NASA open data for NASA Space Apps Challenge.</p>
        </div>
      </div>
    </footer>
  )
}
