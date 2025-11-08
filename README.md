# Intelligent Workflow Automation Platform

An AI-powered backend system designed to automate repetitive business workflows through intelligent decision-making and rule engines.

## 🚀 Features

- **Workflow Management**: Create, manage, and execute automated workflows
- **AI-Powered Optimization**: Machine learning models predict optimal execution times
- **Task Scheduling**: Celery-based scheduling for time-based automation
- **External Integrations**: Connect with email, cloud storage, CRM, and more
- **Real-time Monitoring**: Track workflow execution and performance metrics
- **RESTful API**: Comprehensive API built with FastAPI

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Task Queue**: Celery with Redis
- **ML**: scikit-learn
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development without Docker)
- Git

## 🔧 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd -Intelligent-Workflow-Automation-Platform
```

### 2. Environment Configuration

Copy the example environment file and update as needed:

```bash
cp .env.example .env
```

Edit `.env` and update the `SECRET_KEY` and other settings if needed.

### 3. Start with Docker Compose

```bash
cd docker
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis (port 6379)
- FastAPI application (port 8000)
- Celery worker
- Flower (Celery monitoring, port 5555)

### 4. Verify Installation

Check if all services are running:

```bash
docker-compose ps
```

Access the API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Flower (Celery)**: http://localhost:5555

Health check:
```bash
curl http://localhost:8000/health
```

### 5. Run Database Migrations

```bash
# Enter the API container
docker-compose exec api bash

# Run Alembic migrations
alembic upgrade head

# (Optional) Seed sample data
python scripts/seed_data.py
```

## 💻 Local Development (Without Docker)

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Local Services

You'll need PostgreSQL and Redis running locally. Update `.env` with local connection strings:

```env
DATABASE_URL=postgresql+asyncpg://workflow_user:workflow_pass@localhost:5432/workflow_db
DATABASE_SYNC_URL=postgresql://workflow_user:workflow_pass@localhost:5432/workflow_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the Application

```bash
# Terminal 1: Start FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Celery Worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3 (Optional): Start Flower
celery -A app.workers.celery_app flower --port=5555
```

## 📁 Project Structure

```
intelligent-workflow-platform/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core functionality (database, cache, logging)
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── workers/         # Celery tasks
│   ├── ml/              # Machine learning models
│   ├── integrations/    # External service integrations
│   └── utils/           # Utility functions
├── tests/               # Test suites
├── migrations/          # Alembic migrations
├── docker/              # Docker configuration
├── scripts/             # Utility scripts
└── docs/                # Documentation
```

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_workflows.py
```

## 📊 API Endpoints

### Health Check
- `GET /health` - Health status

### Workflows (Coming in Phase 2)
- `POST /api/v1/workflows` - Create workflow
- `GET /api/v1/workflows` - List workflows
- `GET /api/v1/workflows/{id}` - Get workflow details
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow
- `POST /api/v1/workflows/{id}/execute` - Execute workflow

Full API documentation available at `/docs` when running.

## 🔐 Security

- Environment variables for sensitive configuration
- Password hashing with bcrypt
- JWT-based authentication (Phase 7)
- CORS configuration
- Input validation with Pydantic

## 📈 Monitoring

- **Flower**: Monitor Celery tasks at http://localhost:5555
- **Logs**: Available in `logs/` directory
- **Health Check**: `/health` endpoint

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db
```

### Celery Worker Not Processing Tasks

```bash
# Check worker status
docker-compose ps worker

# View worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## 🚧 Development Roadmap

- [x] **Phase 1**: Project Foundation & Setup ← **Current Phase**
- [ ] **Phase 2**: Core Workflow Management
- [ ] **Phase 3**: Advanced Scheduling & Automation
- [ ] **Phase 4**: Machine Learning Integration
- [ ] **Phase 5**: External Integrations
- [ ] **Phase 6**: Monitoring & Analytics
- [ ] **Phase 7**: Security & Performance
- [ ] **Phase 8**: Testing & Documentation
- [ ] **Phase 9**: Deployment & DevOps
- [ ] **Phase 10**: Advanced Features & Optimization

See [plan.md](plan.md) for detailed roadmap.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Celery for distributed task processing
- SQLAlchemy for database ORM

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Contact: your-email@example.com

---

**Happy Automating! 🎉**