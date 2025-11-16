# Where to DINE - Complete Usage Guide

> A step-by-step guide to set up, run, and use the Where to DINE restaurant recommendation system.

---

## 📑 Table of Contents

1. [Quick Start](#-quick-start)
2. [Detailed Setup Guide](#-detailed-setup-guide)
3. [Data Processing Workflow](#-data-processing-workflow)
4. [Running the Application](#-running-the-application)
5. [Using the Application](#-using-the-application)
6. [Troubleshooting](#-troubleshooting)
7. [Advanced Configuration](#-advanced-configuration)

---

## 🚀 Quick Start

### TL;DR (Experienced Developers)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Mapbox token in frontend HTML
# Edit: frontend/index.html (line with MAPBOX_TOKEN)

# 3. Start backend server
python backend/main.py

# 4. Open frontend in browser
# Open: frontend/index.html in your browser
```

---

## 📖 Detailed Setup Guide

### Step 1: Prerequisites Check

Before starting, ensure you have:

- [ ] **Python 3.7+** installed
  ```bash
  python --version
  # Should output: Python 3.7.x or higher
  ```

- [ ] **pip** (Python package manager)
  ```bash
  pip --version
  ```

- [ ] **Modern web browser** (Chrome, Firefox, Safari, or Edge)

- [ ] **Mapbox Account** with access token
  - Sign up at: https://account.mapbox.com/
  - Get your token at: https://account.mapbox.com/access-tokens/

- [ ] **Internet connection** (for API calls and map tiles)

---

### Step 2: Project Setup

#### 2.1 Clone the Repository

```bash
git clone https://github.com/Shi0v0Jasmine/GE5226_WHERE-TO-DINE-FINAL.git
cd GE5226_WHERE-TO-DINE-FINAL
```

#### 2.2 Create Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

#### 2.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

**Verification:**
```bash
pip list | grep fastapi
# Should show: fastapi 0.104.1
```

---

### Step 3: Configure API Keys

#### 3.1 Mapbox Access Token

1. Open `frontend/index.html` (or `where-to-dine-front-end.html`)
2. Locate the line (around line 132):
   ```javascript
   const MAPBOX_TOKEN = "pk.eyJ1IjoiamFzbWluZTB2MCIsImEiOiJjbWkwbTF1ejMwbzlnMmtxNGVqN2pvdXVoIn0.EQRczgzFqAndRDGJaxRCWg";
   ```
3. Replace with your own token:
   ```javascript
   const MAPBOX_TOKEN = "YOUR_MAPBOX_ACCESS_TOKEN_HERE";
   ```

#### 3.2 Backend Configuration (Optional)

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DEBUG=True

# Optional: Database connection
# DATABASE_URL=postgresql://user:password@localhost/dine_db
```

---

## 🗃️ Data Processing Workflow

### Overview

The data pipeline consists of three stages:
1. **Data Collection** - Download restaurant data from Google Places API
2. **Data Processing** - Clean, analyze, and generate hotspot areas
3. **Data Export** - Convert to GeoJSON format for the application

---

### Stage 1: Data Collection (Jupyter Notebook)

#### Required Files

**📌 Important:** You should upload your data collection Jupyter Notebook to the repository for reproducibility and documentation purposes.

**Recommended structure:**
```
data_processing/
├── 01_data_collection.ipynb       # Google Places API data download
├── 02_data_cleaning.ipynb         # Data cleaning and validation
├── 03_hotspot_generation.ipynb    # Generate hotspot areas
└── README.md                      # Data processing documentation
```

#### Creating the Data Collection Notebook

1. **Create a new Jupyter notebook** (if not already existing):
   ```bash
   mkdir -p data_processing
   cd data_processing
   jupyter notebook
   ```

2. **Google Places API Setup**:
   ```python
   # Install required libraries
   !pip install googlemaps pandas geopandas

   # Import libraries
   import googlemaps
   import pandas as pd
   import json
   from datetime import datetime

   # Initialize Google Maps client
   API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"
   gmaps = googlemaps.Client(key=API_KEY)

   # Example: Search for restaurants in NYC
   location = (40.730610, -73.935242)  # NYC coordinates
   radius = 5000  # 5km radius

   places_result = gmaps.places_nearby(
       location=location,
       radius=radius,
       type='restaurant'
   )
   ```

3. **Extract and save data**:
   ```python
   # Parse results
   restaurants = []
   for place in places_result['results']:
       restaurant = {
           'name': place.get('name'),
           'address': place.get('vicinity'),
           'lat': place['geometry']['location']['lat'],
           'lon': place['geometry']['location']['lng'],
           'rating': place.get('rating', 0),
           'user_ratings_total': place.get('user_ratings_total', 0),
           'types': place.get('types', [])
       }
       restaurants.append(restaurant)

   # Save to CSV
   df = pd.DataFrame(restaurants)
   df.to_csv('../backend/data/raw_restaurants.csv', index=False)
   ```

#### **Yes, you SHOULD upload the .ipynb file** because:
- ✅ Ensures data collection process is reproducible
- ✅ Documents the API parameters and query logic
- ✅ Allows others to understand data sources
- ✅ Enables future updates and expansions

---

### Stage 2: Data Processing

#### Clean and Enrich Data

```python
# In 02_data_cleaning.ipynb

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load raw data
df = pd.read_csv('../backend/data/raw_restaurants.csv')

# Remove duplicates
df = df.drop_duplicates(subset=['name', 'lat', 'lon'])

# Filter out low-quality data
df = df[df['rating'] >= 3.0]
df = df[df['user_ratings_total'] >= 10]

# Calculate weighted score
df['weighted_score'] = (
    df['rating'] * 0.6 +
    (df['user_ratings_total'] / df['user_ratings_total'].max()) * 100 * 0.4
)

# Create GeoDataFrame
geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

# Save processed data
gdf.to_file('../backend/data/restaurants.geojson', driver='GeoJSON')
```

---

### Stage 3: Generate Hotspot Areas

```python
# In 03_hotspot_generation.ipynb

import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import Voronoi
import numpy as np

# Load restaurant data
restaurants = gpd.read_file('../backend/data/restaurants.geojson')

# Method 1: Kernel Density Estimation
from scipy.stats import gaussian_kde

coords = np.array([(p.x, p.y) for p in restaurants.geometry])
kde = gaussian_kde(coords.T)

# Generate hotspot polygons (simplified example)
# In practice, you'd use clustering algorithms like DBSCAN

from sklearn.cluster import DBSCAN

clustering = DBSCAN(eps=0.01, min_samples=5).fit(coords)
restaurants['cluster'] = clustering.labels_

# Create convex hulls for each cluster
hotspots = restaurants[restaurants['cluster'] != -1].dissolve(
    by='cluster',
    aggfunc='first'
).convex_hull

# Save hotspots
hotspots_gdf = gpd.GeoDataFrame(geometry=hotspots, crs='EPSG:4326')
hotspots_gdf.to_file('../backend/data/hotspots.geojson', driver='GeoJSON')
```

---

### Data Files Structure

After data processing, you should have:

```
backend/data/
├── raw_restaurants.csv        # Original data from Google API
├── restaurants.geojson        # Processed restaurant points
└── hotspots.geojson          # Generated hotspot polygons
```

---

## 🎬 Running the Application

### Step 1: Start the Backend Server

#### Option A: Direct Python Execution

```bash
# Navigate to backend directory
cd backend

# Run the server
python main.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

#### Option B: Using Uvicorn Directly

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Flags explained:**
- `--reload`: Auto-restart on code changes (development only)
- `--host`: Server address
- `--port`: Server port

#### Verify Backend is Running

Open browser and visit:
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/api/hotspots

You should see JSON data or Swagger UI.

---

### Step 2: Open the Frontend

#### Option A: Direct Browser Access (Simplest)

1. Navigate to the `frontend/` directory in your file explorer
2. Double-click `index.html` (or `where-to-dine-front-end.html`)
3. The application will open in your default browser

#### Option B: Using a Local Web Server (Recommended)

**Why use a web server?**
- Avoids CORS issues
- Mimics production environment
- Better for testing

**Python HTTP Server:**
```bash
cd frontend
python -m http.server 8080
```

Then visit: http://localhost:8080

**Node.js HTTP Server:**
```bash
cd frontend
npx http-server -p 8080
```

**VS Code Live Server:**
1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

---

### Step 3: Verify Everything is Working

✅ **Checklist:**

1. Backend server is running (check terminal for no errors)
2. Frontend page loads without console errors
   - Press `F12` to open browser console
   - Should see no red error messages
3. Map displays correctly (dark themed map with tiles)
4. Sidebar shows "Where to DINE?" header and controls
5. Background hotspot areas are visible (if data is loaded)

---

## 🎮 Using the Application

### Basic Workflow

#### 1. Set Your Origin Point

- **Action**: Click anywhere on the map
- **Result**: A marker appears at the clicked location
- **Status**: Sidebar shows "Origin set. Click 'Find Recommendations' to search."

#### 2. Configure Search Parameters

**Travel Mode:**
- 🚶 **Walking**: Best for short distances, urban exploration
- 🚗 **Driving**: Best for longer distances, suburban areas

**Time Range:**
- Slide the time slider (5-60 minutes)
- See the value update in real-time

#### 3. Find Recommendations

- **Action**: Click the blue "Find Recommendations" button
- **Process**:
  1. Fetches isochrone from Mapbox (blue overlay appears)
  2. Queries backend for restaurants within the area
  3. Displays results on map and sidebar

#### 4. Explore Results

**Map Interaction:**
- Click yellow circle markers to view restaurant details
- Popup shows: Name, Address, Zone, Weighted Score

**Sidebar Interaction:**
- Restaurants are listed by score (highest first)
- Click any list item to fly to that location on the map
- Scroll through the list to see all recommendations

---

### Example Use Cases

#### Scenario 1: Quick Lunch Break
```
Origin: Your office location
Mode: Walking
Time: 15 minutes
Expected Result: 5-10 nearby restaurants within walking distance
```

#### Scenario 2: Weekend Dinner
```
Origin: Your home
Mode: Driving
Time: 30 minutes
Expected Result: 20+ restaurants across multiple neighborhoods
```

#### Scenario 3: Tourist Exploration
```
Origin: Hotel location
Mode: Walking
Time: 20 minutes
Expected Result: Restaurants in walkable tourist areas
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

#### Issue 2: Blank Map or Map Not Loading

**Symptoms**: Gray screen, no map tiles visible

**Causes & Solutions**:

1. **Invalid Mapbox Token**
   ```javascript
   // Check console for error message:
   // "401 Unauthorized: Invalid access token"

   // Fix: Replace token in index.html
   const MAPBOX_TOKEN = "YOUR_VALID_TOKEN_HERE";
   ```

2. **JavaScript Not Loading**
   ```bash
   # Open browser console (F12)
   # Look for red error messages

   # Fix: Ensure Leaflet.js CDN is accessible
   # Check internet connection
   ```

3. **Flexbox Rendering Issue**
   - Already fixed in code with `map.invalidateSize()`
   - If still occurs, try refreshing the page (F5)

---

#### Issue 3: CORS Error

**Error in Console**:
```
Access to fetch at 'http://127.0.0.1:8000/api/hotspots' from origin 'null'
has been blocked by CORS policy
```

**Solution**:

1. **Ensure backend has CORS enabled**:
   ```python
   # In backend/main.py
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # In production, specify exact origins
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Use a local web server** instead of opening HTML directly (see Step 2, Option B above)

---

#### Issue 4: No Recommendations Found

**Message**: "No hotspots found within this range."

**Possible Causes**:

1. **No data files loaded**
   - Check that `backend/data/restaurants.geojson` exists
   - Verify file is not empty

2. **Origin point outside data coverage area**
   - Try clicking in a major city center
   - Check if your data covers the selected area

3. **Time range too small**
   - Increase time slider to 20-30 minutes
   - Switch to driving mode for larger coverage

---

#### Issue 5: Slow Performance

**Symptoms**: Long loading times, laggy map

**Solutions**:

1. **Reduce data size**:
   ```python
   # In data processing, limit number of restaurants
   df = df.nlargest(500, 'weighted_score')  # Top 500 only
   ```

2. **Implement caching**:
   ```python
   # Use Redis or simple dict caching for API responses
   ```

3. **Use map clustering**:
   ```javascript
   // Add Leaflet.markercluster plugin for many markers
   ```

---

#### Issue 6: Backend Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Option 1: Kill the process using port 8000
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Option 2: Use a different port
uvicorn main:app --port 8001
# Then update frontend BACKEND_URL to http://127.0.0.1:8001
```

---

## ⚙️ Advanced Configuration

### Customizing the Backend

#### Change Port and Host

```python
# backend/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Accessible from other devices on network
        port=8080,       # Custom port
        reload=True
    )
```

#### Add API Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/recommend")
@limiter.limit("10/minute")
async def recommend(...):
    ...
```

---

### Customizing the Frontend

#### Change Default Map Center

```javascript
// In index.html, line ~139
const map = L.map('map').setView(
    [40.730610, -73.935242],  // [lat, lng] - Change to your city
    12  // Zoom level
);
```

#### Modify Time Range

```javascript
// In index.html, line ~88
<input type="range" class="form-range"
    min="5"    // Change minimum time
    max="60"   // Change maximum time
    step="5"   // Change step size
    value="15"
    id="time-slider">
```

#### Update Color Scheme

```css
/* In <style> section */
:root {
    --primary-bg: #1a1a1a;
    --accent-color: #ffc107;  /* Change to your brand color */
}
```

---

### Performance Optimization

#### Enable Gzip Compression

```python
# backend/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### Implement Response Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_hotspots_cached():
    return load_hotspots_from_file()
```

---

## 📊 Monitoring and Logging

### Backend Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend/logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.get("/api/recommend")
async def recommend(...):
    logger.info(f"Recommendation request: lat={lat}, lon={lon}")
    ...
```

### Frontend Error Tracking

```javascript
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Send to error tracking service (e.g., Sentry)
});
```

---

## 🎓 Additional Resources

- **Full API Documentation**: http://127.0.0.1:8000/docs (when backend is running)
- **Project Structure**: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Main README**: See [README.md](README.md)

### External Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Leaflet.js Tutorials](https://leafletjs.com/examples.html)
- [Mapbox Isochrone API](https://docs.mapbox.com/api/navigation/isochrone/)
- [GeoJSON Specification](https://geojson.org/)

---

## 📝 Quick Reference

### File Locations
```
Frontend HTML:  frontend/index.html
Backend Server: backend/main.py
Data Files:     backend/data/*.geojson
Config:         backend/.env
Dependencies:   requirements.txt
```

### Important URLs
```
Backend API:    http://127.0.0.1:8000
API Docs:       http://127.0.0.1:8000/docs
Frontend:       http://localhost:8080 (or direct file)
```

### Key Commands
```bash
# Start backend
python backend/main.py

# Start frontend server
python -m http.server 8080

# Install dependencies
pip install -r requirements.txt

# Activate venv
source venv/bin/activate
```

---

**Need more help?** Open an issue on GitHub or contact the project maintainers.

**Happy dining! 🍽️**
