# Where to DINE - Project Structure Diagram

## Project Overview
**Where to DINE** is a location-based restaurant recommendation system that allows users to select an origin point on a map, then find recommended restaurant hotspot areas based on travel mode and time.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Where to DINE System                      │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌───────────────┐                    ┌───────────────┐
│  Frontend     │                    │   Backend     │
│    Layer      │ ◄────HTTP────►     │    Layer      │
└───────────────┘                    └───────────────┘
        │                                     │
        │                                     │
        ▼                                     ▼
┌───────────────┐                    ┌───────────────┐
│ Third-party   │                    │     Data      │
│     APIs      │                    │     Layer     │
│ (Mapbox API)  │                    │  (Database)   │
└───────────────┘                    └───────────────┘
```

---

## Project File Structure

```
GE5226_WHERE-TO-DINE-FINAL/
│
├── .git/                                    # Git version control directory
│
├── where-to-dine-front-end.html            # Frontend main file (deleted)
│   └── Features:
│       ├── Interactive map interface (Leaflet)
│       ├── User input control panel
│       ├── Isochrone visualization
│       └── Recommended restaurant list display
│
└── [Backend Files] (not in repository)
    ├── main.py / app.py                    # Backend API server (inferred)
    │   └── API endpoints:
    │       ├── /api/hotspots               # Get all hotspot areas
    │       └── /api/recommend              # Get recommended restaurants
    │
    └── [Data Files]                        # Restaurant and hotspot data (inferred)
```

---

## Technology Stack Details

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **HTML5** | - | Page structure |
| **CSS3** | - | Styling (dark theme) |
| **JavaScript** | ES6+ | Interactive logic |
| **Leaflet.js** | 1.9.4 | Map rendering and interaction |
| **Bootstrap** | 5.3.3 | UI components and responsive layout |
| **Bootstrap Icons** | 1.11.3 | Icon library |

### Backend Stack (Inferred)

| Technology | Purpose |
|------------|---------|
| **Python** | Backend programming language |
| **FastAPI/Flask** | Web framework (inferred from port 8000) |
| **GeoJSON** | Geographic data format |

### Third-party Services

| Service | Purpose |
|---------|---------|
| **Mapbox Isochrone API** | Generate isochrones (reachability areas) |
| **CartoDB Dark Matter** | Map tile service for base layer |

---

## Core Functional Modules

### 1. Map Interaction Module
```
┌─────────────────────────────────┐
│        Map Module                │
├─────────────────────────────────┤
│ • Map initialization (Leaflet)   │
│ • Click to set origin point      │
│ • Layer management:              │
│   - hotspotsLayer (background)   │
│   - isoLayer (isochrone)         │
│   - recommendedLayer (points)    │
│   - markerLayer (user marker)    │
└─────────────────────────────────┘
```

### 2. User Control Module
```
┌─────────────────────────────────┐
│       Control Panel              │
├─────────────────────────────────┤
│ • Travel mode selection:         │
│   - Walking                      │
│   - Driving                      │
│ • Time range slider: 5-60 mins   │
│ • Search button                  │
└─────────────────────────────────┘
```

### 3. Data Processing Module
```
┌─────────────────────────────────┐
│      Data Processing             │
├─────────────────────────────────┤
│ • Load all hotspot areas         │
│ • Fetch Mapbox isochrone data    │
│ • Request backend recommendation │
│ • Parse GeoJSON data             │
│ • Sort results by weighted score │
└─────────────────────────────────┘
```

### 4. Results Display Module
```
┌─────────────────────────────────┐
│      Results Display             │
├─────────────────────────────────┤
│ • Sidebar list display:          │
│   - Restaurant name              │
│   - Zone                         │
│   - Weighted score               │
│ • Map marker display:            │
│   - Circle markers (yellow)      │
│   - Popup info windows           │
│ • Click list item to fly to map  │
└─────────────────────────────────┘
```

---

## Data Flow Diagram

```
User Actions
  │
  ├─ 1. Click map to set origin
  │     └─► Create marker in markerLayer
  │
  ├─ 2. Select travel mode & time
  │     └─► Update control panel state
  │
  └─ 3. Click "Find Recommendations" button
        │
        ├─► API Call 1: Mapbox Isochrone API
        │   └─► Return isochrone GeoJSON
        │       └─► Render to isoLayer
        │
        └─► API Call 2: Backend /api/recommend
            ├─ Parameters: lat, lon, mode, minutes
            │
            └─► Return recommended restaurants GeoJSON
                ├─► Render to map (recommendedLayer)
                └─► Render to sidebar list (results-list)
```

---

## API Specification

### Backend API Endpoints

#### 1. Get All Hotspot Areas
```
GET /api/hotspots
Response: GeoJSON string
{
  "type": "FeatureCollection",
  "features": [...]
}
```

#### 2. Get Recommended Restaurants
```
GET /api/recommend?lat={lat}&lon={lon}&mode={mode}&minutes={minutes}
Parameters:
  - lat: Latitude
  - lon: Longitude
  - mode: Travel mode (walking/driving)
  - minutes: Time range (5-60)

Response: GeoJSON string
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [lon, lat]
      },
      "properties": {
        "name": "Restaurant name",
        "address": "Address",
        "zone": "Zone",
        "weighted_score": score
      }
    },
    ...
  ]
}
```

---

## UI Design Specification

### Color Scheme
- **Primary Background**: `#1a1a1a` (deep black)
- **Sidebar**: `#212529` (dark gray)
- **Card Background**: `#343a40` (medium gray)
- **List Items**: `#495057` (light gray)
- **List Hover**: `#6c757d` (lighter gray)
- **Theme Color**: `#ffc107` (yellow - for titles and markers)
- **Text**: `#f8f9fa` (light text)

### Layout Structure
```
┌──────────────────────────────────────────────┐
│                 100vh                         │
├─────────────┬────────────────────────────────┤
│             │                                 │
│  Sidebar    │        Map Container           │
│  (30% width)│        (remaining space)        │
│  Max 400px  │                                 │
│  Min 300px  │        Leaflet Map             │
│             │        (100% width & height)    │
│  ┌────────┐│                                 │
│  │Control ││                                 │
│  │ Panel  ││                                 │
│  └────────┘│                                 │
│  ┌────────┐│                                 │
│  │Results ││                                 │
│  │  List  ││                                 │
│  └────────┘│                                 │
│             │                                 │
└─────────────┴────────────────────────────────┘
```

---

## Key Features

1. **Responsive Design**: Uses Flexbox layout, adapts to different screen sizes
2. **Dark Theme**: Modern dark UI interface
3. **Real-time Interaction**: Instant map click feedback, list click to fly to map
4. **Isochrone Visualization**: Intuitive display of reachability areas
5. **Smart Recommendations**: Restaurant ranking based on weighted scores
6. **Dual Display**: Map markers + sidebar list

---

## Technical Highlights

1. **DOM Load Optimization**: Uses `DOMContentLoaded` to ensure scripts execute after DOM loads
2. **Map Rendering Fix**: Uses `invalidateSize()` to solve Leaflet blank map issue in Flexbox
3. **Layer Management**: Uses multiple `LayerGroup` for clear layer separation
4. **Async Data Processing**: Uses `async/await` for API calls
5. **Error Handling**: Comprehensive try-catch error catching mechanism

---

## Deployment Requirements

### Frontend Deployment
- Any static web server (e.g., Nginx, Apache)
- Or open HTML file directly in browser

### Backend Deployment
- Python 3.7+
- Backend server must run at `http://127.0.0.1:8000`

### Environment Variables
- **MAPBOX_TOKEN**: Valid Mapbox access token required

---

## Development Status

### Git History
```
cb3cffd - Delete where-to-dine-front-end.html (current HEAD)
aad7641 - Add files via upload
```

### Current Status
- Frontend HTML file has been deleted
- Project is in blank state
- Backend files are not in version control

---

## Recommended Complete Project Structure

```
GE5226_WHERE-TO-DINE-FINAL/
│
├── frontend/
│   ├── index.html                  # Frontend main file
│   ├── css/
│   │   └── style.css               # Separate stylesheet
│   └── js/
│       └── app.js                  # Separate JavaScript file
│
├── backend/
│   ├── main.py                     # FastAPI/Flask server
│   ├── requirements.txt            # Python dependencies
│   ├── models/
│   │   └── recommendation.py       # Recommendation algorithm model
│   └── data/
│       ├── hotspots.geojson        # Hotspot area data
│       └── restaurants.geojson     # Restaurant data
│
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
└── PROJECT_STRUCTURE.md            # This structure document
```

---

**Document Generated**: 2025-11-16
**Project Status**: Files need to be restored and backend code needs to be completed
