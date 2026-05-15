"""
Chunked Binary Frame Operations

Epic 01.B7: Split v2 frame payloads into short binary chunks stored in data/artifacts/
instead of one monolithic .bin file to reduce memory pressure and enable progressive loading.
"""

import os
import struct
from pathlib import Path
from typing import List, Optional, BinaryIO
import numpy as np


class ChunkedFrameWriter:
    """
    Writes RGB frames to binary chunks on disk.
    
    Each chunk contains multiple complete frames to reduce I/O overhead
    while maintaining manageable memory usage.
    """
    
    BYTES_PER_PIXEL = 3  # RGB
    CANVAS_WIDTH = 100
    CANVAS_HEIGHT = 50
    BYTES_PER_FRAME = CANVAS_WIDTH * CANVAS_HEIGHT * BYTES_PER_PIXEL  # 15,000 bytes
    
    def __init__(self, output_dir: str, chunk_size: int = 100):
        """
        Initialize frame writer.
        
        Args:
            output_dir: Directory to write chunks to
            chunk_size: Number of frames per chunk (default 100 frames ≈ 1.5 MB per chunk)
        """
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.chunk_index = 0
        self.frames_in_current_chunk = 0
        self.current_chunk_file: Optional[BinaryIO] = None
        self.chunk_paths: List[str] = []
    
    def write_frame(self, frame: np.ndarray) -> None:
        """
        Write a single RGB frame to current chunk.
        
        Args:
            frame: RGB frame array (100x50x3, dtype uint8)
        """
        # Ensure correct shape and dtype
        if frame.shape != (self.CANVAS_HEIGHT, self.CANVAS_WIDTH, 3):
            raise ValueError(f"Expected shape ({self.CANVAS_HEIGHT}, {self.CANVAS_WIDTH}, 3), got {frame.shape}")
        
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        
        # Open new chunk if needed
        if self.current_chunk_file is None or self.frames_in_current_chunk >= self.chunk_size:
            self._start_new_chunk()
        
        # Write frame as raw bytes
        frame_bytes = frame.tobytes()
        self.current_chunk_file.write(frame_bytes)
        self.frames_in_current_chunk += 1
    
    def write_frames(self, frames: List[np.ndarray]) -> None:
        """
        Write multiple frames to chunks.
        
        Args:
            frames: List of RGB frame arrays
        """
        for frame in frames:
            self.write_frame(frame)
    
    def finalize(self) -> List[str]:
        """
        Close current chunk and return list of chunk paths.
        
        Returns:
            List of relative paths to chunk files
        """
        if self.current_chunk_file is not None:
            self.current_chunk_file.close()
            self.current_chunk_file = None
        
        return self.chunk_paths
    
    def _start_new_chunk(self) -> None:
        """Start a new chunk file."""
        if self.current_chunk_file is not None:
            self.current_chunk_file.close()
        
        chunk_filename = f"chunk_{self.chunk_index}.bin"
        chunk_path = self.output_dir / chunk_filename
        
        self.current_chunk_file = open(chunk_path, 'wb')
        self.chunk_paths.append(str(chunk_path))
        
        self.chunk_index += 1
        self.frames_in_current_chunk = 0


class ChunkedFrameReader:
    """
    Reads RGB frames from binary chunks on disk.
    
    Supports random access and progressive loading of frame sequences.
    """
    
    BYTES_PER_PIXEL = 3  # RGB
    CANVAS_WIDTH = 100
    CANVAS_HEIGHT = 50
    BYTES_PER_FRAME = CANVAS_WIDTH * CANVAS_HEIGHT * BYTES_PER_PIXEL  # 15,000 bytes
    
    def __init__(self, chunk_paths: List[str]):
        """
        Initialize frame reader.
        
        Args:
            chunk_paths: List of paths to chunk files (in order)
        """
        self.chunk_paths = [Path(p) for p in chunk_paths]
        self.chunk_index = 0
        self.frames_per_chunk: List[int] = []
        self.total_frames = 0
        
        # Scan chunks to count frames
        for chunk_path in self.chunk_paths:
            if chunk_path.exists():
                chunk_size = chunk_path.stat().st_size
                frames_in_chunk = chunk_size // self.BYTES_PER_FRAME
                self.frames_per_chunk.append(frames_in_chunk)
                self.total_frames += frames_in_chunk
    
    def read_frame(self, frame_index: int) -> np.ndarray:
        """
        Read a single frame by index.
        
        Args:
            frame_index: 0-based frame index
            
        Returns:
            RGB frame array (100x50x3, dtype uint8)
        """
        if frame_index >= self.total_frames:
            raise IndexError(f"Frame index {frame_index} out of range (total: {self.total_frames})")
        
        # Find which chunk contains this frame
        cumulative = 0
        chunk_idx = 0
        frame_in_chunk_idx = frame_index
        
        for idx, frames_in_chunk in enumerate(self.frames_per_chunk):
            if cumulative + frames_in_chunk > frame_index:
                chunk_idx = idx
                frame_in_chunk_idx = frame_index - cumulative
                break
            cumulative += frames_in_chunk
        
        # Read from chunk
        chunk_path = self.chunk_paths[chunk_idx]
        with open(chunk_path, 'rb') as f:
            # Seek to frame position within chunk
            offset = frame_in_chunk_idx * self.BYTES_PER_FRAME
            f.seek(offset)
            
            # Read frame data
            frame_data = f.read(self.BYTES_PER_FRAME)
            if len(frame_data) != self.BYTES_PER_FRAME:
                raise IOError(f"Failed to read complete frame from chunk {chunk_idx}")
            
            # Convert to numpy array and reshape
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = frame.reshape((self.CANVAS_HEIGHT, self.CANVAS_WIDTH, 3))
            
            return frame
    
    def read_frames(self, start_index: int = 0, end_index: Optional[int] = None) -> List[np.ndarray]:
        """
        Read a range of frames.
        
        Args:
            start_index: Starting frame index (inclusive)
            end_index: Ending frame index (exclusive), or None for all remaining
            
        Returns:
            List of RGB frame arrays
        """
        if end_index is None:
            end_index = self.total_frames
        
        frames = []
        for i in range(start_index, min(end_index, self.total_frames)):
            frames.append(self.read_frame(i))
        
        return frames
    
    def read_all_frames(self) -> List[np.ndarray]:
        """
        Read all frames (be mindful of memory usage for large renders).
        
        Returns:
            List of all RGB frame arrays
        """
        return self.read_frames(0, self.total_frames)


class ChunkedFrameIterator:
    """
    Progressive frame iterator for streaming rendering.
    
    Yields frames in order, loading from disk as needed.
    """
    
    def __init__(self, reader: ChunkedFrameReader, batch_size: int = 1):
        """
        Initialize iterator.
        
        Args:
            reader: ChunkedFrameReader instance
            batch_size: Number of frames to load at once (1 for streaming)
        """
        self.reader = reader
        self.batch_size = batch_size
        self.current_index = 0
    
    def __iter__(self):
        """Return iterator."""
        self.current_index = 0
        return self
    
    def __next__(self) -> List[np.ndarray]:
        """Get next batch of frames."""
        if self.current_index >= self.reader.total_frames:
            raise StopIteration
        
        end_index = min(self.current_index + self.batch_size, self.reader.total_frames)
        frames = self.reader.read_frames(self.current_index, end_index)
        self.current_index = end_index
        
        return frames


# Example usage (for reference):
"""
# Writing chunked frames
writer = ChunkedFrameWriter('data/artifacts/song_1.canvas.chunks', chunk_size=100)
for frame in frame_generator():
    writer.write_frame(frame)
chunk_paths = writer.finalize()

# Reading chunked frames
reader = ChunkedFrameReader(chunk_paths)
frame_42 = reader.read_frame(42)  # Random access
frames_100_200 = reader.read_frames(100, 200)  # Range read

# Streaming frames
iterator = ChunkedFrameIterator(reader, batch_size=30)
for batch in iterator:
    # Process batch of 30 frames
    pass
"""
