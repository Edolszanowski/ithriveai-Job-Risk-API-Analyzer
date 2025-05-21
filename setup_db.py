import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, text
import datetime

# Get database URL from environment and fix format if needed
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    # Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
    database_url = database_url.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database...")

# Create database engine
engine = create_engine(database_url if database_url else "")

# Create metadata object
metadata = MetaData()

# Define job_searches table
job_searches = Table(
    'job_searches',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('job_title', String(255), nullable=False),
    Column('timestamp', DateTime, default=datetime.datetime.utcnow),
    Column('year_1_risk', Float),
    Column('year_5_risk', Float),
    Column('risk_category', String(50)),
    Column('job_category', String(50))
)

# Create the table in the database
try:
    metadata.create_all(engine)
    print("Database tables created successfully!")
    
    # Check if the table exists and has the right structure
    with engine.connect() as conn:
        result = conn.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'job_searches'")
        print("\nTable structure:")
        for row in result:
            print(f"Column: {row[0]}, Type: {row[1]}")
            
except Exception as e:
    print(f"Error setting up database: {str(e)}")