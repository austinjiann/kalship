const blobCache = new Map<string, string>()
const cacheOrder: string[] = []
const inflightFetches = new Map<string, Promise<string | null>>()
const MAX_CACHE_ENTRIES = 8

function evictIfNeeded() {
  while (cacheOrder.length > MAX_CACHE_ENTRIES) {
    const url = cacheOrder.shift()
    if (!url) break
    const objectUrl = blobCache.get(url)
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl)
      blobCache.delete(url)
    }
  }
}

export function getPrefetchedVideoUrl(url?: string): string | undefined {
  if (!url) return undefined
  return blobCache.get(url)
}

export function prefetchVideoBlob(url?: string) {
  if (!url || typeof window === 'undefined' || blobCache.has(url)) {
    return inflightFetches.get(url ?? '')
  }
  if (inflightFetches.has(url)) {
    return inflightFetches.get(url)
  }

  const promise = fetch(url, { mode: 'cors', cache: 'force-cache' })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Prefetch failed: ${response.status}`)
      }
      const blob = await response.blob()
      const objectUrl = URL.createObjectURL(blob)
      blobCache.set(url, objectUrl)
      cacheOrder.push(url)
      evictIfNeeded()
      return objectUrl
    })
    .catch((error) => {
      console.warn('[video-cache] Failed to prefetch', url, error)
      return null
    })
    .finally(() => {
      inflightFetches.delete(url)
    })

  inflightFetches.set(url, promise)
  return promise
}
