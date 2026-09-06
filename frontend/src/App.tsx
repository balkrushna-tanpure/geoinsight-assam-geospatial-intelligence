import { useEffect, useState } from 'react'
import './App.css'
import MapView from './MapView'
import { GradientBackground } from './components/ui/jade-sky'
import KineticGrid from './components/ui/kinetic-grid'
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001'

type LayerKey = 'boundary' | 'vegetation' | 'water' | 'rainfall'

const metrics = [
  { label: 'Average NDVI', value: '0.58', note: 'Healthy canopy signal', tone: 'green', icon: 'ND' },
  { label: 'Monthly rainfall', value: '421 mm', note: 'CHIRPS district average', tone: 'blue', icon: 'RN' },
  { label: 'Surface water', value: '4.7%', note: 'Of total district area', tone: 'aqua', icon: 'SW' },
  { label: 'Water area', value: '37.2 km2', note: 'Masked surface-water pixels', tone: 'gold', icon: 'AR' },
]

const districtsByState: Record<string, string[]> = {
  Assam: ['Kamrup', 'Kamrup Metropolitan', 'Dibrugarh'],
}

function App() {
  const [activeLayers, setActiveLayers] = useState<Record<LayerKey, boolean>>({ boundary: true, vegetation: true, water: true, rainfall: false })
  const [state, setState] = useState('Assam')
  const [district, setDistrict] = useState('Kamrup')
  const [month, setMonth] = useState('June 2026')
  const [metricValues, setMetricValues] = useState(metrics)
  const [rainfallHistory, setRainfallHistory] = useState<{ month: string; rainfall_mm: number }[]>([])
  const [liveWeather, setLiveWeather] = useState<{ temperature_2m?: number; relative_humidity_2m?: number; precipitation?: number; wind_speed_10m?: number } | null>(null)
  const [risks, setRisks] = useState({ flood_risk: 'low', drought_risk: 'low', crop_stress: 'low' })
  const [isLoading, setIsLoading] = useState(false)
  const [dataError, setDataError] = useState('')
  const [showProcessingDetails, setShowProcessingDetails] = useState(false)

  useEffect(() => {
    const [monthName, year] = month.split(' ')
    const monthNumber = { January: '01', February: '02', March: '03', April: '04', May: '05', June: '06', July: '07', August: '08', September: '09', October: '10', November: '11', December: '12' }[monthName]
    const monthValue = `${year}-${monthNumber}`
    setIsLoading(true)
    setDataError('')
    const predictionRequest = fetch(`${API_BASE}/api/v1/prediction?district=${encodeURIComponent(district)}&month=${monthValue}`).then((response) => {
      if (!response.ok) throw new Error('Prediction API unavailable')
      return response.json()
    })
    const liveRequest = fetch(`${API_BASE}/api/v1/live?district=${encodeURIComponent(district)}`).then((response) => response.ok ? response.json() : null).catch(() => null)
    predictionRequest.then((result) => {
        if (!result.prediction) throw new Error('Prediction data is empty')
        setMetricValues([
          { ...metrics[0], value: String(result.prediction.ndvi) },
          { ...metrics[1], value: `${result.prediction.rainfall_mm} mm` },
          { ...metrics[2], value: `${result.prediction.water_percent}%` },
          { ...metrics[3], value: `${result.prediction.water_area_km2} km2` },
        ])
        setRainfallHistory(result.rainfall_history ?? [])
        setRisks(result.risks ?? risks)
      })
      .catch((error: Error) => { setDataError(error.message); setRainfallHistory([]) })
    liveRequest.then((liveResult) => setLiveWeather(liveResult?.current ?? null))
      .finally(() => setIsLoading(false))
  }, [district, month])

  const toggleLayer = (layer: LayerKey) => {
    setActiveLayers((current) => ({ ...current, [layer]: !current[layer] }))
  }

  return (
    <main className={`app-shell district-${district.toLowerCase().replaceAll(' ', '-')}`}>
      <GradientBackground className="background-layer" />
      <KineticGrid className="kinetic-grid-layer" />
      <div className="content-layer">
      <header className="topbar"><a className="brand" href="/" aria-label="GeoInsight home"><span className="brand-mark">G</span><span><strong>GEO</strong>INSIGHT</span></a><div className="topbar-meta"><span className="status-dot" /> Live data workspace <span className="divider" /> API v1.0</div><button className="icon-button" type="button" aria-label="Open settings">•••</button></header>
      <section className="intro-row"><div><p className="eyebrow">DISTRICT INTELLIGENCE / {state.toUpperCase()}</p><h1>{district} <span>in focus.</span></h1><p className="lede">A clear read on land, rain, and water from public Earth observation data.</p></div><div className="controls" aria-label="Report controls"><label>State <select value={state} onChange={(event) => { setState(event.target.value); setDistrict(districtsByState[event.target.value][0]) }}><option>Assam</option></select></label><label>District <select value={district} onChange={(event) => setDistrict(event.target.value)}>{districtsByState[state].map((option) => <option key={option}>{option}</option>)}</select></label><label>Observation month <select value={month} onChange={(event) => setMonth(event.target.value)}><option>April 2025</option><option>May 2025</option><option>June 2025</option><option>April 2026</option><option>May 2026</option><option>June 2026</option><option>July 2026</option></select></label><button className="refresh-button" type="button"><span>↻</span> {isLoading ? 'Loading...' : 'Refresh report'}</button></div></section>
      {dataError && <div className="data-error">{dataError}. Start the backend with <strong>run.bat</strong>, then refresh.</div>}
      <section className="metrics-grid" aria-label="Environmental indicators">{metricValues.map((metric) => <article className="metric-card" key={metric.label}><div className={`metric-icon ${metric.tone}`}>{metric.icon}</div><p>{metric.label}</p><strong>{metric.value}</strong><small><span className="trend">PREDICTED</span> {metric.note}</small></article>)}<article className="metric-card live-card"><div className="metric-icon live">NOW</div><p>Live temperature</p><strong>{liveWeather?.temperature_2m ?? '--'}°C</strong><small><span className="trend">LIVE</span> Humidity {liveWeather?.relative_humidity_2m ?? '--'}% / Wind {liveWeather?.wind_speed_10m ?? '--'} km/h</small></article></section>
      <section className="workspace-grid"><article className="map-panel"><div className="panel-heading"><div><p className="eyebrow">SATELLITE SPATIAL VIEW</p><h2>{district} environmental layers</h2></div><span className="map-date">{month} <span className="live-pill">LIVE MAP</span></span></div><div className="map-frame"><MapView district={district} showBoundary={activeLayers.boundary} showWater={activeLayers.water} showVegetation={activeLayers.vegetation} showRainfall={activeLayers.rainfall} /></div><div className="layer-bar"><p>Layers</p>{(['boundary', 'vegetation', 'water', 'rainfall'] as LayerKey[]).map((layer) => <button className={activeLayers[layer] ? 'layer active' : 'layer'} onClick={() => toggleLayer(layer)} type="button" key={layer}><i className={layer} /> {layer === 'boundary' ? 'District boundary' : layer === 'vegetation' ? 'NDVI vegetation' : layer === 'water' ? 'Surface water' : 'Rainfall pulse'}<b>{activeLayers[layer] ? '✓' : ''}</b></button>)}</div></article><aside className="insight-panel"><div className="panel-heading"><div><p className="eyebrow">FIELD NOTE</p><h2>What the data says</h2></div><span className="spark">↗</span></div><p className="insight-copy">{district} shows <em>moderate-to-healthy</em> vegetation health in {month.toLowerCase()}, supported by a strong rainfall signal. Surface water is present across <strong>{metricValues[2].value}</strong> of the district.</p><div className="signal"><span className="signal-icon">i</span><div><strong>{isLoading ? 'Updating prediction' : 'Prediction ready'}</strong><p>Forecast and layers update with your selected district.</p></div></div><div className="source-list"><p className="eyebrow">DATA SOURCES</p><div><span className="source-dot sentinel" /> Sentinel-2 / Copernicus <b>NDVI</b></div><div><span className="source-dot chirps" /> CHIRPS / UCSB <b>Rainfall</b></div><div><span className="source-dot jrc" /> JRC Global Surface Water <b>Water</b></div></div><button className="outline-button" type="button" aria-expanded={showProcessingDetails} onClick={() => setShowProcessingDetails((visible) => !visible)}>View processing details <span>{showProcessingDetails ? '↑' : '→'}</span></button>{showProcessingDetails && <div className="processing-details"><div><span>BOUNDARY</span><strong>{district}, Assam</strong></div><div><span>OBSERVATION</span><strong>{month}</strong></div><div><span>PROCESS</span><strong>Clip → calculate → predict</strong></div><div><span>MODEL</span><strong>Random Forest baseline</strong></div><div><span>HISTORY</span><strong>{rainfallHistory.length} monthly records</strong></div><div><span>STATUS</span><strong>{dataError ? 'Needs backend' : 'Ready'}</strong></div></div>}</aside></section>
      <section className="history-panel"><div className="panel-heading"><div><p className="eyebrow">HISTORICAL RECORDS</p><h2>{district} monthly rainfall</h2></div><span className="live-pill">{rainfallHistory.length} MONTHS</span></div><div className="rainfall-chart">{rainfallHistory.slice(-12).map((record) => <div className="rainfall-column" key={record.month} title={`${record.month}: ${record.rainfall_mm} mm`}><span style={{ height: `${Math.max(8, Math.min(100, record.rainfall_mm / 5))}%` }} /><small>{record.month.slice(5)}</small></div>)}</div><div className="history-table">{rainfallHistory.slice(-6).reverse().map((record) => <span key={record.month}><b>{record.month}</b><strong>{record.rainfall_mm} mm</strong></span>)}</div></section>
      <section className="risk-panel"><div><p className="eyebrow">FIELD AND DISASTER OUTLOOK</p><h2>What needs attention next</h2></div><div className="risk-grid"><div className={`risk-item ${risks.flood_risk}`}><span>FLOOD</span><strong>{risks.flood_risk}</strong><small>Rainfall threshold</small></div><div className={`risk-item ${risks.drought_risk}`}><span>DROUGHT</span><strong>{risks.drought_risk}</strong><small>Rainfall deficit</small></div><div className={`risk-item ${risks.crop_stress}`}><span>CROP STRESS</span><strong>{risks.crop_stress}</strong><small>NDVI signal</small></div></div></section>
      <section className="pipeline"><div><p className="eyebrow">PROCESSING PIPELINE</p><h2>From satellite pixels to a decision-ready signal.</h2></div><div className="pipeline-steps"><span className="complete">01 <b>Boundary</b></span><i>→</i><span className="complete">02 <b>Sentinel-2</b></span><i>→</i><span className="complete">03 <b>CHIRPS</b></span><i>→</i><span className="complete">04 <b>JRC water</b></span><i>→</i><span>05 <b>API response</b></span></div></section>
      <footer><span>GEOINSIGHT / KAMRUP, ASSAM</span><span>PUBLIC DATA, MADE USEFUL <i>•</i> {month.toUpperCase()}</span></footer>
      </div>
    </main>
  )
}

export default App
