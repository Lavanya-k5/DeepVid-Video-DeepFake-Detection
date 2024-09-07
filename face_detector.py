import os
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
#os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import List
import cv2
cv2.ocl.setUseOpenCL(False)
cv2.setNumThreads(0)
from PIL import Image
from facenet_pytorch.models.mtcnn import MTCNN
from torch.utils.data import Dataset

class VideoFaceDetector(ABC):
    def __init__(self, **kwargs) -> None:
        super().__init__()
    @property
    @abstractmethod
    def _batch_size(self) -> int:
        pass
    @abstractmethod
    def _detect_faces(self, frames) -> List:
        pass

class FacenetDetector(VideoFaceDetector):
    def __init__(self, device="cuda:0") -> None:
        super().__init__()
        self.detector = MTCNN(margin=0, thresholds=[0.85, 0.95, 0.95], device=device)
    def _detect_faces(self, frames) -> List:
        batch_boxes, *_ = self.detector.detect(frames, landmarks=False)
        return [b.tolist() if b is not None else None for b in batch_boxes]
    @property
    def _batch_size(self):
        return 32

class VideoDataset(Dataset):
    def __init__(self, videos) -> None:
        super().__init__()
        self.videos = videos
    
    def _get_dynamic_frame_rate(self, total_frames,fps):
        # Define frame rate based on the number of frames
        if total_frames > 350:
            return min(6, fps)
        elif 300 < total_frames <= 350:
            return min(5, fps)
        elif 250 < total_frames <= 300:
            return min(4, fps)
        elif 200 < total_frames <= 250:
            return min(3, fps)
        elif 100 < total_frames <= 200:
            return min(2, fps)
        else:
            return 1
    
    def __getitem__(self, index: int):
        video = self.videos[index]
        capture = cv2.VideoCapture(video)

        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(capture.get(cv2.CAP_PROP_FPS))
        interval = self._get_dynamic_frame_rate(total_frames,fps)  # Adjust frame rate based on total frames
        #frame_interval = max(fps//frame_rate,  1)
        frame_interval = max(interval,  1)
        frames_to_process = list(range(0, total_frames, frame_interval))
        print("frames_to_process",frames_to_process)

        print("Total frames: ", total_frames)
        print("Frames per sec: ", fps)
        print("Frames interval: ", frame_interval)

        frames = OrderedDict()
        #count = 0
        #max_frames = 60  # Set the maximum number of frames to process

        for i in frames_to_process:
            capture.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, frame = capture.read()
            print(f"Trying to read frame at index: {i}, Success: {success}")
            if not success:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = frame.resize(size=[s // 2 for s in frame.size])
            frames[i] = frame
            #count += 1  # Increment the processed frame count
            
            #if count >= max_frames:
              #  print("Count:",count)
             #   break
        capture.release()  # Release the video capture object
        return video, list(frames.keys()), list(frames.values())

    def __len__(self) -> int:
        return len(self.videos)
