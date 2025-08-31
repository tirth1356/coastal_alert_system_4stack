# 🌊 Coastal Alarm System - Frontend & Backend Integration Guide

## 🚀 Quick Start

### 1. Start the Backend (Django)
```bash
cd coastal_backend
python start_system.py
```

### 2. Start the Frontend (React)
```bash
cd coastal-dashboard
npm install
npm start
```

### 3. Test the Integration
```bash
cd coastal_backend
python test_integration.py
```

## 📊 What You Should See

### Backend (http://localhost:8000)
- **API Health**: `GET /api/health/` - Returns system status
- **Dashboard Data**: `GET /api/dashboard/` - Overview statistics
- **Locations**: `GET /api/locations/` - All coastal monitoring locations
- **Active Alerts**: `GET /api/alerts/active/` - Current alerts
- **Admin Panel**: `http://localhost:8000/admin/` - Full system management

### Frontend (http://localhost:3000)
Your React dashboard should now display:

1. **📈 Real-time Metrics Cards**:
   - Active Locations (5)
   - Active Alerts (0 initially)
   - High Risk Areas (0 initially)
   - Latest Water Level data

2. **🚨 Alert Panel** (appears when alerts exist):
   - Active alerts with real-time data
   - Alert resolution buttons
   - Risk scores and locations

3. **🗺️ Interactive Location Map**:
   - 5 coastal locations (Miami Beach, Virginia Beach, etc.)
   - Color-coded risk levels
   - Hover tooltips with location details
   - Alert indicators with pulsing animations

4. **📊 Water Level Chart**:
   - Real sensor data visualization
   - Location selector dropdown
   - 24-hour data patterns
   - Interactive tooltips

5. **🔄 Auto-refresh**:
   - Data updates every 30 seconds
   - Manual refresh button in header
   - System status indicators

## 🔧 Testing the Complete Flow

### 1. Trigger Risk Prediction
```bash
curl -X POST http://localhost:8000/api/locations/1/run_prediction/
```

### 2. Add High-Risk Sensor Data (might trigger alerts)
```bash
curl -X POST http://localhost:8000/api/sensor-data/ \
  -H "Content-Type: application/json" \
  -d '{
    "location": 1,
    "measurement_type": "water_level",
    "value": 6.0,
    "unit": "meters",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "data_source": "manual_test"
  }'
```

### 3. Check Frontend Updates
- Visit http://localhost:3000
- Should see updated metrics
- If alert triggered (risk > 0.7), you'll see alert panel
- Map will show location with new risk color

## 🎯 Key Features Working

### ✅ Real-time Data Integration
- **Backend**: Fetches data from NOAA/USGS APIs (when available)
- **Frontend**: Displays live coastal measurements
- **Updates**: Auto-refresh every 30 seconds

### ✅ ML Model Integration
- **Dummy Model**: Currently uses a Random Forest model for testing
- **Your Model**: Replace with your trained model (see `integrate_your_model.py`)
- **Predictions**: Risk scores from 0-1, categorized as low/medium/high/critical

### ✅ Alert System
- **Automatic**: Triggers when risk score > 0.7 (configurable)
- **Types**: Storm surge, high waves, coastal flooding, erosion, etc.
- **Management**: Frontend allows alert resolution

### ✅ Interactive Dashboard
- **Responsive**: Works on desktop and mobile
- **Real-time**: Live updates without page refresh
- **Visual**: Color-coded risk indicators and charts

## 🛠️ Customization Options

### Backend Customization

1. **Add Your ML Model**:
   ```bash
   python integrate_your_model.py
   ```

2. **Configure Alert Thresholds**:
   Edit `coastal_backend/settings.py`:
   ```python
   ALERT_THRESHOLD = 0.7  # Change as needed
   ```

3. **Add External APIs**:
   Edit API configurations in settings for your data sources

### Frontend Customization

1. **Update API URL** (for deployment):
   Edit `coastal-dashboard/src/services/api.js`:
   ```javascript
   const API_BASE_URL = 'https://your-domain.com/api';
   ```

2. **Customize Styling**:
   Edit `coastal-dashboard/src/App.css` for colors, layout, etc.

3. **Add New Components**:
   Create new React components in `src/components/`

## 🐛 Common Issues & Solutions

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'pandas'`
```bash
pip install pandas numpy scikit-learn
```

**Issue**: `CORS errors` in browser console
- Check `coastal_backend/settings.py` CORS configuration
- Ensure `CORS_ALLOW_ALL_ORIGINS = True` for development

**Issue**: `No locations found`
```bash
python manage.py seed_data
```

### Frontend Issues

**Issue**: `Cannot connect to backend`
- Ensure Django server is running on http://localhost:8000
- Check browser console for CORS errors
- Verify API URL in `src/services/api.js`

**Issue**: `npm start` fails
```bash
cd coastal-dashboard
npm install
npm audit fix
npm start
```

**Issue**: Blank dashboard/no data
- Check browser console for JavaScript errors
- Verify backend APIs are working: `curl http://localhost:8000/api/health/`

## 📈 Performance Considerations

### Backend
- **Database**: Switch to PostgreSQL for production
- **Caching**: Add Redis for improved performance
- **Background Tasks**: Use Celery for data ingestion
- **Monitoring**: Add logging and error tracking

### Frontend
- **Bundling**: Production build with `npm run build`
- **API Calls**: Implement proper error handling and retry logic
- **State Management**: Consider Redux for complex state
- **Real-time**: Upgrade to WebSockets for live updates

## 🚀 Deployment Ready

### Backend Deployment
1. Set `DEBUG=False` in production
2. Configure proper database (PostgreSQL)
3. Set up web server (nginx + gunicorn)
4. Add proper secret key and security settings

### Frontend Deployment
1. Update API URL to production backend
2. Build production version: `npm run build`
3. Deploy to static hosting (Netlify, Vercel, etc.)
4. Configure CORS on backend for frontend domain

## 🎉 Success Indicators

If everything is working correctly, you should see:

1. ✅ Backend API responding at http://localhost:8000
2. ✅ Frontend loading at http://localhost:3000
3. ✅ Dashboard showing real location data
4. ✅ Charts displaying sensor measurements
5. ✅ Map showing coastal locations with risk indicators
6. ✅ Auto-refresh working (data updates every 30 seconds)
7. ✅ ML predictions generating risk scores
8. ✅ Alerts appearing when high risk is detected

## 📞 Need Help?

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Check Django server logs for backend errors
3. Run `python test_integration.py` to diagnose issues
4. Ensure all dependencies are installed
5. Verify API endpoints are accessible

Your coastal alarm system is now fully integrated and ready for real-world use! 🌊🚨
