from __future__ import annotations

import base64
import binascii

from fastapi import APIRouter, HTTPException

from fastapi.responses import Response

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator
)

from backend.config import get_settings

from backend.schemas import (
    DocumentRequest,
    ExportRequest
)

from backend.services.document_service import (
    make_docx,
    make_pdf,
    make_txt
)


router = APIRouter()

settings = get_settings()

generator = GeminiDocumentGenerator(
    settings
)


@router.get("/document-types")
def document_types():

    return {

        "document_types": [

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
    }


@router.post("/generate")
def generate_document(
    request: DocumentRequest
):

    total = (

        len(request.parties)

        + len(request.terms)

        + len(
            request.additional_instructions
        )
    )

    if total > settings.max_input_chars:

        raise HTTPException(

            status_code=413,

            detail=(
                "Input is too large. "
                f"Maximum combined input is "
                f"{settings.max_input_chars} "
                "characters."
            )
        )

    try:

        result = generator.generate_document(

            document_type=request.document_type,

            parties=request.parties,

            terms=request.terms,

            effective_date=request.effective_date,

            additional_instructions=(
                request.additional_instructions
            ),
        )

        return {

            "success": True,

            "document": result.text,

            "provider": result.provider,

            "model": result.model,
        }

    except RuntimeError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=(
                "Unexpected generation error: "
                f"{exc}"
            )
        ) from exc


def _decode_logo(
    logo_base64: str | None
) -> bytes | None:

    if not logo_base64:

        return None

    try:

        encoded = (

            logo_base64.split(
                ",",
                1
            )[1]

            if "," in logo_base64

            else logo_base64
        )

        return base64.b64decode(
            encoded,
            validate=True
        )

    except (
        binascii.Error,
        ValueError
    ) as exc:

        raise HTTPException(

            status_code=400,

            detail="Invalid logo data."
        ) from exc


@router.post("/export")
def export_document(
    request: ExportRequest,
    format: str = "txt"
):

    format = format.lower()

    if format not in {
        "txt",
        "docx",
        "pdf"
    }:

        raise HTTPException(

            status_code=400,

            detail=(
                "Format must be "
                "txt, docx, or pdf."
            )
        )

    logo_bytes = _decode_logo(
        request.logo_base64
    )

    try:

        if format == "txt":

            payload = make_txt(
                request.content
            )

            media_type = (
                "text/plain; charset=utf-8"
            )

            filename = (
                "legalease-document.txt"
            )

        elif format == "docx":

            payload = make_docx(

                text=request.content,

                doc_type=request.document_type,

                terms=request.terms,

                brand_name=request.brand_name,

                footer_text=request.footer_text,

                logo_bytes=logo_bytes,
            )

            media_type = (
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )

            filename = (
                "legalease-document.docx"
            )

        else:

            payload = make_pdf(

                text=request.content,

                doc_type=request.document_type,

                brand_name=request.brand_name,

                footer_text=request.footer_text,

                logo_bytes=logo_bytes,
            )

            media_type = (
                "application/pdf"
            )

            filename = (
                "legalease-document.pdf"
            )

        return Response(

            content=payload,

            media_type=media_type,

            headers={
                "Content-Disposition":
                    f'attachment; '
                    f'filename="{filename}"'
            }
        )

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Export failed: {exc}"
            )
        ) from exc