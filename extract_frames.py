import cv2
from rich.progress import Progress, BarColumn, TextColumn
import argparse
import os
import numpy as np
from PIL import Image
import shutil


def main(args):
    if os.path.exists("dataset"):
        shutil.rmtree("dataset")
    os.makedirs("dataset", exist_ok=True)
    os.makedirs("dataset/input",exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(args.vid)
    # if not cap.isOpened():
    #     print("Error opening the  video file. Either path is correct or video is corrupted")
    #     return

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


    # intended for beautiful print terminal progress
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

                    # Convert the frame to RGB and start the color identificatio and annotation process
                    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    if current_frame>230 and current_frame<400:

                        cv2.imwrite(f"dataset/input/image {extracted_count}.png", frame)
                        original_image = Image.fromarray(frame)
                        extracted_count += 1

                current_frame += 1

            cap.release()

    print(f"Extracted {extracted_count} frames")
    print("Frames saved in images directory")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract frames from a video file")
    parser.add_argument("--vid", type=str, help="Path to the video file")
    parser.add_argument("--percent_frames", type=float, help="Percentage of frames to extract")
    args = parser.parse_args()

    main(args)



