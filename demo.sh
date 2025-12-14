#!/bin/bash

# Demo script for Calculator API with Authentication
# This script demonstrates the complete workflow

echo "========================================="
echo "Calculator API Demo"
echo "========================================="
echo ""

BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Register a new user${NC}"
echo "----------------------------------------"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "demo_password123"
  }')
echo "$REGISTER_RESPONSE" | python3 -m json.tool
echo ""

echo -e "${BLUE}Step 2: Login to get authentication token${NC}"
echo "----------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "demo_password123"
  }')
echo "$LOGIN_RESPONSE" | python3 -m json.tool

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")
echo ""
echo -e "${GREEN}Token obtained: ${TOKEN:0:50}...${NC}"
echo ""

echo -e "${BLUE}Step 3: Get current user info${NC}"
echo "----------------------------------------"
curl -s -X GET "$BASE_URL/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo -e "${BLUE}Step 4: Perform calculations${NC}"
echo "----------------------------------------"

echo -e "${YELLOW}4a. Addition: 5 + 3${NC}"
curl -s -X POST "$BASE_URL/calculator" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "operation": "add",
    "operand1": 5,
    "operand2": 3
  }' | python3 -m json.tool
echo ""

echo -e "${YELLOW}4b. Subtraction: 10 - 4${NC}"
curl -s -X POST "$BASE_URL/calculator" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "operation": "subtract",
    "operand1": 10,
    "operand2": 4
  }' | python3 -m json.tool
echo ""

echo -e "${YELLOW}4c. Multiplication: 6 × 7${NC}"
curl -s -X POST "$BASE_URL/calculator" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "operation": "multiply",
    "operand1": 6,
    "operand2": 7
  }' | python3 -m json.tool
echo ""

echo -e "${YELLOW}4d. Division: 15 ÷ 3${NC}"
curl -s -X POST "$BASE_URL/calculator" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "operation": "divide",
    "operand1": 15,
    "operand2": 3
  }' | python3 -m json.tool
echo ""

echo -e "${BLUE}Step 5: View calculation history${NC}"
echo "----------------------------------------"
curl -s -X GET "$BASE_URL/calculator/history" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo -e "${BLUE}Step 6: Test error handling (divide by zero)${NC}"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/calculator" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "operation": "divide",
    "operand1": 10,
    "operand2": 0
  }' | python3 -m json.tool
echo ""

echo -e "${BLUE}Step 7: Test authentication requirement${NC}"
echo "----------------------------------------"
echo "Trying to calculate without token:"
curl -s -X POST "$BASE_URL/calculator" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "add",
    "operand1": 1,
    "operand2": 1
  }' | python3 -m json.tool
echo ""

echo -e "${GREEN}Demo completed!${NC}"
echo ""
echo "========================================="
echo "Visit http://localhost:8000/docs for interactive API documentation"
echo "========================================="
