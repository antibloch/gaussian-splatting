import cv2
from rich.progress import Progress, BarColumn, TextColumn
import argparse
import os
import numpy as np
from PIL import Image
import shutil


def extract_overlapping_regions(frame, overlap_percent=80):
    """
    Extract overlapping regions from a frame with the specified overlap percentage.
    
    Args:
        frame: The input frame
        overlap_percent: Percentage of overlap between adjacent regions (0-100)
        
    Returns:
        List of overlapping regions
    """
    height, width = frame.shape[:2]
    
    # Define region size (for example, divide the frame into quarters)
    # You can adjust these values based on your needs
    region_height = height // 2
    region_width = width // 2
    
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
    
    # Calculate x positions
    x_positions = []
    x = 0
    while x + region_width <= width:
        x_positions.append(x)
        x += step_size_w
    
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
                    regions = extract_overlapping_regions(frame, overlap_percent=80)
                    
                    # Save each region
                    for region in regions:
                        region_filename = f"dataset/input/image {region_count}.png"
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
    args = parser.parse_args()

    main(args)
