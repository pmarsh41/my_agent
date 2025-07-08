# 🍽️ Smart Meal Analyzer
AI-powered food identification and protein tracking with realistic AI-assistance

## ✨ Features
- OpenAI Vision API for food identification
- Smart nutrition database with 40+ foods
- LangGraph workflows for structured AI processing
- React frontend with Material-UI
- Confidence-based food recognition
- Interactive portion adjustment
- Real-time protein calculations

## 🏗️ Architecture
- **Backend**: FastAPI + LangGraph + OpenAI Vision
- **Frontend**: React + TypeScript + Material-UI
- **AI Framework**: LangChain + LangGraph
- **Database**: SQLite with comprehensive nutrition data

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- OpenAI API key

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd my_agent

# Set up backend
cd backend
cp .env.example .env
# Edit .env with your OpenAI API key

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# In a new terminal, set up frontend
cd frontend
npm install
npm start
```

### Environment Variables
Copy `backend/.env.example` to `backend/.env` and configure:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ARIZE_SPACE_ID`: (Optional) Arize observability
- `ARIZE_API_KEY`: (Optional) Arize API key

## 🎯 Usage

### Core Workflow
1. **Upload Meal Photo**: Take a photo of your meal
2. **AI Analysis**: System identifies foods with confidence scores
3. **Portion Adjustment**: Review and adjust portion sizes
4. **Protein Calculation**: Get accurate protein estimates
5. **Track Progress**: Monitor daily protein intake

### Example API Usage
```bash
# Analyze a meal image
curl -X POST "http://localhost:8000/analyze-meal-smart/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@meal_photo.jpg" \
  -F "user_id=1"
```

## 🧠 AI Architecture
The system uses a 4-agent LangGraph workflow:
1. **Food ID Agent**: Analyzes images to identify foods with confidence scores
2. **DB Matching Agent**: Matches identified foods to nutrition database
3. **Portion Agent**: Suggests portion sizes based on visual cues
4. **Conversation Agent**: Generates natural language responses

## 🛠️ Development

## 📱 Usage

### Core Workflow
1. **Create User Profile**: Set up weight, activity level, and protein goals
2. **Upload Meal Photos**: Take photos of your meals
3. **AI Analysis**: System identifies foods and estimates protein content
4. **Track Progress**: View daily summaries and goal achievement
5. **Review History**: Analyze protein intake trends over time

### API Endpoints

#### New LangGraph-Powered Endpoints
- `POST /analyze-meal-ai/`: Advanced AI meal analysis with workflow tracing
- `POST /analyze-meal/`: Simple meal analysis (legacy compatibility)

#### User Management
- `POST /users/`: Create user profile
- `GET /users/{user_id}`: Get user details
- `PUT /users/{user_id}`: Update user profile

#### Meal Tracking
- `GET /users/{user_id}/meals`: Get user's meal history
- `GET /users/{user_id}/daily-summaries`: Get daily protein summaries

## 🔍 Observability

The system includes comprehensive observability through Arize Phoenix:
- **LLM Call Tracing**: Monitor OpenAI API usage and performance
- **Workflow Visualization**: See LangGraph execution paths
- **Error Tracking**: Detailed error logs and debugging information
- **Performance Metrics**: Response times and token usage analytics

## 🗄️ Data Models

### User
- Profile information (weight, age, activity level)
- Personalized protein goals
- Dietary preferences and restrictions

### Meal
- Image URL and analysis results
- Detected foods and protein estimates
- Automatic daily summary integration

### Daily Summary
- Total protein intake and goal progress
- Status tracking (on_track, met, missed)
- Historical trend analysis

## 🔒 Security

- Environment-based configuration for API keys
- No hardcoded credentials in source code
- CORS configuration for frontend-backend communication
- Input validation and error handling

## 🚢 Deployment

### Docker Production Deployment
```bash
docker-compose -f docker-compose.yml up -d
```

### Manual Deployment
1. Configure production environment variables
2. Build frontend: `cd frontend && npm run build`
3. Deploy backend with: `uvicorn main:app --host 0.0.0.0 --port 8000`

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Migration Notes

This project was migrated from Google Vision API to OpenAI Vision with LangGraph workflows for improved reliability and observability. The migration includes:

- ✅ Replaced Google Vision with OpenAI Vision API
- ✅ Implemented LangGraph workflows for structured AI processing
- ✅ Added Arize Phoenix observability
- ✅ Upgraded to React 19 with Material-UI
- ✅ Added Docker containerization
- ✅ Environment-based configuration

The original Google Vision implementation is backed up in `main_backup.py`.

## Project Structure

```
my_agent/
├── backend/
│   ├── main.py              # FastAPI + LangGraph application
│   ├── main_backup.py       # Original Google Vision implementation
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend container
│   └── .env.example         # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── App.tsx         # Main app component
│   │   └── index.tsx       # Entry point
│   ├── package.json        # Node.js dependencies (Material-UI)
│   └── Dockerfile          # Frontend container
├── docker-compose.yml      # Multi-service orchestration
├── start.sh               # Quick start script
└── README.md              # This file
```