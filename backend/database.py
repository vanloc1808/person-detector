# postgresql://postgres:[YOUR-PASSWORD]@db.nnhtuhibplvgylzycswg.supabase.co:5432/postgres
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.nnhtuhibplvgylzycswg.supabase.co:5432/postgres"  # Replace with your database URL
DB_HOST = "aws-0-ap-southeast-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.nnhtuhibplvgylzycswg"
DB_PASSWORD = "1234"

# Create engine and session
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()