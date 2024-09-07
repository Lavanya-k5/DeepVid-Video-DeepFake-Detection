import json
import os
#os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN

import cv2
from mtcnn import MTCNN
import time

def extract_video(video_path, output_path, data_path):
    start_time = time.time()  # Record start time
    try:
        bboxes_path = os.path.join(data_path, os.path.splitext(os.path.basename(video_path))[0], os.path.basename(video_path).split('.')[0] + ".json")
        if not os.path.exists(bboxes_path) or not os.path.exists(video_path):
            print("Bounding boxes file or video not found.")
            return
        
        with open(bboxes_path, "r") as bbox_f:
            bboxes_dict = json.load(bbox_f)

        detector = MTCNN()
        capture = cv2.VideoCapture(video_path)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(capture.get(cv2.CAP_PROP_FPS))

        # Define frame rate based on the number of frames
        if total_frames > 350:
            frame_interval=min(6, fps)
        elif 300 < total_frames <= 350:
            frame_interval= min(5, fps)
        elif 250 < total_frames <= 300:
            frame_interval= min(4, fps) 
        elif 200 < total_frames <= 250:
            frame_interval= min(3, fps)
        elif 100 < total_frames <= 200:
            frame_interval= min(2, fps)
        else:
            frame_interval=1

        #frame_interval = max(fps//frame_rate,  1)
        print("Total frames: ", total_frames)
        print("Frames per sec: ", fps)
        print("Frames interval: ", frame_interval)

        # Process frames
        counter = 0
        for i in range(0, total_frames, frame_interval):
            capture.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, frame = capture.read()
            if not success or str(i) not in bboxes_dict:
                continue
            
            id = os.path.splitext(os.path.basename(video_path))[0]
            crops = []
            results = detector.detect_faces(frame)
            bboxes = []

            for result in results:
                bounding_box = result['box']
                x, y, w, h = bounding_box  # Extract x, y, width, height
                
                # Apply margin similar to Haar Cascade
                margin_x = int(w * 0.3)
                margin_y = int(h * 0.3)
                
                x1 = max(0, x - margin_x)
                y1 = max(0, y - margin_y)
                x2 = min(frame.shape[1], x + w + margin_x)
                y2 = min(frame.shape[0], y + h + margin_y)

                w_new = x2 - x1
                h_new = y2 - y1

                bboxes.append((x1, y1, w_new, h_new))  # Convert to (x, y, w, h) format

            if not bboxes:
                continue

            counter += 1
            # Ensure output directories exist
            output_id_path = os.path.join(output_path, id)
            os.makedirs(output_id_path, exist_ok=True)  # Create the main directory for video ID
            os.makedirs(os.path.join(output_id_path, "frames"), exist_ok=True)
            os.makedirs(os.path.join(output_id_path, "faces"), exist_ok=True)

            for j, bbox in enumerate(bboxes):
                x, y, w, h = bbox
                crop = frame[y:y+h, x:x+w]
                #cv2.imwrite(os.path.join(output_path, id, "{}_{}.png".format(i, j)), crop)
                cv2.imwrite(os.path.join(output_id_path, "faces", "{}_{}.png".format(i, j)), crop)

            # Optionally save the frame itself
            cv2.imwrite(os.path.join(output_id_path, "frames", "frame_{}.png".format(i)), frame)
            # Stop processing if we have saved enough frames
            if counter >= 60:
                print(f"Reached the maximum frame limit of 60. Stopping processing.")
                break      
        if counter == 0:
            print("No faces found in the video.")
    except Exception as e:
        print("Error:", e)   

    end_time = time.time()  # Record end time
    elapsed_time = end_time - start_time
    print(f"Time elapsed after extracting faces: {elapsed_time:.2f} seconds")
