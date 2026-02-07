'use client'

import { KalshiMarket } from '@/types'

interface KalshiOverlayProps {
  market: KalshiMarket
  onYes: () => void
  onNo: () => void
}

export default function KalshiOverlay({ market, onYes, onNo }: KalshiOverlayProps) {
  return (
    <div className="kalshi-overlay">
      <div className="kalshi-question">{market.title}</div>
      <div className="kalshi-buttons">
        <button className="kalshi-btn kalshi-yes" onClick={onYes}>
          <span className="kalshi-label">YES</span>
          <span className="kalshi-price">{market.yes_price}¢</span>
        </button>
        <button className="kalshi-btn kalshi-no" onClick={onNo}>
          <span className="kalshi-label">NO</span>
          <span className="kalshi-price">{market.no_price}¢</span>
        </button>
      </div>
    </div>
  )
}
