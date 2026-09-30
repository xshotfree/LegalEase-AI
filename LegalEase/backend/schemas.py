from typing import Literal

from pydantic import BaseModel, Field, field_validator


DocumentType = Literal[
    "Agreement",
    "Contract",
    "Non-Disclosure Agreement",
    "Lease Agreement",
    "Employment Offer Letter",
    "Employment Contract",
    "Freelance Work Contract",
    "Service Agreement",
    "Other",
]


class DocumentRequest(BaseModel):

    document_type: DocumentType

    parties: str = Field(
        ...,
        min_length=3,
        max_length=10000
    )

    terms: str = Field(
        ...,
        min_length=3,
        max_length=15000
    )

    effective_date: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    additional_instructions: str = Field(
        default="",
        max_length=5000
    )

    @field_validator(
        "parties",
        "terms",
        "effective_date"
    )
    @classmethod
    def validate_required_fields(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value


class ExportRequest(BaseModel):

    content: str = Field(
        ...,
        min_length=10,
        max_length=100000
    )

    document_type: str = Field(
        default="Legal Document",
        max_length=200
    )

    terms: str = Field(
        default="",
        max_length=15000
    )

    brand_name: str = Field(
        default="LegalEase",
        max_length=100
    )

    footer_text: str = Field(
        default=(
            "Generated with LegalEase. "
            "Review by a qualified legal professional is recommended."
        ),
        max_length=500
    )

    logo_base64: str | None = Field(
        default=None,
        max_length=5000000
    )