"""Database initialization script."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import init_db
from app.utils.logger import app_logger


def main():
    """Initialize database tables."""
    try:
        app_logger.info("Initializing database...")
        init_db()
        app_logger.info("✅ Database initialized successfully!")
        app_logger.info("Tables created: leads")
        
    except Exception as e:
        app_logger.error(f"❌ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
