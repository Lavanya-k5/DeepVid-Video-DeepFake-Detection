import json
import os
#os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN

from os import cpu_count
import numpy as np
from torch import cuda
from typing import Type
from torch.utils.data.dataloader import DataLoader
from tqdm import tqdm
import face_detector
from face_detector import VideoDataset, VideoFaceDetector
import time

def collate_fn(x):
    return x
    
def process_video(video_path, root_dir, detector_cls: Type[VideoFaceDetector]):
    start_time = time.time()  # Record start time
    detector = face_detector.__dict__[detector_cls](device="cpu")  # Use "cuda:0" if cuda is available
    dataset = VideoDataset([video_path])  
    loader = DataLoader(dataset, shuffle=False, num_workers=cpu_count() - 2, batch_size=1, collate_fn=collate_fn)
    for item in tqdm(loader):
        result = {}
        video, indices, frames = item[0]
        batches = [frames[i:i + detector._batch_size] for i in range(0, len(frames), detector._batch_size)]
        for j, frames in enumerate(batches):
            result.update({int(j * detector._batch_size) + i: b for i, b in zip(indices, detector._detect_faces(frames))})
        
        id = os.path.splitext(os.path.basename(video))[0]
        out_dir = os.path.join(root_dir, id)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, f"{id}.json"), "w") as f:
            json.dump(result, f)
        print(f"Processed video saved in: {out_dir}/{id}.json")
    end_time = time.time()  # Record end time
    elapsed_time = end_time - start_time
    print(f"Time elapsed to detect faces save to .json: {elapsed_time:.2f} seconds")
