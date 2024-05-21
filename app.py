import streamlit as st
import cv2
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer
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
        video_bytes = uploaded_files.read()
        with st.spinner("Uploading..."):
            with open("capture.mp4", "wb") as f:
                f.write(video_bytes)
        st.success("Video uploaded successfully!")
        
        if st.button("Preview"):
            st.video(f.name)
            if st.button("Close"):
                f.close()
                os.remove(f.name)
                st.success("Preview closed.")

def submit_button(username):
    df, score = final_score(username)
    if score > 70:
        st.success(f"Congratulations! Your KYC is verified, and the liveliness score is {score}")
    else:
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
        if st.button('Signup'):
            st.session_state.stage = 1

    if st.session_state.stage == 1:
        name = st.text_input('Enter Your Name:')
        if name:
            st.session_state.name = name
            st.session_state.stage = 2

    if st.session_state.stage == 2:
        st.markdown("<h4 style='text-align: center;'>Please read the instructions carefully:</h4>", unsafe_allow_html=True)
        st.markdown("""
            <ul>
                <li>Stay close to the camera</li>
                <li>Blink your eyes frequently</li>
                <li>Smile</li>
                <li>Show a thumbs-up</li>
                <li>Show a victory sign</li>
            </ul>
        """, unsafe_allow_html=True)
        if st.button("I have read the instructions"):
            st.session_state.stage = 3

    if st.session_state.stage >= 3:
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
            if st.button('Submit video for KYC'):
                st.session_state.stage = 4

    if st.session_state.stage == 4:
        st.text("Please wait while the KYC is being verified, it may take a few minutes")
        with st.spinner("Processing..."):
            df, score = final_score(st.session_state.name)
        
        if score > 70:
            st.success(f"Congratulations! Your KYC is verified, and the liveliness score is {round(score, 0)}")
            st.balloons()
            st.dataframe(df)
            video_file = open('Gif.mp4', 'rb')
            video_bytes = video_file.read()
            st.video(video_bytes)
        else:
            st.error("Sorry, we couldn't verify your identity. Please try again.")
            if st.button('Restart'):
                st.session_state.stage = 0

if __name__ == "__main__":
    main()
