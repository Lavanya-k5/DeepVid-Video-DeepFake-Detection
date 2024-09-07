import os
#os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN
import re
import cv2
import numpy as np
import yaml
from albumentations import Compose, PadIfNeeded
from transforms.albu import IsotropicResize
import torch
from efficient_vit import EfficientViT
from utils import custom_video_round
import time
import shutil

def create_base_transform(size):
    return Compose([
        IsotropicResize(max_side=size, interpolation_down=cv2.INTER_AREA, interpolation_up=cv2.INTER_CUBIC),
        PadIfNeeded(min_height=size, min_width=size, border_mode=cv2.BORDER_CONSTANT, value=(0, 0, 0)),
    ])

# Load the pre-trained model
def load_model(model_path, config, efficient_net=0):
    if efficient_net == 0:
        channels = 1280
    else:
        channels = 2560

    if os.path.exists(model_path):
        model = EfficientViT(config=config, channels=channels, selected_efficient_net=efficient_net)
        # Load the model state dictionary
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        if torch.cuda.is_available():
            model = model.cuda()
        return model
    else:
        print("No model found.")
        exit()

# Function to read frames from video path and save transformed frames
def read_frames(video_path, faces_folder, frames_folder, output_dir, frames_per_video, config):
    video_folder_name = os.path.basename(video_path)
    output_folder = os.path.join(output_dir, video_folder_name)
    
    # Delete existing frames folder if it exists
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)  # Remove entire directory and its contents

    # Create folders for frames and faces
    os.makedirs(output_folder, exist_ok=True)
    faces_output_folder = os.path.join(output_folder, "faces")
    frames_output_folder = os.path.join(output_folder, "frames")
    os.makedirs(faces_output_folder, exist_ok=True)
    os.makedirs(frames_output_folder, exist_ok=True)

    # Read faces
    faces_paths = os.listdir(faces_folder)
    frames_paths = os.listdir(frames_folder)
    faces_paths_dict = {}

    # Group faces by index
    for path in faces_paths:
        for i in range(3):
            if f"_{i}" in path:
                if i not in faces_paths_dict:
                    faces_paths_dict[i] = [path]
                else:
                    faces_paths_dict[i].append(path)

    # Select frames at certain intervals
    frames_interval = max(len(frames_paths) // frames_per_video, 1)
    #selected_faces = []
    #selected_faces.extend(faces_paths_dict[key])
    for key in faces_paths_dict.keys():
        if len(faces_paths_dict[key]) > frames_interval:
            faces_paths_dict[key] = faces_paths_dict[key][::frames_interval]
        faces_paths_dict[key] = faces_paths_dict[key][:frames_per_video]

    # Transform and save frames in folder and list 
    faces_list = []
    transform = create_base_transform(config['model']['image-size'])
    for key in faces_paths_dict.keys():
        for index, face_image in enumerate(faces_paths_dict[key]):
            face_image_path = os.path.join(faces_folder,  face_image)
            image = cv2.imread(face_image_path)
            if image is not None:
                transformed = transform(image=image)['image']
                faces_list.append(transformed)
                save_path = os.path.join(faces_output_folder, f"{key}_{index}.png")
                cv2.imwrite(save_path, transformed)

                # Extract the frame index from the face image name using regex
                match = re.match(r'(\d+)_\d+\.png', face_image)
                if match:
                    frame_index = match.group(1)  # Extract the first number (e.g., 9 from 9_0.png)
                
                # Construct the corresponding frame file name
                corresponding_frame = f"frame_{frame_index}.png"
                if corresponding_frame in frames_paths:
                    src_frame_path = os.path.join(frames_folder, corresponding_frame)
                    dst_frame_path = os.path.join(frames_output_folder, corresponding_frame)
                    frame_image = cv2.imread(src_frame_path)
                    if frame_image is not None:
                        cv2.imwrite(dst_frame_path, frame_image)
                    else:
                        print(f"Warning: Could not read frame {corresponding_frame}")
            else:
                print(f"Warning: Could not read image {face_image}")
    return faces_list

def process_video(faces_lists, model, config, batch_size=32):
    preds = []
    video_faces_preds = []  # List to store predictions for all frames in the video

    # Iterate through frames in batches
    for i in range(0, len(faces_lists), batch_size):
        faces_preds = []
        faces = faces_lists[i:i+batch_size]
        faces = torch.tensor(np.asarray(faces))
        if faces.shape[0] == 0:
            print(f"Warning: Could not read frame {faces_lists[i]}")  # Print error message
            continue
        faces = np.transpose(faces, (0, 3, 1, 2))
        if torch.cuda.is_available():
            faces = faces.cuda().float()
        else:
            faces = faces.float()
            
        pred = model(faces)
        scaled_pred = [torch.sigmoid(p) for p in pred]
        faces_preds.extend(scaled_pred)
                
        current_faces_pred = sum(faces_preds) / len(faces_preds)
        face_pred = current_faces_pred.cpu().detach().numpy()[0]
        video_faces_preds.append(face_pred)
        if len(video_faces_preds) > 1:
            video_pred = custom_video_round(video_faces_preds)
        else:
            video_pred = video_faces_preds[0]
        preds.append([video_pred])
    
    return np.mean(preds)

def main(video_path, model_path, config_path, output_dir, frames_per_video, efficient_net=0):
    start_time = time.time()  # Record start time
    # Load config
    with open(config_path, 'r') as ymlfile:
        config = yaml.safe_load(ymlfile)

    # Load the model
    model = load_model(model_path, config, efficient_net)
    faces_folder = os.path.join(video_path, "faces")
    frames_folder = os.path.join(video_path, "frames")

    # Read frames from the video and save transformed frames
    faces_list = read_frames(video_path, faces_folder, frames_folder,output_dir, frames_per_video, config)

    faces_found = 0 if not faces_list else 1  # Check if no frames were detected
    if faces_found == 0:
        return None  # No faces detected

    # Process the video frames
    prediction = process_video(faces_list, model, config)
    end_time = time.time()  # Record end time
    elapsed_time = end_time - start_time
    print(f"Time elapsed for prediction: {elapsed_time:.2f} seconds")

    return prediction
