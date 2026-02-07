'use client'

import { useEffect, useRef, useState, useImperativeHandle, forwardRef } from 'react'
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
  const activeIndexRef = useRef(0)
  const scrollFnRef = useRef<(index: number) => void>(() => {})

  scrollFnRef.current = (index: number) => {
    if (!containerRef.current || index < 0 || index >= items.length) return
    const container = containerRef.current
    const itemHeight = container.clientHeight
    container.scrollTo({ top: index * itemHeight, behavior: 'smooth' })
    activeIndexRef.current = index
    setActiveIndex(index)
    if (items[index]) {
      onCurrentItemChange?.(items[index])
    }
  }

  useImperativeHandle(ref, () => ({
    scrollToNext: () => scrollFnRef.current(activeIndexRef.current + 1),
    scrollToPrev: () => scrollFnRef.current(activeIndexRef.current - 1),
  }), [])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleScroll = () => {
      const scrollTop = container.scrollTop
      const itemHeight = container.clientHeight
      const currentIndex = Math.round(scrollTop / itemHeight)

      if (currentIndex !== activeIndexRef.current && items[currentIndex]) {
        activeIndexRef.current = currentIndex
        setActiveIndex(currentIndex)
        onCurrentItemChange?.(items[currentIndex])
      }
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [items, onCurrentItemChange])

  useEffect(() => {
    if (items.length > 0 && onCurrentItemChange) {
      onCurrentItemChange(items[0])
    }
  }, [items, onCurrentItemChange])

  return (
    <div ref={containerRef} className="feed-container">
      {items.map((item, index) => (
        <ShortCard key={item.id} item={item} isActive={index === activeIndex} />
      ))}
    </div>
  )
})
