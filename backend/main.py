import os
from datetime import datetime, timedelta
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from twilio.rest import Client

from ai_service import chat_response
from database import Base, engine, get_db
from models import Appointment, AuditLog, CallLog, Doctor, Patient, User
from schemas import (
    AIChatRequest,
    AIChatResponse,
    AppointmentCreate,
    AppointmentOut,
    AppointmentStatusUpdate,
    CallCreate,
    CallOut,
    DoctorCreate,
    DoctorOut,
    LoginRequest,
    PatientCreate,
    PatientOut,
    UserOut,
)
from security import create_access_token, decode_token, hash_password, verify_password

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MediCall AI Clinic API",
    version="2.0.0",
    description="Clinic operations API with patient, appointment, communication and AI-assistance modules.",
)

origins = [
    item.strip()
    for item in os.getenv("CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",")
    if item.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    user = db.get(User, user_id)
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="User account is inactive.")

    return user


def audit(db, user, action, resource=None, resource_id=None, details=None):
    db.add(
        AuditLog(
            user_id=user.id if user else None,
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id is not None else None,
            details=details,
        )
    )


def ensure_admin_user(db: Session):
    email = os.getenv("ADMIN_EMAIL", "admin@medicall.com").lower()
    password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
    user = db.query(User).filter(func.lower(User.email) == email).first()

    if not user:
        user = User(
            email=email,
            full_name=os.getenv("ADMIN_NAME", "Clinic Administrator"),
            password_hash=hash_password(password),
            role="ADMIN",
            active=True,
        )
        db.add(user)
        db.commit()


@app.on_event("startup")
def startup():
    db = next(get_db())
    try:
        ensure_admin_user(db)
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "service": "MediCall AI Clinic API",
        "version": "2.0.0",
        "status": "ok",
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(func.count(User.id).select())
    return {"status": "healthy", "database": "connected"}


@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == payload.email.lower()).first()

    if not user or not user.active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": UserOut.model_validate(user).model_dump(),
    }


@app.get("/auth/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user


@app.get("/dashboard/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    patients = db.query(Patient).filter(Patient.status == "ACTIVE").count()

    appointments_today = (
        db.query(Appointment)
        .filter(
            Appointment.appointment_date >= datetime.combine(today, datetime.min.time()),
            Appointment.appointment_date < datetime.combine(tomorrow, datetime.min.time()),
        )
        .count()
    )

    confirmed = db.query(Appointment).filter(Appointment.status == "CONFIRMED").count()
    pending = db.query(Appointment).filter(Appointment.status == "SCHEDULED").count()
    completed_calls = db.query(CallLog).filter(CallLog.status == "COMPLETED").count()
    missed_calls = db.query(CallLog).filter(CallLog.status == "MISSED").count()

    return {
        "patients": patients,
        "appointments_today": appointments_today,
        "confirmed": confirmed,
        "pending": pending,
        "completed_calls": completed_calls,
        "missed_calls": missed_calls,
    }


@app.get("/patients", response_model=list[PatientOut])
def list_patients(
    search: str = Query("", max_length=100),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    query = db.query(Patient).order_by(Patient.created_at.desc())

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(pattern),
                Patient.last_name.ilike(pattern),
                Patient.phone.ilike(pattern),
                Patient.patient_number.ilike(pattern),
            )
        )

    return query.all()


@app.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    return patient


@app.post("/patients", response_model=PatientOut)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_number = f"MC-{datetime.now():%Y%m%d}-{uuid4().hex[:6].upper()}"

    patient = Patient(
        patient_number=patient_number,
        **payload.model_dump(),
    )

    db.add(patient)
    db.flush()
    audit(db, user, "CREATE", "patient", patient.id)
    db.commit()
    db.refresh(patient)

    return patient


@app.patch("/patients/{patient_id}/archive")
def archive_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = db.get(Patient, patient_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")

    patient.status = "ARCHIVED"
    audit(db, user, "ARCHIVE", "patient", patient.id)
    db.commit()

    return {"message": "Patient archived."}


@app.get("/doctors", response_model=list[DoctorOut])
def list_doctors(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return db.query(Doctor).filter(Doctor.active.is_(True)).order_by(Doctor.name).all()


@app.post("/doctors", response_model=DoctorOut)
def create_doctor(
    payload: DoctorCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    doctor = Doctor(**payload.model_dump())
    db.add(doctor)
    db.flush()
    audit(db, user, "CREATE", "doctor", doctor.id)
    db.commit()
    db.refresh(doctor)

    return doctor


@app.get("/appointments", response_model=list[AppointmentOut])
def list_appointments(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return (
        db.query(Appointment)
        .order_by(Appointment.appointment_date.asc())
        .all()
    )


@app.post("/appointments", response_model=AppointmentOut)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = db.get(Patient, payload.patient_id)
    doctor = db.get(Doctor, payload.doctor_id)

    if not patient or patient.status != "ACTIVE":
        raise HTTPException(status_code=404, detail="Active patient not found.")

    if not doctor or not doctor.active:
        raise HTTPException(status_code=404, detail="Active doctor not found.")

    conflicting = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == payload.doctor_id,
            Appointment.appointment_date == payload.appointment_date,
            Appointment.status.in_(["SCHEDULED", "CONFIRMED"]),
        )
        .first()
    )

    if conflicting:
        raise HTTPException(
            status_code=409,
            detail="This doctor already has an appointment at that time.",
        )

    appointment = Appointment(
        **payload.model_dump(),
        status="SCHEDULED",
    )

    db.add(appointment)
    db.flush()
    audit(db, user, "CREATE", "appointment", appointment.id)
    db.commit()
    db.refresh(appointment)

    return appointment


@app.patch("/appointments/{appointment_id}/status", response_model=AppointmentOut)
def update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    allowed = {"SCHEDULED", "CONFIRMED", "COMPLETED", "CANCELLED", "NO_SHOW"}

    status = payload.status.upper()

    if status not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported appointment status.")

    appointment = db.get(Appointment, appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    appointment.status = status
    audit(db, user, "STATUS_UPDATE", "appointment", appointment.id, status)
    db.commit()
    db.refresh(appointment)

    return appointment


@app.post("/ai/chat", response_model=AIChatResponse)
def ai_chat(
    payload: AIChatRequest,
    user=Depends(current_user),
):
    return {"reply": chat_response(payload.message)}


@app.post("/calls", response_model=CallOut)
def create_call(
    payload: CallCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = db.get(Patient, payload.patient_id)

    if not patient or patient.status != "ACTIVE":
        raise HTTPException(status_code=404, detail="Active patient not found.")

    appointment = None

    if payload.appointment_id:
        appointment = db.get(Appointment, payload.appointment_id)

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found.")

    call = CallLog(
        patient_id=patient.id,
        appointment_id=appointment.id if appointment else None,
        phone=patient.phone,
        purpose=payload.purpose,
        status="QUEUED",
    )

    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_number = os.getenv("TWILIO_PHONE", "").strip()
    twiml_url = os.getenv("TWILIO_TWIML_URL", "").strip()

    if sid and token and from_number and twiml_url:
        try:
            client = Client(sid, token)
            twilio_call = client.calls.create(
                to=patient.phone,
                from_=from_number,
                url=twiml_url,
            )
            call.provider_call_id = twilio_call.sid
            call.status = "QUEUED"
        except Exception as exc:
            call.status = "FAILED"
            call.notes = f"Telephony provider error: {type(exc).__name__}"
    else:
        call.status = "SIMULATED"
        call.notes = "Twilio not configured; call stored without placing a real call."

    db.add(call)
    db.flush()
    audit(db, user, "CREATE", "call", call.id)
    db.commit()
    db.refresh(call)

    return call


@app.get("/calls", response_model=list[CallOut])
def list_calls(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return db.query(CallLog).order_by(CallLog.created_at.desc()).limit(100).all()


@app.get("/audit")
def audit_logs(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Administrator access required.")

    rows = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )

    return [
        {
            "id": row.id,
            "user_id": row.user_id,
            "action": row.action,
            "resource": row.resource,
            "resource_id": row.resource_id,
            "details": row.details,
            "created_at": row.created_at,
        }
        for row in rows
    ]
