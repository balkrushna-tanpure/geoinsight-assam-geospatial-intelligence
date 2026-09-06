# GeoInsight Hosting Guide

## Recommended production layout

```text
Netlify  -> React frontend
Render   -> FastAPI and ML backend
Neon/Supabase/Render -> hosted PostgreSQL database
```

Netlify is used for the frontend. The Python API and scikit-learn model run on Render because Netlify is not a persistent Python server.

## 1. Push the code to GitHub

From the project root:

```powershell
git init
git add .
git commit -m "Build GeoInsight geospatial intelligence prototype"
git branch -M main
git remote add origin https://github.com/balkrushna-tanpure/geoinsight-assam-geospatial-intelligence.git
git push -u origin main
```

Do not commit `backend/.env`. It is ignored by `.gitignore`.

## 2. Deploy the backend on Render

1. Open Render and choose **New + Web Service**.
2. Connect the GitHub repository.
3. Select Python runtime.
4. Set Python version to `3.13.5`.
5. Use these values:

```text
Build command: pip install -r backend/requirements.txt
Start command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

6. Add environment variable:

```text
DATABASE_URL=<your hosted PostgreSQL connection string>
```

7. Deploy and copy the Render URL, for example:

```text
https://geoinsight-api.onrender.com
```

The API documentation will be at `/docs`.

## 3. Prepare the hosted database

Use a hosted PostgreSQL provider such as Neon, Supabase, or Render PostgreSQL. Run `backend/db/schema.sql` against that database. Do not use the local password `root` in production.

## 4. Deploy the frontend on Netlify

1. Open Netlify and choose **Add new site > Import an existing project**.
2. Select the GitHub repository.
3. Use:

```text
Base directory: frontend
Build command: npm run build
Publish directory: frontend/dist
```

4. Add this environment variable in Netlify site settings:

```text
VITE_API_BASE_URL=https://geoinsight-api.onrender.com
```

5. Deploy the site.

## 5. Update backend CORS

After Netlify gives you a domain, add it to `allow_origins` in `backend/app/main.py`, then push the change. For example:

```python
allow_origins=[
    "https://your-site.netlify.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

## 6. Verify production

Open these URLs:

```text
https://your-api.onrender.com/api/v1/health
https://your-api.onrender.com/api/v1/districts
https://your-api.onrender.com/docs
https://your-site.netlify.app
```

Then change district and month in the dashboard and confirm that the cards, history, live weather, map, and risk indicators update.

## Current data note

The application currently labels environmental history as `demo_dataset`. Replace it with government-validated Sentinel-2, CHIRPS, JRC Global Surface Water, and geoBoundaries data before presenting values as official results.