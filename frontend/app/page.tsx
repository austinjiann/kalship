'use client'

import { useState, useRef } from 'react'
import { Iphone } from '@/components/ui/iphone'
import Feed, { FeedRef } from '@/components/Feed'
import { mockFeedItems } from '@/data/mockFeed'
import { KalshiMarket } from '@/types'

export default function Home() {
  const [currentMarket, setCurrentMarket] = useState<KalshiMarket>(mockFeedItems[0]?.kalshi)
  const feedRef = useRef<FeedRef>(null)

  const handleBet = (side: 'YES' | 'NO') => {
    console.log(`Bet placed: ${side} on ${currentMarket?.ticker}`)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#9a9a7f] p-8 gap-8">
      <Iphone className="max-w-[340px]" frameColor="#2a2a2a">
        <Feed ref={feedRef} items={mockFeedItems} onCurrentItemChange={(item) => setCurrentMarket(item.kalshi)} />
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
            <div className="text-lg font-semibold text-white leading-snug">{currentMarket.title}</div>
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
