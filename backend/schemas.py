from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class PatientCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(default="", max_length=80)
    phone: str = Field(min_length=3, max_length=30)
    email: Optional[EmailStr] = None
    preferred_language: str = "English"
    date_of_birth: Optional[str] = None
    notes: Optional[str] = None


class PatientOut(PatientCreate):
    id: int
    patient_number: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    specialization: str = Field(min_length=1, max_length=120)
    phone: Optional[str] = None


class DoctorOut(DoctorCreate):
    id: int
    active: bool

    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: str


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str]
    status: str

    model_config = ConfigDict(from_attributes=True)


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class AIChatResponse(BaseModel):
    reply: str


class CallCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    purpose: str = "Appointment reminder"


class CallOut(BaseModel):
    id: int
    patient_id: Optional[int]
    appointment_id: Optional[int]
    phone: Optional[str]
    direction: str
    status: str
    purpose: Optional[str]
    provider_call_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)
