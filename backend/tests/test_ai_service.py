import os
import tempfile
from unittest.mock import patch, MagicMock
from services.ai_service import _ensure_audio, _split_audio, AUDIO_EXTENSIONS


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
        path = make_temp_file(".avi")
        with patch.dict("sys.modules", {"pydub": mock_pydub_module()}):
            result = _ensure_audio(path)
        assert result != path
        assert result.endswith(".mp3")
        assert os.path.isfile(result)
        os.remove(path)
        os.remove(result)

    def test_original_path_not_removed(self):
        path = make_temp_file(".avi")
        with patch.dict("sys.modules", {"pydub": mock_pydub_module()}):
            result = _ensure_audio(path)
        assert os.path.isfile(path)
        os.remove(path)
        os.remove(result)


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
