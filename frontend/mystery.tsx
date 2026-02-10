export enum VideoTopic {
  SUPERBOWL = 'SUPERBOWL',
  WEATHER_SNOW = 'WEATHER_SNOW',
  MARS_SPACE = 'MARS_SPACE',
  GENERAL = 'GENERAL',
}

export type VideoSource =
  | { type: 'youtube'; videoId: string }
  | { type: 'mp4'; url: string }

export interface VideoEntry {
  source: VideoSource
  topic: VideoTopic
  label?: string
}

export const AI_REEL_VIDEOS: VideoEntry[] = [
  {
    source: { type: 'mp4', url: 'https://storage.googleapis.com/qhacks-486618-storage/videos/13118567516871963719/la.mp4' },
    topic: VideoTopic.WEATHER_SNOW,
    label: 'good los angeles snow',
  },
  {
    source: { type: 'mp4', url: 'https://storage.googleapis.com/qhacks-486618-storage/videos/13118567516871963719/la.mp4' },
    topic: VideoTopic.WEATHER_SNOW,
    label: 'decent los angeles snow',
  },
  {
    source: { type: 'mp4', url: 'https://storage.googleapis.com/qhacks-486618-storage/videos/13118567516871963719/superbowl.mp4' },
    topic: VideoTopic.SUPERBOWL,
    label: 'good superbowl',
  },
  {
    source: { type: 'mp4', url: 'https://storage.googleapis.com/qhacks-486618-storage/videos/13118567516871963719/superbowl.mp4' },
    topic: VideoTopic.SUPERBOWL,
    label: 'good superbowl but has weird text',
  },
  {
    source: { type: 'mp4', url: 'https://storage.googleapis.com/qhacks-486618-storage/videos/13118567516871963719/mars.mp4' },
    topic: VideoTopic.MARS_SPACE,
    label: 'cars mars',
  },
]

export const VISUALIZATION_VIDEOS: VideoEntry[] = [
  ...AI_REEL_VIDEOS,
]

const TOPIC_KEYWORDS: Record<VideoTopic, string[]> = {
  [VideoTopic.SUPERBOWL]: ['superbowl', 'super bowl', 'nfl', 'football', 'chiefs', 'eagles', 'halftime'],
  [VideoTopic.WEATHER_SNOW]: ['snow', 'weather', 'los angeles', 'la snow', 'blizzard', 'winter', 'storm', 'cold'],
  [VideoTopic.MARS_SPACE]: ['mars', 'space', 'nasa', 'spacex', 'rocket', 'planet', 'astronaut'],
  [VideoTopic.GENERAL]: [],
}

const SERIES_TO_TOPIC: Record<string, VideoTopic> = {
  'KXSB': VideoTopic.SUPERBOWL,
  'KXNBAGAME': VideoTopic.SUPERBOWL,
  'KXMLBGAME': VideoTopic.SUPERBOWL,
  'KXNHLGAME': VideoTopic.SUPERBOWL,
  'KXWCGAME': VideoTopic.SUPERBOWL,
}

export function findVisualizationBySeriesTicker(seriesTicker?: string, question?: string): VideoEntry | null {
  const topic = seriesTicker ? SERIES_TO_TOPIC[seriesTicker] : undefined
  if (topic) {
    const pool = VISUALIZATION_VIDEOS.filter(v => v.topic === topic)
    if (pool.length > 0) return pool[Math.floor(Math.random() * pool.length)]
  }
  // Fallback: keyword match from market question
  if (question) {
    const keywords = question.split(/\s+/)
    const match = findVisualizationVideo(keywords)
    if (match) return match
  }
  // Last resort: random from entire pool
  if (VISUALIZATION_VIDEOS.length === 0) return null
  return VISUALIZATION_VIDEOS[Math.floor(Math.random() * VISUALIZATION_VIDEOS.length)]
}

export function findVisualizationVideo(keywords: string[]): VideoEntry | null {
  const lowerKeywords = keywords.map(k => k.toLowerCase())

  let bestTopic: VideoTopic | null = null
  let bestScore = 0

  for (const [topic, topicKeywords] of Object.entries(TOPIC_KEYWORDS)) {
    if (topic === VideoTopic.GENERAL) continue
    let score = 0
    for (const kw of lowerKeywords) {
      for (const tk of topicKeywords) {
        if (kw.includes(tk) || tk.includes(kw)) {
          score++
        }
      }
    }
    if (score > bestScore) {
      bestScore = score
      bestTopic = topic as VideoTopic
    }
  }

  const pool = bestTopic
    ? VISUALIZATION_VIDEOS.filter(v => v.topic === bestTopic)
    : VISUALIZATION_VIDEOS

  if (pool.length === 0) return null
  return pool[Math.floor(Math.random() * pool.length)]
}

