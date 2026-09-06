import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './MapView.css'

const locations: Record<string, { center: [number, number]; zoom: number; color: string }> = {
  Kamrup: { center: [26.1445, 91.7362], zoom: 10, color: '#ef805a' },
  'Kamrup Metropolitan': { center: [26.1445, 91.7362], zoom: 11, color: '#7b65b1' },
  Dibrugarh: { center: [27.4728, 94.912], zoom: 10, color: '#3c8c87' },
}

type MapViewProps = { district: string; showBoundary: boolean; showWater: boolean; showVegetation: boolean; showRainfall: boolean }

export default function MapView({ district, showBoundary, showWater, showVegetation, showRainfall }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const leafletMapRef = useRef<L.Map | null>(null)
  const layersRef = useRef<Record<string, L.Layer>>({})

  useEffect(() => {
    if (!mapRef.current) return
    const location = locations[district] ?? locations.Kamrup
    const map = L.map(mapRef.current, { zoomControl: false }).setView(location.center, location.zoom)
    leafletMapRef.current = map
    L.control.zoom({ position: 'topright' }).addTo(map)

    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18, attribution: 'Esri World Imagery' }).addTo(map)
    const labels = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { opacity: 0.28, attribution: '&copy; OpenStreetMap' }).addTo(map)
    const boundary = L.polygon([
      [location.center[0] + 0.24, location.center[1] - 0.24], [location.center[0] + 0.16, location.center[1] + 0.28],
      [location.center[0] - 0.18, location.center[1] + 0.22], [location.center[0] - 0.23, location.center[1] - 0.2],
    ], { color: location.color, weight: 3, fillColor: location.color, fillOpacity: 0.12 }).addTo(map)
    boundary.bindTooltip(district.toUpperCase(), { permanent: true, direction: 'center', className: 'district-tooltip' })

    const water = L.circle([location.center[0] - 0.02, location.center[1] + 0.04], { radius: 5200, color: '#55d0d1', fillColor: '#45b8c1', fillOpacity: 0.36, weight: 1 })
    const vegetation = L.circle([location.center[0] + 0.08, location.center[1] - 0.08], { radius: 10500, color: '#91cb78', fillColor: '#73b167', fillOpacity: 0.2, weight: 1 })
    const rainfall = L.circleMarker([location.center[0] + 0.03, location.center[1] - 0.02], { radius: 30, color: '#f2c461', fillColor: '#f2c461', fillOpacity: 0.24, className: 'rain-pulse' })
    layersRef.current = { satellite, labels, boundary, water, vegetation, rainfall }

    return () => { map.remove() }
  }, [district])

  useEffect(() => {
    const layers = layersRef.current
    if (!layers.water) return
    const mapInstance = leafletMapRef.current
    if (!mapInstance) return
    ;[['water', showWater], ['vegetation', showVegetation], ['rainfall', showRainfall]].forEach(([key, visible]) => {
      const layer = layers[key as string]
      if (visible && !mapInstance.hasLayer(layer)) layer.addTo(mapInstance)
      if (!visible && mapInstance.hasLayer(layer)) mapInstance.removeLayer(layer)
    })
    if (showBoundary && !mapInstance.hasLayer(layers.boundary)) layers.boundary.addTo(mapInstance)
    if (!showBoundary && mapInstance.hasLayer(layers.boundary)) mapInstance.removeLayer(layers.boundary)
  }, [showBoundary, showWater, showVegetation, showRainfall, district])

  return <div className="real-map" ref={mapRef} />
}