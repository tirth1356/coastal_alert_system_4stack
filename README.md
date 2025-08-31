This is the official submission of team 4Stack for HACKOUT'25 organised by Dhirubhai Ambani University (formerly DAIICT) 

The challenge track was coast warning system with dashboard, interactive map and notification system 

The team members were
Tirth Patel,
Divy Mevada [github](https://github.com/divy-mevada),
Lakshya Mehta [github](https://github.com/LakshyaMehta16)



# 🌊 Coastal Alarm System

A comprehensive real-time coastal monitoring and alert system that combines machine learning predictions with live data feeds to provide early warnings for coastal hazards.

## 🎯 Overview

The Coastal Alarm System is designed to monitor coastal conditions in real-time, predict potential risks using machine learning, and alert users to dangerous conditions. The system integrates multiple data sources including NOAA and USGS APIs to provide accurate, timely information about coastal threats.

## 🏗️ Project Structure

```
coastal-alarm-system/
├── 📱 coastal-dashboard/       # React Frontend Application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API integration
│   │   ├── contexts/          # React contexts (Auth, etc.)
│   │   └── data/             # Static data and configurations
│   ├── public/               # Static assets
│   └── package.json          # Frontend dependencies
├── 🔧 coastal_backend/        # Django Backend API
│   ├── coastal_backend/      # Main Django project
│   ├── monitoring/           # Core monitoring application
│   ├── ml_integration/       # ML model integration
│   ├── ml_models/           # Machine learning model files
│   └── requirements.txt     # Backend dependencies
├── 📋 INTEGRATION_GUIDE.md   # Detailed integration instructions
└── 📖 README.md             # This file
```

## ✨ Features

### 🎛️ Frontend (React Dashboard)
- **Real-time Dashboard**: Live metrics and status indicators
- **Interactive Map**: Visual representation of monitoring locations
- **Alert Management**: Real-time alert notifications and resolution
- **Data Visualization**: Charts and graphs for sensor data
- **User Authentication**: Secure login and signup system
- **Responsive Design**: Works on desktop and mobile devices

### ⚙️ Backend (Django API)
- **RESTful API**: Comprehensive API for all system operations
- **Real-time Data Ingestion**: Automated data collection from NOAA/USGS
- **ML Integration**: Seamless integration with machine learning models
- **Alert System**: Automated alert generation and management
- **Background Processing**: Celery-based task queue for data processing
- **Admin Interface**: Django admin for system management

### 🤖 Machine Learning
- **Risk Prediction**: ML models for coastal risk assessment
- **Customizable Models**: Easy integration of your own trained models
- **Real-time Processing**: Continuous risk evaluation
- **Historical Analysis**: Trend analysis and pattern recognition

## 🚀 Quick Start

### Prerequisites
- **Frontend**: Node.js 16+ and npm
- **Backend**: Python 3.8+ and pip
- **Optional**: Redis (for production background tasks)

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd coastal-alarm-system
```

### 2. Start the Backend (Django)
```bash
cd coastal_backend

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py makemigrations
python manage.py migrate

# Create sample data
python manage.py seed_data

# Create admin user (optional)
python manage.py createsuperuser

# Start the server
python start_system.py
```

The backend will be available at **http://localhost:8000**

### 3. Start the Frontend (React)
```bash
cd coastal-dashboard

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at **http://localhost:3000**

### 4. Verify Integration
```bash
cd coastal_backend
python test_integration.py
```

## 📊 What You'll See

### Frontend Dashboard (http://localhost:3000)
- **📈 Metrics Cards**: Active locations, alerts, risk areas, and latest data
- **🗺️ Interactive Map**: 5 coastal monitoring locations with risk indicators
- **📊 Data Charts**: Real-time sensor data visualization
- **🚨 Alert Panel**: Active alerts with resolution capabilities
- **🔄 Auto-refresh**: Data updates every 30 seconds

### Backend API (http://localhost:8000)
- **API Documentation**: Available endpoints and usage
- **Admin Panel**: `/admin/` - Full system management interface
- **Health Check**: `/api/health/` - System status monitoring

## 🔧 Technology Stack

### Frontend
- **Framework**: React 19.1.1
- **Routing**: React Router DOM 7.8.2
- **HTTP Client**: Axios 1.11.0
- **Authentication**: Google OAuth + JWT
- **Styling**: CSS3 with responsive design

### Backend
- **Framework**: Django 5.2.5
- **API**: Django REST Framework 3.16.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **Background Tasks**: Celery 5.5.3
- **Cache/Message Broker**: Redis 6.4.0
- **ML Libraries**: Pandas, NumPy, Scikit-learn

### External APIs
- **NOAA Tides and Currents API**: Water levels and meteorological data
- **USGS Water Services**: Stream gauge and water quality data

## 📚 API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | System health check |
| GET | `/api/dashboard/` | Dashboard overview data |
| GET | `/api/locations/` | List all monitoring locations |
| GET | `/api/alerts/active/` | Get active alerts |
| GET | `/api/sensor-data/` | Retrieve sensor measurements |
| POST | `/api/sensor-data/` | Add new sensor data |
| GET | `/api/risk-assessments/` | Get ML risk predictions |

### Location-Specific
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/locations/{id}/` | Get location details |
| POST | `/api/locations/{id}/run_prediction/` | Trigger ML prediction |
| GET | `/api/locations/{id}/sensor_data/` | Get location sensor data |

### Alert Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts/` | List all alerts (filterable) |
| POST | `/api/alerts/{id}/resolve/` | Resolve an alert |

## 🤖 Machine Learning Integration

### Adding Your Own Model

1. **Prepare Your Model**:
   - Ensure it accepts pandas DataFrame with standard coastal data columns
   - Implement `predict_proba()` method for risk assessment
   - Save as `.pkl` or `.joblib` file

2. **Integrate the Model**:
   ```bash
   cd coastal_backend
   python integrate_your_model.py
   ```

3. **Model Requirements**:
   Your model should process these input features:
   - `water_level`, `wave_height`, `wind_speed`, `wind_direction`
   - `air_pressure`, `water_temperature`, `hour_of_day`, `day_of_year`

### Example Model Integration
```python
# Example of how your model should be structured
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class CoastalRiskModel:
    def __init__(self):
        self.model = RandomForestClassifier()
    
    def predict_proba(self, X):
        # X is a pandas DataFrame with coastal data
        return self.model.predict_proba(X)
```

## 🔧 Configuration

### Backend Configuration
1. **Environment Variables**:
   ```bash
   cp coastal_backend/.env.example coastal_backend/.env
   ```
   
2. **Edit `.env` file**:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   NOAA_API_KEY=your-noaa-api-key
   USGS_API_KEY=your-usgs-api-key
   ALERT_THRESHOLD=0.7
   ```

### Frontend Configuration
1. **API URL** (for production):
   Edit `coastal-dashboard/src/services/api.js`:
   ```javascript
   const API_BASE_URL = 'https://your-backend-domain.com/api';
   ```

## 🧪 Testing

### Backend Tests
```bash
cd coastal_backend

# Run all tests
python manage.py test

# Test API endpoints
python test_api.py

# Test integration
python test_integration.py
```

### Frontend Tests
```bash
cd coastal-dashboard

# Run React tests
npm test

# Build production version
npm run build
```

## 🚀 Deployment

### Backend Deployment
1. **Production Settings**:
   - Set `DEBUG=False`
   - Configure PostgreSQL database
   - Set up Redis for Celery
   - Configure proper security settings

2. **Web Server Setup**:
   ```bash
   # Using gunicorn
   pip install gunicorn
   gunicorn coastal_backend.wsgi:application --bind 0.0.0.0:8000
   ```

3. **Background Tasks**:
   ```bash
   # Start Celery worker
   celery -A coastal_backend worker --loglevel=info
   
   # Start Celery beat (scheduler)
   celery -A coastal_backend beat --loglevel=info
   ```

### Frontend Deployment
1. **Build for Production**:
   ```bash
   cd coastal-dashboard
   npm run build
   ```

2. **Deploy**: Upload `build/` folder to your hosting service (Netlify, Vercel, AWS S3, etc.)

3. **Update CORS**: Configure backend CORS settings for your production domain

## 🛠️ Development Workflow

### Adding New Features

1. **Backend Development**:
   ```bash
   cd coastal_backend
   python manage.py startapp new_feature
   # Add your models, views, and URLs
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Frontend Development**:
   ```bash
   cd coastal-dashboard
   # Create new components in src/components/
   # Add new routes in src/App.js
   # Update API calls in src/services/api.js
   ```

### Data Flow
1. **Data Ingestion**: Backend fetches data from NOAA/USGS APIs
2. **ML Processing**: Models analyze data and generate risk scores
3. **Alert Generation**: High-risk conditions trigger automatic alerts
4. **Frontend Display**: Dashboard shows real-time data and alerts
5. **User Interaction**: Users can view details and resolve alerts

## 🐛 Troubleshooting

### Common Issues

**❌ Backend won't start**
```bash
# Check if port 8000 is in use
netstat -an | findstr :8000
# Or use a different port
python manage.py runserver 8001
```

**❌ Frontend can't connect to backend**
- Ensure Django server is running on http://localhost:8000
- Check browser console for CORS errors
- Verify API URL in `coastal-dashboard/src/services/api.js`

**❌ No data in dashboard**
```bash
cd coastal_backend
python manage.py seed_data
```

**❌ ML predictions not working**
- Check if model file exists in `ml_models/` directory
- Run `python create_dummy_model.py` to create a test model
- Verify model format matches expected interface

## 📈 Monitoring & Maintenance

### System Health
- **Health Check**: `GET /api/health/`
- **Admin Interface**: Monitor system status via Django admin
- **Logs**: Check Django and Celery logs for issues

### Data Management
- **Cleanup**: Old data is automatically cleaned up via scheduled tasks
- **Backup**: Regular database backups recommended for production
- **Monitoring**: Set up alerting for system failures

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make your changes**
4. **Test thoroughly**: Run both frontend and backend tests
5. **Submit a pull request**

### Development Guidelines
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation for API changes
- Ensure CORS and security considerations

## 📄 License

[Add your license information here]

## 👥 Team

[Add team member information here]

## 🆘 Support

For help and support:
1. Check the [Integration Guide](INTEGRATION_GUIDE.md) for detailed setup instructions
2. Review API documentation in the backend README
3. Check existing issues in the repository
4. Create a new issue with detailed error information

## 🔗 Related Documentation

- **[Integration Guide](INTEGRATION_GUIDE.md)**: Detailed setup and integration instructions
- **[Backend README](coastal_backend/README.md)**: Backend-specific documentation
- **[Frontend README](coastal-dashboard/README.md)**: Frontend-specific documentation

---

**🌊 Built for coastal safety and environmental monitoring**

[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org/)
[![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
