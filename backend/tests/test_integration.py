import os
import tempfile
from unittest.mock import patch, AsyncMock, MagicMock
import pytest


pytestmark = pytest.mark.asyncio


class TestTranscribeIntegration:
    async def test_transcribe_full_flow(self):
        from services.ai_service import transcribe_audio

        fd, audio_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        with patch("services.ai_service._ensure_audio", return_value=audio_path):
            with patch("services.ai_service._split_audio", return_value=[audio_path]):
                with patch("services.ai_service.client.audio.transcriptions.create", new_callable=AsyncMock) as mock_groq:
                    mock_groq.return_value = "Test transcript."
                    result = await transcribe_audio("/tmp/dummy.mp3")

        assert result == "Test transcript."
        assert not os.path.isfile(audio_path)

    async def test_transcribe_with_chunking(self):
        from services.ai_service import transcribe_audio

        fd1, audio_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd1)
        fd2, chunk_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd2)

        with patch("services.ai_service._ensure_audio", return_value=audio_path):
            with patch("services.ai_service._split_audio", return_value=[chunk_path]):
                with patch("services.ai_service.client.audio.transcriptions.create", new_callable=AsyncMock) as mock_groq:
                    mock_groq.return_value = "Chunk transcript."
                    result = await transcribe_audio("/tmp/dummy.mp3")

        assert result == "Chunk transcript."
        assert not os.path.isfile(chunk_path)


class TestGenerateIntegration:
    async def test_generate_full_flow(self):
        from services.ai_service import generate_study_materials

        raw_json = '{"summary": "Sum.", "notes": ["N1"], "quiz": [{"question": "Q?", "options": ["A", "B"], "answer": "A"}]}'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_json))]

        with patch("services.ai_service.client.chat.completions.create", new_callable=AsyncMock) as mock_groq:
            mock_groq.return_value = mock_response
            result = await generate_study_materials("Some transcript.")

        assert result["summary"] == "Sum."
        assert result["notes"] == ["N1"]
        assert result["quiz"][0]["answer"] == "A"

    async def test_generate_with_normalized_answer(self):
        from services.ai_service import generate_study_materials

        raw_json = '{"summary": "S.", "notes": ["N"], "quiz": [{"question": "Q?", "options": ["A. Mitosis", "B. Meiosis"], "answer": "A"}]}'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=raw_json))]

        with patch("services.ai_service.client.chat.completions.create", new_callable=AsyncMock) as mock_groq:
            mock_groq.return_value = mock_response
            result = await generate_study_materials("X.")

        assert result["quiz"][0]["answer"] == "A. Mitosis"

    async def test_generate_invalid_json_raises(self):
        from services.ai_service import generate_study_materials

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="not json"))]

        with patch("services.ai_service.client.chat.completions.create", new_callable=AsyncMock) as mock_groq:
            mock_groq.return_value = mock_response
            with pytest.raises(ValueError, match="Failed to generate valid study materials"):
                await generate_study_materials("Test.")
