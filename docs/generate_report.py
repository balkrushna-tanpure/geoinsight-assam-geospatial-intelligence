from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "GeoInsight_Project_Report.pdf"

NAVY = colors.HexColor("#183B3E")
JADE = colors.HexColor("#356F5B")
MINT = colors.HexColor("#E8F5EF")
LIME = colors.HexColor("#B7D98E")
SKY = colors.HexColor("#CFE9F0")
INK = colors.HexColor("#183B3E")
MUTED = colors.HexColor("#52706F")
LINE = colors.HexColor("#A7C9B1")


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle("cover_title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=31, leading=36, textColor=colors.white, alignment=TA_LEFT, spaceAfter=12),
        "cover_subtitle": ParagraphStyle("cover_subtitle", parent=base["Normal"], fontName="Helvetica", fontSize=13, leading=20, textColor=colors.HexColor("#DFF0DC")),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=21, leading=26, textColor=NAVY, spaceBefore=8, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=JADE, spaceBefore=10, spaceAfter=5),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5, leading=15, textColor=INK, spaceAfter=7),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED),
        "table": ParagraphStyle("table", parent=base["BodyText"], fontName="Helvetica", fontSize=8.3, leading=11, textColor=INK),
        "table_header": ParagraphStyle("table_header", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8.3, leading=11, textColor=colors.white),
        "quote": ParagraphStyle("quote", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=13, leading=20, textColor=NAVY, leftIndent=15, rightIndent=15, spaceBefore=10, spaceAfter=10),
        "code": ParagraphStyle("code", parent=base["Code"], fontName="Courier", fontSize=8, leading=11, textColor=INK, backColor=MINT, borderPadding=8),
    }


def P(text, style):
    return Paragraph(text, style)


def table(rows, widths, style_set=None):
    prepared = []
    for row in rows:
        prepared.append([cell if isinstance(cell, Paragraph) else P(str(cell), style_set["table"] if style_set else styles()["table"]) for cell in row])
    result = Table(prepared, colWidths=widths, repeatRows=1)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, MINT]),
    ]))
    return result


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "GEOINSIGHT / KAMRUP, ASSAM")
    canvas.drawRightString(192 * mm, 9 * mm, f"PROJECT REPORT  |  {doc.page}")
    canvas.restoreState()


def build():
    s = styles()
    story = []

    story.extend([
        Spacer(1, 28 * mm),
        P("GEOINSIGHT", s["cover_title"]),
        P("Geospatial intelligence for environmental decisions", s["cover_subtitle"]),
        Spacer(1, 18 * mm),
        HRFlowable(width="100%", thickness=1.2, color=LIME),
        Spacer(1, 10 * mm),
        P("KAMRUP DISTRICT, ASSAM", s["cover_subtitle"]),
        P("Project report and technical documentation", s["cover_subtitle"]),
        Spacer(1, 90 * mm),
        P("A full-stack prototype combining a React dashboard, FastAPI, PostgreSQL/PostGIS-ready storage, public weather data, an ML baseline, and an interactive satellite map.", s["cover_subtitle"]),
        PageBreak(),
    ])

    story.extend([
        P("1. Executive Summary", s["h1"]),
        P("GeoInsight turns difficult geospatial processing into a simple district-level environmental report. A user selects an Assam district and observation month; the application returns vegetation health, rainfall, surface-water coverage, a historical rainfall view, current weather, and baseline risk signals.", s["body"]),
        P("The prototype currently supports Kamrup, Kamrup Metropolitan, and Dibrugarh. The interface is designed for real Sentinel-2, CHIRPS, JRC Global Surface Water, and geoBoundaries data. Its API and database structure are ready for those datasets, while the current metric training records are explicitly labeled as demo data.", s["body"]),
        P("Problem statement", s["h2"]),
        P("Public Earth observation datasets are valuable but difficult for normal applications to consume because they have different formats, resolutions, coordinate systems, and processing requirements. GeoInsight provides one standardized interface for turning those datasets into understandable environmental indicators.", s["quote"]),
        P("2. Goals and Outcomes", s["h1"]),
        table([
            ["Goal", "GeoInsight outcome"],
            ["District selection", "State and district selectors with three Assam districts."],
            ["Vegetation analysis", "NDVI metric and vegetation layer slot in the map workflow."],
            ["Rainfall analysis", "Monthly rainfall prediction, historical rainfall chart, and live weather card."],
            ["Surface-water analysis", "Coverage percentage and calculated water area in square kilometres."],
            ["Disaster and field outlook", "Baseline flood, drought, and crop-stress signals."],
            ["Application integration", "FastAPI REST endpoints consumed by the React dashboard."],
        ], [52 * mm, 122 * mm], s),
        PageBreak(),
    ])

    story.extend([
        P("3. Architecture", s["h1"]),
        P("The system is split into a browser dashboard, an API and processing layer, and a PostgreSQL persistence layer. The map uses Leaflet with Esri World Imagery and OpenStreetMap labels. Current weather is retrieved from Open-Meteo without an API key.", s["body"]),
        P("Request flow", s["h2"]),
        P("User selection -> React dashboard -> FastAPI endpoint -> model/data services -> PostgreSQL records -> JSON response -> cards, charts, risks, and map layers", s["code"]),
        P("Technology stack", s["h2"]),
        table([
            ["Layer", "Technology", "Purpose"],
            ["Frontend", "React + TypeScript + Vite", "Responsive dashboard, selectors, charts, map controls."],
            ["Map", "Leaflet + Esri World Imagery", "Interactive satellite map with district-aware center and overlays."],
            ["Backend", "Python + FastAPI", "REST API, validation, live weather retrieval, risk logic."],
            ["ML", "scikit-learn Random Forest", "Baseline next-month rainfall, NDVI, and water prediction."],
            ["Database", "PostgreSQL, PostGIS-ready", "Districts, environmental metrics, prediction runs, model runs."],
            ["External data", "Open-Meteo, Esri, OpenStreetMap", "Current weather and map tiles."],
        ], [36 * mm, 50 * mm, 88 * mm], s),
        P("4. Processing Workflow", s["h1"]),
        table([
            ["Step", "Description"],
            ["1. Input", "Select Assam state, district, and month."],
            ["2. Boundary", "Resolve the selected district boundary and area."],
            ["3. Data loading", "Load satellite, rainfall, and surface-water datasets."],
            ["4. Spatial processing", "Clip and mask records to the district boundary."],
            ["5. Indicators", "Calculate NDVI, rainfall statistics, water percentage, and area."],
            ["6. Prediction", "Train on historical records and test on unseen later records."],
            ["7. Delivery", "Store results and expose standardized JSON through FastAPI."],
        ], [32 * mm, 142 * mm], s),
        PageBreak(),
    ])

    story.extend([
        P("5. API Documentation", s["h1"]),
        table([
            ["Endpoint", "Purpose"],
            ["GET /api/v1/health", "Check API availability."],
            ["GET /api/v1/districts", "Return supported districts."],
            ["GET /api/v1/prediction?district=Kamrup&month=2026-07", "Return prediction, risks, water area, and rainfall history."],
            ["GET /api/v1/live?district=Kamrup", "Return current Open-Meteo conditions."],
            ["GET /api/v1/model/validation", "Return MAE, RMSE, R2, test period, and database status."],
        ], [78 * mm, 96 * mm], s),
        P("Example prediction response", s["h2"]),
        P('{"district":"Kamrup","state":"Assam","prediction":{"rainfall_mm":400.8,"ndvi":0.599,"water_percent":4.97,"water_area_km2":215.9},"risks":{"flood_risk":"high","drought_risk":"low","crop_stress":"low"}}', s["code"]),
        P("6. Machine Learning and Validation", s["h1"]),
        P("The current model is a simple RandomForestRegressor baseline. It uses chronological validation: earlier records are used for training and the latest records are held out for testing. The final model then trains on the full available history for future prediction.", s["body"]),
        table([
            ["Output", "MAE", "RMSE", "R2"],
            ["Rainfall (mm)", "54.2", "62.2097", "0.7483"],
            ["NDVI", "0.0188", "0.0197", "-0.3472"],
            ["Surface water (%)", "0.267", "0.2882", "0.657"],
        ], [62 * mm, 32 * mm, 32 * mm, 32 * mm], s),
        P("These metrics are from the built-in demo dataset and are not official accuracy claims. The report must be updated after government-validated historical data is loaded.", s["small"]),
        PageBreak(),
    ])

    story.extend([
        P("7. Database Design", s["h1"]),
        table([
            ["Table", "Stored information"],
            ["districts", "District name, state, area, and boundary GeoJSON."],
            ["environmental_metrics", "Monthly NDVI, rainfall, water coverage, area, and source."],
            ["prediction_runs", "Predicted indicators, target month, model, and training source."],
            ["model_training_runs", "Train/test counts, test period, MAE, RMSE, R2, and model metadata."],
        ], [55 * mm, 125 * mm], s),
        P("8. Testing and Verification", s["h1"]),
        table([
            ["Check", "Result"],
            ["Frontend TypeScript/Vite production build", "Passed"],
            ["Python backend compilation", "Passed"],
            ["Prediction endpoint", "HTTP 200"],
            ["District list endpoint", "Three Assam districts returned"],
            ["Live weather endpoint", "HTTP 200 when Open-Meteo is reachable"],
            ["Historical rainfall response", "18 records returned from demo history"],
            ["PostgreSQL schema", "Tables created and district seed verified"],
            ["Model validation persistence", "Validation run stored in PostgreSQL"],
        ], [82 * mm, 98 * mm], s),
        P("9. Setup and Demonstration", s["h1"]),
        P("Prerequisites: PostgreSQL running locally, Python with backend dependencies, and Node.js/npm. From the project root, run the one-command launcher:", s["body"]),
        P("run.bat", s["code"]),
        P("Dashboard: http://127.0.0.1:5173/  |  API docs: http://127.0.0.1:8001/docs", s["body"]),
        P("Select a district and month, toggle map layers, inspect historical rainfall, open processing details, and review field/disaster outlook cards. The API source field identifies demo data until real government datasets are loaded.", s["body"]),
        P("10. Limitations and Next Steps", s["h1"]),
        P("The current environmental history is a clearly labeled demo dataset. District profile adjustments make the multi-district interface demonstrable, but they are not a replacement for actual district raster/vector processing. The next production step is to load geoBoundaries, Sentinel-2, CHIRPS, and JRC data, clip them with PostGIS/rasterio, store derived metrics, and retrain/evaluate the model on real historical observations.", s["body"]),
        P("Project status: working prototype, API and database verified, real government geospatial ingestion pending.", s["quote"]),
    ])

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=22 * mm, title="GeoInsight Project Report", author="GeoInsight Team")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()