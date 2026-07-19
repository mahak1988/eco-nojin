import { useEffect, useRef, useCallback } from "react"
import type { Map as LeafletMap } from "leaflet"

/**
 * رفع دائمی رندرینگ Tileهای Leaflet در لایه‌های React
 */
export function useMapFix() {
  const mapRef = useRef<LeafletMap | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const observerRef = useRef<ResizeObserver | null>(null)

  const invalidate = useCallback(() => {
    if (mapRef.current) {
      mapRef.current.invalidateSize({ animate: false, pan: false })
    }
  }, [])

  const onMapReady = useCallback((map: LeafletMap) => {
    mapRef.current = map
    // افزایش تدریجی برای شناسایی layout
    invalidate()
    setTimeout(invalidate, 50)
    setTimeout(invalidate, 150)
    setTimeout(invalidate, 400)
  }, [invalidate])

  const setContainerRef = useCallback((node: HTMLDivElement | null) => {
    if (observerRef.current) {
      observerRef.current.disconnect()
      observerRef.current = null
    }

    containerRef.current = node

    if (node) {
      observerRef.current = new ResizeObserver(() => {
        invalidate()
      })
      observerRef.current.observe(node)
    }
  }, [invalidate])

  useEffect(() => {
    window.addEventListener("resize", invalidate)
    return () => window.removeEventListener("resize", invalidate)
  }, [invalidate])

  useEffect(() => {
    return () => {
      observerRef.current?.disconnect()
    }
  }, [])

  return { setContainerRef, onMapReady, invalidate }
}