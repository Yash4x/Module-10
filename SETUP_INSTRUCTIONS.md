# FastAPI User Management - Setup Instructions

## Project Overview

This is a complete FastAPI application with secure user management, featuring:
- SQLAlchemy User model with unique constraints
- Pydantic schemas for validation
- Bcrypt password hashing
- Comprehensive unit and integration tests
- Docker containerization
- CI/CD pipeline with GitHub Actions

## Local Development Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials if needed.

### 3. Running Locally (Without Docker)

Make sure PostgreSQL is installed and running, then:

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Running with Docker Compose (Recommended)

```bash
docker-compose up --build
```

This starts both the PostgreSQL database and the FastAPI application.

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only
```bash
pytest tests/test_unit.py -v
```

### Integration Tests Only
```bash
pytest tests/test_integration.py -v
```

### With Coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

View the HTML coverage report at `htmlcov/index.html`

## Docker Hub Deployment

### Building and Pushing Docker Image

```bash
# Build
docker build -t your-dockerhub-username/fastapi-user-management .

# Push
docker push your-dockerhub-username/fastapi-user-management
```

### GitHub Secrets Configuration

For automatic deployment via GitHub Actions, add these secrets in your repository:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password or access token

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automatically:

1. **On every push/PR:**
   - Runs all tests with PostgreSQL
   - Performs code quality checks (Black, isort)
   - Generates coverage reports

2. **On push to main/master:**
   - Builds Docker image
   - Pushes to Docker Hub with multiple tags:
     - `latest`
     - Branch name
     - Git SHA

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health status

### User Management
- `POST /users` - Create new user
- `GET /users/{user_id}` - Get user by ID
- `GET /users` - List all users (paginated)
- `DELETE /users/{user_id}` - Delete user

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
├── .github/workflows/
│   └── ci-cd.yml              # CI/CD pipeline
├── src/
│   ├── calculator/            # Legacy calculator module
│   ├── main.py               # FastAPI application
│   ├── models.py             # SQLAlchemy User model
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # Database configuration
│   └── security.py           # Password hashing
├── tests/
│   ├── test_unit.py          # Unit tests
│   ├── test_integration.py   # Integration tests
│   └── conftest.py           # Pytest configuration
├── Dockerfile                # Container image
├── docker-compose.yml        # Multi-container orchestration
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project configuration
└── README.md                # Documentation
```

## Key Features

### User Model (SQLAlchemy)
- `id`: Primary key
- `username`: Unique, indexed
- `email`: Unique, indexed, validated
- `password_hash`: Bcrypt hashed password
- `created_at`: Timestamp with timezone

### Security
- Passwords hashed using bcrypt
- Passwords never exposed in API responses
- Email validation via Pydantic
- Input validation for all fields

### Testing
- **Unit Tests**: Password hashing, schema validation
- **Integration Tests**: Full API workflow with SQLite
- **Coverage**: Comprehensive test coverage
- **CI**: Automated testing with PostgreSQL in GitHub Actions

## Troubleshooting

### Tests Failing
Make sure the `TESTING` environment variable is set:
```bash
TESTING=1 pytest
```

### Docker Build Issues
Clean up old containers and images:
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Database Connection Issues
Check PostgreSQL is running:
```bash
pg_isready -U postgres
```

## Next Steps

1. **Add Authentication**: Implement JWT tokens for API authentication
2. **Add User Login**: Create login endpoint with password verification
3. **Add Database Migrations**: Use Alembic for schema management
4. **Add More Endpoints**: Update user, change password, etc.
5. **Add Logging**: Implement structured logging
6. **Add Rate Limiting**: Protect endpoints from abuse

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Docker Hub Repository](https://hub.docker.com/r/YOUR_USERNAME/fastapi-user-management)
