# FastAPI User Management System

A production-ready FastAPI application featuring secure user authentication, SQLAlchemy database integration, comprehensive testing, and automated CI/CD deployment.

## 🚀 Features

- **Secure User Management**: Create, read, and delete users with unique constraints
- **Password Security**: Bcrypt password hashing with verification
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Data Validation**: Pydantic schemas for request/response validation
- **Comprehensive Testing**: Unit and integration tests with pytest
- **CI/CD Pipeline**: Automated testing and Docker Hub deployment via GitHub Actions
- **Containerization**: Docker and Docker Compose for easy deployment

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional, for containerized deployment)

## 🛠️ Installation & Setup

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd is218-test1-Yash
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run with Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```
   
   The API will be available at `http://localhost:8000`

### Manual Database Setup

If running without Docker:

```bash
# Create PostgreSQL database
createdb fastapi_db

# Set DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db

# Run the application
uvicorn src.main:app --reload
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/test_unit.py -v
```

### Run Integration Tests Only
```bash
pytest tests/test_integration.py -v
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

View coverage report:
```bash
open htmlcov/index.html  # On macOS
# Or navigate to htmlcov/index.html in your browser
```

### Test Requirements

- **Unit tests** test individual components (password hashing, schema validation)
- **Integration tests** require a database connection and test complete workflows
- The test suite uses SQLite for integration tests to avoid database setup complexity

## 📚 API Documentation

Once the application is running, visit:
- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc

### API Endpoints

#### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check status

#### User Management
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user by ID
- `GET /users` - List all users (with pagination)
- `DELETE /users/{user_id}` - Delete a user

### Example API Usage

**Create a User:**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Get a User:**
```bash
curl "http://localhost:8000/users/1"
```

## 🐳 Docker

### Build Docker Image
```bash
docker build -t fastapi-user-management .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f web
```

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for automated testing and deployment:

### Workflow Steps
1. **Test**: Runs all tests with PostgreSQL service
2. **Lint**: Code quality checks with Black and isort
3. **Build & Push**: Builds and pushes Docker image to Docker Hub (on main branch)

### GitHub Secrets Required

Set these in your GitHub repository settings (Settings → Secrets and variables → Actions):

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password or access token

### Docker Hub Repository

The Docker image is automatically pushed to Docker Hub on successful builds:

**Docker Hub Link**: `https://hub.docker.com/r/<YOUR_DOCKER_USERNAME>/fastapi-user-management`

To pull and run the image:
```bash
docker pull <YOUR_DOCKER_USERNAME>/fastapi-user-management:latest
docker run -p 8000:8000 -e DATABASE_URL=<your-db-url> <YOUR_DOCKER_USERNAME>/fastapi-user-management:latest
```

## 🏗️ Project Structure

```
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions workflow
├── src/
│   ├── calculator/            # Original calculator module (legacy)
│   ├── main.py               # FastAPI application
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # Database configuration
│   └── security.py           # Password hashing utilities
├── tests/
│   ├── conftest.py           # Pytest configuration
│   ├── test_unit.py          # Unit tests
│   └── test_integration.py   # Integration tests
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Multi-container setup
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🔒 Security Features

- **Password Hashing**: Uses bcrypt via passlib for secure password storage
- **Unique Constraints**: Ensures username and email uniqueness at database level
- **Input Validation**: Pydantic schemas validate all input data
- **Password Requirements**: Minimum 8 characters enforced
- **No Password Exposure**: Password hashes never returned in API responses

## 🧰 Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Security**: Passlib (bcrypt)
- **Testing**: Pytest, HTTPx
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## 📝 Development

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Run linter
pylint src/
```

### Database Migrations (Future Enhancement)

For production deployments, consider using Alembic for database migrations:
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of an academic assignment for IS 218.

## 👤 Author

**Yash**

- GitHub: [@Yash1x](https://github.com/Yash1x)
- Docker Hub: `https://hub.docker.com/r/<YOUR_DOCKER_USERNAME>/fastapi-user-management`

## 🙏 Acknowledgments

- FastAPI documentation and community
- SQLAlchemy team
- Course instructor and teaching assistants
