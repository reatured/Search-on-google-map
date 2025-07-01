from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class SearchHistory(Base):
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True)
    location = Column(String(255), nullable=False)
    search_timestamp = Column(DateTime, default=datetime.utcnow)
    user_ip = Column(String(45))
    search_status = Column(String(50))
    store_count = Column(Integer)
    response_time_ms = Column(Integer)
    
    stores = relationship("Store", back_populates="search")

class Store(Base):
    __tablename__ = 'stores'
    
    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, ForeignKey('search_history.id'))
    name = Column(String(255), nullable=False)
    address = Column(Text)
    website = Column(String(500))
    phone = Column(String(50))
    place_id = Column(String(255), unique=True)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    search = relationship("SearchHistory", back_populates="stores")

class LocationCache(Base):
    __tablename__ = 'location_cache'
    
    location_hash = Column(String(64), primary_key=True)
    location = Column(String(255), nullable=False)
    results = Column(JSON)
    cached_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)