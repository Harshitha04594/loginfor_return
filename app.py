import streamlit as st
import requests

# Backend API URL
API_URL = "https://ai-powered-fraud-detection.onrender.com"

# Page Configuration
st.set_page_config(page_title="AI-Powered Return Verification", page_icon="🛡️", layout="wide")

# Custom CSS for styling + animated marquee
st.markdown(
    """
    <style>
        /* Page background color */
        .stApp {
            background-color: #f4f7fc;
        }

        /* Main container box */
        .main-container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 3px 3px 20px rgba(0, 0, 0, 0.1);
            max-width: 700px;
            margin: auto;
        }

        /* Marquee container */
        .marquee-container {
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
            background: linear-gradient(to right, #0066cc, #0099ff);
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        /* Marquee animation */
        .marquee-text {
            display: inline-block;
            animation: marquee-scroll 10s linear infinite;
        }

        @keyframes marquee-scroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }

        /* Custom buttons */
        .stButton>button {
            background-color: #008CBA !important;
            color: white !important;
            padding: 10px 15px;
            border-radius: 8px;
            font-weight: bold;
            border: none;
        }

        /* Input fields */
        .stTextInput>div>div>input {
            border-radius: 8px;
            padding: 10px;
        }

        /* Image borders */
        .stImage img {
            border-radius: 10px;
            border: 2px solid #008CBA;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Moving Marquee
st.markdown(
    '<div class="marquee-container">'
    '<span class="marquee-text">🚀 AI-Powered Return Verification - Secure & Smart! 🚀</span>'
    '</div>',
    unsafe_allow_html=True
)

# Centered Content Box
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Title
st.markdown("### 🛡️ AI-Powered Return Verification System", unsafe_allow_html=True)

# Input fields
product_id = st.text_input("🔍 Enter Product ID")
uploaded_file = st.file_uploader("📤 Upload Return Image", type=["jpg", "png"])

if uploaded_file and product_id:
    if st.button("✅ Verify Return"):
        try:
            # ✅ Send return image and product ID for verification
            files = {"file": uploaded_file.getvalue()}
            params = {"product_id": product_id}

            # Send verification request
            response = requests.post(f"{API_URL}/verify_return", files=files, params=params)

            if response.status_code == 200:
                result = response.json()

                # ✅ Convert similarity score to 1-100 scale
                similarity_percentage = round(result['best_similarity'] * 100, 2)

                # Display verification results
                st.success(f"✅ Status: {result['status']}")
                st.info(f"📊 Similarity: {similarity_percentage:.2f}%")

                # ✅ Show uploaded return image
                st.image(uploaded_file, caption="📷 Uploaded Return Image", use_column_width=True)

                # ✅ Fetch and display original product images
                image_response = requests.get(f"{API_URL}/list_product_images")
                
                if image_response.status_code == 200:
                    images = image_response.json().get("available_images", [])

                    # Filter product images for entered product_id
                    product_images = [img for img in images if img.startswith(f"{product_id}_")]

                    if product_images:
                        st.subheader("📸 Original Product Images")
                        for img in product_images:
                            image_url = f"{API_URL}/get_product_image?filename={img}"
                            st.image(image_url, caption=f"Original: {img}", use_column_width=True)
                    else:
                        st.warning("⚠️ No original product images found for this Product ID.")

                else:
                    st.error(f"❌ Failed to fetch original product images. Error: {image_response.text}")

                # ✅ Display stored return image (if available)
                return_image_url = f"{API_URL}/get_return_image?product_id={product_id}"
                st.image(return_image_url, caption="📦 Stored Return Image", use_column_width=True)

            else:
                st.error(f"❌ Error verifying return. Response: {response.text}")

        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")

else:
    st.warning("⚠️ Please enter a Product ID and upload a return image.")

st.markdown('</div>', unsafe_allow_html=True)  # Close main container