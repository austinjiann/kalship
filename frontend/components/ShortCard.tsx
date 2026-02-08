'use client'

import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { FeedItem } from '@/types'
import { getPrefetchedVideoUrl, prefetchVideoBlob } from '@/lib/videoCache'

const YT_BASE_ORIGIN = 'https://www.youtube.com'
const ALLOWED_ORIGINS = new Set<string>([YT_BASE_ORIGIN, 'https://www.youtube-nocookie.com'])

let globalMuted = true
const muteListeners = new Set<(value: boolean) => void>()

const emitMuteChange = () => {
  for (const listener of muteListeners) {
    listener(globalMuted)
  }
}

const subscribeToMute = (listener: (value: boolean) => void) => {
  muteListeners.add(listener)
  return () => { muteListeners.delete(listener) }
}

interface ShortCardProps {
  item: FeedItem
  isActive: boolean
  shouldRender?: boolean
}

function ShortCard({ item, isActive, shouldRender = true }: ShortCardProps) {
  const isMP4 = item.video?.type === 'mp4'

  const iframeRef = useRef<HTMLIFrameElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerReadyRef = useRef(false)
  const videoReadyRef = useRef(false)
  const activeStateRef = useRef(isActive)
  const listeningTimersRef = useRef<ReturnType<typeof setTimeout>[]>([])
  const iframeId = useMemo(() => `short-${item.id}`, [item.id])
  const [playerOrigin] = useState(() => (typeof window !== 'undefined' ? window.location.origin : ''))
  const [isMuted, setIsMuted] = useState(globalMuted)
  const [mp4Source, setMp4Source] = useState(() => (isMP4 && item.video?.type === 'mp4' ? item.video.url : ''))

  const iframeSrc = useMemo(() => {
    if (isMP4) return ''
    const originParam = playerOrigin ? `&origin=${encodeURIComponent(playerOrigin)}` : ''
    return (
      `${YT_BASE_ORIGIN}/embed/${item.youtube.video_id}` +
      `?autoplay=1&loop=1&mute=1&playlist=${item.youtube.video_id}` +
      '&controls=0&playsinline=1&rel=0&enablejsapi=1' +
      originParam
    )
  }, [isMP4, item.youtube.video_id, playerOrigin])

  const postPlayerMessage = useCallback((func: string, args: unknown[] = []) => {
    const iframe = iframeRef.current
    if (!iframe) return
    iframe.contentWindow?.postMessage(JSON.stringify({
      event: 'command',
      func,
      args,
      id: iframeId,
    }), YT_BASE_ORIGIN)
  }, [iframeId])

  const syncPlayback = useCallback((shouldPlay: boolean) => {
    if (isMP4) {
      const vid = videoRef.current
      if (!vid) return
      if (shouldPlay) {
        if (videoReadyRef.current) {
          vid.play().catch(() => {})
        }
      } else {
        vid.pause()
      }
      return
    }
    if (!playerReadyRef.current) return
    postPlayerMessage(shouldPlay ? 'playVideo' : 'pauseVideo')
  }, [isMP4, postPlayerMessage])

  const syncMute = useCallback(() => {
    if (isMP4) {
      const vid = videoRef.current
      if (vid) vid.muted = globalMuted
      return
    }
    if (!playerReadyRef.current) return
    postPlayerMessage(globalMuted ? 'mute' : 'unMute')
  }, [isMP4, postPlayerMessage])

  const toggleMute = useCallback(() => {
    globalMuted = !globalMuted
    emitMuteChange()
    if (isMP4) {
      const vid = videoRef.current
      if (vid) vid.muted = globalMuted
    } else {
      postPlayerMessage(globalMuted ? 'mute' : 'unMute')
    }
  }, [isMP4, postPlayerMessage])

  useEffect(() => {
    activeStateRef.current = isActive
    if (!shouldRender) return
    syncPlayback(isActive)
    if (isActive) {
      syncMute()
    }
  }, [isActive, shouldRender, syncPlayback, syncMute])

  useEffect(() => {
    if (!isMP4 || !item.video?.url) {
      setMp4Source('')
      return
    }
    let cancelled = false
    const cached = getPrefetchedVideoUrl(item.video.url)
    if (cached) {
      setMp4Source(cached)
    } else {
      setMp4Source(item.video.url)
      prefetchVideoBlob(item.video.url)?.then((objectUrl) => {
        if (!cancelled && objectUrl) {
          setMp4Source(objectUrl)
        }
      })
    }
    return () => {
      cancelled = true
    }
  }, [isMP4, item.video?.url])

  useEffect(() => {
    if (!isMP4) return
    videoReadyRef.current = false
  }, [isMP4, mp4Source])

  const handleVideoReady = useCallback(() => {
    if (!isMP4) return
    videoReadyRef.current = true
    if (activeStateRef.current) {
      videoRef.current?.play().catch(() => {})
    }
  }, [isMP4])

  useEffect(() => {
    const handleMuteChange = (value: boolean) => {
      setIsMuted((prev) => (prev === value ? prev : value))
    }
    return subscribeToMute(handleMuteChange)
  }, [])

  // YouTube message listener (only for YouTube videos)
  useEffect(() => {
    if (isMP4 || typeof window === 'undefined') return

    playerReadyRef.current = false

    const handleMessage = (event: MessageEvent) => {
      if (!ALLOWED_ORIGINS.has(event.origin)) {
        return
      }
      let data: { event?: string; id?: string; info?: { playerState?: number } } | null = null
      try {
        data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data
      } catch {
        return
      }
      if (data?.event === 'onReady' && data?.id === iframeId) {
        playerReadyRef.current = true
        syncPlayback(activeStateRef.current)
        if (!globalMuted) {
          postPlayerMessage('unMute')
        }
      }
      // When video ends (state 0), restart to prevent end-screen recommendations
      if (data?.event === 'onStateChange' && data?.id === iframeId && data?.info?.playerState === 0) {
        postPlayerMessage('seekTo', [0, true])
        postPlayerMessage('playVideo')
      }
    }

    window.addEventListener('message', handleMessage)
    return () => {
      window.removeEventListener('message', handleMessage)
      listeningTimersRef.current.forEach(clearTimeout)
      listeningTimersRef.current = []
      playerReadyRef.current = false
    }
  }, [isMP4, iframeId, syncPlayback, postPlayerMessage])

  const handleIframeLoad = useCallback(() => {
    const iframe = iframeRef.current
    if (!iframe) return

    // Clear any previous retry timers
    listeningTimersRef.current.forEach(clearTimeout)
    listeningTimersRef.current = []

    const sendListening = () => {
      iframe.contentWindow?.postMessage(JSON.stringify({
        event: 'listening',
        id: iframeId,
      }), YT_BASE_ORIGIN)
    }

    // Send immediately, then retry — YouTube's player script needs time to initialize
    sendListening()
    listeningTimersRef.current.push(
      setTimeout(sendListening, 250),
      setTimeout(sendListening, 750),
      setTimeout(sendListening, 2000),
    )
  }, [iframeId])

  if (!shouldRender) {
    return (
      <div className="short-card">
        <div className="video-container" style={{ width: '100%', height: '100%', background: '#000' }} />
      </div>
    )
  }

  return (
    <div className="short-card">
      <div className="video-container">
        {isMP4 && item.video?.type === 'mp4' ? (
          <video
            ref={videoRef}
            key={mp4Source || item.video.url}
            src={mp4Source || item.video.url}
            preload="auto"
            autoPlay
            loop
            muted
            playsInline
            disablePictureInPicture
            controlsList="nodownload nofullscreen noplaybackrate"
            onLoadedData={handleVideoReady}
            onCanPlay={handleVideoReady}
            onCanPlayThrough={handleVideoReady}
            className="video-native"
          />
        ) : (
          <iframe
            ref={iframeRef}
            id={iframeId}
            src={iframeSrc}
            title={item.youtube.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="video-iframe"
            style={{ pointerEvents: 'auto' }}
            onLoad={handleIframeLoad}
          />
        )}
      </div>

      <button
        onClick={toggleMute}
        style={{
          position: 'absolute',
          bottom: 80,
          right: 12,
          zIndex: 15,
          width: 36,
          height: 36,
          borderRadius: '50%',
          border: 'none',
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          pointerEvents: 'auto',
          padding: 0,
        }}
        aria-label={isMuted ? 'Unmute' : 'Mute'}
      >
        {isMuted ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <line x1="23" y1="9" x2="17" y2="15" />
            <line x1="17" y1="9" x2="23" y2="15" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
          </svg>
        )}
      </button>

    </div>
  )
}

export default memo(ShortCard, (prevProps, nextProps) => {
  return (
    prevProps.item.id === nextProps.item.id &&
    prevProps.isActive === nextProps.isActive &&
    prevProps.shouldRender === nextProps.shouldRender
  )
})
