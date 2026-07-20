from pathlib import Path


def test_readme_documents_the_v1_security_contract() -> None:
    readme = Path("README.md").read_text()

    for text in ("Python 3.11", "AES-256-GCM", "RSA-OAEP", "0.x ciphertexts are not supported"):
        assert text in readme


def test_token_format_document_matches_the_v1_contract() -> None:
    token_format = Path("docs/token-format.md").read_text()

    for text in ("`v`", "`ek`", "`n`", "`ct`", "AES-256-GCM", "RSA-OAEP-SHA-256"):
        assert text in token_format


def test_ci_covers_all_supported_python_versions() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text()

    for version in ('"3.11"', '"3.12"', '"3.13"', '"3.14"'):
        assert version in workflow
