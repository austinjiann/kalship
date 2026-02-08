'use client'

import { useState, useCallback, useEffect, useRef, useMemo } from 'react'
import { QueueItem, FeedItem } from '@/types'
import { VIDEO_IDS } from '@/mystery'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const BATCH_SIZE = 10

const buildInitialQueue = (): QueueItem[] =>
  VIDEO_IDS.map(id => ({
    video_id: id,
    status: 'pending',
  }))

export function useVideoQueue() {
  const [queue, setQueue] = useState<QueueItem[]>(() => buildInitialQueue())
  const [isProcessing, setIsProcessing] = useState(false)
  const isProcessingRef = useRef(false)
  const [injectedItems, setInjectedItems] = useState<{ item: FeedItem; afterIndex: number }[]>([])

  const processQueue = useCallback(async () => {
    if (isProcessingRef.current) return
    setIsProcessing(true)
    isProcessingRef.current = true

    let pendingIds: string[] = []
    setQueue(prev => {
      pendingIds = prev
        .filter(q => q.status === 'pending')
        .map(q => q.video_id)
        .slice(0, BATCH_SIZE)
      if (pendingIds.length === 0) {
        return prev
      }
      return prev.map(item =>
        pendingIds.includes(item.video_id) && item.status === 'pending'
          ? { ...item, status: 'processing' }
          : item
      )
    })

    if (pendingIds.length === 0) {
      setIsProcessing(false)
      isProcessingRef.current = false
      return
    }

    try {
      console.log('[videoQueue] requesting feed for', pendingIds)
      const res = await fetch(`${API_URL}/shorts/feed?video_ids=${pendingIds.join(',')}`)
      if (!res.ok) {
        throw new Error(`Failed to fetch feed: ${res.status}`)
      }
      const results: FeedItem[] = await res.json()
      const resultsMap = new Map(results.map(r => [r.youtube.video_id, r]))

      setQueue(prev => {
        const next = prev.map(item => {
          if (pendingIds.includes(item.video_id)) {
            const result = resultsMap.get(item.video_id)
            if (result) {
              return { ...item, status: 'matched' as const, result }
            }
            if (item.status === 'matched' && item.result) {
              return item
            }
            return { ...item, status: 'failed' as const, error: 'No match found', result: undefined }
          }
          return item
        })

        return next
      })
    } catch (err) {
      setQueue(prev => prev.map(item => {
        if (pendingIds.includes(item.video_id) && item.status === 'processing') {
          console.error('[videoQueue] feed request failed', err)
          return { ...item, status: 'failed', error: String(err) }
        }
        return item
      }))
    } finally {
      setIsProcessing(false)
      isProcessingRef.current = false
    }
  }, [])

  const addVideos = useCallback((videoIds: string[]) => {
    setQueue(prev => {
      const existingIds = new Set(prev.map(q => q.video_id))
      const newItems: QueueItem[] = videoIds
        .filter(id => !existingIds.has(id))
        .map(id => ({ video_id: id, status: 'pending' }))
      return [...prev, ...newItems]
    })
  }, [])

  const clearQueue = useCallback(() => {
    setQueue(buildInitialQueue())
    setInjectedItems([])
    setTimeout(() => {
      if (!isProcessingRef.current) {
        processQueue()
      }
    }, 0)
  }, [processQueue])

  useEffect(() => {
    isProcessingRef.current = isProcessing
  }, [isProcessing])

  // Ensure processing starts immediately when the hook mounts
  useEffect(() => {
    if (!isProcessingRef.current) {
      processQueue()
    }
  }, [processQueue])

  useEffect(() => {
    if (queue.length === 0) return
    const hasPending = queue.some(q => q.status === 'pending')
    if (hasPending && !isProcessingRef.current) {
      processQueue()
    }
  }, [queue, processQueue])

  const feedItems = useMemo(() => {
    const base = queue
      .filter(q => q.status === 'matched' && q.result)
      .map(q => q.result!)

    if (injectedItems.length === 0) return base

    const ready = injectedItems.filter(({ afterIndex }) => afterIndex < base.length)
    if (ready.length === 0) {
      return base
    }

    // Sort injections by position descending so splicing doesn't shift indices
    const sorted = [...ready].sort((a, b) => b.afterIndex - a.afterIndex)
    const result = [...base]
    for (const { item, afterIndex } of sorted) {
      const insertAt = Math.min(afterIndex + 1, result.length)
      result.splice(insertAt, 0, item)
    }
    return result
  }, [queue, injectedItems])

  const stats = useMemo(() => ({
    total: queue.length,
    pending: queue.filter(q => q.status === 'pending').length,
    processing: queue.filter(q => q.status === 'processing').length,
    matched: queue.filter(q => q.status === 'matched').length,
    failed: queue.filter(q => q.status === 'failed').length,
  }), [queue])

  const feedError = useMemo(() => {
    const failed = queue.find(q => q.status === 'failed' && q.error)
    return failed?.error ?? null
  }, [queue])

  const injectFeedItem = useCallback((item: FeedItem, afterIndex: number) => {
    setInjectedItems(prev => [...prev, { item, afterIndex }])
  }, [])

  const retryFailed = useCallback(() => {
    setQueue(prev =>
      prev.map(item =>
        item.status === 'failed'
          ? { ...item, status: 'pending' as const, error: undefined }
          : item
      )
    )
  }, [])

  return {
    queue,
    feedItems,
    stats,
    feedError,
    isProcessing,
    addVideos,
    clearQueue,
    processQueue,
    retryFailed,
    injectFeedItem,
  }
}
