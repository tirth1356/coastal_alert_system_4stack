from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from monitoring.models import CoastalLocation, SensorData
from ml_integration.models import MLModel


class Command(BaseCommand):
    help = 'Seed initial data for coastal monitoring system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--locations-only',
            action='store_true',
            help='Only create coastal locations without sensor data',
        )

    def handle(self, *args, **options):
        self.stdout.write('Seeding coastal monitoring data...')

        # Create coastal locations
        locations_data = [
            {
                'name': 'Miami Beach',
                'latitude': 25.7617,
                'longitude': -80.1918,
                'station_id': '8723214',
                'description': 'Popular beach location in Miami, Florida'
            },
            {
                'name': 'Virginia Beach',
                'latitude': 36.8529,
                'longitude': -75.9780,
                'station_id': '8638863',
                'description': 'Major beach resort city in Virginia'
            },
            {
                'name': 'Monterey Bay',
                'latitude': 36.6002,
                'longitude': -121.8947,
                'station_id': '9413450',
                'description': 'Marine sanctuary in California'
            },
            {
                'name': 'Charleston Harbor',
                'latitude': 32.7767,
                'longitude': -79.9311,
                'station_id': '8665530',
                'description': 'Historic harbor in South Carolina'
            },
            {
                'name': 'Key West',
                'latitude': 24.5551,
                'longitude': -81.8065,
                'station_id': '8724580',
                'description': 'Southernmost point in Florida Keys'
            }
        ]

        created_locations = []
        for location_data in locations_data:
            location, created = CoastalLocation.objects.get_or_create(
                station_id=location_data['station_id'],
                defaults=location_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created location: {location.name}')
                )
            else:
                self.stdout.write(f'Location already exists: {location.name}')
            created_locations.append(location)

        # Create ML Model record
        ml_model, created = MLModel.objects.get_or_create(
            name='Coastal Risk Predictor',
            version='1.0',
            defaults={
                'description': 'Machine learning model for predicting coastal risks',
                'model_file_path': 'ml_models/coastal_risk_model.pkl',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created ML model record')
            )

        if not options['locations_only']:
            # Create sample sensor data for the last 24 hours
            self.stdout.write('Creating sample sensor data...')
            
            measurement_types = [
                ('water_level', 'meters'),
                ('wave_height', 'meters'),
                ('wind_speed', 'm/s'),
                ('wind_direction', 'degrees'),
                ('air_pressure', 'mb'),
                ('water_temperature', 'celsius')
            ]

            for location in created_locations:
                # Create data for the last 24 hours (every hour)
                for hours_ago in range(24):
                    timestamp = timezone.now() - timedelta(hours=hours_ago)
                    
                    for measurement_type, unit in measurement_types:
                        # Generate realistic sample data
                        if measurement_type == 'water_level':
                            value = random.uniform(0.5, 3.0)
                        elif measurement_type == 'wave_height':
                            value = random.uniform(0.5, 4.0)
                        elif measurement_type == 'wind_speed':
                            value = random.uniform(2.0, 15.0)
                        elif measurement_type == 'wind_direction':
                            value = random.uniform(0, 360)
                        elif measurement_type == 'air_pressure':
                            value = random.uniform(1005, 1025)
                        elif measurement_type == 'water_temperature':
                            value = random.uniform(18.0, 28.0)
                        else:
                            value = random.uniform(0, 100)

                        SensorData.objects.create(
                            location=location,
                            measurement_type=measurement_type,
                            value=value,
                            unit=unit,
                            timestamp=timestamp,
                            data_source='sample_data'
                        )

            self.stdout.write(
                self.style.SUCCESS('Created sample sensor data for all locations')
            )

        self.stdout.write(
            self.style.SUCCESS('Data seeding completed successfully!')
        )
