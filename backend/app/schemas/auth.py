from pydantic import BaseModel


class PatientDemoLoginRequest(BaseModel):
    patient_id: str


class PatientDemoLoginResponse(BaseModel):
    patient_id: str
    subject_id: str
    access_token: str


class StaffDemoLoginRequest(BaseModel):
    staff_id: str


class StaffDemoLoginResponse(BaseModel):
    access_token: str
    staff: dict
