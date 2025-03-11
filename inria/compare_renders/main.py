import os
import cv2
import numpy as np
from glob import glob

def create_comparison_video(folder1, folder2, output_file, fps=30, title="20.psnr"):
    """
    Create a video comparing images from two folders side by side.
    
    Args:
        folder1 (str): Path to the first folder containing images
        folder2 (str): Path to the second folder containing images
        output_file (str): Path to the output video file
        fps (int): Frames per second for the output video
        title (str): Title to display at the top of the video
    """
    # Get sorted lists of image files from both folders
    images1 = sorted(glob(os.path.join(folder1, "*.png")))
    images2 = sorted(glob(os.path.join(folder2, "*.png")))
    
    if not images1 or not images2:
        print("Error: One or both folders do not contain PNG images.")
        return
    
    # Make sure we have the same number of images in both folders
    min_images = min(len(images1), len(images2))
    if len(images1) != len(images2):
        print(f"Warning: Folders contain different numbers of images. Using only the first {min_images} images.")
        images1 = images1[:min_images]
        images2 = images2[:min_images]
    
    # Read the first image to get dimensions
    sample_img = cv2.imread(images1[0])
    height, width, _ = sample_img.shape
    
    # Create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use 'XVID' for AVI format
    label_height = 30  # Height for bottom labels
    video_height = height + 50 + label_height  # Extra space for title and labels
    video_width = width * 2  # Side by side
    out = cv2.VideoWriter(output_file, fourcc, fps, (video_width, video_height))
    
    # Define font properties for the title
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    font_color = (255, 255, 255)  # White
    
    # Process each pair of images
    for i in range(min_images):
        # Read images
        img1 = cv2.imread(images1[i])
        img2 = cv2.imread(images2[i])
        
        # Create a blank space for the title
        title_space = np.zeros((50, video_width, 3), dtype=np.uint8)
        
        # Add title text to the blank space
        text_size = cv2.getTextSize(title, font, font_scale, font_thickness)[0]
        text_x = (video_width - text_size[0]) // 2
        text_y = 35  # Position from top
        cv2.putText(title_space, title, (text_x, text_y), font, font_scale, font_color, font_thickness)
        
        # Add frame number
        frame_text = f"Frame: {i:04d}"
        cv2.putText(title_space, frame_text, (10, 35), font, 0.5, font_color, 1)
        
        # Add labels to the bottom of each image
        label_height = 30
        label_space1 = np.zeros((label_height, width, 3), dtype=np.uint8)
        label_space2 = np.zeros((label_height, width, 3), dtype=np.uint8)
        
        # Add "Ground Truth" label to the first image
        gt_text = "Ground Truth"
        text_size = cv2.getTextSize(gt_text, font, 0.7, 1)[0]
        text_x = (width - text_size[0]) // 2
        cv2.putText(label_space1, gt_text, (text_x, 20), font, 0.7, font_color, 1)
        
        # Add "Render" label to the second image
        render_text = "Render"
        text_size = cv2.getTextSize(render_text, font, 0.7, 1)[0]
        text_x = (width - text_size[0]) // 2
        cv2.putText(label_space2, render_text, (text_x, 20), font, 0.7, font_color, 1)
        
        # Add labels to images
        img1_with_label = np.vstack((img1, label_space1))
        img2_with_label = np.vstack((img2, label_space2))
        
        # Concatenate images side by side
        side_by_side = np.hstack((img1_with_label, img2_with_label))
        
        # Concatenate title space and side-by-side images
        full_frame = np.vstack((title_space, side_by_side))
        
        # Write the frame to the video file
        out.write(full_frame)
        
        # Display progress
        if i % 10 == 0:
            print(f"Processing frame {i}/{min_images}...")
    
    # Release the VideoWriter
    out.release()
    print(f"Video saved as {output_file}")

def main():
    # Example usage
    folder1 = "gt"  # Path to first folder containing images
    folder2 = "renders"  # Path to second folder containing images
    output_file = "comparison_video.mp4"  # Output video filename
    
    create_comparison_video(folder1, folder2, output_file, fps=3, title="44.6 PSNR")
    
if __name__ == "__main__":
    main()