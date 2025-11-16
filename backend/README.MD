# Where to DINE?

## A Mobility-Based Dining Recommendation System for NYC

This project is a WebGIS application designed to answer the question, **"Where should I eat?"** Instead of relying on subjective user reviews (like Yelp or Google Maps), this system provides recommendations based on objective, real-world mobility data.

Our core philosophy is **"Vote with FEET!!"** [cite: Where to DINE(Pre).pptx] — a dining area is only "hot" if people actually go there to dine.

The application allows a user to click anywhere on a map of New York City, select a travel mode (Walking or Driving) and a travel time, and instantly receive a ranked list of the best restaurants within their reachable area.

---

## Key Features

* **Mobility-Based Popularity**
  We use a temporally weighted score derived from millions of NYC Taxi drop-offs during peak dining hours [cite: temporal_weighting.md] to define an area's true popularity.

* **Data-Driven Hotspots**
  We use a two-layered analysis to find our "golden zones":

  * **HDBSCAN** identifies 191 statistically dense restaurant clusters (the "Supply") [cite: 191 个餐厅集群].
  * **Pysal (Getis-Ord Gi*)** identifies 23 statistically significant taxi drop-off hotspots (the "Demand") [cite: 23 个统计显著的热点区].
  * A **Spatial Intersection** fuses these two layers to find the 28 final **"Hotspot Dining Areas"** where supply and demand overlap [cite: 识别出 28 个最终的 '热点餐饮区'].

* **Dynamic Accessibility**
  Users can click anywhere on the map to set their origin.

* **Isochrone Filtering**
  The app calls the Mapbox API in real-time to generate a travel-time polygon (isochrone) for the user's selected mode and time.

* **Weighted Restaurant Ranking**
  The system performs a spatial query to find all restaurants within the user's isochrone and within a pre-calculated hotspot. It then ranks these **14,330 restaurants** [cite: --- 成功加载 14330 家餐厅 ---] by their `weighted_score` [cite: temporal_weighting.md] and presents them to the user.

* **Interactive UI**
  A two-panel layout (map on top, controls/results below) [cite: 1763277231612.jpg] provides an intuitive user experience.

---

## Technical Architecture

This project uses a modern, decoupled three-part architecture:

### 1. Backend (Data Pipeline): Google Colab

* **Stack:** Python, GeoPandas, Pysal, HDBSCAN
* **Purpose:** This is where all the heavy-lifting (data science) happens. We run scripts here to process all raw data and pre-calculate two final GeoJSON files.

  * `final_hotspot_polygons_weighted.geojson`: The 28 final hotspot zones [cite: --- 成功加载 28 个最终热点多边形 ---].
  * `restaurants_with_hotspot_scores.geojson`: All 14,330+ restaurants "tagged" with their hotspot score [cite: --- 成功加载 14330 家餐厅 ---].

---

### 2. Backend (API Server): FastAPI

* **Stack:** Python, FastAPI, Uvicorn, HTTPX
* **Purpose:** A lightweight API server (`main.py`) [cite: python main.py] that:

  * Serves the pre-calculated GeoJSON files from the pipeline.
  * Provides a `/api/recommend` endpoint that handles all real-time logic (proxying Mapbox, spatial querying, and ranking).

---

### 3. Frontend (Web App): `index.html`

* **Stack:** HTML, CSS, JavaScript, Leaflet.js, Bootstrap 5 (Light Theme) [cite: 1763277231612.jpg], Mapbox (for basemap & isochrones).
* **Purpose:** A single-page application that:

  * Provides the user interface
  * Manages user input
  * Communicates with the FastAPI backend

---

## Data Sources

* **NYC TLC Trip Records (2024)**
  Used for mobility analysis (`yellow_tripdata_*.parquet` files) [cite: yellow_tripdata_2024-01.parquet].

* **Google Maps Places**
  Used for restaurant locations (`restaurants_nyc_googlemaps.csv`) [cite: restaurants_nyc_googlemaps.csv].

* **NYC Taxi Zones**
  Official boundaries used as the aggregation unit for mobility data (`taxi_zones.shp`) [cite: taxi_zones.shp].

---

## How to Run the Project

You must run the project in **three phases**.

---

### Phase 1: Data Pipeline (Google Colab)

1. Open the Google Colab notebook containing the analysis scripts (Stages 2.A, 2.B, and 2.C).

2. Ensure your data is in the correct Google Drive paths referenced in the scripts:

   ```text
   /content/drive/MyDrive/Where-to-dine-demo/data/raw/taxi/*.parquet
   ```

   [cite: yellow_tripdata_2024-01.parquet (and others)]

   ```text
   /content/drive/MyDrive/Where-to-dine-demo/data/external/boundaries/taxi_zones.shp
   ```

   [cite: taxi_zones.shp]

   * `restaurants_nyc_googlemaps.csv` (in the Colab root) [cite: restaurants_nyc_googlemaps.csv]
   * `dining_zones.geojson` (in the Colab root) [cite: dining_zones.geojson]

3. Run all cells in the notebook.

4. Download the three final output files:

   * `hotspot_arrival_areas_weighted.geojson`
   * `final_hotspot_polygons_weighted.geojson` [cite: final_hotspot_polygons_weighted.geojson]
   * `restaurants_with_hotspot_scores.geojson` [cite: restaurants_with_hotspot_scores.geojson]

---

### Phase 2: Backend (API Server)

1. Create a project folder (e.g., `where-to-dine-backend`).

2. Place the following files inside it:

   * `main.py` [cite: python main.py]
   * `final_hotspot_polygons_weighted.geojson` (from Phase 1)
   * `restaurants_with_hotspot_scores.geojson` (from Phase 1)

3. Create a file named `.env` in the same folder and add your Mapbox token:

   ```env
   MAPBOX_ACCESS_TOKEN="pk.eyJ1...YOUR_TOKEN_HERE"
   ```

4. Install the required Python dependencies:

   ```bash
   pip install "fastapi[all]" uvicorn geopandas httpx python-dotenv
   ```

5. Run the server from your terminal:

   ```bash
   python main.py
   ```

6. The server will start running at:

   ```text
   http://127.0.0.1:8000
   ```

---

### Phase 3: Frontend (Web App)

1. Open the `index.html` file (the final "map-on-top" version [cite: 1763277231612.jpg]) in a text editor.

2. Find the line (around line 103):

   ```js
   const MAPBOX_TOKEN = "...";
   ```

3. Paste your Mapbox Access Token into the quotes. This is required for the isochrones and basemap to load.

4. Save the `index.html` file.

5. Open the `index.html` file in any modern web browser (like Chrome or Edge).

6. As long as the backend server (Phase 2) is running, the application will be fully functional.
