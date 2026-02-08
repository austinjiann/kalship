'use client'

import { useEffect, useRef, useImperativeHandle, forwardRef, memo, useState, useCallback } from 'react'
import { FeedItem } from '@/types'
import ShortCard from './ShortCard'
import { prefetchVideoBlob } from '@/lib/videoCache'

const PREFETCH_LOOKAHEAD = 3
const PREFETCH_BEHIND = 1
const prefetchedVideoUrls = new Set<string>()

function prefetchMp4Source(url?: string) {
  if (!url || prefetchedVideoUrls.has(url) || typeof document === 'undefined') {
    return
  }
  try {
    prefetchedVideoUrls.add(url)
    const link = document.createElement('link')
    link.rel = 'preload'
    link.as = 'video'
    link.href = url
    link.crossOrigin = 'anonymous'
    link.setAttribute('fetchpriority', 'high')
    link.dataset.prefetch = 'ai-video'
    document.head.appendChild(link)
  } catch (error) {
    console.warn('[prefetch] Failed to warm AI video', error)
  }
}

interface FeedProps {
  items: FeedItem[]
  onCurrentItemChange?: (item: FeedItem) => void
  paused?: boolean
}

export interface FeedRef {
  scrollToNext: () => void
  scrollToPrev: () => void
}

const FeedComponent = forwardRef<FeedRef, FeedProps>(function Feed({ items, onCurrentItemChange, paused }, ref) {
  const containerRef = useRef<HTMLDivElement>(null)
  const activeIndexRef = useRef(0)
  const onCurrentItemChangeRef = useRef(onCurrentItemChange)
  const lastNotifiedVideoRef = useRef<string | undefined>(undefined)
  const [activeIndex, setActiveIndex] = useState(0)
  useEffect(() => {
    onCurrentItemChangeRef.current = onCurrentItemChange
  }, [onCurrentItemChange])

  const itemsRef = useRef(items)
  useEffect(() => {
    itemsRef.current = items
  }, [items])

  const maxAvailableIndex = Math.max(items.length - 1, 0)
  const safeActiveIndex = Math.max(Math.min(activeIndex, maxAvailableIndex), 0)

  useEffect(() => {
    activeIndexRef.current = safeActiveIndex
  }, [safeActiveIndex])

  const setActiveItem = useCallback((index: number) => {
    if (index < 0 || index >= itemsRef.current.length) {
      return
    }
    activeIndexRef.current = index
    setActiveIndex(index)
    const activeItem = itemsRef.current[index]
    if (activeItem) {
      lastNotifiedVideoRef.current = activeItem.id
      onCurrentItemChangeRef.current?.(activeItem)
    }
  }, [])

  const scrollTo = useCallback((index: number) => {
    if (!containerRef.current || index < 0 || index >= itemsRef.current.length) {
      return
    }
    const container = containerRef.current
    const itemHeight = container.clientHeight
    container.scrollTo({ top: index * itemHeight, behavior: 'smooth' })
    setActiveItem(index)
  }, [setActiveItem])

  useImperativeHandle(ref, () => ({
    scrollToNext: () => scrollTo(activeIndexRef.current + 1),
    scrollToPrev: () => scrollTo(activeIndexRef.current - 1),
  }), [scrollTo])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleScroll = () => {
      const scrollTop = container.scrollTop
      const itemHeight = container.clientHeight
      const currentIndex = Math.round(scrollTop / itemHeight)

      if (currentIndex !== activeIndexRef.current && itemsRef.current[currentIndex]) {
        setActiveItem(currentIndex)
      }
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [setActiveItem])

  useEffect(() => {
    const activeItem = items[safeActiveIndex]
    if (!activeItem) {
      lastNotifiedVideoRef.current = undefined
      return
    }
    if (lastNotifiedVideoRef.current === activeItem.id) {
      return
    }
    lastNotifiedVideoRef.current = activeItem.id
    onCurrentItemChangeRef.current?.(activeItem)
  }, [items, safeActiveIndex])

  useEffect(() => {
    if (typeof document === 'undefined') return
    const indicesToWarm = new Set<number>()
    for (let offset = -PREFETCH_BEHIND; offset <= PREFETCH_LOOKAHEAD; offset++) {
      const idx = safeActiveIndex + offset
      if (idx >= 0 && idx < items.length) {
        indicesToWarm.add(idx)
      }
    }
    indicesToWarm.forEach((idx) => {
      const candidate = items[idx]
      if (candidate?.video?.type === 'mp4') {
        prefetchMp4Source(candidate.video.url)
        prefetchVideoBlob(candidate.video.url)
      }
    })
  }, [items, safeActiveIndex])

  return (
    <div ref={containerRef} className="feed-container">
      {items.map((item, index) => {
        const renderWindow = item.video?.type === 'mp4' ? 3 : 2
        const shouldRender = Math.abs(index - safeActiveIndex) <= renderWindow
        return (
          <ShortCard
            key={`${item.id}-${index}`}
            item={item}
            isActive={index === safeActiveIndex && !paused}
            shouldRender={shouldRender}
          />
        )
      })}
    </div>
  )
})

export default memo(FeedComponent, (prev, next) => {
  return prev.items === next.items && prev.onCurrentItemChange === next.onCurrentItemChange && prev.paused === next.paused
})
