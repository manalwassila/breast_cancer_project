from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="staff")  # 'staff' or 'doctor'
    
    analyses = relationship("Analysis", back_populates="doctor")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    date_of_birth = Column(String) # YYYY-MM-DD
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    analyses = relationship("Analysis", back_populates="patient")

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    image_path = Column(String)
    ai_result = Column(String) # High Risk / Low Risk
    probability = Column(Float)
    
    doctor_decision = Column(String, nullable=True)
    doctor_result = Column(String, nullable=True)  # Final result if corrected: 'High Risk' or 'Low Risk'
    status = Column(String, default="Pending") # Pending, Confirmed, Corrected
    doctor_notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    doctor = relationship("User", back_populates="analyses")
    patient = relationship("Patient", back_populates="analyses")

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    subject = Column(String)
    message = Column(String)
    admin_reply = Column(String, nullable=True)
    status = Column(String, default="open") # open, closed
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="tickets")

# Add relationship back to User
User.tickets = relationship("SupportTicket", back_populates="user")
