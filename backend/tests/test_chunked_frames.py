"""
Tests for Epic 01.B7: Chunked Binary Frames
"""

import pytest
import sys
from pathlib import Path
import tempfile
import numpy as np

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.chunked_frames import (
    ChunkedFrameWriter,
    ChunkedFrameReader,
    ChunkedFrameIterator,
)


@pytest.fixture
def temp_chunk_dir():
    """Create temporary directory for chunks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_frames():
    """Generate sample RGB frames for testing."""
    frames = []
    for i in range(250):  # 2.5 chunks at 100 frames per chunk
        # Create varied frames for testing
        frame = np.ones((50, 100, 3), dtype=np.uint8) * (100 + i % 100)
        frames.append(frame)
    return frames


class TestChunkedFrameWriter:
    """Test frame writing to chunks."""
    
    def test_write_single_frame(self, temp_chunk_dir, sample_frames):
        """Epic 01.B7: Write single frame to chunk."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frame(sample_frames[0])
        chunk_paths = writer.finalize()
        
        assert len(chunk_paths) == 1
        assert Path(chunk_paths[0]).exists()
    
    def test_write_multiple_frames(self, temp_chunk_dir, sample_frames):
        """Write multiple frames across chunks."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        # Should have 3 chunks: 100 + 100 + 50
        assert len(chunk_paths) == 3
        for path in chunk_paths:
            assert Path(path).exists()
    
    def test_write_frames_respects_chunk_size(self, temp_chunk_dir, sample_frames):
        """Chunk size should be respected."""
        chunk_size = 50
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=chunk_size)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        # 250 frames / 50 per chunk = 5 chunks
        assert len(chunk_paths) == 5
    
    def test_chunk_file_size(self, temp_chunk_dir, sample_frames):
        """Verify chunk file sizes are correct."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames[:100])  # Exactly one chunk
        chunk_paths = writer.finalize()
        
        chunk_path = Path(chunk_paths[0])
        expected_size = 100 * 50 * 100 * 3  # 100 frames * 50h * 100w * 3 bytes
        assert chunk_path.stat().st_size == expected_size


class TestChunkedFrameReader:
    """Test frame reading from chunks."""
    
    def test_read_single_frame(self, temp_chunk_dir, sample_frames):
        """Epic 01.B7: Read single frame by index."""
        # Write frames
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        # Read frame
        reader = ChunkedFrameReader(chunk_paths)
        frame = reader.read_frame(42)
        
        assert frame.shape == (50, 100, 3)
        assert frame.dtype == np.uint8
        # Verify it matches original
        np.testing.assert_array_equal(frame, sample_frames[42])
    
    def test_read_frame_range(self, temp_chunk_dir, sample_frames):
        """Read range of frames."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        reader = ChunkedFrameReader(chunk_paths)
        frames = reader.read_frames(100, 150)
        
        assert len(frames) == 50
        for i, frame in enumerate(frames):
            np.testing.assert_array_equal(frame, sample_frames[100 + i])
    
    def test_read_across_chunk_boundary(self, temp_chunk_dir, sample_frames):
        """Read frames spanning multiple chunks."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        reader = ChunkedFrameReader(chunk_paths)
        # Read from middle of first chunk to middle of third chunk
        frames = reader.read_frames(80, 120)
        
        assert len(frames) == 40
        for i, frame in enumerate(frames):
            np.testing.assert_array_equal(frame, sample_frames[80 + i])
    
    def test_read_all_frames(self, temp_chunk_dir, sample_frames):
        """Read all frames at once."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        reader = ChunkedFrameReader(chunk_paths)
        frames = reader.read_all_frames()
        
        assert len(frames) == len(sample_frames)
        for i, frame in enumerate(frames):
            np.testing.assert_array_equal(frame, sample_frames[i])
    
    def test_total_frames_count(self, temp_chunk_dir, sample_frames):
        """Verify total frame count."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        reader = ChunkedFrameReader(chunk_paths)
        assert reader.total_frames == len(sample_frames)


class TestChunkedFrameIterator:
    """Test progressive frame iteration."""
    
    def test_iterate_all_frames(self, temp_chunk_dir, sample_frames):
        """Epic 01.B7: Progressive loading via iterator."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        reader = ChunkedFrameReader(chunk_paths)
        iterator = ChunkedFrameIterator(reader, batch_size=50)
        
        collected_frames = []
        for batch in iterator:
            collected_frames.extend(batch)
        
        assert len(collected_frames) == len(sample_frames)
        for i, frame in enumerate(collected_frames):
            np.testing.assert_array_equal(frame, sample_frames[i])
    
    def test_iterate_with_batches(self, temp_chunk_dir, sample_frames):
        """Verify batching works correctly."""
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=100)
        writer.write_frames(sample_frames)
        chunk_paths = writer.finalize()
        
        reader = ChunkedFrameReader(chunk_paths)
        iterator = ChunkedFrameIterator(reader, batch_size=30)
        
        batch_count = 0
        for batch in iterator:
            batch_count += 1
            assert len(batch) in [30, 10]  # Last batch will have 10
        
        # 250 / 30 = 8 full batches + 1 partial = 9 total
        assert batch_count == 9


class TestMemoryEfficiency:
    """Verify chunked frames reduce memory pressure."""
    
    def test_chunked_vs_monolithic(self, temp_chunk_dir):
        """Demonstrate memory efficiency of chunking."""
        # Create large number of frames
        large_frame_count = 1000
        chunk_size = 100
        
        writer = ChunkedFrameWriter(temp_chunk_dir, chunk_size=chunk_size)
        
        # Write frames one at a time (monolithic approach would load all)
        for i in range(large_frame_count):
            frame = np.ones((50, 100, 3), dtype=np.uint8) * (i % 256)
            writer.write_frame(frame)
        
        chunk_paths = writer.finalize()
        
        # Verify we have 10 chunks (1000 / 100)
        assert len(chunk_paths) == 10
        
        # Can read progressively without loading all into memory
        reader = ChunkedFrameReader(chunk_paths)
        iterator = ChunkedFrameIterator(reader, batch_size=10)
        
        batch_count = 0
        for batch in iterator:
            batch_count += 1
            assert len(batch) == 10
        
        assert batch_count == 100  # 1000 frames / 10 per batch


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
