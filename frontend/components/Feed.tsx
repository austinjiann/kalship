'use client'

import { useEffect, useRef, useCallback, useState, useImperativeHandle, forwardRef } from 'react'
import { FeedItem } from '@/types'
import ShortCard from './ShortCard'

interface FeedProps {
  items: FeedItem[]
  onCurrentItemChange?: (item: FeedItem) => void
}

export interface FeedRef {
  scrollToNext: () => void
  scrollToPrev: () => void
}

export default forwardRef<FeedRef, FeedProps>(function Feed({ items, onCurrentItemChange }, ref) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [activeIndex, setActiveIndex] = useState(0)

  const scrollToIndex = useCallback((index: number) => {
    if (!containerRef.current || index < 0 || index >= items.length) return
    const container = containerRef.current
    const itemHeight = container.clientHeight
    container.scrollTo({ top: index * itemHeight, behavior: 'smooth' })
  }, [items.length])

  useImperativeHandle(ref, () => ({
    scrollToNext: () => scrollToIndex(activeIndex + 1),
    scrollToPrev: () => scrollToIndex(activeIndex - 1),
  }), [activeIndex, scrollToIndex])

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return
    
    const container = containerRef.current
    const scrollTop = container.scrollTop
    const itemHeight = container.clientHeight
    const currentIndex = Math.round(scrollTop / itemHeight)
    
    if (currentIndex !== activeIndex && items[currentIndex]) {
      setActiveIndex(currentIndex)
      onCurrentItemChange?.(items[currentIndex])
    }
  }, [items, onCurrentItemChange, activeIndex])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    
    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [handleScroll])

  useEffect(() => {
    if (items.length > 0 && onCurrentItemChange) {
      onCurrentItemChange(items[0])
    }
  }, [])

  return (
    <div ref={containerRef} className="feed-container">
      {items.map((item, index) => (
        <ShortCard key={item.id} item={item} isActive={index === activeIndex} />
      ))}
    </div>
  )
})
