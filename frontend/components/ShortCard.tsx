'use client'

import { FeedItem } from '@/types'

interface ShortCardProps {
  item: FeedItem
  isActive?: boolean
}

export default function ShortCard({ item, isActive = false }: ShortCardProps) {
  const kalshi = item.kalshi

  return (
    <div className="short-card">
      <div className="video-container">
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${item.youtube.video_id}?autoplay=${isActive ? 1 : 0}&loop=1&mute=0&playlist=${item.youtube.video_id}&controls=1&modestbranding=1&playsinline=1&rel=0`}
          title={item.youtube.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="video-iframe"
          style={{ pointerEvents: 'auto' }}
        />
      </div>

      {kalshi && (
        <div className="bet-card">
          <div className="bet-card-header">
            {kalshi.image_url && (
              <img src={kalshi.image_url} alt="" className="bet-card-image" />
            )}
            <span className="bet-card-question">{kalshi.question}</span>
          </div>
          <div className="bet-card-outcome">
            <span className="bet-card-outcome-name">{kalshi.outcome}</span>
            <div className="bet-card-buttons">
              <button className="bet-btn bet-btn-yes">Yes</button>
              <button className="bet-btn bet-btn-no">No</button>
            </div>
          </div>
          <div className="bet-card-footer">
            {kalshi.volume && <span className="bet-card-volume">${Math.round(kalshi.volume / 1000)}k Vol.</span>}
          </div>
        </div>
      )}

      <div className="short-info">
        <span className="channel-name">@{item.youtube.channel}</span>
        <span className="video-title">{item.youtube.title}</span>
      </div>
    </div>
  )
}
