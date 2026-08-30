import pytest
from sqlalchemy import text
from app.db.session import engine
from app.db.redis import ping_redis

def test_database_connectivity():
    """Test that the application can connect to PostgreSQL."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

def test_pgvector_extension():
    """Test that the pgvector extension is available in PostgreSQL."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            ).scalar()
            assert result == 'vector', "pgvector extension is not enabled"
    except Exception as e:
        pytest.fail(f"Querying pg_extension failed: {e}")

def test_redis_connectivity():
    """Test that the application can connect to Redis."""
    assert ping_redis() is True, "Redis ping failed"
