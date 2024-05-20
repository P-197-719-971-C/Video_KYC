import streamlit as st
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import time
import json
import av
import os
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import VideoTransformerBase, WebRtcMode, webrtc_streamer
from src.components.predict import final_score

def capture():
    class VideoTransformer(VideoTransformerBase):
        def __init__(self):
            self.i = 0
            self.out = cv2.VideoWriter('capture.mp4', cv2.VideoWriter_fourcc(*'X264'), 30.0, (640, 480))

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
            with open("capture.mp4", "wb") as f:
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

def submit_button(username):
   # sends the video to prediction pipeline and predict the output
    
    df, score = final_score(username) 
    if score > 70:
            # displays a success message if the score is greater than 70
        st.success(f"Congratulations! Your KYC is verified, and the liveliness score is {score}")
    else:
        # displays an error message if the score is less than or equal to 70
        st.error("Sorry, we couldn't verify your identity. Please try again.")
    return df

def main():
    st.set_page_config(
        page_title="Video KYC App",
        page_icon=":id:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_state(i):
        st.session_state.stage = i

    if st.session_state.stage == 0:
        st.button('Signup', on_click=set_state, args=[1])

    if st.session_state.stage >= 1:
        name = st.text_input('Enter Your Name:', on_change=set_state, args=[2])

    if st.session_state.stage >= 2:
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
            st.button('Submit video for Kyc', on_click= set_state, args=[3])
        # st.button('Submit video for Kyc', on_click= set_state, args=[3])
            if "capture.avi" is None:
                set_state(2)

    if st.session_state.stage >= 3:
        st.text("Please wait while the Kyc is being verified, it may take few minutes")
        with col44:
            with st.spinner("processing"):
                df, score = final_score(name)
        if score > 70:
                # displays a success message if the score is greater than 70
            st.success(f"Congratulations! Your KYC is verified, and the liveliness score is {round(score, 0)}")
            st.balloons()
            df
            video_file = open('Gif.mp4', 'rb')
            video_bytes = video_file.read()
            st.video(video_bytes)
            
            
        else:
            # displays an error message if the score is less than or equal to 70
            st.error("Sorry, we couldn't verify your identity. Please try again.")
            
            
            st.button('Restart', on_click=set_state, args=[0])
            
if __name__ == "__main__":
    main()
