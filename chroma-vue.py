import argparse
import subprocess
import multiprocessing
import numpy as np
from PIL import Image
from tqdm import tqdm
import time
import logging
import os

# ---------- GLOBALS FOR SHARED STATE ----------
counter = None
total_frames = None

def init_worker(shared_counter, shared_total):
    """Initializer for workers to inherit shared counter and total frames."""
    global counter, total_frames
    counter = shared_counter
    total_frames = shared_total


def get_video_info(video_path):
    """Get duration (s) and fps using ffprobe."""
    logging.info(f"Probing video: {video_path}")
    # Duration
    duration_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    duration = float(subprocess.check_output(duration_cmd).decode().strip())

    # FPS
    fps_cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    fps_str = subprocess.check_output(fps_cmd).decode().strip()
    num, denom = fps_str.split('/')
    fps = float(num) / float(denom)

    total = int(duration * fps)
    logging.info(f"Video duration: {duration:.2f}s, FPS: {fps}, Total frames: {total}")
    return duration, fps, total


def process_chunk(args):
    """Worker: Extract average colors from a segment of the video."""
    start_time, duration, video_path = args

    cmd = [
        "ffmpeg",
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", video_path,
        "-vf", "scale=1:1",
        "-f", "image2pipe",
        "-pix_fmt", "rgb24",
        "-vcodec", "rawvideo",
        "-threads", "1",  # important for multi-worker balance
        "-"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
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


def main():
    parser = argparse.ArgumentParser(
        description="Generate a color timeline image from a video.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument("--width", type=int, default=3000, help="Final image width in pixels")
    parser.add_argument("--height", type=int, default=800, help="Final image height in pixels")
    parser.add_argument("--workers", type=int, default=multiprocessing.cpu_count(), help="Number of worker processes")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    video_path = args.video
    logging.info(f"Video : {args.video}")
    final_width = args.width
    logging.info(f"Width: {args.width}")
    final_height = args.height
    logging.info(f"Height: {args.height}")

    # Get video info
    duration, fps, total = get_video_info(video_path)

    # Create shared counter
    shared_counter = multiprocessing.Value('i', 0)
    shared_total = total

    # Divide into chunks per worker
    chunk_dur = duration / args.workers
    chunks = [(i * chunk_dur, chunk_dur, video_path) for i in range(args.workers)]

    # Start pool
    logging.info(f"Using {args.workers} workers")
    pool = multiprocessing.Pool(
        processes=args.workers,
        initializer=init_worker,
        initargs=(shared_counter, shared_total)
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

    pool.close()
    pool.join()

    logging.info(f"Total extracted colors: {len(results)}")
    logging.info("Averaging to final width...")
    avg_colors = average_to_width(results, final_width)

    logging.info("Creating image...")
    img = Image.new("RGB", (final_width, final_height))
    for x, color in enumerate(avg_colors):
        img.paste(color, (x, 0, x + 1, final_height))

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_file = f"{base_name}_{final_width}_{final_height}.png"
    img.save(output_file)
    logging.info(f"Saved timeline image to: {output_file}")


if __name__ == "__main__":
    main()
