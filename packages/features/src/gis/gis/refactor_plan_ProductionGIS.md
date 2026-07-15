# Refactor Plan: ProductionGIS.tsx

## خلاصه
- خطوط فعلی: 1090
- States: 19
- Effects: 2
- Handlers: 5
- Business Logic: 3
- API Calls: 1

## States برای انتقال به useProductionGIS.ts

- خط 176: `isClient, setIsClient`
- خط 177: `baseLayer, setBaseLayer`
- خط 178: `overlays, setOverlays`
- خط 179: `showHeatmap, setShowHeatmap`
- خط 180: `showLayerPanel, setShowLayerPanel`
- خط 181: `showSavedPanel, setShowSavedPanel`
- خط 183: `measureMode, setMeasureMode`
- خط 184: `measurePoints, setMeasurePoints`
- خط 185: `measureResult, setMeasureResult`
- خط 187: `mousePosition, setMousePosition`
- خط 188: `savedLocations, setSavedLocations`
- خط 189: `showSaveDialog, setShowSaveDialog`
- خط 190: `pendingSavePoint, setPendingSavePoint`
- خط 191: `saveForm, setSaveForm`
- خط 199: `searchQuery, setSearchQuery`
- خط 200: `isSearching, setIsSearching`
- خط 201: `searchResults, setSearchResults`
- خط 203: `mapCenter, setMapCenter`
- خط 204: `zoom, setZoom`

## Handlers برای انتقال به useProductionGISHandlers.ts

- خط 287: `handleMapClick`
- خط 312: `handleMouseMove`
- خط 364: `handleSaveLocation`
- خط 387: `handleDeleteLocation`
- خط 401: `handleSearch`

## Logic برای انتقال به utils/productionGIS.ts

- خط 226: `calculateDistance`
- خط 246: `calculateArea`
- خط 267: `calculateRadius`
