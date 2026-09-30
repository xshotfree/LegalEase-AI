from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "running"
    )


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "healthy"
    )


def test_document_types():

    response = client.get(
        "/document-types"
    )

    assert response.status_code == 200

    assert (
        "Non-Disclosure Agreement"
        in response.json()["document_types"]
    )


def test_generate_demo():

    from backend.routes import generator

    generator.settings.gemini_api_key = ""

    generator.client = None

    response = client.post(

        "/generate",

        json={

            "document_type":
                "Non-Disclosure Agreement",

            "parties":
                "Alice (Disclosing Party), "
                "Example Corp (Receiving Party)",

            "terms":
                "Protect confidential information; "
                "Use information only for business purposes",

            "effective_date":
                "30 September 2026",

            "additional_instructions":
                "Use clear language."
        }
    )


    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True

    assert (
        body["provider"]
        == "local-demo"
    )

    assert (
        "NON-DISCLOSURE AGREEMENT"
        in body["document"]
    )


def test_generate_validation():

    response = client.post(

        "/generate",

        json={

            "document_type":
                "Contract",

            "parties":
                "",

            "terms":
                "Payment within 30 days",

            "effective_date":
                "30 September 2026"
        }
    )

    assert response.status_code == 422