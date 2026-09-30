from backend.services.document_service import (
    format_html_preview,
    make_docx,
    make_pdf,
    make_txt,
    sanitize_text,
)


def test_sanitize_text():

    value = sanitize_text(
        "Hello\u2014world\u201c!"
    )

    assert value == 'Hello-world"!'


def test_txt_export():

    result = make_txt(
        "LegalEase document"
    )

    assert (
        result
        == b"LegalEase document"
    )


def test_docx_export():

    result = make_docx(

        "EMPLOYMENT CONTRACT\n\n"
        "1. Compensation: [INSERT AMOUNT]",

        "Employment Contract",

        "Compensation must be specified; "
        "Notice period must be specified"
    )

    assert result.startswith(
        b"PK"
    )

    assert len(result) > 1000


def test_pdf_export():

    result = make_pdf(

        "AGREEMENT\n\n"
        "1. Payment within 30 days.",

        "Agreement"
    )

    assert result.startswith(
        b"%PDF"
    )

    assert len(result) > 500


def test_html_preview():

    result = format_html_preview(
        "<script>alert(1)</script>"
    )

    assert (
        "&lt;script&gt;"
        in result
    )