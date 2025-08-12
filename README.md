# Chroma-Vue

A fast, multiprocessed video color timeline generator that extracts the average color from each frame of a video and creates a beautiful color timeline visualization.

## Sample Output

I used this [Youtube video](https://www.youtube.com/watch?v=WO2b03Zdu4Q) for a sample testing. The sample output image shown in the video is available at `/sample/sample.png` in this repository.

Also, there is a sample of the movie "La La Land" as well. (`/sample/La.La.Land.2016.720p_3000_800.png`)

### Movie Examples

Below are examples of color timelines generated from various movies:

| Movie | Color Timeline |
|-------|----------------|
| **Blade Runner 2049** | ![Blade Runner 2049](movies/Blade.Runner.2049_3000_800.png) |
| **Cars** | ![Cars](movies/Cars_3000_800.png) |
| **Fight Club** | ![Fight Club](movies/Fight.Club_3000_800.png) |
| **John Wick Chapter 2** | ![John Wick Chapter 2](movies/John.Wick.Chapter.2_3000_800.png) |
| **John Wick Chapter 3** | ![John Wick Chapter 3](movies/John.Wick.Chapter.3_3000_800.png) |
| **Mad Max: Fury Road** | ![Mad Max: Fury Road](movies/Mad.Max.Fury.Road_3000_800.png) |
| **Midsommar** | ![Midsommar](movies/Midsommar_3000_800.png) |
| **Spider-Man: Into the Spider-Verse** | ![Spider-Man: Into the Spider-Verse](movies/Spider-Man.Into.The.Spider-Verse_3000_800.png) |
| **The Grand Budapest Hotel** | ![The Grand Budapest Hotel](movies/The.Grand.Budapest.Hotel_3000_800.png) |
| **The Matrix** | ![The Matrix](movies/The.Matrix_3000_800.png) |
| **Tron: Legacy** | ![Tron: Legacy](movies/Tron.Legacy_3000_800.png) |

*All examples were generated at 3000x800 resolution using the default settings.*

## Features

- **High Performance**: Utilizes multiprocessing to maximize CPU usage
- **Memory Efficient**: Processes video in chunks to handle large files
- **Customizable Output**: Configurable image dimensions
- **Progress Tracking**: Real-time progress bar with frame processing rate
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Docker Support**: Run anywhere with Docker, no local dependencies required

## Quick Start with Docker (Recommended)

The easiest way to use Chroma-Vue is with Docker. No need to install Python, FFmpeg, or manage dependencies!

### Prerequisites for Docker
- Docker installed on your system ([Get Docker](https://docs.docker.com/get-docker/))
- Your video file accessible on your local machine

### Pull the Docker Image

First, pull the pre-built image from Docker Hub:

```bash
docker pull shmdtt/chroma-vue
```

Alternatively, you can pull and run in one command (Docker will automatically pull if the image doesn't exist locally).

### Docker Usage

**Basic usage:**
```bash
docker run --rm -v /path/to/your/videos:/videos shmdtt/chroma-vue your_video.mp4
```

**With custom options:**
```bash
docker run --rm -v /path/to/your/videos:/videos shmdtt/chroma-vue your_video.mp4 --width 4000 --height 1000 --workers 8
```

#### Platform-Specific Examples

**Windows Command Prompt:**
```cmd
# Basic usage
docker run --rm -v C:\Users\YourName\Videos:/videos shmdtt/chroma-vue my_video.mp4

# With custom options
docker run --rm -v C:\Users\YourName\Videos:/videos shmdtt/chroma-vue my_video.mp4 --width 2000 --height 600

# Using current directory (if video is in current folder)
docker run --rm -v %cd%:/videos shmdtt/chroma-vue my_video.mp4
```

**Windows PowerShell:**
```powershell
# Basic usage
docker run --rm -v C:\Users\YourName\Videos:/videos shmdtt/chroma-vue my_video.mp4

# With custom options
docker run --rm -v C:\Users\YourName\Videos:/videos shmdtt/chroma-vue "my video with spaces.mp4" --width 2000

# Using current directory
docker run --rm -v ${PWD}:/videos shmdtt/chroma-vue my_video.mp4
```

**macOS/Linux:**
```bash
# Basic usage
docker run --rm -v ~/Videos:/videos shmdtt/chroma-vue my_video.mp4

# With custom options
docker run --rm -v ~/Videos:/videos shmdtt/chroma-vue my_video.mp4 --width 4000 --height 1000

# Using current directory
docker run --rm -v $(pwd):/videos shmdtt/chroma-vue my_video.mp4
```

## Common Docker Commands

### Quick Reference

**Process a video in current directory:**
```bash
# Linux/macOS
docker run --rm -v $(pwd):/videos shmdtt/chroma-vue "your_video.mp4"

# Windows Command Prompt  
docker run --rm -v %cd%:/videos shmdtt/chroma-vue "your_video.mp4"

# Windows PowerShell
docker run --rm -v ${PWD}:/videos shmdtt/chroma-vue "your_video.mp4"
```

**Custom dimensions:**
```bash
# Linux/macOS
docker run --rm -v $(pwd):/videos shmdtt/chroma-vue "your_video.mp4" --width 2000 --height 400

# Windows Command Prompt
docker run --rm -v %cd%:/videos shmdtt/chroma-vue "your_video.mp4" --width 2000 --height 400

# Windows PowerShell  
docker run --rm -v ${PWD}:/videos shmdtt/chroma-vue "your_video.mp4" --width 2000 --height 400
```

**Limit CPU usage (useful for large files):**
```bash
# Linux/macOS
docker run --rm -v $(pwd):/videos shmdtt/chroma-vue "your_video.mp4" --workers 4

# Windows Command Prompt
docker run --rm -v %cd%:/videos shmdtt/chroma-vue "your_video.mp4" --workers 4

# Windows PowerShell
docker run --rm -v ${PWD}:/videos shmdtt/chroma-vue "your_video.mp4" --workers 4
```

# Building the Docker Image Yourself

If you want to build the image yourself instead of using the pre-built one:

```bash
# Clone the repository
git clone <repository-url>
cd chroma-vue

# Build the Docker image
docker build -t chromavue .

# Run with your video (Linux/macOS)
docker run --rm -v $(pwd):/videos chromavue your_video.mp4

# Run with your video (Windows Command Prompt)
docker run --rm -v %cd%:/videos chromavue your_video.mp4

# Run with your video (Windows PowerShell)
docker run --rm -v ${PWD}:/videos chromavue your_video.mp4
```

### Docker Volume Mounting

The Docker container expects videos to be mounted to `/videos` inside the container. Here's how the volume mounting works:

- **Host path**: The directory on your computer containing video files
- **Container path**: Always `/videos`
- **Syntax**: `-v /host/path:/videos`

**Examples:**
```bash
# Linux/macOS: If your video is in /home/user/Downloads/
docker run --rm -v /home/user/Downloads:/videos shmdtt/chroma-vue video.mp4

# Windows Command Prompt: If your video is in C:\Users\John\Desktop\
docker run --rm -v C:\Users\John\Desktop:/videos shmdtt/chroma-vue video.mp4

# Windows PowerShell: Using current directory
docker run --rm -v ${PWD}:/videos shmdtt/chroma-vue video.mp4

# Process multiple videos with different settings
docker run --rm -v ~/MyVideos:/videos shmdtt/chroma-vue video1.mp4 --width 2000
docker run --rm -v ~/MyVideos:/videos shmdtt/chroma-vue video2.mp4 --height 600

# Handle videos with spaces in filename (use quotes)
docker run --rm -v "C:\My Videos":/videos shmdtt/chroma-vue "my video file.mp4"
```

## Local Installation (Alternative)

If you prefer to run without Docker:

### Prerequisites

#### System Requirements
- Python 3.6+
- FFmpeg (must be installed and accessible from command line)
- Sufficient RAM for your video file size

#### Installing FFmpeg

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

### Installation Steps

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

### Local Usage

Basic usage:
```bash
python chroma-vue.py your_video.mp4
```

With custom options:
```bash
python chroma-vue.py your_video.mp4 --width 4000 --height 1000 --workers 16
```

## Command Line Arguments

- `video`: Path to the input video file (required)
- `--width`: Final image width in pixels (default: 3000)
- `--height`: Final image height in pixels (default: 800)
- `--workers`: Number of worker processes (default: CPU count)

### Docker-Specific Notes

- The output image will be saved in the same directory as your input video
- Container runs as non-root user for security
- All processing happens inside the container - no temporary files on host
- Container automatically cleans up after processing

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
5. **Docker**: Docker adds minimal overhead but provides consistency across platforms

## Troubleshooting

### Docker Issues

**"docker: command not found"**: Install Docker from [docker.com](https://docs.docker.com/get-docker/)

**"permission denied"**: On Linux, you might need to add your user to the docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in, or restart your session
```

**Volume mounting issues**: Ensure your path is absolute and the directory exists:
```bash
# Linux/macOS: Good - Absolute path
docker run --rm -v /home/user/Videos:/videos shmdtt/chroma-vue video.mp4

# Windows Command Prompt: Good - Absolute path
docker run --rm -v C:\Users\YourName\Videos:/videos shmdtt/chroma-vue video.mp4

# Windows PowerShell: Good - Absolute path  
docker run --rm -v C:\Users\YourName\Videos:/videos shmdtt/chroma-vue video.mp4

# Bad: Relative path (may not work consistently)
docker run --rm -v ./Videos:/videos shmdtt/chroma-vue video.mp4
```

**Windows-specific path issues**: 
- Use forward slashes in the container path: `/videos` (not `\videos`)
- For paths with spaces, use quotes: `"C:\My Videos"`
- Ensure Docker Desktop is running and has access to your drive

**File not found in container**: Make sure your video file is in the mounted directory:
```bash
# List files in mounted directory (Linux/macOS)
docker run --rm -v $(pwd):/videos --entrypoint ls shmdtt/chroma-vue -la /videos

# List files in mounted directory (Windows Command Prompt)
docker run --rm -v %cd%:/videos --entrypoint ls shmdtt/chroma-vue -la /videos

# List files in mounted directory (Windows PowerShell)
docker run --rm -v ${PWD}:/videos --entrypoint ls shmdtt/chroma-vue -la /videos
```

### General Issues

**"ffmpeg not found"** (local installation): Ensure FFmpeg is installed and in your system PATH

**"Out of memory"**: Reduce the number of workers or ensure you have sufficient RAM

**Slow processing**: Try adjusting the worker count or check if your storage is the bottleneck

**Terminal doesn't show typing after running**: This was a known issue that has been fixed in the latest version. The problem was caused by FFmpeg/FFprobe interfering with terminal stdin. If you still experience this issue:
1. The script now automatically restores terminal settings on exit
2. If your terminal is still unresponsive, manually fix it with:
   - Linux/macOS: Type `reset` or `stty sane` and press Enter
   - Windows: Press Ctrl+C, type `cls` and press Enter

## Dependencies

### Docker (Included in image)
- Python 3.9
- FFmpeg
- All Python dependencies

### Local Installation
- `numpy`: Numerical operations for color averaging
- `Pillow`: Image creation and manipulation
- `tqdm`: Progress bar display

## Recent Updates

### Version 1.2
- **NEW**: Full Docker support with optimized container
- Added non-root user for enhanced security
- Improved cross-platform compatibility
- Streamlined installation process

### Version 1.1
- **MAJOR FIX**: Resolved terminal input visibility issue (typing not showing after script execution)
- Fixed FFmpeg/FFprobe stdin interference with terminal
- Added automatic terminal state restoration on exit
- Improved subprocess isolation to prevent terminal corruption
- Enhanced cross-platform terminal handling

## Contributing

Feel free to submit issues, feature requests, or pull requests. When reporting issues, please include:
- Your operating system
- Whether you're using Docker or local installation
- Video file format and size
- Error messages or unexpected behavior

## License

This project is open source. Feel free to modify and distribute as needed.