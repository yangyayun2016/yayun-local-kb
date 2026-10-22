"use client"

import { useRef, useState } from "react"
import { Header } from "@/components/header"
import { HeroSection } from "@/components/hero-section"
import { TrendingSection } from "@/components/trending-section"
import { LatestActivity } from "@/components/latest-activity"
import { LeaderboardList } from "@/components/leaderboard-list"
import { Footer } from "@/components/footer"
import { MobileLayout } from "@/components/mobile-layout"

export default function Home() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [selectedRank, setSelectedRank] = useState<number | undefined>()
  const [selectedBid, setSelectedBid] = useState<number | undefined>()

  const handleClaimClick = (rank: number, bid: number) => {
    setSelectedRank(rank)
    setSelectedBid(bid)
    if (inputRef.current) {
      inputRef.current.focus()
      inputRef.current.scrollIntoView({ behavior: "smooth", block: "center" })
    }
  }

  return (
    <MobileLayout>
      <div className="min-h-screen flex flex-col overflow-x-hidden">
        <Header />
        <main className="flex-1">
          <div className="max-w-4xl mx-auto px-4 py-8">
            <HeroSection key={selectedRank} ref={inputRef} selectedRank={selectedRank} selectedBid={selectedBid} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <TrendingSection />
              <LatestActivity />
            </div>
            <div className="mt-8">
              <LeaderboardList onClaimClick={handleClaimClick} />
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </MobileLayout>
  )
}