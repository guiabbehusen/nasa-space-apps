"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, Clock } from "lucide-react"
import type { TimelineData } from "@/lib/weather-data"

interface TimelineScrubberProps {
  data: TimelineData[]
  currentIndex: number
  onIndexChange: (index: number) => void
}

export default function TimelineScrubber({ data, currentIndex, onIndexChange }: TimelineScrubberProps) {
  const [isDragging, setIsDragging] = useState(false)
  const sliderRef = useRef<HTMLDivElement>(null)

  const currentData = data[currentIndex]
  const currentTime = new Date(currentData.timestamp)
  const now = new Date()
  const isPast = currentTime < now
  const isFuture = currentTime > now

  // 🧩 util para achar o índice mais próximo do "now"
  const getClosestToNowIndex = () => {
    const nowMs = Date.now()
    let closestIndex = 0
    let minDiff = Infinity
    data.forEach((item, i) => {
      const diff = Math.abs(new Date(item.timestamp).getTime() - nowMs)
      if (diff < minDiff) {
        minDiff = diff
        closestIndex = i
      }
    })
    return closestIndex
  }

  const handleSliderClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!sliderRef.current) return
    const rect = sliderRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percentage = x / rect.width
    const newIndex = Math.round(percentage * (data.length - 1))
    onIndexChange(Math.max(0, Math.min(data.length - 1, newIndex)))
  }

  const handleTouchStart = () => setIsDragging(true)
  const handleTouchEnd = () => setIsDragging(false)
  const handleMouseDown = () => setIsDragging(true)
  const handleMouseUp = () => setIsDragging(false)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !sliderRef.current) return
      const rect = sliderRef.current.getBoundingClientRect()
      const x = e.clientX - rect.left
      const percentage = Math.max(0, Math.min(1, x / rect.width))
      const newIndex = Math.round(percentage * (data.length - 1))
      onIndexChange(newIndex)
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (!isDragging || !sliderRef.current) return
      const rect = sliderRef.current.getBoundingClientRect()
      const x = e.touches[0].clientX - rect.left
      const percentage = Math.max(0, Math.min(1, x / rect.width))
      const newIndex = Math.round(percentage * (data.length - 1))
      onIndexChange(newIndex)
    }

    if (isDragging) {
      window.addEventListener("mousemove", handleMouseMove)
      window.addEventListener("mouseup", handleMouseUp)
      window.addEventListener("touchmove", handleTouchMove)
      window.addEventListener("touchend", handleTouchEnd)
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mouseup", handleMouseUp)
      window.removeEventListener("touchmove", handleTouchMove)
      window.removeEventListener("touchend", handleTouchEnd)
    }
  }, [isDragging, data.length, onIndexChange])

  const formatTime = (date: Date) => {
    const hours = date.getHours().toString().padStart(2, "0")
    const minutes = date.getMinutes().toString().padStart(2, "0")
    return `${hours}:${minutes}`
  }

  const formatDate = (date: Date) => {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (date.toDateString() === today.toDateString()) return "Today"
    if (date.toDateString() === tomorrow.toDateString()) return "Tomorrow"
    if (date.toDateString() === yesterday.toDateString()) return "Yesterday"

    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
  }

  const getRelativeTime = () => {
    const diffMs = currentTime.getTime() - now.getTime()
    const diffHours = Math.round(diffMs / (1000 * 60 * 60))

    if (diffHours === 0) return "Now"
    if (diffHours > 0) return `+${diffHours}h`
    return `${diffHours}h`
  }

  const nowIndex = getClosestToNowIndex() // 🧩 usado p/ cálculo de barra e botão Now

  return (
    <Card className="border-2">
      <CardContent className="pt-4 md:pt-6 space-y-4 md:space-y-6 px-3 md:px-6">
        {/* Time Display */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Clock className="h-3 w-3 md:h-4 md:w-4 text-muted-foreground" />
              <span className="text-xs md:text-sm font-medium text-muted-foreground">
                {isPast && "Historical Data"}
                {!isPast && !isFuture && "Current"}
                {isFuture && "Forecast"}
              </span>
            </div>
            <div className="flex items-baseline gap-2 md:gap-3">
              <span className="text-2xl md:text-3xl font-bold">{formatTime(currentTime)}</span>
              <span className="text-base md:text-lg text-muted-foreground">{formatDate(currentTime)}</span>
            </div>
          </div>
          <div className="text-left sm:text-right">
            <div className="text-xl md:text-2xl font-bold text-primary">{getRelativeTime()}</div>
            <div className="text-xs md:text-sm text-muted-foreground">from now</div>
          </div>
        </div>

        {/* Timeline Slider */}
        <div className="space-y-3 md:space-y-4">
          <div className="flex items-center gap-2 md:gap-4">
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8 md:h-10 md:w-10 shrink-0 bg-transparent"
              onClick={() => onIndexChange(Math.max(0, currentIndex - 1))}
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="h-3 w-3 md:h-4 md:w-4" />
            </Button>

            <div className="flex-1 space-y-2">
              {/* Slider Track */}
              <div
                ref={sliderRef}
                className="relative h-10 md:h-12 bg-muted rounded-lg cursor-pointer select-none touch-none"
                onClick={handleSliderClick}
                onMouseDown={handleMouseDown}
                onTouchStart={handleTouchStart}
              >
                {/* Past/Future Indicator */}
                <div className="absolute inset-0 flex">
                  <div
                    className="bg-primary/10 rounded-l-lg transition-all"
                    style={{ width: `${(nowIndex / (data.length - 1)) * 100}%` }} // 🧩 fix alinhado com closestIndex
                  />
                </div>

                {/* Hour Markers */}
                <div className="absolute inset-0 flex items-center justify-between px-1 md:px-2">
                  {data
                    .filter((_, i) => i % 12 === 0)
                    .map((d, i) => (
                      <div key={i} className="flex flex-col items-center">
                        <div className="w-px h-2 md:h-3 bg-border" />
                        <span className="text-[9px] md:text-[10px] text-muted-foreground mt-0.5 md:mt-1 hidden sm:block">
                          {formatTime(new Date(d.timestamp))}
                        </span>
                      </div>
                    ))}
                </div>

                {/* Current Position Indicator */}
                <div
                  className="absolute top-0 bottom-0 w-1 bg-primary rounded-full shadow-lg transition-all"
                  style={{ left: `${(currentIndex / (data.length - 1)) * 100}%`, transform: "translateX(-50%)" }}
                >
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 md:w-4 md:h-4 bg-primary rounded-full border-2 border-background shadow-lg" />
                </div>
              </div>

              {/* Labels */}
              <div className="flex items-center justify-between text-[10px] md:text-xs text-muted-foreground px-1">
                <span>48h ago</span>
                <span className="font-medium text-foreground">Now</span>
                <span>48h ahead</span>
              </div>
            </div>

            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8 md:h-10 md:w-10 shrink-0 bg-transparent"
              onClick={() => onIndexChange(Math.min(data.length - 1, currentIndex + 1))}
              disabled={currentIndex === data.length - 1}
            >
              <ChevronRight className="h-3 w-3 md:h-4 md:w-4" />
            </Button>
          </div>

          {/* Quick Jump Buttons */}
          <div className="flex items-center gap-1.5 md:gap-2 justify-center flex-wrap">
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs md:h-8 md:text-sm px-2 md:px-3 bg-transparent"
              onClick={() => onIndexChange(Math.max(0, currentIndex - 24))}
              disabled={currentIndex < 24}
            >
              -24h
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs md:h-8 md:text-sm px-2 md:px-3 bg-transparent"
              onClick={() => onIndexChange(Math.max(0, currentIndex - 6))}
              disabled={currentIndex < 6}
            >
              -6h
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs md:h-8 md:text-sm px-2 md:px-3 bg-transparent"
              // 🧩 fix “Now” indo 1 à frente → usa índice mais próximo
              onClick={() => onIndexChange(getClosestToNowIndex())}
            >
              Now
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs md:h-8 md:text-sm px-2 md:px-3 bg-transparent"
              onClick={() => onIndexChange(Math.min(data.length - 1, currentIndex + 6))}
              disabled={currentIndex >= data.length - 6}
            >
              +6h
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs md:h-8 md:text-sm px-2 md:px-3 bg-transparent"
              onClick={() => onIndexChange(Math.min(data.length - 1, currentIndex + 24))}
              disabled={currentIndex >= data.length - 24}
            >
              +24h
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
