# WeatherPro - Weather Analysis Application

## Overview
WeatherPro is a full-stack weather analysis application that provides weather probability analysis, trip planning, and AI-powered recommendations. The application analyzes historical weather patterns to help users make informed decisions about their outdoor activities and travel plans.

## Recent Changes
- **2025-10-05**: Initial Replit setup completed
  - Configured frontend to run on port 5000 with Vite (host: 0.0.0.0, allowedHosts: true)
  - Configured backend to run on port 8000 with FastAPI (host: 0.0.0.0)
  - Fixed database configuration to use SQLite (forced via Settings override)
  - Set up CORS for Replit proxy (allow all origins)
  - Added comprehensive .gitignore for Python and Node.js
  - Removed exposed API credentials from backend/.env (replaced with placeholders)
  - Configured VM deployment with both backend and frontend

## Project Architecture

### Technology Stack
- **Frontend**: React + TypeScript + Vite
  - UI Framework: Radix UI components
  - Styling: Tailwind CSS
  - State Management: TanStack Query
  - Routing: React Router v6
  
- **Backend**: Python FastAPI
  - Database: SQLite (SQLAlchemy ORM)
  - Authentication: JWT-based
  - Data Analysis: Pandas, NumPy, Matplotlib
  - Weather APIs: NASA, Meteomatics, Google Weather

### Project Structure
```
.
├── Frontend/           # React frontend application
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # API client and utilities
│   │   └── hooks/        # Custom React hooks
│   ├── public/          # Static assets
│   └── package.json
│
├── backend/            # FastAPI backend application
│   ├── app/
│   │   ├── api/routes/  # API endpoints
│   │   ├── core/        # Config and security
│   │   ├── db/          # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
│   ├── main.py         # Application entry point
│   ├── requirements.txt # Python dependencies
│   └── weather_app.db  # SQLite database
│
└── scripts/           # Utility scripts
```

### Key Features
1. **Weather Analysis**: Historical weather probability predictions
2. **Trip Management**: CRUD operations for trip planning
3. **AI Recommendations**: Smart location and date recommendations
4. **User Reports**: Community weather reports with photo uploads
5. **Data Export**: CSV, JSON, and calendar event exports
6. **Authentication**: Secure user authentication with JWT

## Development Setup

### Running Locally
The application is already configured to run in Replit:
- Frontend automatically starts on port 5000 (visible to users via Replit proxy)
- Backend runs on port 8000 (accessible via Replit domain)

To start the backend manually:
```bash
bash backend/start.sh
```

### Environment Variables
The backend uses the following environment variables (configured in `backend/.env`):
- `DATABASE_URL`: SQLite database path (set to sqlite:///./weather_app.db)
- `GOOGLE_WEATHER_API_KEY`: Google Weather API key
- `METEOMATICS_USERNAME`: Meteomatics API username
- `METEOMATICS_PASSWORD`: Meteomatics API password
- `SECRET_KEY`: JWT secret key (change in production)

The frontend uses:
- `VITE_API_BASE_URL`: Backend API URL (automatically set to Replit domain)

### Database
- The application uses SQLite for simplicity
- Database file: `backend/weather_app.db`
- Migrations are handled automatically on startup
- Pre-populated with sample data

### Deployment
The application is configured for VM deployment with:
- Build step: Builds the frontend static files
- Run step: Runs both backend (port 8000) and frontend preview (port 5000)

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Login and get access token
- `GET /auth/user` - Get current user info

### Weather
- `POST /api/weather-probability` - Analyze weather probability
- `GET /api/weather-history` - Get historical weather data

### Trips
- `GET /api/trips` - List user's trips
- `POST /api/trips` - Create new trip
- `PUT /api/trips/{id}` - Update trip
- `DELETE /api/trips/{id}` - Delete trip

### Other Endpoints
- Location search, recommendations, reports, profile management
- See `backend/README.md` for full API documentation

## User Preferences
- No specific user preferences configured yet

## Important Notes

### Security
- **API Keys Required**: Before running the application, you need to add your own API keys to `backend/.env`
  - Copy `backend/.env.example` to `backend/.env` if it doesn't exist
  - Add your Google Weather API key, Meteomatics credentials
  - Change the SECRET_KEY for JWT authentication

### Configuration
- The application uses Replit's proxy system, so the frontend is configured to allow all hosts
- Backend binds to 0.0.0.0 to allow Replit proxy access
- CORS is configured to allow all origins for development
- Database is forced to use SQLite (even if DATABASE_URL env var is set to PostgreSQL)
- LSP warnings about missing imports are expected (packages are installed via pip in .pythonlibs)
