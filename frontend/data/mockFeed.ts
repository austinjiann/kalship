import { FeedItem } from '@/types'

export const mockFeedItems: FeedItem[] = [
  {
    id: '1',
    kalshi: {
      ticker: 'KXBTC-150K-JUN',
      question: 'Bitcoin Price',
      outcome: 'Will Bitcoin hit $150,000 by June 2025?',
      yes_price: 45,
      no_price: 55,
    },
    youtube: {
      video_id: 'vHaPgrSMlI0',
      title: 'Bitcoin price prediction',
      thumbnail: 'https://img.youtube.com/vi/vHaPgrSMlI0/maxresdefault.jpg',
      channel: 'CryptoNews'
    }
  },
  {
    id: '2',
    kalshi: {
      ticker: 'KXNFL-EAGLES-SB',
      question: 'NFL Super Bowl',
      outcome: 'Will the Eagles repeat as Super Bowl champs?',
      yes_price: 28,
      no_price: 72,
    },
    youtube: {
      video_id: 'HZOkwNsYFdo',
      title: 'Eagles Super Bowl highlights',
      thumbnail: 'https://img.youtube.com/vi/HZOkwNsYFdo/maxresdefault.jpg',
      channel: 'NFL'
    }
  },
  {
    id: '3',
    kalshi: {
      ticker: 'KXAI-GPT5-Q2',
      question: 'AI Release',
      outcome: 'Will GPT-5 be released by Q2 2025?',
      yes_price: 62,
      no_price: 38,
    },
    youtube: {
      video_id: 'w1rbnM6A4AA',
      title: 'AI news update',
      thumbnail: 'https://img.youtube.com/vi/w1rbnM6A4AA/maxresdefault.jpg',
      channel: 'TechNews'
    }
  },
  {
    id: '4',
    kalshi: {
      ticker: 'KXSPACE-STARSHIP',
      question: 'SpaceX Mars',
      outcome: 'Will Starship complete a Mars mission by 2026?',
      yes_price: 15,
      no_price: 85,
    },
    youtube: {
      video_id: '_qW6a1A9gb0',
      title: 'SpaceX Starship launch',
      thumbnail: 'https://img.youtube.com/vi/_qW6a1A9gb0/maxresdefault.jpg',
      channel: 'SpaceX'
    }
  },
  {
    id: '5',
    kalshi: {
      ticker: 'KXCLIMATE-2025',
      question: 'Climate',
      outcome: 'Will 2025 be the hottest year on record?',
      yes_price: 78,
      no_price: 22,
    },
    youtube: {
      video_id: '3fQhDJlRJYg',
      title: 'Climate change explained',
      thumbnail: 'https://img.youtube.com/vi/3fQhDJlRJYg/maxresdefault.jpg',
      channel: 'ScienceNews'
    }
  },
  {
    id: '6',
    kalshi: {
      ticker: 'KXNFL-CHIEFS-PO',
      question: 'NFL Playoffs',
      outcome: 'Will the Chiefs make the playoffs in 2025?',
      yes_price: 82,
      no_price: 18,
    },
    youtube: {
      video_id: 'LQ8uCvKYu3Y',
      title: 'Chiefs season highlights',
      thumbnail: 'https://img.youtube.com/vi/LQ8uCvKYu3Y/maxresdefault.jpg',
      channel: 'NFL'
    }
  }
]
