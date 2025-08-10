import argparse
import subprocess
import multiprocessing
import numpy as np
from PIL import Image
from tqdm import tqdm
import time
import logging
import os
import sys
import signal
import atexit

# ---------- GLOBALS FOR SHARED STATE ----------
counter = None
total_frames = None


def init_worker(shared_counter, shared_total):
    """Initializer for workers to inherit shared counter and total frames."""
    global counter, total_frames
    counter = shared_counter
    total_frames = shared_total
    # Ignore SIGINT in worker processes to let main process handle cleanup
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def get_video_info(video_path):
    """Get duration (s) and fps using ffprobe."""
    logging.info(f"Probing video: {video_path}")
    # Duration
    duration_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    try:
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to get video duration: {e}")
        sys.exit(1)

    # FPS
    fps_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=r_frame_rate",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    try:
        fps_str = subprocess.check_output(fps_cmd).decode().strip()
        num, denom = fps_str.split("/")
        fps = float(num) / float(denom)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to get video FPS: {e}")
        sys.exit(1)

    total = int(duration * fps)
    logging.info(f"Video duration: {duration:.2f}s, FPS: {fps}, Total frames: {total}")
    return duration, fps, total


def process_chunk(args):
    """Worker: Extract average colors from a segment of the video."""
    start_time, duration, video_path = args

    cmd = [
        "ffmpeg",
        "-ss",
        str(start_time),
        "-t",
        str(duration),
        "-i",
        video_path,
        "-vf",
        "scale=1:1",
        "-f",
        "image2pipe",
        "-pix_fmt",
        "rgb24",
        "-vcodec",
        "rawvideo",
        "-threads",
        "1",  # important for multi-worker balance
        "-nostdin",  # Prevent ffmpeg from interfering with stdin
        "-loglevel",
        "quiet",  # Suppress ffmpeg output
        "-",
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,  # Prevent stdin interference
            preexec_fn=(
                os.setsid if os.name != "nt" else None
            ),  # Create new process group on Unix
        )
        colors = []
        frame_size = 3  # 1x1 RGB pixel = 3 bytes

        while True:
            raw = proc.stdout.read(frame_size)
            if len(raw) < frame_size:
                break
            r, g, b = raw
            colors.append((r, g, b))

            # Update shared counter
            with counter.get_lock():
                counter.value += 1

        proc.stdout.close()
        proc.wait()
        return colors
    except Exception as e:
        logging.error(f"Error in process_chunk: {e}")
        return []


def average_to_width(colors, final_width):
    """Average colors into exactly `final_width` columns."""
    total_frames = len(colors)
    if total_frames == 0:
        return []

    group_size = total_frames / final_width
    averaged_colors = []
    for i in range(final_width):
        start = int(i * group_size)
        end = int((i + 1) * group_size)
        if end <= start:
            end = start + 1
        group = colors[start:end]
        arr = np.array(group, dtype=np.float32)
        avg = tuple(np.mean(arr, axis=0).astype(np.uint8))
        averaged_colors.append(avg)
    return averaged_colors


def restore_terminal():
    """Restore terminal to normal state"""
    try:
        # Reset terminal settings
        if os.name != "nt":  # Unix/Linux/macOS
            os.system("stty sane")
        else:  # Windows
            os.system("echo off")
            # Force cursor to be visible
            print("\033[?25h", end="", flush=True)
    except:
        pass


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nInterrupt received, cleaning up...")
    restore_terminal()
    sys.exit(0)


def main():
    # Register terminal restoration function to run on exit
    atexit.register(restore_terminal)

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(
        description="Generate a color timeline image from a video.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument(
        "--width", type=int, default=3000, help="Final image width in pixels"
    )
    parser.add_argument(
        "--height", type=int, default=800, help="Final image height in pixels"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of worker processes",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    video_path = args.video
    if not os.path.exists(video_path):
        logging.error(f"Video file not found: {video_path}")
        sys.exit(1)

    logging.info(f"Video : {args.video}")
    final_width = args.width
    logging.info(f"Width: {args.width}")
    final_height = args.height
    logging.info(f"Height: {args.height}")

    # Get video info
    duration, fps, total = get_video_info(video_path)

    # Create shared counter
    shared_counter = multiprocessing.Value("i", 0)
    shared_total = total

    # Divide into chunks per worker
    chunk_dur = duration / args.workers
    chunks = [(i * chunk_dur, chunk_dur, video_path) for i in range(args.workers)]

    # Start pool
    logging.info(f"Using {args.workers} workers")
    pool = None

    try:
        pool = multiprocessing.Pool(
            processes=args.workers,
            initializer=init_worker,
            initargs=(shared_counter, shared_total),
        )

        # Start progress bar in main process
        results = []
        async_results = [pool.apply_async(process_chunk, (chunk,)) for chunk in chunks]

        with tqdm(total=total, unit="frame", desc="Processing frames") as pbar:
            last_count = 0
            while True:
                if all(r.ready() for r in async_results):
                    break
                time.sleep(0.2)
                with shared_counter.get_lock():
                    new_count = shared_counter.value
                pbar.update(new_count - last_count)
                last_count = new_count
            # Final update
            with shared_counter.get_lock():
                new_count = shared_counter.value
            pbar.update(new_count - last_count)

        # Collect results
        for r in async_results:
            results.extend(r.get())

        logging.info(f"Total extracted colors: {len(results)}")
        logging.info("Averaging to final width...")
        avg_colors = average_to_width(results, final_width)

        logging.info("Creating image...")
        img = Image.new("RGB", (final_width, final_height))
        for x, color in enumerate(avg_colors):
            img.paste(color, (x, 0, x + 1, final_height))

        base_name = os.path.splitext(os.path.basename(video_path))[0]

        output_file = os.path.join(
            os.path.dirname(video_path), f"{base_name}_{final_width}_{final_height}.png"
        )
        img.save(output_file)
        logging.info(f"Saved timeline image to: {output_file}")

    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Ensure proper cleanup
        if pool is not None:
            pool.close()
            pool.join()
        restore_terminal()  # Ensure terminal is restored
        logging.info("Cleanup complete")


if __name__ == "__main__":
    # This is CRITICAL for multiprocessing on Windows and helps on other platforms
    multiprocessing.set_start_method("spawn", force=True)
    main()
