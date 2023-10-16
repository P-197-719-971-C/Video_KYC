import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import time
import json
import av
import os
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import VideoTransformerBase, WebRtcMode, webrtc_streamer


def capture():
    class VideoTransformer(VideoTransformerBase):
        def __init__(self):
            self.i = 0
            self.out = cv2.VideoWriter('capture.avi', cv2.VideoWriter_fourcc(*'XVID'), 30.0, (640, 480))

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            self.out.write(img)
            return img
    webrtc_streamer(key="video_recording", video_processor_factory=VideoTransformer)

def upload():
    uploaded_files = st.file_uploader("Upload video for KYC", type=['mp4', 'avi', 'mov'], accept_multiple_files=False)
    
    if uploaded_files is not None:
        
        # Read the video file
        video_bytes = uploaded_files.read()
        # Save the video as upload.avi
        with st.spinner("Uploading..."):
            with open("upload.avi", "wb") as f:
                f.write(video_bytes)
        st.success("Video uploaded successfully!")

        # Display preview
        if st.button("preview"):
            st.video(f.name)       
            if st.button("Close"):
                # Close the temporary file and remove it
                f.close()
                os.remove(f.name)
                st.success("Preview closed.")

def submit_button():
   # sends the video to prediction pipeline and predict the output
    st.button("submit")   
 
def main():
     # Set Streamlit page configuration for Video KYC App
    st.set_page_config(
        page_title="Video KYC App",
        page_icon=":id:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(
        "<div style='text-align: center;'><h1>Welcome to the Video KYC App</h1>"
        "<p>Please choose one of the following options:</p></div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p style='text-align: center;'>Press start to record video for KYC</p>", unsafe_allow_html=True)
        capture()

    with col2:
        upload()

    col11, col22, col33, col44, col55 = st.columns(5)
    with col33:
        submit_button()
    





if __name__ == "__main__":
   main()
   