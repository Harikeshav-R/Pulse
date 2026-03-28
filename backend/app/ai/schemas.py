"""Pydantic schemas for AI agent structured outputs.

These schemas are used with LangChain v1's create_agent response_format
to get validated, type-safe structured responses from the LLM.
"""

from pydantic import BaseModel, Field


class SymptomClassification(BaseModel):
    """A single classified symptom extracted from a check-in conversation."""

    symptom_text: str = Field(description="The patient's verbatim description of the symptom")
    meddra_pt_term: str = Field(description="MedDRA Preferred Term (e.g., 'Nausea', 'Headache')")
    meddra_pt_code: str = Field(description="MedDRA PT code (e.g., '10028813')")
    meddra_soc: str = Field(description="System Organ Class (e.g., 'Gastrointestinal disorders')")
    severity_ctcae: int = Field(
        description="CTCAE v5 grade 1-5 based on the patient's description",
        ge=1,
        le=5,
    )
    confidence: float = Field(
        description="Classification confidence score 0.0-1.0",
        ge=0.0,
        le=1.0,
    )
    onset: str = Field(default="", description="When the symptom started, if mentioned")
    is_ongoing: bool = Field(default=True, description="Whether the symptom is still present")


class ClassificationResult(BaseModel):
    """Complete symptom classification result from a check-in conversation."""

    symptoms: list[SymptomClassification] = Field(
        default_factory=list,
        description="List of all symptoms extracted and classified from the conversation",
    )
    total_symptoms: int = Field(
        description="Total number of symptoms found in the conversation"
    )
    has_severe_symptoms: bool = Field(
        default=False,
        description="True if any symptom is Grade 3 or above",
    )


class CheckinSummary(BaseModel):
    """Structured summary produced at the end of a check-in session."""

    overall_feeling: int = Field(
        description="Patient's overall feeling on a 1-5 scale",
        ge=1,
        le=5,
    )
    symptoms_reported: list[str] = Field(
        default_factory=list,
        description="List of symptom names the patient reported",
    )
    key_concerns: list[str] = Field(
        default_factory=list,
        description="Key concerns or notable points from the conversation",
    )
    requires_urgent_review: bool = Field(
        default=False,
        description="True if the patient reported any urgent/severe symptoms",
    )
    summary_text: str = Field(
        description="A brief natural-language summary of the check-in",
    )
