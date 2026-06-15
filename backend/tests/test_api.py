import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

@pytest.fixture
def mock_transcribe():
    with patch("main.transcribe_audio", new_callable=AsyncMock) as m:
        m.return_value = "This is a test transcript."
        yield m

@pytest.fixture
def mock_generate():
    with patch("main.generate_study_materials", new_callable=AsyncMock) as m:
        m.return_value = {
            "summary": "Test summary.",
            "notes": ["Note 1", "Note 2"],
            "quiz": [
                {
                    "question": "Q1?",
                    "options": ["A", "B", "C", "D"],
                    "answer": "A"
                }
            ]
        }
        yield m

class TestHealth:
    def test_health_endpoint(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

class TestTranscribe:
    def test_transcribe_invalid_extension(self, client: TestClient):
        response = client.post("/transcribe", files={"file": ("test.txt", b"hello", "text/plain")})
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]

    def test_transcribe_success(self, client: TestClient, mock_transcribe):
        response = client.post("/transcribe", files={"file": ("test.mp3", b"fake audio data", "audio/mpeg")})
        assert response.status_code == 200
        data = response.json()
        assert data["transcript"] == "This is a test transcript."
        assert data["filename"] == "test.mp3"

class TestGenerate:
    def test_generate_success(self, client: TestClient, mock_generate):
        response = client.post("/generate", json={
            "filename": "test.mp3",
            "transcript": "Some transcript content."
        })
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.mp3"
        assert data["materials"]["summary"] == "Test summary."
        assert len(data["materials"]["quiz"]) == 1

    def test_generate_empty_transcript(self, client: TestClient, mock_generate):
        response = client.post("/generate", json={
            "filename": "test.mp3",
            "transcript": ""
        })
        assert response.status_code == 200

class TestHistory:
    def test_empty_history(self, client: TestClient):
        response = client.get("/history")
        assert response.status_code == 200
        assert response.json() == []

    def test_history_after_creation(self, client: TestClient, mock_transcribe, mock_generate):
        client.post("/transcribe", files={"file": ("test.mp3", b"data", "audio/mpeg")})
        client.post("/generate", json={"filename": "test.mp3", "transcript": "data"})

        response = client.get("/history")
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert items[0]["filename"] == "test.mp3"

    def test_get_lecture_by_id(self, client: TestClient, mock_transcribe, mock_generate):
        client.post("/transcribe", files={"file": ("test.mp3", b"data", "audio/mpeg")})
        gen = client.post("/generate", json={"filename": "test.mp3", "transcript": "data"})
        lecture_id = gen.json()["id"]

        response = client.get(f"/history/{lecture_id}")
        assert response.status_code == 200
        assert response.json()["id"] == lecture_id

    def test_get_lecture_not_found(self, client: TestClient):
        response = client.get("/history/999")
        assert response.status_code == 404

    def test_delete_lecture(self, client: TestClient, mock_transcribe, mock_generate):
        client.post("/transcribe", files={"file": ("test.mp3", b"data", "audio/mpeg")})
        gen = client.post("/generate", json={"filename": "test.mp3", "transcript": "data"})
        lecture_id = gen.json()["id"]

        response = client.delete(f"/history/{lecture_id}")
        assert response.status_code == 200

        response = client.get(f"/history/{lecture_id}")
        assert response.status_code == 404

class TestPdfExport:
    def test_export_nonexistent_lecture(self, client: TestClient):
        response = client.get("/export-pdf/999")
        assert response.status_code == 404

    def test_export_pdf(self, client: TestClient, mock_transcribe, mock_generate):
        client.post("/transcribe", files={"file": ("test.mp3", b"data", "audio/mpeg")})
        gen = client.post("/generate", json={"filename": "test.mp3", "transcript": "data"})
        lecture_id = gen.json()["id"]

        response = client.get(f"/export-pdf/{lecture_id}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
