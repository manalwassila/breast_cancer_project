from pydantic import BaseModel
from typing import Optional, List
import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str

class PatientCreate(PatientBase):
    pass

class AnalysisBase(BaseModel):
    image_path: str
    ai_result: str
    probability: float
    doctor_decision: Optional[str] = None
    doctor_result: Optional[str] = None
    status: str = "Pending"
    doctor_notes: Optional[str] = None

class AnalysisCreate(AnalysisBase):
    patient_id: int

class Analysis(AnalysisBase):
    id: int
    user_id: int
    patient_id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class Patient(PatientBase):
    id: int
    created_at: datetime.datetime
    analyses: List[Analysis] = []
    class Config:
        from_attributes = True

class SupportTicketBase(BaseModel):
    subject: str
    message: str

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicket(SupportTicketBase):
    id: int
    user_id: int
    admin_reply: Optional[str] = None
    status: str
    created_at: datetime.datetime
    class Config:
        from_attributes = True
