#!/bin/bash

# Script de Verificação de Qualidade antes de PRs/Commits
# Este script roda todas as checagens de qualidade do projeto

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  SaaS Platform - Quality Checks${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Function to print success
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print section
section() {
    echo ""
    echo -e "${YELLOW}━━━ $1 ━━━${NC}"
}

# Track if any checks failed
FAILED=0

# ========================================
# BACKEND CHECKS
# ========================================
section "Backend Checks"

cd backend

echo "→ Running Ruff linter..."
if poetry run ruff check .; then
    success "Ruff linter passed"
else
    error "Ruff linter failed"
    FAILED=1
fi

echo ""
echo "→ Running Black formatter check..."
if poetry run black --check .; then
    success "Black formatter check passed"
else
    error "Black formatter check failed (run 'poetry run black .' to fix)"
    FAILED=1
fi

echo ""
echo "→ Running MyPy type checker..."
if poetry run mypy app/; then
    success "MyPy type checker passed"
else
    error "MyPy type checker failed"
    FAILED=1
fi

echo ""
echo "→ Testing if backend imports work..."
if poetry run python -c "from app.main import app; print('✓ Backend imports successfully')"; then
    success "Backend imports work"
else
    error "Backend has import errors"
    FAILED=1
fi

cd ..

# ========================================
# FRONTEND CHECKS
# ========================================
section "Frontend Checks"

cd frontend

echo "→ Running ESLint..."
if npm run lint; then
    success "ESLint passed"
else
    error "ESLint failed"
    FAILED=1
fi

echo ""
echo "→ Running TypeScript type check..."
if npm run type-check; then
    success "TypeScript type check passed"
else
    error "TypeScript type check failed"
    FAILED=1
fi

echo ""
echo "→ Running frontend build..."
if npm run build; then
    success "Frontend build passed"
else
    error "Frontend build failed"
    FAILED=1
fi

cd ..

# ========================================
# SUMMARY
# ========================================
echo ""
section "Summary"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}    ✓ ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}    Your code is ready to commit/PR${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}    ✗ SOME CHECKS FAILED${NC}"
    echo -e "${RED}    Please fix the errors before committing${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
