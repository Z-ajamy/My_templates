# ==============================================================================
# Environment Configuration Template (.env)
# 
# Instructions:
# 1. Do not commit this file to version control (ensure it is in .gitignore).
# 2. String values do not require quotes unless they contain spaces or special characters.
# 3. Pydantic-Settings will automatically cast types (e.g., 'true' -> True, '5000' -> 5000).
# ==============================================================================

# --- Application State ---
# Accepted values: development, testing, staging, production
ENVIRONMENT=development
# Enables detailed error traces and hot-reloading (must be false in production)
DEBUG=true

# --- Server Configuration ---
HOST=0.0.0.0
# Port must be between 1024 and 65535
PORT=5000

# --- Database Connections ---
# Format: dialect+driver://username:password@host:port/database_name
# Example for PostgreSQL via psycopg2: postgresql+psycopg2://user:pass@localhost:5432/mydb
DATABASE_URL=postgresql://db_user:db_password@localhost:5432/development_db

# Redis connection string (optional in local dev, uncomment if needed)
# REDIS_URL=redis://localhost:6379/0

# Database Pooling Limits (Optional overrides)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# --- Security & Authentication ---
# Generate a secure key (e.g., via `openssl rand -hex 32`)
SECRET_KEY=replace_this_with_a_secure_random_string_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# --- External Services ---
# External API endpoints and configurations
EXTERNAL_API_BASE_URL=https://api.example.com/v1
API_TIMEOUT_SECONDS=10.0
