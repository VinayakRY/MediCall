import os
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="MediCall",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background:#f5f7fb; }

section[data-testid="stSidebar"] {
    background:#0f172a;
}
section[data-testid="stSidebar"] * {
    color:#e2e8f0;
}

section[data-testid="stSidebar"] .stButton > button {
    background:#17213a;
    border:1px solid #263452;
    color:#e2e8f0 !important;
    text-align:left;
}
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {
    color:#e2e8f0 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background:#243250;
    border-color:#3b82f6;
}

.brand {
    padding:12px 8px 22px;
    border-bottom:1px solid #334155;
    margin-bottom:18px;
}
.brand-row { display:flex; align-items:center; gap:10px; }
.brand-icon {
    width:42px;height:42px;border-radius:12px;background:#2563eb;
    display:flex;align-items:center;justify-content:center;font-size:21px;
}
.brand-title { color:#fff;font-size:20px;font-weight:700; }
.brand-subtitle { color:#94a3b8;font-size:11px;margin-top:2px; }

.section-label {
    color:#64748b !important;
    font-size:10px;font-weight:700;letter-spacing:.12em;
    text-transform:uppercase;margin:20px 8px 7px;
}

.hero {
    background:linear-gradient(135deg,#0f172a,#1d4ed8);
    color:#fff;border-radius:18px;padding:28px;margin-bottom:22px;
}
.hero-title { font-size:28px;font-weight:700; }
.hero-text { color:#dbeafe;font-size:13px;margin-top:7px; }

.metric {
    background:#fff;border:1px solid #e2e8f0;border-radius:16px;
    padding:19px;min-height:130px;
    box-shadow:0 3px 12px rgba(15,23,42,.04);
}
.metric-icon {
    width:40px;height:40px;border-radius:11px;background:#eff6ff;
    display:flex;align-items:center;justify-content:center;font-size:18px;
}
.metric-label { color:#64748b;font-size:12px;margin-top:14px; }
.metric-value { color:#0f172a;font-size:29px;font-weight:700; }
.metric-help { color:#94a3b8;font-size:11px; }

.card {
    background:#fff;border:1px solid #e2e8f0;border-radius:16px;
    padding:20px;box-shadow:0 3px 12px rgba(15,23,42,.04);
}
.card-title { font-size:17px;font-weight:700;color:#0f172a; }
.card-subtitle { color:#94a3b8;font-size:12px;margin:4px 0 16px; }

.page-title { font-size:30px;font-weight:700;color:#0f172a; }
.page-subtitle { color:#64748b;font-size:14px;margin-bottom:22px; }

.patient-profile {
    background:linear-gradient(135deg,#111827,#1e3a8a);
    color:#fff;border-radius:18px;padding:23px;
}
.patient-name { font-size:23px;font-weight:700; }
.patient-meta { color:#cbd5e1;font-size:13px;margin-top:4px; }

.stButton > button {
    border-radius:10px;
    font-weight:600;
}
</style>
""",
    unsafe_allow_html=True,
)


def api(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            headers=headers,
            timeout=15,
            **kwargs,
        )
    except requests.RequestException as exc:
        st.error(
            f"Cannot connect to backend at {API_URL}. "
            f"Start FastAPI first. Error: {exc}"
        )
        return None

    if response.status_code == 401:
        st.session_state.clear()
        st.rerun()

    return response


def show_error(response):
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    st.error(detail)


def login():
    left, center, right = st.columns([1, 1.2, 1])

    with center:
        st.markdown("## MediCall")
        st.caption("Practice Management")

        with st.form("login"):
            email = st.text_input("Email", "admin@medicall.com")
            password = st.text_input("Password", "ChangeMe123!", type="password")

            if st.form_submit_button(
                "Sign in",
                type="primary",
                use_container_width=True,
            ):
                try:
                    response = requests.post(
                        f"{API_URL}/auth/login",
                        json={"email": email, "password": password},
                        timeout=15,
                    )

                    if response.ok:
                        st.session_state.token = response.json()["access_token"]
                        st.session_state.page = "Dashboard"
                        st.rerun()
                    else:
                        show_error(response)
                except requests.RequestException as exc:
                    st.error(f"Backend unavailable: {exc}")

        st.info(
            "Use your clinic account to sign in."
        )


if "token" not in st.session_state:
    login()
    st.stop()


me = api("GET", "/auth/me")
if not me or not me.ok:
    st.stop()

user = me.json()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-row">
                <div class="brand-icon">🏥</div>
                <div>
                    <div class="brand-title">MediCall</div>
                    <div class="brand-subtitle">Practice Management</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)

    nav = [
        ("Dashboard", "▣"),
        ("Patients", "👥"),
        ("Doctors", "🩺"),
        ("Appointments", "📅"),
        ("Patient Outreach", ""),
        ("Clinic Assistant", ""),
    ]

    for name, icon in nav:
        if st.button(
            f"{icon}   {name}",
            key=f"nav_{name}",
            use_container_width=True,
        ):
            st.session_state.page = name
            st.rerun()

    if user.get("role") == "ADMIN":
        st.markdown('<div class="section-label">Administration</div>', unsafe_allow_html=True)

        if st.button("▤   Audit Log", key="nav_Audit", use_container_width=True):
            st.session_state.page = "Audit Log"
            st.rerun()

    st.divider()
    st.caption(f"**{user.get('full_name', 'User')}**")
    st.caption(user.get("role", "STAFF"))

    if st.button("Sign out", use_container_width=True):
        st.session_state.clear()
        st.rerun()


page = st.session_state.page


# ---------------- DASHBOARD ----------------

if page == "Dashboard":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Good morning, Admin 👋</div>
            <div class="hero-text">
                A real-time view of clinic operations, appointments and patient communication.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    response = api("GET", "/dashboard/summary")
    summary = response.json() if response and response.ok else {}

    metrics = [
        ("👥", "Active Patients", summary.get("patients", 0), "Current patient records"),
        ("📅", "Today's Appointments", summary.get("appointments_today", 0), "Scheduled for today"),
        ("✓", "Confirmed", summary.get("confirmed", 0), "Confirmed appointments"),
        ("⏳", "Pending", summary.get("pending", 0), "Awaiting confirmation"),
        ("☎", "Completed Calls", summary.get("completed_calls", 0), "Recorded completed calls"),
        ("!", "Missed Calls", summary.get("missed_calls", 0), "Calls requiring follow-up"),
    ]

    cols = st.columns(6)
    for col, (icon, label, value, help_text) in zip(cols, metrics):
        col.markdown(
            f"""
            <div class="metric">
                <div class="metric-icon">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-help">{help_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    left, right = st.columns([1.7, 1])

    with left:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">Upcoming appointments</div>
                <div class="card-subtitle">Scheduled clinic visits</div>
            """,
            unsafe_allow_html=True,
        )

        response = api("GET", "/appointments")
        appointments = response.json() if response and response.ok else []
        patients_r = api("GET", "/patients")
        doctors_r = api("GET", "/doctors")
        patient_names = {p["id"]: f'{p["first_name"]} {p["last_name"]}'.strip() for p in (patients_r.json() if patients_r and patients_r.ok else [])}
        doctor_names = {d["id"]: d["name"] for d in (doctors_r.json() if doctors_r and doctors_r.ok else [])}

        if appointments:
            rows = []
            for item in appointments[:10]:
                rows.append({
                    "ID": item["id"],
                    "Patient": patient_names.get(item["patient_id"], "Unknown"),
                    "Doctor": doctor_names.get(item["doctor_id"], "Unknown"),
                    "Date": str(item["appointment_date"]).replace("T", " ")[:16],
                    "Status": item["status"].replace("_", " ").title(),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No appointments yet.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="card">
                <div class="card-title">Operations snapshot</div>
                <div class="card-subtitle">Live database metrics</div>
            """,
            unsafe_allow_html=True,
        )

        st.metric("Active patients", summary.get("patients", 0))
        st.metric("Appointments today", summary.get("appointments_today", 0))
        st.metric("Pending", summary.get("pending", 0))
        st.metric("Completed calls", summary.get("completed_calls", 0))

        st.markdown("</div>", unsafe_allow_html=True)


# ---------------- PATIENTS ----------------

elif page == "Patients":
    st.markdown('<div class="page-title">Patients</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Search patients and open a complete patient profile.</div>', unsafe_allow_html=True)

    if "selected_patient_id" not in st.session_state:
        st.session_state.selected_patient_id = None

    if st.session_state.selected_patient_id:
        patient_id = st.session_state.selected_patient_id
        patient_response = api("GET", f"/patients/{patient_id}")
        if not patient_response or not patient_response.ok:
            if patient_response:
                show_error(patient_response)
            st.session_state.selected_patient_id = None
            st.rerun()

        patient = patient_response.json()

        if st.button("← Back to patients", key="back_patients"):
            st.session_state.selected_patient_id = None
            st.rerun()

        full_name = f"{patient['first_name']} {patient['last_name'] or ''}".strip()
        st.markdown(
            f'<div class="patient-profile"><div class="patient-name">{full_name}</div>'
            f'<div class="patient-meta">{patient["patient_number"]} · {patient["phone"]} · {patient["preferred_language"]}</div></div>',
            unsafe_allow_html=True,
        )

        st.write("")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Patient ID",patient["patient_number"])
        c2.metric("Phone",patient["phone"])
        c3.metric("Language",patient["preferred_language"])
        c4.metric("Status",patient["status"])

        tabs=st.tabs(["Overview","Appointments","Communication","Notes"])
        with tabs[0]:
            st.subheader("Patient information")
            st.dataframe(pd.DataFrame([
                ["First name",patient["first_name"]],
                ["Last name",patient["last_name"] or "—"],
                ["Phone",patient["phone"]],
                ["Email",patient["email"] or "—"],
                ["Date of birth",patient["date_of_birth"] or "—"],
                ["Preferred language",patient["preferred_language"]],
                ["Status",patient["status"]],
                ["Created",str(patient["created_at"])[:19]],
            ],columns=["Field","Value"]),use_container_width=True,hide_index=True)

        with tabs[1]:
            r=api("GET","/appointments")
            appointments=[a for a in (r.json() if r and r.ok else []) if a["patient_id"]==patient["id"]]
            if appointments:
                st.dataframe(pd.DataFrame([{
                    "Appointment":a["id"],
                    "Date":str(a["appointment_date"]).replace("T"," ")[:16],
                    "Doctor ID":a["doctor_id"],
                    "Status":a["status"],
                    "Reason":a.get("reason") or "—"
                } for a in appointments]),use_container_width=True,hide_index=True)
            else:
                st.info("No appointments for this patient.")

        with tabs[2]:
            r=api("GET","/calls")
            calls=[c for c in (r.json() if r and r.ok else []) if c.get("patient_id")==patient["id"]]
            if calls:
                st.dataframe(pd.DataFrame([{
                    "Call":c["id"],
                    "Purpose":c.get("purpose") or "—",
                    "Phone":c.get("phone") or patient["phone"],
                    "Status":c["status"],
                    "Provider ID":c.get("provider_call_id") or "—"
                } for c in calls]),use_container_width=True,hide_index=True)
            else:
                st.info("No communication records for this patient.")

        with tabs[3]:
            st.subheader("Patient notes")
            st.text_area("Notes",value=patient.get("notes") or "",height=180,disabled=True)
            st.caption("Clinical documentation should be completed by authorized staff using your organization's approved clinical workflow.")

        st.divider()
        if patient["status"]=="ACTIVE" and st.button("Archive patient",key=f"archive_{patient['id']}"):
            r=api("PATCH",f"/patients/{patient['id']}/archive")
            if r and r.ok:
                st.success("Patient archived.")
                st.session_state.selected_patient_id=None
                st.rerun()
            elif r:
                show_error(r)

    else:
        with st.expander("＋ Add new patient"):
            with st.form("patient_form"):
                c1,c2=st.columns(2)
                first_name=c1.text_input("First name *")
                last_name=c2.text_input("Last name")
                phone=c1.text_input("Phone *")
                email=c2.text_input("Email")
                language=c1.selectbox("Preferred language",["English","Hindi","Hinglish","Tamil","Telugu","Bengali"])
                dob=c2.text_input("Date of birth",placeholder="YYYY-MM-DD")
                notes=st.text_area("Notes")
                if st.form_submit_button("Create patient",type="primary"):
                    r=api("POST","/patients",json={"first_name":first_name,"last_name":last_name,"phone":phone,"email":email or None,"preferred_language":language,"date_of_birth":dob or None,"notes":notes or None})
                    if r and r.ok:
                        st.success("Patient created successfully.")
                        st.rerun()
                    elif r:
                        show_error(r)

        search=st.text_input("Search",placeholder="Patient number, name or phone...")
        r=api("GET","/patients",params={"search":search} if search else {})
        if r and r.ok:
            patients=r.json()
            st.caption(f"{len(patients)} patient(s)")
            if patients:
                st.dataframe(pd.DataFrame([{
                    "Patient ID":p["patient_number"],
                    "Name":f"{p['first_name']} {p['last_name']}".strip(),
                    "Phone":p["phone"],
                    "Language":p["preferred_language"],
                    "Status":p["status"]
                } for p in patients]),use_container_width=True,hide_index=True)

                st.subheader("Open patient profile")
                options={f"{p['patient_number']} · {p['first_name']} {p['last_name']}".strip():p["id"] for p in patients}
                label=st.selectbox("Patient",list(options),key="patient_profile_selector")
                if st.button("Open profile",type="primary",key="open_patient_profile"):
                    st.session_state.selected_patient_id=options[label]
                    st.rerun()
            else:
                st.info("No patients found.")

# ---------------- DOCTORS ----------------

elif page == "Doctors":
    st.markdown('<div class="page-title">Doctors</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Manage active clinicians and specialties.</div>',
        unsafe_allow_html=True,
    )

    with st.form("doctor_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Doctor name")
        specialization = c2.text_input("Specialization", "General Medicine")
        phone = st.text_input("Phone")

        if st.form_submit_button("Add doctor", type="primary"):
            response = api(
                "POST",
                "/doctors",
                json={
                    "name": name,
                    "specialization": specialization,
                    "phone": phone or None,
                },
            )
            if response and response.ok:
                st.success("Doctor added.")
                st.rerun()
            elif response:
                show_error(response)

    response = api("GET", "/doctors")

    if response and response.ok:
        doctors = response.json()

        if doctors:
            st.dataframe(
                pd.DataFrame([
                    {
                        "ID": d["id"],
                        "Doctor": d["name"],
                        "Specialization": d["specialization"],
                        "Phone": d.get("phone") or "",
                        "Status": "Active" if d["active"] else "Inactive",
                    }
                    for d in doctors
                ]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No doctors added yet.")


# ---------------- APPOINTMENTS ----------------

elif page == "Appointments":
    st.markdown('<div class="page-title">Appointments</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Schedule and manage clinic visits.</div>',
        unsafe_allow_html=True,
    )

    patients_response = api("GET", "/patients")
    doctors_response = api("GET", "/doctors")

    if (
        patients_response and patients_response.ok
        and doctors_response and doctors_response.ok
    ):
        patients = [
            p for p in patients_response.json()
            if p["status"] == "ACTIVE"
        ]
        doctors = doctors_response.json()

        if not patients:
            st.warning("Create an active patient first.")
        elif not doctors:
            st.warning("Create a doctor first.")
        else:
            patient_map = {
                f"{p['patient_number']} · {p['first_name']} {p['last_name']}".strip(): p["id"]
                for p in patients
            }
            doctor_map = {
                f"{d['name']} · {d['specialization']}": d["id"]
                for d in doctors
            }

            with st.form("appointment_form"):
                c1, c2 = st.columns(2)
                patient_label = c1.selectbox("Patient", list(patient_map))
                doctor_label = c2.selectbox("Doctor", list(doctor_map))
                date = c1.date_input("Date", datetime.now().date() + timedelta(days=1))
                time = c2.time_input("Time", datetime.now().replace(minute=0, second=0, microsecond=0).time())
                reason = st.text_area("Reason for visit")

                if st.form_submit_button("Book appointment", type="primary"):
                    response = api(
                        "POST",
                        "/appointments",
                        json={
                            "patient_id": patient_map[patient_label],
                            "doctor_id": doctor_map[doctor_label],
                            "appointment_date": datetime.combine(date, time).isoformat(),
                            "reason": reason or None,
                        },
                    )

                    if response and response.ok:
                        st.success("Appointment booked.")
                        st.rerun()
                    elif response:
                        show_error(response)

    st.write("")

    response = api("GET", "/appointments")
    if response and response.ok:
        appointments = response.json()

        if appointments:
            patient_names = {p["id"]: f'{p["first_name"]} {p["last_name"]}'.strip() for p in (patients_response.json() if patients_response and patients_response.ok else [])}
            doctor_names = {d["id"]: d["name"] for d in (doctors_response.json() if doctors_response and doctors_response.ok else [])}
            rows = []
            for a in appointments:
                rows.append({
                    "ID": a["id"],
                    "Patient": patient_names.get(a["patient_id"], "Unknown"),
                    "Doctor": doctor_names.get(a["doctor_id"], "Unknown"),
                    "Date": str(a["appointment_date"]).replace("T", " ")[:16],
                    "Status": a["status"],
                    "Reason": a.get("reason") or "",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.subheader("Update appointment status")
            selected_id = st.selectbox(
                "Appointment",
                [a["id"] for a in appointments],
            )
            status = st.selectbox(
                "New status",
                ["SCHEDULED", "CONFIRMED", "COMPLETED", "CANCELLED", "NO_SHOW"],
            )

            if st.button("Update status", type="primary"):
                response = api(
                    "PATCH",
                    f"/appointments/{selected_id}/status",
                    json={"status": status},
                )
                if response and response.ok:
                    st.success("Appointment status updated.")
                    st.rerun()
                elif response:
                    show_error(response)
        else:
            st.info("No appointments yet.")


# ---------------- AI CALLING ----------------

elif page == "Patient Outreach":
    st.markdown('<div class="page-title">Patient Outreach</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Patient communication and appointment reminder calls.</div>',
        unsafe_allow_html=True,
    )

    st.warning(
        "Select a patient and create an outreach record. Live calling requires telephony configuration. "
        "Without telephony configuration, the record is stored without placing a call."
    )

    response = api("GET", "/patients")
    if response and response.ok:
        patients = [p for p in response.json() if p["status"] == "ACTIVE"]

        if patients:
            patient_map = {
                f"{p['patient_number']} · {p['first_name']} {p['last_name']} · {p['phone']}": p
                for p in patients
            }

            selected = st.selectbox("Patient", list(patient_map))
            patient = patient_map[selected]

            st.markdown(
                f"""
                <div class="patient-profile">
                    <div class="patient-name">{patient['first_name']} {patient['last_name']}</div>
                    <div class="patient-meta">{patient['phone']} · {patient['preferred_language']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            purpose = st.selectbox(
                "Purpose",
                [
                    "Appointment reminder",
                    "Appointment confirmation",
                    "Follow-up",
                    "General clinic communication",
                ],
            )

            if st.button("Start outreach", type="primary"):
                response = api(
                    "POST",
                    "/calls",
                    json={
                        "patient_id": patient["id"],
                        "purpose": purpose,
                    },
                )

                if response and response.ok:
                    call = response.json()
                    st.success(f"Call record created. Status: {call['status']}")
                elif response:
                    show_error(response)

            st.subheader("Recent call records")
            response = api("GET", "/calls")

            if response and response.ok:
                calls = response.json()

                if calls:
                    st.dataframe(
                        pd.DataFrame([
                            {
                                "ID": c["id"],
                                "Patient": c["patient_id"],
                                "Phone": c["phone"],
                                "Purpose": c["purpose"],
                                "Status": c["status"],
                                "Provider ID": c.get("provider_call_id") or "",
                            }
                            for c in calls
                        ]),
                        use_container_width=True,
                        hide_index=True,
                    )


# ---------------- AI ASSISTANT ----------------

elif page == "Clinic Assistant":
    st.markdown('<div class="page-title">Clinic Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">General information and clinic assistance.</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "This assistant provides staff support and general health information. "
        "It does not diagnose conditions or prescribe treatment."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Search clinic information or ask a general health question...")

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        response = api(
            "POST",
            "/ai/chat",
            json={"message": prompt},
        )

        if response and response.ok:
            reply = response.json()["reply"]
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
        elif response:
            show_error(response)

        st.rerun()


# ---------------- AUDIT ----------------

elif page == "Audit Log":
    st.markdown('<div class="page-title">Audit Log</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Administrator activity history.</div>',
        unsafe_allow_html=True,
    )

    response = api("GET", "/audit")

    if response and response.ok:
        rows = response.json()

        if rows:
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No audit events yet.")
    elif response:
        show_error(response)
