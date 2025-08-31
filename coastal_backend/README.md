# Coastal Alarm System - Django Backend

A Django-based backend system for monitoring coastal conditions and triggering alerts when unusual conditions are detected using machine learning predictions.

## Features

- **Real-time Data Ingestion**: Fetches coastal data from NOAA and USGS APIs
- **ML Integration**: Processes data through machine learning models to predict coastal risks
- **Alert System**: Automatically generates alerts when high-risk conditions are detected
- **REST API**: Comprehensive API for frontend integration
- **Background Processing**: Celery-based task queue for real-time data processing
- **Admin Interface**: Django admin for system management

## Project Structure

```
coastal_backend/
├── coastal_backend/          # Main Django project
├── monitoring/              # Core monitoring app
│   ├── models.py           # Data models (Location, SensorData, Alert, etc.)
│   ├── views.py            # API views and endpoints
│   ├── serializers.py      # DRF serializers
│   ├── services.py         # Data ingestion services
│   ├── tasks.py            # Celery background tasks
│   └── admin.py            # Django admin configuration
├── ml_integration/          # ML model integration
│   ├── models.py           # ML model tracking
│   ├── services.py         # ML prediction services
│   └── admin.py            # ML admin interface
├── ml_models/              # Directory for ML model files
└── requirements.txt        # Python dependencies
```

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Initial Data**:
   ```bash
   python manage.py seed_data
   ```

4. **Create Dummy ML Model** (for testing):
   ```bash
   python create_dummy_model.py
   ```

5. **Create Admin User**:
   ```bash
   python manage.py createsuperuser
   ```

## Running the System

### Quick Start
```bash
python start_system.py
```

### Manual Start
```bash
# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker (optional)
celery -A coastal_backend worker --loglevel=info

# In another terminal, start Celery beat for scheduled tasks (optional)
celery -A coastal_backend beat --loglevel=info
```

## API Endpoints

### Dashboard
- `GET /api/dashboard/` - Get dashboard overview data

### Locations
- `GET /api/locations/` - List all coastal locations
- `POST /api/locations/` - Create new location
- `GET /api/locations/{id}/` - Get location details
- `POST /api/locations/{id}/run_prediction/` - Trigger ML prediction
- `GET /api/locations/{id}/sensor_data/` - Get sensor data for location

### Sensor Data
- `GET /api/sensor-data/` - List sensor data (filterable)
- `POST /api/sensor-data/` - Add new sensor data
- Query parameters: `location`, `measurement_type`, `hours`

### Risk Assessments
- `GET /api/risk-assessments/` - List risk assessments (read-only)
- Query parameters: `location`, `risk_level`, `hours`

### Alerts
- `GET /api/alerts/` - List alerts (filterable)
- `POST /api/alerts/{id}/resolve/` - Resolve an alert
- `GET /api/alerts/active/` - Get active alerts only
- Query parameters: `status`, `severity`, `location`

### System
- `GET /api/health/` - Health check endpoint
- `POST /api/ingest-data/` - Trigger manual data ingestion

## Data Models

### CoastalLocation
- Represents monitoring locations with coordinates and station IDs
- Links to NOAA/USGS station identifiers

### SensorData
- Stores real-time measurements (water level, waves, wind, etc.)
- Timestamps and data source tracking
- Data validation and quality flags

### RiskAssessment
- ML model predictions and risk scores
- Links to input data and model versions
- Risk levels: low, medium, high, critical

### Alert
- Automated alerts based on risk assessments
- Different alert types (flooding, storms, etc.)
- Status tracking (active, resolved, dismissed)

## ML Model Integration

### Your Model Requirements
Your ML model should:
1. Accept pandas DataFrame with these columns:
   - `water_level`, `wave_height`, `wind_speed`, `wind_direction`
   - `air_pressure`, `water_temperature`, `hour_of_day`, `day_of_year`

2. Have a `predict_proba()` method returning risk probabilities
3. Be saved as a pickle/joblib file

### Adding Your Model
1. Save your trained model as `ml_models/coastal_risk_model.pkl`
2. Or register it via Django admin interface
3. The system will automatically load and use it

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:
- API keys for NOAA and USGS
- Database settings
- Redis configuration
- Alert thresholds

### External APIs
The system integrates with:
- **NOAA Tides and Currents API**: Water levels, meteorological data
- **USGS Water Services**: Water level and discharge data

## Background Tasks

### Celery Tasks
- `ingest_coastal_data`: Fetch latest data from APIs
- `run_risk_predictions`: Generate ML predictions
- `cleanup_old_data`: Remove old records
- `check_system_health`: Monitor system status

### Scheduled Tasks
Add to your Celery beat schedule:
```python
CELERY_BEAT_SCHEDULE = {
    'ingest-data-every-15-minutes': {
        'task': 'monitoring.tasks.ingest_coastal_data',
        'schedule': 15.0 * 60,  # 15 minutes
    },
    'run-predictions-every-30-minutes': {
        'task': 'monitoring.tasks.run_risk_predictions',
        'schedule': 30.0 * 60,  # 30 minutes
    },
}
```

## Frontend Integration

The API is designed to work with your coastal dashboard frontend. Key endpoints for frontend:

1. **Dashboard Data**: `GET /api/dashboard/`
2. **Location List**: `GET /api/locations/`
3. **Active Alerts**: `GET /api/alerts/active/`
4. **Real-time Data**: `GET /api/sensor-data/?hours=1`

### CORS Configuration
CORS is configured to allow requests from `localhost:3000` (React development server).

## Development Workflow

1. **Add New Locations**: Use Django admin or API
2. **Test Data Ingestion**: `POST /api/ingest-data/`
3. **Monitor Predictions**: Check `/api/risk-assessments/`
4. **View Alerts**: Check `/api/alerts/`
5. **System Health**: Monitor `/api/health/`

## Production Deployment

For production deployment:
1. Set `DEBUG=False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up Redis for Celery
4. Configure proper secret keys
5. Set up web server (nginx + gunicorn)
6. Configure monitoring and logging

## API Examples

### Get Dashboard Data
```bash
curl http://localhost:8000/api/dashboard/
```

### Get Locations with Risk Data
```bash
curl http://localhost:8000/api/locations/
```

### Add Sensor Data
```bash
curl -X POST http://localhost:8000/api/sensor-data/ \
  -H "Content-Type: application/json" \
  -d '{
    "location": 1,
    "measurement_type": "water_level",
    "value": 2.5,
    "unit": "meters",
    "timestamp": "2025-08-30T16:00:00Z",
    "data_source": "manual"
  }'
```

### Trigger Prediction
```bash
curl -X POST http://localhost:8000/api/locations/1/run_prediction/
```

## Troubleshooting

### Common Issues

1. **No Predictions Generated**: Check if ML model file exists in `ml_models/`
2. **API Errors**: Verify NOAA/USGS API keys in `.env` file
3. **No Data**: Run `python manage.py seed_data` to create sample data

### Logs
Check Django logs for detailed error information:
```bash
python manage.py runserver --verbosity=2
```

## Support

For issues or questions:
1. Check the Django admin interface for system status
2. Review API endpoint documentation
3. Check Celery task logs for background processing issues
