from __future__ import annotations

import base64
import html
import os

import requests

import streamlit as st

from dotenv import load_dotenv


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


TIMEOUT = 120


st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide"
)


# =========================
# CSS
# =========================

st.markdown(
    """
    <style>

    .main-title {

        text-align: center;

        font-size: 2.7rem;

        font-weight: 800;

        margin-bottom: 0.1rem;
    }

    .subtitle {

        text-align: center;

        color: #6b7280;

        margin-bottom: 1.5rem;
    }

    .preview {

        border: 1px solid #334155;

        border-radius: 12px;

        padding: 22px;

        background: #0f172a;

        color: #e5e7eb;

        max-height: 650px;

        overflow-y: auto;

        line-height: 1.7;
    }

    .notice {

        padding: 12px 15px;

        border-radius: 10px;

        background: #fff7ed;

        border: 1px solid #fed7aa;

        color: #7c2d12;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# HEADER
# =========================

st.markdown(

    '<div class="main-title">'
    '⚖️ LegalEase'
    '</div>',

    unsafe_allow_html=True
)


st.markdown(

    '<div class="subtitle">'
    'AI-assisted legal document drafting, '
    'editing and export'
    '</div>',

    unsafe_allow_html=True
)


st.markdown(

    '<div class="notice">'
    '<b>Important:</b> LegalEase creates drafts '
    'and does not provide legal advice. '
    'Review the result with a qualified legal '
    'professional before relying on it.'
    '</div>',

    unsafe_allow_html=True
)


# =========================
# SESSION STATE
# =========================

if "document" not in st.session_state:

    st.session_state.document = ""


if "provider" not in st.session_state:

    st.session_state.provider = ""


# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.header("⚙️ Settings")

    backend_url = st.text_input(

        "Backend URL",

        value=BACKEND_URL
    )

    brand_name = st.text_input(

        "Brand name",

        value="LegalEase"
    )

    footer_text = st.text_input(

        "Footer",

        value=(
            "Generated with LegalEase. "
            "Review by a qualified legal "
            "professional is recommended."
        )
    )

    logo = st.file_uploader(

        "Optional logo",

        type=[
            "png",
            "jpg",
            "jpeg"
        ],

        help=(
            "Logo will be embedded "
            "into DOCX/PDF exports."
        )
    )


# =========================
# LAYOUT
# =========================

left, right = st.columns(
    [0.95, 1.05],
    gap="large"
)


# =========================
# INPUT
# =========================

with left:

    st.subheader(
        "1. Document details"
    )

    document_type = st.selectbox(

        "Document type",

        [

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
    )


    parties = st.text_area(

        "Parties involved",

        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),

        height=100
    )


    terms = st.text_area(

        "Terms & conditions",

        placeholder=(
            "Payment within 30 days of invoice; "
            "Confidentiality must be maintained; "
            "Either party may terminate with "
            "15 days notice"
        ),

        height=170,

        help=(
            "Separate multiple terms using "
            "semicolons or new lines."
        )
    )


    effective_date = st.text_input(

        "Effective date",

        placeholder=(
            "30 September 2026"
        )
    )


    additional_instructions = st.text_area(

        "Additional instructions",

        placeholder=(
            "Use clear professional English."
        ),

        height=100
    )


    # =========================
    # GENERATE
    # =========================

    if st.button(

        "✨ Generate Document",

        type="primary",

        use_container_width=True
    ):

        if (

            not parties.strip()

            or not terms.strip()

            or not effective_date.strip()
        ):

            st.error(
                "Please complete all required fields."
            )

        else:

            payload = {

                "document_type":
                    document_type,

                "parties":
                    parties,

                "terms":
                    terms,

                "effective_date":
                    effective_date,

                "additional_instructions":
                    additional_instructions,
            }

            try:

                with st.spinner(
                    "Generating your document..."
                ):

                    response = requests.post(

                        f"{backend_url}/generate",

                        json=payload,

                        timeout=TIMEOUT
                    )


                if response.ok:

                    data = response.json()

                    st.session_state.document = (
                        data["document"]
                    )

                    st.session_state.provider = (
                        data.get(
                            "provider",
                            "unknown"
                        )
                    )

                    st.success(

                        "Document generated using "
                        f"{st.session_state.provider}."
                    )

                else:

                    try:

                        detail = (
                            response.json()
                            .get(
                                "detail",
                                response.text
                            )
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Generation failed: {detail}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Could not connect to the "
                    f"FastAPI backend:\n{exc}"
                )


# =========================
# DOCUMENT PREVIEW
# =========================

with right:

    st.subheader(
        "2. Preview & edit"
    )

    if st.session_state.document:

        edited_document = st.text_area(

            "Editable document",

            value=st.session_state.document,

            height=520
        )

        st.session_state.document = (
            edited_document
        )


        st.markdown(
            "**Live Preview**"
        )


        safe_document = html.escape(
            edited_document
        ).replace(
            "\n",
            "<br>"
        )


        st.markdown(

            f"""
            <div class="preview">
            {safe_document}
            </div>
            """,

            unsafe_allow_html=True
        )


        # =========================
        # EXPORT
        # =========================

        st.subheader(
            "3. Download"
        )


        logo_base64 = None


        if logo:

            logo_base64 = base64.b64encode(
                logo.getvalue()
            ).decode(
                "ascii"
            )


        export_payload = {

            "content":
                st.session_state.document,

            "document_type":
                document_type,

            "terms":
                terms,

            "brand_name":
                brand_name,

            "footer_text":
                footer_text,

            "logo_base64":
                logo_base64,
        }


        col1, col2, col3 = st.columns(3)


        def export_document(
            file_format: str,
            column,
            label: str
        ):

            with column:

                if st.button(

                    label,

                    use_container_width=True
                ):

                    try:

                        response = requests.post(

                            f"{backend_url}/export",

                            params={
                                "format":
                                    file_format
                            },

                            json=export_payload,

                            timeout=TIMEOUT
                        )


                        if response.ok:

                            if file_format == "txt":

                                mime = (
                                    "text/plain"
                                )

                            elif file_format == "docx":

                                mime = (
                                    "application/"
                                    "vnd.openxmlformats-"
                                    "officedocument."
                                    "wordprocessingml.document"
                                )

                            else:

                                mime = (
                                    "application/pdf"
                                )


                            st.download_button(

                                label=(
                                    f"⬇️ Download "
                                    f"{file_format.upper()}"
                                ),

                                data=response.content,

                                file_name=(
                                    "legalease-document."
                                    f"{file_format}"
                                ),

                                mime=mime,

                                use_container_width=True
                            )

                        else:

                            try:

                                detail = (
                                    response.json()
                                    .get(
                                        "detail",
                                        response.text
                                    )
                                )

                            except Exception:

                                detail = response.text

                            st.error(
                                f"Export failed: {detail}"
                            )

                    except requests.RequestException as exc:

                        st.error(
                            f"Export error: {exc}"
                        )


        export_document(
            "txt",
            col1,
            "Prepare TXT"
        )

        export_document(
            "docx",
            col2,
            "Prepare DOCX"
        )

        export_document(
            "pdf",
            col3,
            "Prepare PDF"
        )

    else:

        st.info(
            "Your generated document "
            "will appear here."
        )


# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "LegalEase • Drafting assistant only • "
    "Verify facts, clauses and jurisdiction-specific "
    "requirements before use."
)