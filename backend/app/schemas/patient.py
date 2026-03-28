from datetime import date
from pydantic import BaseModel


class PatientProfileResponse(BaseModel):
    patient_id: str
    subject_id: str
    trial_name: str
    site_name: str
    enrollment_date: date
    checkin_frequency: str
    wearable_connected: bool
