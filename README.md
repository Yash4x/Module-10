# Calculator API with User Authentication

A secure FastAPI calculator application with user authentication, JWT tokens, and calculation history tracking.

## 🚀 Features

### User Management
- User registration with email validation
- Secure password hashing with bcrypt
- JWT token-based authentication
- User profile management

### Calculator Operations
- **Addition**: Add two numbers
- **Subtraction**: Subtract two numbers
- **Multiplication**: Multiply two numbers
- **Division**: Divide two numbers (with zero-division protection)
- All operations require authentication
- Automatic calculation history tracking

### Calculation History
- View your calculation history
- Pagination support for large histories
- Clear history option
- Per-user isolation (users only see their own calculations)

### Production Ready
- PostgreSQL database with SQLAlchemy ORM
- Docker containerization
- Comprehensive test suite (40+ tests)
- CI/CD pipeline with GitHub Actions
- Automatic Docker Hub deployment
- Interactive API documentation (Swagger UI)

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional, for containerized deployment)

## 🏁 Quick Start

### Using Docker (Recommended)

```bash
# Start the application
docker-compose up --build

# Application will be available at:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Alternative docs: http://localhost:8000/redoc
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the application
uvicorn src.main:app --reload
```

## 🔐 Using the API

### 1. Register a User

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### 2. Login to Get Token

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use the Calculator

```bash
# Addition
curl -X POST http://localhost:8000/calculator \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "operation": "add",
    "operand1": 5,
    "operand2": 3
  }'

# Subtraction
curl -X POST http://localhost:8000/calculator \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "operation": "subtract",
    "operand1": 10,
    "operand2": 4
  }'

# Multiplication
curl -X POST http://localhost:8000/calculator \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "operation": "multiply",
    "operand1": 6,
    "operand2": 7
  }'

# Division
curl -X POST http://localhost:8000/calculator \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "operation": "divide",
    "operand1": 15,
    "operand2": 3
  }'
```

### 4. View Calculation History

```bash
# Get all history
curl http://localhost:8000/calculator/history \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get paginated history
curl "http://localhost:8000/calculator/history?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Clear History

```bash
curl -X DELETE http://localhost:8000/calculator/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📚 API Endpoints

### Authentication
- `POST /users` - Register a new user
- `POST /login` - Login and get JWT token
- `GET /me` - Get current user info (requires authentication)

### Calculator Operations (All require authentication)
- `POST /calculator` - Perform calculation
  - Operations: `add`, `subtract`, `multiply`, `divide`
  - Request body: `{"operation": "add", "operand1": 5, "operand2": 3}`
  - Returns: `{"operation": "add", "operand1": 5, "operand2": 3, "result": 8, "message": "..."}`

### Calculation History (Requires authentication)
- `GET /calculator/history` - Get calculation history
  - Query params: `skip` (default: 0), `limit` (default: 100)
- `DELETE /calculator/history` - Clear all calculation history

### User Management
- `GET /users/{id}` - Get user by ID
- `GET /users` - List all users
- `DELETE /users/{id}` - Delete user

**Interactive Documentation**: Visit http://localhost:8000/docs for Swagger UI

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_calculator_integration.py -v

# Run specific test class
pytest tests/test_calculator_integration.py::TestCalculatorEndpoints -v
```

### Test Coverage

The project includes 40+ tests:
- **Unit Tests** (11 tests)
  - Password hashing (6 tests)
  - Schema validation (5 tests)
  
- **Integration Tests - User Management** (14 tests)
  - User creation, retrieval, deletion
  - Error handling
  
- **Integration Tests - Calculator & Auth** (15+ tests)
  - Authentication endpoints
  - Calculator operations
  - Calculation history
  - User isolation

## 🏗️ Project Structure

```
is218-test1-Yash/
├── src/
│   ├── calculator/
│   │   ├── __init__.py
│   │   └── operations.py          # Core calculator functions
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   ├── models.py                   # SQLAlchemy User model
│   ├── calculation_model.py        # SQLAlchemy Calculation model
│   ├── schemas.py                  # Pydantic user schemas
│   ├── calculator_schemas.py       # Pydantic calculator schemas
│   ├── database.py                 # Database configuration
│   ├── security.py                 # Password hashing
│   └── auth.py                     # JWT authentication
├── tests/
│   ├── __init__.py
│   ├── test_unit.py               # Unit tests
│   ├── test_integration.py        # User management integration tests
│   ├── test_calculator_integration.py  # Calculator integration tests
│   └── test_operations.py         # Original calculator tests
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── README.md
```

## 🔧 Environment Variables

Create a `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Testing
TESTING=0  # Set to 1 for test mode
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

### Manual Docker Build

```bash
# Build image
docker build -t calculator-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  calculator-api
```

## 🚀 CI/CD Pipeline

The project includes a GitHub Actions workflow that:
1. Runs on every push and pull request
2. Sets up Python 3.11 environment
3. Installs dependencies
4. Runs PostgreSQL service for integration tests
5. Executes all tests
6. Builds Docker image
7. Pushes to Docker Hub (on main branch)

**Required GitHub Secrets:**
- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Your Docker Hub access token

## 📖 Development Guide

### Adding New Calculator Operations

1. Add function to `src/calculator/operations.py`
2. Update `src/main.py` calculate endpoint to handle new operation
3. Add tests to `tests/test_calculator_integration.py`

### Security Considerations

- JWT tokens expire after 30 minutes (configurable)
- Passwords are hashed with bcrypt
- Database passwords stored in environment variables
- HTTPS recommended for production
- SECRET_KEY must be changed in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📝 License

This project is for educational purposes as part of IS218.

## 🙋 Support

For issues or questions:
- Check the interactive docs at http://localhost:8000/docs
- Review test files for usage examples
- Open an issue on GitHub

---

**Built with**: FastAPI, SQLAlchemy, PostgreSQL, Docker, pytest
