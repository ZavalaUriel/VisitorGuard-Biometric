from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    purpose = Column(String(255))
    host_name = Column(String(100))
    location = Column(String(100))
    
    check_in = Column(DateTime, default=datetime.utcnow)
    check_out = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    
    verification_photo = Column(String(255))
    verification_score = Column(String(10))
    is_verified = Column(Boolean, default=False)
    
    notes = Column(Text)
    # Metadatos
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="visits")_id}, check_in={self.check_in})>"