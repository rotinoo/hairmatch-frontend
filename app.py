import streamlit as st
import cv2
import numpy as np
from PIL import Image
import requests
import base64

# Define API base URL
BASE_URL = "http://35.240.201.36:5000"

# Title and Subheader
st.title("Hair Style Recommendation")
st.subheader("Discover the best hairstyle for you!")

# Option for Image Upload or Camera
option = st.radio("Choose an option to provide an image:", ("Upload an Image", "Use Camera"))

# Placeholder for uploaded or captured image
image = None

if option == "Upload an Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width =True)
elif option == "Use Camera":
    st.write("Use your webcam to capture an image.")
    captured_image = st.camera_input("Capture an image")
    if captured_image is not None:
        image = Image.open(captured_image)

# Process Image if Provided
if image is not None:
    # Convert image to base64
    buffer = np.array(image)
    _, encoded_image = cv2.imencode('.jpg', cv2.cvtColor(buffer, cv2.COLOR_RGB2BGR))
    base64_image = base64.b64encode(encoded_image).decode("utf-8")

    # Detect Face Type
    if st.button("Analyze My Hairstyle"):
        st.info("Processing... Please wait.")
        
        # Step 1: Detect Face Type
        try:
            face_response = requests.post(f"{BASE_URL}/api/detect/face", json={"gambar": base64_image})
            face_data = face_response.json()
            face_type = face_data.get("tipe_wajah", "Unknown")
            st.write(f"Detected Face Type: {face_type}")
        except Exception as e:
            st.error(f"Error detecting face type: {e}")

        # Step 2: Detect Hair Type
        try:
            hair_response = requests.post(f"{BASE_URL}/api/detect/hair", json={"gambar": base64_image})
            hair_data = hair_response.json()
            hair_type = hair_data.get("tipe_rambut", "Unknown")
            st.write(f"Detected Hair Type: {hair_type}")
        except Exception as e:
            st.error(f"Error detecting hair type: {e}")

        # Step 3: Fetch Recommendations
        if face_type != "Unknown" and hair_type != "Unknown":
            try:
                recommend_response = requests.post(
                    f"{BASE_URL}/api/recommend", 
                    json={"tipe_wajah": face_type, "tipe_rambut": hair_type}
                )
                recommend_data = recommend_response.json()
                recommendations = recommend_data.get("gaya_rambut", [])
                st.write("Recommended Hairstyles:")
                for style in recommendations:
                    st.image(style["gambar"], caption=style["nama"], use_container_width =True)
            except Exception as e:
                st.error(f"Error fetching recommendations: {e}")