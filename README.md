# Where to DINE? 🍽️

> A location-based restaurant recommendation system powered by isochrone analysis and weighted scoring algorithms.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-green.svg)](https://leafletjs.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-purple.svg)](https://getbootstrap.com/)

## 📖 Overview

**Where to DINE?** is an intelligent restaurant recommendation system that helps users discover dining options within a specified time range from their location. By leveraging isochrone mapping and smart recommendation algorithms, the system provides personalized restaurant suggestions based on travel mode (walking/driving) and time constraints.

### Key Highlights

✨ **Real-time Isochrone Visualization** - See exactly where you can reach in 5-60 minutes
🎯 **Smart Recommendations** - Weighted scoring system considering quality, density, and accessibility
🚶🚗 **Multi-modal Travel** - Support for both walking and driving modes
🗺️ **Interactive Map Interface** - Intuitive map-based interaction with Leaflet.js
📱 **Responsive Design** - Modern dark theme UI optimized for all devices
🔄 **Real-time Updates** - Dynamic data loading and seamless map-list synchronization

---

## 🎯 Features

### Core Functionality

1. **Interactive Origin Selection**
   - Click anywhere on the map to set your starting point
   - Real-time marker placement with visual feedback

2. **Customizable Search Parameters**
   - **Travel Mode**: Walking or Driving
   - **Time Range**: 5-60 minutes (adjustable slider)

3. **Isochrone Generation**
   - Powered by Mapbox Isochrone API
   - Visual representation of reachable areas
   - Dynamic updates based on user parameters

4. **Intelligent Recommendations**
   - Weighted scoring algorithm
   - Factors considered:
     - Restaurant quality metrics
     - Hotspot area density
     - Geographic accessibility
   - Results sorted by relevance score

5. **Dual Display System**
   - **Map View**: Yellow circle markers with popup info windows
   - **Sidebar List**: Detailed restaurant information with scores
   - **Interactive Sync**: Click list items to fly to map location

6. **Hotspot Visualization**
   - Background layer showing all restaurant concentration areas
   - Semi-transparent overlay for context awareness

---

## 🛠️ Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **HTML5** | - | Structure and semantics |
| **CSS3** | - | Custom dark theme styling |
| **JavaScript** | ES6+ | Interactive logic and API integration |
| **Leaflet.js** | 1.9.4 | Map rendering and geospatial operations |
| **Bootstrap** | 5.3.3 | UI components and responsive grid |
| **Bootstrap Icons** | 1.11.3 | Icon library |

### Backend (Inferred)

| Technology | Purpose |
|------------|---------|
| **Python** | Server-side language |
| **FastAPI/Flask** | RESTful API framework |
| **GeoJSON** | Geographic data exchange format |

### External Services

| Service | Usage |
|---------|-------|
| **Mapbox Isochrone API** | Generate time-based reachability polygons |
| **CartoDB Dark Matter** | Base map tiles for visualization |

---

## 📁 Project Structure

```
GE5226_WHERE-TO-DINE-FINAL/
│
├── frontend/
│   ├── index.html              # Main application file
│   ├── css/
│   │   └── style.css           # Custom stylesheets
│   └── js/
│       └── app.js              # Application logic
│
├── backend/
│   ├── main.py                 # API server entry point
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   └── recommendation.py   # Recommendation algorithm
│   └── data/
│       ├── hotspots.geojson    # Hotspot area data
│       └── restaurants.geojson # Restaurant database
│
├── .gitignore
├── README.md
└── PROJECT_STRUCTURE.md        # Detailed architecture documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Frontend**: Any modern web browser (Chrome, Firefox, Safari, Edge)
- **Backend**: Python 3.7 or higher
- **API Key**: Valid [Mapbox Access Token](https://account.mapbox.com/access-tokens/)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Shi0v0Jasmine/GE5226_WHERE-TO-DINE-FINAL.git
cd GE5226_WHERE-TO-DINE-FINAL
```

#### 2. Configure Mapbox Token

Open `index.html` and replace the placeholder with your Mapbox token:

```javascript
const MAPBOX_TOKEN = "your_mapbox_access_token_here";
```

#### 3. Set Up Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend server should start at `http://127.0.0.1:8000`

#### 4. Launch Frontend

Option A: **Direct Browser Access**
```bash
# Simply open index.html in your browser
open frontend/index.html
```

Option B: **Local Web Server** (Recommended)
```bash
# Using Python
cd frontend
python -m http.server 8080

# Or using Node.js
npx http-server -p 8080
```

Then navigate to `http://localhost:8080`

---

## 💻 Usage

### Basic Workflow

1. **Set Origin Point**
   - Click anywhere on the map to set your starting location
   - A marker will appear at the selected point

2. **Configure Search Parameters**
   - Choose travel mode: Walking 🚶 or Driving 🚗
   - Adjust time slider (5-60 minutes)

3. **Find Recommendations**
   - Click the "Find Recommendations" button
   - Wait for isochrone and recommendation data to load

4. **Explore Results**
   - View recommendations in the sidebar (sorted by score)
   - Click on any restaurant to see its location on the map
   - Interact with map markers to view detailed popup information

### Example Use Cases

- **Lunch Break**: "Where can I grab lunch within a 15-minute walk?"
- **Dinner Planning**: "What are the best restaurants within a 30-minute drive?"
- **Tourist Exploration**: "Show me dining hotspots I can reach in 20 minutes"

---

## 🔌 API Documentation

### Backend Endpoints

#### 1. Get All Hotspot Areas

```http
GET /api/hotspots
```

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { ... },
      "properties": { ... }
    }
  ]
}
```

#### 2. Get Recommended Restaurants

```http
GET /api/recommend?lat={latitude}&lon={longitude}&mode={mode}&minutes={minutes}
```

**Parameters:**
- `lat` (float): Latitude of origin point
- `lon` (float): Longitude of origin point
- `mode` (string): Travel mode - `walking` or `driving`
- `minutes` (int): Time range - 5 to 60

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "name": "Restaurant Name",
        "address": "123 Main St",
        "zone": "Downtown",
        "weighted_score": 85.5
      }
    }
  ]
}
```

---

## 🎨 UI Design

### Color Palette

```css
--primary-bg:      #1a1a1a  /* Deep Black */
--sidebar-bg:      #212529  /* Dark Gray */
--card-bg:         #343a40  /* Medium Gray */
--list-item:       #495057  /* Light Gray */
--list-hover:      #6c757d  /* Lighter Gray */
--theme-color:     #ffc107  /* Yellow (Accent) */
--text-color:      #f8f9fa  /* Light Text */
```

### Layout

- **Sidebar**: 30% width (max 400px, min 300px)
- **Map Container**: Remaining space (100% height)
- **Responsive**: Flexbox-based adaptive layout

---

## 🏗️ Architecture

### Data Flow

```
User Interaction
    │
    ├─ Click Map → Set Origin Marker
    │
    ├─ Select Mode & Time → Update UI State
    │
    └─ Click "Find Recommendations"
        │
        ├─► API Call 1: Mapbox Isochrone API
        │   └─► Returns: GeoJSON polygon
        │       └─► Render: Blue overlay on map
        │
        └─► API Call 2: Backend /api/recommend
            └─► Returns: GeoJSON restaurant points
                ├─► Render: Yellow markers on map
                └─► Render: Sorted list in sidebar
```

### Layer Management

```javascript
hotspotsLayer       // All restaurant hotspot areas (background)
isoLayer            // Isochrone polygon (reachable area)
recommendedLayer    // Recommended restaurant points
markerLayer         // User-selected origin marker
```

---

## 🔧 Technical Highlights

### 1. DOM Load Optimization
```javascript
document.addEventListener("DOMContentLoaded", function() {
    // Ensures all scripts run after DOM is fully loaded
});
```

### 2. Leaflet Rendering Fix
```javascript
setTimeout(function() {
    map.invalidateSize();  // Fixes blank map in Flexbox containers
}, 100);
```

### 3. Async Data Handling
```javascript
async function handleSearch() {
    try {
        const isoResponse = await fetch(mapbox_url);
        const recResponse = await fetch(recommend_url);
        // Process responses...
    } catch (error) {
        // Robust error handling
    }
}
```

### 4. Multi-layer Architecture
- Clear separation of concerns
- Independent layer control
- Efficient rendering updates

---

## 📊 Performance Considerations

- **Lazy Loading**: Hotspot data loaded on app initialization
- **Layer Optimization**: Efficient use of Leaflet layer groups
- **API Caching**: Potential for caching isochrone results
- **Debouncing**: Slider input optimization (if needed)

---

## 🐛 Known Issues & Limitations

1. **Backend Dependency**: Requires running backend server at `http://127.0.0.1:8000`
2. **API Rate Limits**: Mapbox free tier has usage restrictions
3. **Browser Compatibility**: Requires modern browser with ES6+ support
4. **Mobile Responsiveness**: Optimized for desktop, mobile UX can be improved

---

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] Core isochrone visualization
- [x] Basic recommendation system
- [x] Interactive map interface

### Phase 2 (Planned)
- [ ] User authentication and saved searches
- [ ] Restaurant reviews and ratings integration
- [ ] Advanced filtering (cuisine type, price range)
- [ ] Multi-destination support

### Phase 3 (Future)
- [ ] Mobile native app (React Native)
- [ ] Real-time traffic data integration
- [ ] Social features (share recommendations)
- [ ] Machine learning-based personalization

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Add comments for complex logic
- Update documentation for new features
- Test thoroughly before submitting PR

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Jasmine Shi** - *Initial work* - [@Shi0v0Jasmine](https://github.com/Shi0v0Jasmine)

---

## 🙏 Acknowledgments

- **Mapbox** - Isochrone API and geocoding services
- **Leaflet.js** - Open-source mapping library
- **CartoDB** - Base map tiles
- **Bootstrap** - UI framework
- **GE5226 Course** - Project inspiration and guidance

---

## 📧 Contact

For questions or feedback, please open an issue or contact:
- GitHub: [@Shi0v0Jasmine](https://github.com/Shi0v0Jasmine)

---

## 📚 Additional Resources

- [Project Structure Documentation](PROJECT_STRUCTURE.md) - Detailed architecture and design
- [Mapbox Isochrone API Docs](https://docs.mapbox.com/api/navigation/isochrone/)
- [Leaflet Documentation](https://leafletjs.com/reference.html)
- [GeoJSON Specification](https://geojson.org/)

---

**Made with ❤️ for food lovers and explorers**
