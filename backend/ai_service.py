"""
Safety-first clinic assistant.

This module deliberately avoids diagnosing conditions, prescribing medication,
or presenting generated text as medical certainty. It provides administrative
help and general safety guidance and directs urgent cases to human care.
"""

URGENT_TERMS = {
    "chest pain",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "unconscious",
    "passed out",
    "seizure",
    "stroke",
    "face drooping",
    "suicidal",
    "overdose",
}

def chat_response(message: str) -> str:
    text = (message or "").strip()
    lower = text.lower()

    if not text:
        return "Please enter a question or describe what you need help with."

    if any(term in lower for term in URGENT_TERMS):
        return (
            "This may require urgent medical attention. Please contact your "
            "local emergency service or go to the nearest emergency department "
            "now. MediCall AI cannot assess emergencies or replace a clinician."
        )

    if any(word in lower for word in ["appointment", "booking", "schedule", "doctor"]):
        return (
            "I can help with clinic scheduling and general information. "
            "For an appointment, use the Appointments section or ask clinic staff."
        )

    if any(word in lower for word in ["fever", "cough", "cold", "headache", "pain"]):
        return (
            "I can provide general information, but I cannot diagnose the cause "
            "of symptoms. Consider contacting a qualified healthcare professional, "
            "especially if symptoms are severe, worsening, persistent, or concerning."
        )

    return (
        "I can help with clinic information, appointments, patient communication, "
        "and general health information. I cannot diagnose conditions or prescribe "
        "medication. For personal medical advice, please speak with a qualified clinician."
    )
