from __future__ import annotations

from dataclasses import dataclass

from google import genai
from google.genai import types

from backend.config import Settings


SYSTEM_INSTRUCTION = """
You are LegalEase's legal-document drafting assistant.

Your job is to produce a structured legal document draft
based ONLY on the information supplied by the user.

IMPORTANT RULES:

1. Do not invent names.
2. Do not invent dates.
3. Do not invent amounts.
4. Do not invent addresses.
5. Do not invent legal citations.
6. Do not invent registration numbers.
7. Do not invent facts.

If information is missing, use a placeholder such as:

[INSERT NOTICE PERIOD]

[INSERT JURISDICTION]

[INSERT AMOUNT]

Use professional and neutral language.

Use clear headings.

Use numbered clauses.

Do not use markdown code fences.

Do not claim that the document is legally valid.

Do not claim that the document was reviewed by a lawyer.

This system provides drafting assistance and is not a substitute
for professional legal advice.

Return ONLY the document draft.
"""


@dataclass
class GenerationResult:

    text: str

    provider: str

    model: str


class GeminiDocumentGenerator:

    def __init__(self, settings: Settings):

        self.settings = settings

        self.api_key = settings.gemini_api_key.strip()

        self.model = settings.gemini_model

        if self.api_key:

            self.client = genai.Client(
                api_key=self.api_key
            )

        else:

            self.client = None

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        additional_instructions: str = "",
    ) -> GenerationResult:

        # Local demo mode
        if not self.client:

            return GenerationResult(

                text=self._demo_document(
                    document_type,
                    parties,
                    terms,
                    effective_date,
                    additional_instructions,
                ),

                provider="local-demo",

                model="deterministic-template",
            )

        prompt = f"""
Create a professional draft for this document.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

TERMS AND CONDITIONS:
{terms}

ADDITIONAL INSTRUCTIONS:
{additional_instructions or "None"}

STRUCTURE:

1. Document title

2. Introduction

3. Parties

4. Definitions where appropriate

5. Main numbered clauses

6. Responsibilities

7. Term and termination

8. Confidentiality where applicable

9. Intellectual property where applicable

10. Dispute/governing-law section

11. Signature section

12. Final review note

Do not invent missing information.

Use [INSERT ...] placeholders where information is missing.
"""

        try:

            response = self.client.models.generate_content(

                model=self.model,

                contents=(
                    SYSTEM_INSTRUCTION
                    + "\n\n"
                    + prompt
                ),

                config=types.GenerateContentConfig(

    max_output_tokens=(
        self.settings.max_output_tokens
    ),
),
            )

            text = (
                response.text
                if response.text
                else ""
            ).strip()

            if not text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return GenerationResult(

                text=text,

                provider="gemini",

                model=self.model,
            )

        except Exception as exc:

            raise RuntimeError(
                f"Gemini generation failed: {exc}"
            ) from exc

    @staticmethod
    def _demo_document(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        additional_instructions: str,
    ) -> str:

        term_items = [
            item.strip()
            for item in terms.replace(
                "\n",
                ";"
            ).split(";")
            if item.strip()
        ]

        clauses = "\n".join(

            f"{index}. {item}"

            for index, item
            in enumerate(
                term_items,
                start=1
            )
        )

        instructions = (
            additional_instructions.strip()
            if additional_instructions.strip()
            else "None provided."
        )

        return f"""
{document_type.upper()}

Effective Date: {effective_date}


PARTIES

{parties}


PURPOSE

This draft records the terms supplied by
the user for the selected document type.

Missing information is represented using
placeholders and should be reviewed before use.


TERMS AND CONDITIONS

{clauses or "1. [INSERT TERMS AND CONDITIONS]"}


ADDITIONAL INSTRUCTIONS

{instructions}


TERM AND TERMINATION

Term: [INSERT TERM]

Termination notice:
[INSERT NOTICE PERIOD]


GOVERNING LAW

Jurisdiction:
[INSERT JURISDICTION]


SIGNATURES


Party 1:

Signature: ______________________________

Name: [INSERT NAME]

Date: _________________________________


Party 2:

Signature: ______________________________

Name: [INSERT NAME]

Date: _________________________________


REVIEW NOTE

This is a draft generated by LegalEase.

It is not legal advice and should be reviewed
by a qualified legal professional for the
intended jurisdiction and use.
"""
