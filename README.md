# Chroma-Vue

A fast, multiprocessed video color timeline generator that extracts the average color from each frame of a video and creates a beautiful color timeline visualization.

## Sample Output

I used this [Youtube video](https://www.youtube.com/watch?v=WO2b03Zdu4Q) for a sample testing. The sample output image shown in the video is available at `/sample/sample.png` in this repository.

Also, there is a sample of the movie "La La Land" as well. (`/sample/La.La.Land.2016.720p_3000_800.png`)

## Features

- **High Performance**: Utilizes multiprocessing to maximize CPU usage
- **Memory Efficient**: Processes video in chunks to handle large files
- **Customizable Output**: Configurable image dimensions
- **Progress Tracking**: Real-time progress bar with frame processing rate
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Prerequisites

### System Requirements
- Python 3.6+
- FFmpeg (must be installed and accessible from command line)
- Sufficient RAM for your video file size

### Installing FFmpeg

**Windows:**
```bash
# Using chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python chroma-vue.py your_video.mp4
```

With custom options:
```bash
python chroma-vue.py your_video.mp4 --width 4000 --height 1000 --workers 16
```

### Command Line Arguments

- `video`: Path to the input video file (required)
- `--width`: Final image width in pixels (default: 3000)
- `--height`: Final image height in pixels (default: 800)
- `--workers`: Number of worker processes (default: CPU count)

## Performance Benchmarks

Tests performed on WSL2 with the following specifications:
- **CPU**: Intel Core i7-1065G7 @ 1.30GHz (8 logical cores)
- **RAM**: 16GB total, 8068MB allocated to WSL2
- **Workers**: 8 processes
- **Swap**: 2048MB

| Resolution | File Size | File Duration | FPS | Total Frames | Processing Time(mm:ss) | Speed (fps) |
|------------|-----------|----------|-----|--------------|----------|-------------|
| 720p       | 932 MB    | 7668.13s | 23.98 | 183,850      | 6:27           | 474.67      |
| 1080p      | 1.93 GB   | 7668.13s | 23.98 | 183,850      | 9:01           | 339.29      |
| 4K (2160p) | 5.70 GB   | 7675.92s | 23.98 | 184,038      | 45:59          | 66.69       |

### Performance Notes

- **720p**: Excellent performance, ideal for quick previews
- **1080p**: Good performance, suitable for high-quality timelines
- **4K**: Slower but manageable, recommended for detailed analysis of high-resolution content
- Processing speed decreases significantly with higher resolutions due to increased decoding overhead
- Memory usage scales with video duration and worker count, not resolution

## Output

The script generates a PNG image with the filename format:
```
{original_filename}_{width}_{height}.png
```

Each column in the output image represents the average color of frames from that time segment in the video, creating a visual timeline of the video's color palette progression.

## Tips for Optimal Performance

1. **Worker Count**: Start with your CPU core count. For I/O bound operations, you might benefit from more workers
2. **Memory**: Ensure you have enough RAM. Each worker processes a chunk of the video simultaneously
3. **Storage**: Use fast storage (SSD) for better I/O performance
4. **Video Format**: H.264 videos generally process faster than H.265/HEVC

## Troubleshooting

**"ffmpeg not found"**: Ensure FFmpeg is installed and in your system PATH

**"Out of memory"**: Reduce the number of workers or ensure you have sufficient RAM

**Slow processing**: Try adjusting the worker count or check if your storage is the bottleneck

**Terminal doesn't show typing after running**: This was a known issue that has been fixed in the latest version. The problem was caused by FFmpeg/FFprobe interfering with terminal stdin. If you still experience this issue:
1. The script now automatically restores terminal settings on exit
2. If your terminal is still unresponsive, manually fix it with:
   - Linux/macOS: Type `reset` or `stty sane` and press Enter
   - Windows: Press Ctrl+C, type `cls` and press Enter

**Terminal becomes unresponsive after running**: This was caused by improper multiprocessing cleanup and has been fixed. If you still experience this issue:
1. Make sure you're using the updated version of the script
2. Try reducing the number of workers with `--workers 4`
3. On Windows, ensure you're running the script directly (not in some IDEs)

**Script hangs on exit**: Press Ctrl+C to interrupt gracefully. The script now includes proper cleanup routines.

**Process doesn't respond to Ctrl+C**: This should be fixed in the current version. If it persists, you may need to force-kill the process and restart your terminal.

## Dependencies

- `numpy`: Numerical operations for color averaging
- `Pillow`: Image creation and manipulation
- `tqdm`: Progress bar display

## Recent Updates

### Version 1.1
- **MAJOR FIX**: Resolved terminal input visibility issue (typing not showing after script execution)
- Fixed FFmpeg/FFprobe stdin interference with terminal
- Added automatic terminal state restoration on exit
- Improved subprocess isolation to prevent terminal corruption
- Enhanced cross-platform terminal handling

## License

This project is open source. Feel free to modify and distribute as needed.