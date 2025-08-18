# Database models for MCP Authorization Server
from sqlalchemy import create_engine, Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os

# Use SQLite database file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mcp_auth.db")
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuthCode(Base):
    __tablename__ = "auth_codes"
    
    code = Column(String, primary_key=True, index=True)
    client_id = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))
    used = Column(Boolean, default=False)
    # PKCE parameters
    code_challenge = Column(String, nullable=True)  # SHA256 hash of code_verifier
    code_challenge_method = Column(String, nullable=True)  # "S256" or "plain"
    # Resource binding (Step 11)
    resource = Column(String, nullable=True)

class AccessToken(Base):
    __tablename__ = "access_tokens"
    
    token = Column(String, primary_key=True, index=True)
    client_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
    # Resource binding (Step 11)
    resource = Column(String, nullable=True)

class Client(Base):
    __tablename__ = "clients"
    
    client_id = Column(String, primary_key=True, index=True)
    client_secret = Column(String, nullable=False)  # Added for Step 7
    client_name = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False)  # Single redirect URI (renamed from redirect_uris)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
