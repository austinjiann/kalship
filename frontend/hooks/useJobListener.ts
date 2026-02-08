import { useEffect, useRef } from 'react'

export interface BackendJobStatus {
  status: 'waiting' | 'done' | 'error'
  video_url?: string | null
  video_url_720?: string | null
  error?: string | null
  original_bet_link?: string | null
}

interface UseJobListenerOptions {
  apiUrl: string
  jobId: string | null
  pollMs?: number
  onStatus: (status: BackendJobStatus) => void
}

export function useJobListener({
  apiUrl,
  jobId,
  pollMs = 5000,
  onStatus,
}: UseJobListenerOptions) {
  const stoppedRef = useRef(false)

  useEffect(() => {
    stoppedRef.current = false
    if (!jobId) return

    const baseUrl = apiUrl.replace(/\/$/, '')
    const interval = setInterval(async () => {
      if (stoppedRef.current) return

      try {
        const response = await fetch(`${baseUrl}/jobs/status/${jobId}`)
        if (!response.ok) return
        const status = (await response.json()) as BackendJobStatus
        onStatus(status)
        if (status.status === 'done' || status.status === 'error') {
          stoppedRef.current = true
          clearInterval(interval)
        }
      } catch {
        // Ignore transient polling failures.
      }
    }, pollMs)

    return () => {
      stoppedRef.current = true
      clearInterval(interval)
    }
  }, [apiUrl, jobId, onStatus, pollMs])
}
