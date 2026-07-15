import { useState, useEffect } from 'react'

interface ProductionGISState {
  isClient: any
  baseLayer: any
  overlays: any
  showHeatmap: any
  showLayerPanel: any
  showSavedPanel: any
  measureMode: any
  measurePoints: any
  measureResult: any
  mousePosition: any
  savedLocations: any
  showSaveDialog: any
  pendingSavePoint: any
  saveForm: any
  searchQuery: any
  isSearching: any
  searchResults: any
  mapCenter: any
  zoom: any
}

export function useProductionGIS() {
  const [isClient, setIsClient] = useState<any>(null)
  const [baseLayer, setBaseLayer] = useState<any>(null)
  const [overlays, setOverlays] = useState<any>(null)
  const [showHeatmap, setShowHeatmap] = useState<any>(null)
  const [showLayerPanel, setShowLayerPanel] = useState<any>(null)
  const [showSavedPanel, setShowSavedPanel] = useState<any>(null)
  const [measureMode, setMeasureMode] = useState<any>(null)
  const [measurePoints, setMeasurePoints] = useState<any>(null)
  const [measureResult, setMeasureResult] = useState<any>(null)
  const [mousePosition, setMousePosition] = useState<any>(null)
  const [savedLocations, setSavedLocations] = useState<any>(null)
  const [showSaveDialog, setShowSaveDialog] = useState<any>(null)
  const [pendingSavePoint, setPendingSavePoint] = useState<any>(null)
  const [saveForm, setSaveForm] = useState<any>(null)
  const [searchQuery, setSearchQuery] = useState<any>(null)
  const [isSearching, setIsSearching] = useState<any>(null)
  const [searchResults, setSearchResults] = useState<any>(null)
  const [mapCenter, setMapCenter] = useState<any>(null)
  const [zoom, setZoom] = useState<any>(null)

  // TODO: منتقل کردن useEffect ها از ProductionGIS

  return {
    isClient,
    setIsClient,
    baseLayer,
    setBaseLayer,
    overlays,
    setOverlays,
    showHeatmap,
    setShowHeatmap,
    showLayerPanel,
    setShowLayerPanel,
    showSavedPanel,
    setShowSavedPanel,
    measureMode,
    setMeasureMode,
    measurePoints,
    setMeasurePoints,
    measureResult,
    setMeasureResult,
    mousePosition,
    setMousePosition,
    savedLocations,
    setSavedLocations,
    showSaveDialog,
    setShowSaveDialog,
    pendingSavePoint,
    setPendingSavePoint,
    saveForm,
    setSaveForm,
    searchQuery,
    setSearchQuery,
    isSearching,
    setIsSearching,
    searchResults,
    setSearchResults,
    mapCenter,
    setMapCenter,
    zoom,
    setZoom,
  }
}
