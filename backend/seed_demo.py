from datetime import datetime, timedelta
from database import Base, engine, SessionLocal
from models import Patient, Doctor, Appointment, CallLog

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if db.query(Patient).count() or db.query(Doctor).count():
        print("Demo data not loaded: existing clinic data was found.")
        print("No existing records were changed.")
        raise SystemExit(0)

    patients = [
        ("Ananya", "Sharma", "+91 90000 10001", "ananya.demo@example.com", "Hindi"),
        ("Rahul", "Verma", "+91 90000 10002", "rahul.demo@example.com", "English"),
        ("Priya", "Nair", "+91 90000 10003", "priya.demo@example.com", "English"),
        ("Arjun", "Patel", "+91 90000 10004", "arjun.demo@example.com", "Hindi"),
        ("Neha", "Gupta", "+91 90000 10005", "neha.demo@example.com", "English"),
        ("Kabir", "Mehta", "+91 90000 10006", "kabir.demo@example.com", "Hinglish"),
        ("Riya", "Sen", "+91 90000 10007", "riya.demo@example.com", "English"),
        ("Vikram", "Khan", "+91 90000 10008", "vikram.demo@example.com", "Hindi"),
    ]
    patient_objs = []
    for i, row in enumerate(patients, 1):
        p = Patient(
            patient_number=f"DEMO-{1000+i}",
            first_name=row[0], last_name=row[1], phone=row[2], email=row[3],
            preferred_language=row[4], status="ACTIVE",
        )
        db.add(p); patient_objs.append(p)

    doctors = [
        ("Dr. Mehta", "General Medicine"),
        ("Dr. Singh", "Internal Medicine"),
        ("Dr. Nair", "Pediatrics"),
        ("Dr. Khan", "Dermatology"),
    ]
    doctor_objs = []
    for name, specialty in doctors:
        d = Doctor(name=name, specialization=specialty, active=True)
        db.add(d); doctor_objs.append(d)

    db.flush()
    base = datetime.now().replace(second=0, microsecond=0)
    statuses = ["CONFIRMED", "SCHEDULED", "CONFIRMED", "COMPLETED", "SCHEDULED", "CONFIRMED", "NO_SHOW", "SCHEDULED"]
    for i in range(8):
        when = base + timedelta(days=(i % 3) + 1, hours=(i % 6) + 1)
        db.add(Appointment(
            patient_id=patient_objs[i].id,
            doctor_id=doctor_objs[i % len(doctor_objs)].id,
            appointment_date=when,
            reason="Routine consultation",
            status=statuses[i],
        ))

    for i in range(5):
        db.add(CallLog(
            patient_id=patient_objs[i].id,
            phone=patient_objs[i].phone,
            direction="OUTBOUND",
            status=["COMPLETED", "COMPLETED", "NO_ANSWER", "SIMULATED", "COMPLETED"][i],
            purpose="Appointment reminder",
            notes="Fictional demo communication record.",
        ))

    db.commit()
    print("Demo clinic data loaded successfully.")
finally:
    db.close()
