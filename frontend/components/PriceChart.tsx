'use client'

import { useEffect, useRef } from 'react'
import { createChart, type IChartApi, type ISeriesApi, ColorType } from 'lightweight-charts'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const KALSHI_GREEN = '#00d084'
const KALSHI_AREA_TOP = 'rgba(0, 208, 132, 0.15)'
const KALSHI_AREA_BOTTOM = 'rgba(0, 208, 132, 0)'

interface PriceChartProps {
  ticker: string
  seriesTicker: string
  priceHistory?: { ts: number; price: number }[]
}

function PriceChartInner({ ticker, seriesTicker, priceHistory }: PriceChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Area'> | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 200,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: 'rgba(255, 255, 255, 0.35)',
        fontSize: 11,
        attributionLogo: false,
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { color: 'rgba(255, 255, 255, 0.08)', style: 1 },
      },
      rightPriceScale: {
        borderVisible: false,
        autoScale: false,
        scaleMargins: { top: 0.02, bottom: 0.02 },
      },
      timeScale: {
        borderVisible: false,
        timeVisible: true,
        secondsVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
      crosshair: {
        horzLine: {
          visible: true,
          labelVisible: true,
          style: 3, // dashed
          color: 'rgba(255, 255, 255, 0.3)',
        },
        vertLine: {
          visible: true,
          labelVisible: true,
          style: 3,
          color: 'rgba(255, 255, 255, 0.3)',
        },
      },
      handleScroll: false,
      handleScale: false,
      localization: {
        priceFormatter: (price: number) => `${Math.round(price)}¢`,
      },
    })

    chartRef.current = chart

    const series = chart.addAreaSeries({
      lineColor: KALSHI_GREEN,
      topColor: KALSHI_AREA_TOP,
      bottomColor: KALSHI_AREA_BOTTOM,
      lineWidth: 2,
      crosshairMarkerVisible: true,
      priceLineVisible: true,
      lastValueVisible: true,
      autoscaleInfoProvider: () => ({
        priceRange: { minValue: 0, maxValue: 100 },
      }),
    })

    seriesRef.current = series

    // Set initial data from feed response (60-min candles)
    if (priceHistory && priceHistory.length > 0) {
      const data = priceHistory.map((p) => ({
        time: p.ts as import('lightweight-charts').UTCTimestamp,
        value: p.price,
      }))
      series.setData(data)
      chart.timeScale().fitContent()
    }

    // Fetch 60-min candles over 24h then poll
    let intervalId: ReturnType<typeof setInterval> | null = null

    const fetchCandles = async () => {
      try {
        const params = new URLSearchParams({
          ticker,
          series_ticker: seriesTicker,
          period: '60',
          hours: '24',
        })
        const res = await fetch(`${API_URL}/shorts/candlesticks?${params}`)
        if (!res.ok) return
        const json = await res.json()
        const candles: { ts: number; price: number }[] = json.candlesticks ?? []
        if (candles.length > 0) {
          const data = candles.map((c) => ({
            time: c.ts as import('lightweight-charts').UTCTimestamp,
            value: c.price,
          }))
          series.setData(data)
          chart.timeScale().fitContent()
        }
      } catch {
        // Silently fail — chart keeps showing last known data
      }
    }

    fetchCandles()
    intervalId = setInterval(fetchCandles, 30_000)

    // Handle resize
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        chart.applyOptions({ width: entry.contentRect.width })
      }
    })
    ro.observe(containerRef.current)

    return () => {
      if (intervalId) clearInterval(intervalId)
      ro.disconnect()
      chart.remove()
      chartRef.current = null
      seriesRef.current = null
    }
  }, [ticker, seriesTicker]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div
      ref={containerRef}
      className="w-full price-chart-container"
      style={{ height: 200 }}
    />
  )
}

export default PriceChartInner
