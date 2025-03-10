import cv2
from rich.progress import Progress, BarColumn, TextColumn
import argparse
import os
import numpy as np
from PIL import Image
import shutil

def extract_overlapping_regions(frame, n_regions=4, overlap_percent=80):
    """
    Extract overlapping regions from a frame with the specified overlap percentage.
    
    Args:
        frame: The input frame
        n_regions: Number of regions to divide the frame into (must be a perfect square)
        overlap_percent: Percentage of overlap between adjacent regions (0-100)
        
    Returns:
        List of overlapping regions
    """
    height, width = frame.shape[:2]
    
    # Calculate grid dimensions based on n_regions
    # We'll create a grid of n_rows x n_cols where n_rows = n_cols = sqrt(n_regions)
    import math
    n_rows = n_cols = int(math.sqrt(n_regions))
    
    # If n_regions is not a perfect square, adjust accordingly
    if n_rows * n_cols != n_regions:
        print(f"Warning: {n_regions} is not a perfect square. Using {n_rows*n_cols} regions instead.")
    
    # Define region size
    region_height = height // n_rows
    region_width = width // n_cols
    
    # Calculate step size based on overlap percentage
    step_size_h = int(region_height * (1 - overlap_percent / 100))
    step_size_w = int(region_width * (1 - overlap_percent / 100))
    
    # Ensure step size is at least 1 pixel
    step_size_h = max(1, step_size_h)
    step_size_w = max(1, step_size_w)
    
    regions = []
    
    # Calculate y positions
    y_positions = []
    y = 0
    while y + region_height <= height:
        y_positions.append(y)
        y += step_size_h
        # Add the last position if we're close to the edge but not quite there
        if y + region_height > height and y < height - region_height and y not in y_positions:
            y_positions.append(height - region_height)
    
    # Calculate x positions
    x_positions = []
    x = 0
    while x + region_width <= width:
        x_positions.append(x)
        x += step_size_w
        # Add the last position if we're close to the edge but not quite there
        if x + region_width > width and x < width - region_width and x not in x_positions:
            x_positions.append(width - region_width)
    
    # Extract regions
    for y in y_positions:
        for x in x_positions:
            region = frame[y:y+region_height, x:x+region_width].copy()
            regions.append(region)
    
    return regions


def main(args):
    if os.path.exists("dataset"):
        shutil.rmtree("dataset")
    os.makedirs("dataset", exist_ok=True)
    os.makedirs("dataset/input", exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(args.vid)
    if not cap.isOpened():
        print("Error opening the video file. Either path is incorrect or video is corrupted")
        return

    # Get total number of frames
    K = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames in video: {K}")

    # Compute the number of frames to extract
    N = max(int(K * args.percent_frames), 1)  # Ensure at least one frame is extracted

    print(f"Sampling {N} out of {K} frames")

    # Generate indices of frames to extract
    indices = np.linspace(0, K - 1, N, dtype=int)
    indices_set = set(indices)
    current_frame = 0
    extracted_count = 0
    region_count = 0

    # For beautiful print terminal progress
    with Progress(
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            BarColumn(),
        ) as progress:
            task = progress.add_task("", total=K)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                progress.update(task, advance=1)

                if current_frame in indices_set:
                    # Extract overlapping regions from the frame
                    regions = extract_overlapping_regions(frame, n_regions=args.n_regions, overlap_percent=args.overlap)
                    
                    # Save each region
                    for region in regions:
                        region_filename = f"dataset/input/image_{extracted_count}_{region_count}.png"
                        region = cv2.resize(region, (256, 256))
                        cv2.imwrite(region_filename, region)
                        region_count += 1
                    
                    extracted_count += 1
                current_frame += 1

            cap.release()

    print(f"Extracted {extracted_count} frames with a total of {region_count} overlapping regions")
    print("Frames saved in dataset/input directory")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract frames from a video file with overlapping regions")
    parser.add_argument("--vid", type=str, help="Path to the video file")
    parser.add_argument("--percent_frames", type=float, default=0.1, help="Percentage of frames to extract (default: 0.1)")
    parser.add_argument("--overlap", type=float, default=80, help="Overlap percentage between regions (default: 80)")
    parser.add_argument("--n_regions", type=int, default=4, help="Number of regions to divide each frame into (default: 4)")
    args = parser.parse_args()

    main(args)
