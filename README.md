# SaaS Platform

A comprehensive SaaS platform that connects professionals with clients for project collaboration. Built with modern technologies and following clean architecture principles.

## 🚀 Features

- **User Management**: Professional and client profiles with authentication
- **Project Management**: Create, manage, and track projects
- **Proposal System**: Professionals can submit proposals for projects
- **AI-Powered Matching**: Intelligent project-professional matching
- **Review System**: Rating and review system for both parties
- **Real-time Notifications**: Kafka-based messaging system
- **Advanced Analytics**: Project insights and performance metrics

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI with Python 3.11+
- **Architecture**: Clean Architecture with Use Cases and Services
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT-based with role-based authorization
- **Messaging**: Kafka for event-driven architecture
- **Testing**: pytest with 80%+ coverage requirement
- **Code Quality**: Ruff for linting and formatting

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **UI Components**: Headless UI + Radix UI

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Poetry (Python package manager)
- Make (for automation)

## 🛠️ Quick Start

### Backend Setup

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment and install dependencies:**
```bash
make create-venv
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start database and Kafka:**
```bash
docker-compose up -d postgres kafka
```

5. **Run migrations:**
```bash
make migrate
```

6. **Start the development server:**
```bash
make dev
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
make test-file FILE=test_users.py
```

### Frontend Tests
```bash
# Run tests
npm run test

# Run with coverage
npm run test:coverage
```

## 🔧 Development Commands

### Backend Commands
```bash
# Code quality
make ruff          # Run ruff check and format
make ruff-check    # Only check
make ruff-fix      # Only fix

# Database
make migrate       # Run migrations
make migrate-up    # Upgrade to latest
make migrate-down  # Downgrade one step

# Development
make dev           # Start development server
make shell         # Open Python shell
```

### Frontend Commands
```bash
npm run dev        # Development server
npm run build      # Production build
npm run preview    # Preview production build
npm run lint       # Run ESLint
npm run type-check # Run TypeScript check
```

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - User logout

### Users
- `GET /users/me` - Get current user
- `PUT /users/me` - Update current user
- `GET /users/{user_id}` - Get user by ID

### Professionals
- `GET /professionals` - List professionals
- `GET /professionals/{id}` - Get professional details
- `PUT /professionals/{id}` - Update professional profile
- `POST /professionals/{id}/skills` - Add skill to professional

### Projects
- `GET /projects` - List projects
- `POST /projects` - Create project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Proposals
- `GET /projects/{id}/proposals` - List project proposals
- `POST /projects/{id}/proposals` - Submit proposal
- `PUT /proposals/{id}` - Update proposal
- `DELETE /proposals/{id}` - Delete proposal

### Reviews
- `GET /reviews` - List reviews
- `POST /reviews` - Create review
- `PUT /reviews/{id}` - Update review
- `DELETE /reviews/{id}` - Delete review

## 🗄️ Database Schema

The application uses PostgreSQL with the following main entities:

- **Users**: Base user information and authentication
- **ProfessionalProfiles**: Professional-specific data
- **ClientProfiles**: Client-specific data
- **Skills**: Available skills in the platform
- **ProfessionalSkills**: Skills associated with professionals
- **Projects**: Client-created projects
- **Proposals**: Professional proposals for projects
- **Reviews**: User reviews and ratings
- **AIAnalysis**: AI-powered matching analysis

## 🔐 Authentication & Authorization

The application uses JWT tokens for authentication with role-based authorization:

- **Professional**: Can create profiles, submit proposals, manage skills
- **Client**: Can create projects, manage proposals, give reviews
- **Admin**: Full system access

## 📈 Monitoring & Logging

- **Structured Logging**: JSON format with correlation IDs
- **Request Tracking**: Middleware for request tracing
- **Performance Monitoring**: Response time tracking
- **Error Tracking**: Centralized error handling

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Production build
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/saas_platform

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Redis (for caching)
REDIS_URL=redis://localhost:6379
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure coverage
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository. 