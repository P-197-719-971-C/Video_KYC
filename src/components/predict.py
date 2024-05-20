import cv2 as cv
import pandas as pd
from datetime import datetime
from src.components.detect_eyeblink import detect_eye_blink
from src.components.detect_smile import detect_smile
from src.components.detect_gesture import detect_victory_thumbsUp

def final_score(first_name = "Umrav"):
    
    
    cap = cv.VideoCapture("capture.mp4")
    j, smile_score = detect_smile(cap)
    cap = cv.VideoCapture("capture.mp4")
    i, blink_score = detect_eye_blink(cap)
    cap = cv.VideoCapture("capture.mp4")
    k, class_, prob = detect_victory_thumbsUp(cap)
    cap = cv.VideoCapture("capture.mp4")
    # Create a list of twenty frames around i, j, and k
    width = 640 #int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = 480 #int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv.CAP_PROP_FPS))
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    # Create a VideoWriter object to save the output video
    frame_list = list(range(max(1, i - 20), min(total_frames, i + 20 + 1))) + list(range(max(1, j - 20), min(total_frames, j + 20 + 1))) + list(range(max(1, k - 20), min(total_frames, k + 20 + 1)))
    # Find unique values
    unique_frames = sorted(set(frame_list))

    filtered_frames = [frame for frame in unique_frames if 0 <= frame < total_frames]

    # Create a VideoWriter object to save the output video
    fourcc = cv.VideoWriter_fourcc(*'X264')
    output_video = cv.VideoWriter('Gif.mp4', fourcc, fps, (width, height))

    # Iterate through the filtered frames and append to the output video
    for frame_num in filtered_frames:
        cap.set(cv.CAP_PROP_POS_FRAMES, frame_num - 1)
        ret, frame = cap.read()
        if not ret:
            break
        output_video.write(frame)

    # Release video capture and writer
    cap.release()
    output_video.release()

    timestamp = datetime.now()
    # if class_ == 0:
    #     gesture = 'Victory Sign'
    # elif class_ == 1:
    #     gesture = 'Thumbs Up'

    # Create a dictionary with the data
    data = {
        "First Name": [first_name],
        "Blink Score": [blink_score],
        "Smile Score": [smile_score],
        "Victory Thumbs Up": [prob],
        "Timestamp": [timestamp]
    }
    df = pd.DataFrame(data)
    score = (blink_score + smile_score + prob)/3
    df["Score"] = score
    
    print(score)
    print(df)
    return df, score
    # try:
    #     existing_df = pd.read_csv("data.csv")  # Assuming you have a CSV file to store the data
    #     updated_df = existing_df.append(df, ignore_index=True)
    # except FileNotFoundError:
    #     updated_df = df
    # # Save the updated DataFrame to a CSV file
    # updated_df.to_csv("data.csv", index=False)
    if __name__ == "__main__":
        final_score()