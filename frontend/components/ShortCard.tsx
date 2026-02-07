'use client'

import { FeedItem } from '@/types'

interface ShortCardProps {
  item: FeedItem
  isActive?: boolean
}

export default function ShortCard({ item, isActive = false }: ShortCardProps) {
  return (
    <div className="short-card">
      <div className="video-container">
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${item.youtube.video_id}?autoplay=${isActive ? 1 : 0}&loop=1&mute=0&playlist=${item.youtube.video_id}&controls=0&modestbranding=1&playsinline=1&rel=0`}
          title={item.youtube.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="video-iframe"
        />
      </div>
      <div className="short-sidebar">
        <button className="sidebar-btn">
          <svg viewBox="0 0 24 24" fill="currentColor" className="sidebar-icon">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
          <span className="sidebar-count">12.5K</span>
        </button>
        <button className="sidebar-btn">
          <svg viewBox="0 0 24 24" fill="currentColor" className="sidebar-icon">
            <path d="M21 6h-2V4c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2v2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-4 0H7V4h10v2z"/>
          </svg>
          <span className="sidebar-count">843</span>
        </button>
        <button className="sidebar-btn">
          <svg viewBox="0 0 24 24" fill="currentColor" className="sidebar-icon">
            <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/>
          </svg>
          <span className="sidebar-count">Share</span>
        </button>
      </div>
      <div className="short-info">
        <span className="channel-name">@{item.youtube.channel}</span>
        <span className="video-title">{item.youtube.title}</span>
      </div>
    </div>
  )
}
