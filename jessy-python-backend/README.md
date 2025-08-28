# Jessy AI Backend

A comprehensive FastAPI backend for the Jessy AI assistant with voice capabilities, authentication, and AI chat features.

## Features

- 🔐 **Authentication System**: JWT-based auth with email verification and password reset
- 🗣️ **Voice Processing**: Speech-to-text with AssemblyAI and text-to-speech with Piper
- 🤖 **AI Chat**: Integration with Google Gemini for intelligent conversations
- 🛡️ **Security**: Rate limiting, CORS, token blacklisting, and comprehensive error handling
- 📧 **Email Service**: Email verification and password reset notifications
- 🗄️ **Database**: PostgreSQL with SQLAlchemy ORM and async support

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Redis (optional, for rate limiting)

## Installation

1. **Clone and navigate to the project**:
   ```bash
   cd jessy-ai-backend/jessy-python-backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Database Configuration
   DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/jessy_db
   
   # JWT Configuration
   JWT_SECRET=your_very_secure_jwt_secret_key_here
   
   # Redis Configuration (optional)
   REDIS_URL=redis://localhost:6379
   
   # Email Configuration
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   SMTP_FROM_EMAIL=your_email@gmail.com
   
   # AI Services Configuration
   GEMINI_API_KEY=your_gemini_api_key_here
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
   
   # CORS Configuration
   ENVIRONMENT=development
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

5. **Initialize the database**:
   ```bash
   python src/database_init.py
   ```

6. **Run the server**:
   ```bash
   python run.py
   ```

The server will start on `http://localhost:8003`

## API Documentation

Once the server is running, you can access:
- **API Documentation**: http://localhost:8003/docs
- **ReDoc Documentation**: http://localhost:8003/redoc
- **Health Check**: http://localhost:8003/health

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `POST /auth/verify-email` - Email verification
- `POST /auth/logout` - User logout
- `POST /auth/request-password-reset` - Request password reset
- `POST /auth/reset-password` - Reset password

### AI Chat
- `POST /ai/chat` - Chat with AI (with optional voice)
- `POST /ai/chat/text-only` - Text-only chat
- `GET /ai/chat/voice-simple` - Simple voice chat

### Voice Processing
- `POST /stt/transcribe` - Speech-to-text transcription
- `POST /voice/chat` - Complete voice chat pipeline

## Project Structure

```
src/
├── app.py                  # FastAPI application setup
├── config/                 # Configuration modules
│   ├── database.py        # Database configuration
│   └── cors.py            # CORS configuration
├── controllers/           # Business logic controllers
│   ├── auth_controller.py
│   ├── ai_chat_controller.py
│   └── voice_chat_controller.py
├── middlewares/           # Custom middleware
│   ├── auth_middleware.py
│   ├── error_handler.py
│   └── rate_limit.py
├── models/               # Database models
│   ├── user.py
│   ├── token_blacklist.py
│   └── auth_models.py
├── routes/               # API route definitions
│   ├── auth.py
│   ├── ai_chat.py
│   ├── stt.py
│   └── voice_chat.py
├── utils/                # Utility services
│   ├── jwt.py
│   ├── email_service.py
│   ├── otp_service.py
│   ├── stt_service.py
│   ├── gemini_service.py
│   └── piper_service.py
└── constants/
    └── prompt.py         # AI system prompts
```

## Development

1. **Database Management**:
   ```bash
   # Create tables
   python src/database_init.py
   
   # Drop all tables (careful!)
   python src/database_init.py drop
   ```

2. **Running in Development**:
   ```bash
   # With auto-reload
   python run.py
   
   # Or with uvicorn directly
   uvicorn src.app:app --host localhost --port 8003 --reload
   ```

## Security Features

- JWT tokens with refresh token rotation
- Token blacklisting for logout/revocation
- Rate limiting per IP and endpoint
- CORS protection
- Request validation
- Comprehensive error handling
- Secure password hashing with bcrypt

## Dependencies

See `requirements.txt` for the complete list of dependencies.

## Environment Variables

All configuration is done through environment variables. See the `.env.example` file for a complete list of required variables.

## Troubleshooting

1. **Database Connection Issues**: Ensure PostgreSQL is running and the DATABASE_URL is correct
2. **Redis Connection**: Redis is optional but recommended for rate limiting
3. **AI Services**: Ensure API keys are valid for Gemini and AssemblyAI
4. **Email Service**: Configure SMTP settings for email verification to work

## License

Private project - All rights reserved.
