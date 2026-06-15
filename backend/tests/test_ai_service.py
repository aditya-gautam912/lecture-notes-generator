import os
import tempfile
import copy
from unittest.mock import patch, MagicMock
from services.ai_service import _ensure_audio, _split_audio, _normalize_quiz, AUDIO_EXTENSIONS, VIDEO_EXTENSIONS


def make_temp_file(suffix: str, content: bytes = b"data") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    with open(path, "wb") as f:
        f.write(content)
    return path


def mock_pydub_module():
    mock_audio = MagicMock()
    mock_audio.__len__.return_value = 60000
    mock_audio.__getitem__.return_value = mock_audio
    mock_audio.export.return_value = None
    mock_module = MagicMock()
    mock_module.AudioSegment.from_file.return_value = mock_audio
    return mock_module


class TestEnsureAudio:
    def test_returns_same_path_for_audio_extensions(self):
        for ext in AUDIO_EXTENSIONS:
            path = make_temp_file(ext)
            result = _ensure_audio(path)
            assert result == path
            os.remove(path)

    def test_converts_video_to_mp3(self):
        for ext in VIDEO_EXTENSIONS:
            path = make_temp_file(ext)
            with patch.dict("sys.modules", {"pydub": mock_pydub_module()}):
                result = _ensure_audio(path)
            assert result != path, f"Failed for {ext}"
            assert result.endswith(".mp3"), f"Expected .mp3 for {ext}"
            assert os.path.isfile(result), f"Output missing for {ext}"
            os.remove(path)
            os.remove(result)

    def test_original_path_not_removed(self):
        for ext in VIDEO_EXTENSIONS:
            path = make_temp_file(ext)
            with patch.dict("sys.modules", {"pydub": mock_pydub_module()}):
                result = _ensure_audio(path)
            assert os.path.isfile(path), f"Original removed for {ext}"
            os.remove(path)
            os.remove(result)


class TestNormalizeQuiz:
    def test_exact_match(self):
        quiz = [{"question": "Q?", "options": ["Mitosis", "Meiosis"], "answer": "Mitosis"}]
        result = _normalize_quiz(quiz)
        assert result[0]["answer"] == "Mitosis"

    def test_answer_is_letter_prefix(self):
        quiz = [{"question": "Q?", "options": ["A. Mitosis", "B. Meiosis", "C. Budding", "D. Fission"], "answer": "A"}]
        result = _normalize_quiz(quiz)
        assert result[0]["answer"] == "A. Mitosis"

    def test_answer_is_option_start(self):
        quiz = [{"question": "Q?", "options": ["Binary Fission", "Mitosis Phase", "Cytokinesis"], "answer": "Mitosis"}]
        result = _normalize_quiz(quiz)
        assert result[0]["answer"] == "Mitosis Phase"

    def test_no_match_keeps_original(self):
        quiz = [{"question": "Q?", "options": ["Alpha", "Beta", "Gamma"], "answer": "Delta"}]
        result = _normalize_quiz(quiz)
        assert result[0]["answer"] == "Delta"

    def test_answer_starts_with_option(self):
        quiz = [{"question": "Q?", "options": ["Mitosis", "Meiosis"], "answer": "Mitosis involves cell division"}]
        result = _normalize_quiz(quiz)
        assert result[0]["answer"] == "Mitosis"

    def test_multiple_questions(self):
        quiz = [
            {"question": "Q1?", "options": ["X. One", "Y. Two", "Z. Three"], "answer": "Y"},
            {"question": "Q2?", "options": ["Red", "Blue", "Green"], "answer": "Blue"},
        ]
        result = _normalize_quiz(quiz)
        assert result[0]["answer"] == "Y. Two"
        assert result[1]["answer"] == "Blue"

    def test_does_not_mutate_input(self):
        quiz = [{"question": "Q?", "options": ["A. One", "B. Two"], "answer": "A"}]
        original = copy.deepcopy(quiz)
        _normalize_quiz(quiz)
        assert quiz == original


class TestSplitAudio:
    def test_returns_single_chunk_for_small_file(self):
        path = make_temp_file(".mp3", b"x" * 1024)
        chunks = _split_audio(path)
        assert chunks == [path]
        os.remove(path)

    def test_splits_large_file(self):
        path = make_temp_file(".mp3")
        with patch.dict("sys.modules", {"pydub": mock_pydub_module()}):
            with patch("os.path.getsize") as mock_size:
                from services.ai_service import CHUNK_SIZE_MB
                mock_size.side_effect = [(CHUNK_SIZE_MB + 1) * 1024 * 1024, (CHUNK_SIZE_MB + 1) * 1024 * 1024, 1024]
                chunks = _split_audio(path)

        assert len(chunks) > 1
        for c in chunks:
            assert c.endswith(".mp3")
            if os.path.exists(c):
                os.remove(c)
        assert path not in chunks
