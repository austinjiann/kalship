'use client'

import { useState, useRef, useEffect } from 'react'
import { Iphone } from '@/components/ui/iphone'
import Feed, { FeedRef } from '@/components/Feed'
import { KalshiMarket, FeedItem } from '@/types'

const API_URL = 'http://localhost:8000'

export default function Home() {
  const [feedItems, setFeedItems] = useState<FeedItem[]>([])
  const [currentMarket, setCurrentMarket] = useState<KalshiMarket | undefined>(undefined)
  const [loading, setLoading] = useState(true)
  const feedRef = useRef<FeedRef>(null)

  useEffect(() => {
    async function fetchFeed() {
      try {
        const res = await fetch(`${API_URL}/feed`)
        if (res.ok) {
          const data = await res.json()
          setFeedItems(data)
          if (data[0]?.kalshi) {
            setCurrentMarket(data[0].kalshi)
          }
        }
      } catch (err) {
        console.error('Failed to fetch feed:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchFeed()
  }, [])

  const handleBet = (side: 'YES' | 'NO') => {
    console.log(`Bet placed: ${side} on ${currentMarket?.ticker}`)
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#9a9a7f]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
          <div className="text-white text-xl" style={{ fontFamily: "var(--font-playfair), serif" }}>Loading bets...</div>
        </div>
      </div>
    )
  }

  if (feedItems.length === 0) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#9a9a7f]">
        <div className="text-white text-xl" style={{ fontFamily: "var(--font-playfair), serif" }}>No bets available</div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#9a9a7f] p-8 gap-8">
      <Iphone className="max-w-[340px]" frameColor="#2a2a2a">
        <Feed key={feedItems.length} ref={feedRef} items={feedItems} onCurrentItemChange={(item) => setCurrentMarket(item.kalshi)} />
      </Iphone>

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <button
            onClick={() => feedRef.current?.scrollToPrev()}
            className="flex items-center justify-center w-12 h-12 bg-[#1a1a1a] rounded-full text-white hover:bg-[#2a2a2a] transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
              <path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/>
            </svg>
          </button>
          <button
            onClick={() => feedRef.current?.scrollToNext()}
            className="flex items-center justify-center w-12 h-12 bg-[#1a1a1a] rounded-full text-white hover:bg-[#2a2a2a] transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
              <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6z"/>
            </svg>
          </button>
        </div>
        
        {currentMarket && (
          <div className="flex flex-col gap-4 p-6 bg-[#1a1a1a] rounded-2xl min-w-[280px] max-w-[320px]" style={{ fontFamily: "var(--font-playfair), serif" }}>
            <div className="text-sm text-gray-400 leading-snug">{currentMarket.question}</div>
            <div className="text-xl font-semibold text-white">{currentMarket.outcome}</div>
            <div className="flex flex-col gap-3">
              <button 
                className="flex justify-between items-center px-5 py-4 bg-green-500 text-white font-bold rounded-xl hover:opacity-90 active:scale-[0.97] transition-all"
                onClick={() => handleBet('YES')}
              >
                <span className="text-base">YES</span>
                <span className="text-xl">{currentMarket.yes_price}¢</span>
              </button>
              <button 
                className="flex justify-between items-center px-5 py-4 bg-red-500 text-white font-bold rounded-xl hover:opacity-90 active:scale-[0.97] transition-all"
                onClick={() => handleBet('NO')}
              >
                <span className="text-base">NO</span>
                <span className="text-xl">{currentMarket.no_price}¢</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
