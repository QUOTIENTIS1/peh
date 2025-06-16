import streamlit as st
from streamlit_lottie import st_lottie
from huggingface_hub import InferenceClient
import requests
import json

# --- 1. Initialize InferenceClient ---
api_token = "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"  # Your API key, used publicly as requested
client = InferenceClient(
    token=api_token,
    model="mistralai/Mixtral-8x7B-Instruct-v0.1"  # Accessible model
)

# --- 2. Initialize Session State ---
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "gender": None,
        "messages": []
    }

# --- 3. Animation Loader ---
def load_lottie(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# Load animations from local files
try:
    with open("Animation - 1749395326494.json", "r") as f:
        FEMALE_ANIM = json.load(f)
except FileNotFoundError:
    st.error("Female animation file not found!")
    FEMALE_ANIM = None

try:
    with open("Animation - 1749394556693.json", "r") as f:
        CUSTOM_MALE = json.load(f)
except FileNotFoundError:
    st.error("Male animation file not found!")
    CUSTOM_MALE = None

# --- 4. Gender Selection UI ---
def show_gender_selection():
    st.markdown("""
    <style>
    .gender-title {
        font-size: 2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .gender-option {
        border-radius: 15px;
        padding: 20px;
        transition: all 0.3s;
        text-align: center;
    }
    .gender-option:hover {
        background: #f0f2f6;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="gender-title">🤖 Please select your gender :)</p>', unsafe_allow_html=True)

    male_anim = CUSTOM_MALE
    female_anim = FEMALE_ANIM

    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            if male_anim:
                st_lottie(male_anim, height=200, key="male_anim")
            if st.button("Male", key="male_btn"):
                st.session_state.user_data["gender"] = "male"
                st.rerun()

    with col2:
        with st.container():
            if female_anim:
                st_lottie(female_anim, height=200, key="female_anim")
            if st.button("Female", key="female_btn"):
                st.session_state.user_data["gender"] = "female"
                st.rerun()

# --- 5. Chatbot Functionality ---
def response_generator(prompt):
    try:
        # Prepare message history with system context
        messages = [
            {"role": "system", "content": f"You are a helpful assistant chatting with a {st.session_state.user_data['gender']} user."}
        ] + st.session_state.user_data["messages"] + [{"role": "user", "content": prompt}]
        
        # Get streaming response
        completion = client.chat_completion(
            messages=messages,
            stream=True
        )
        
        # Stream the response chunks
        full_response = ""
        for chunk in completion:
            print(f"Raw Chunk: {chunk}")  # Debug: Log raw chunk
            if chunk.choices and chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                full_response += chunk_content
                yield chunk_content
        # Append full response to history
        st.session_state.user_data["messages"].append({"role": "assistant", "content": full_response})
                
    except Exception as e:
        print(f"Exception: {str(e)}")  # Debug: Log exception
        yield f"🚫 Error: {str(e)}"

# --- 6. Main App Flow ---
if not st.session_state.user_data["gender"]:
    show_gender_selection()
else:
    st.title(f"Yoo, {st.session_state.user_data['gender'].title()}😉")
    st.write("How can I help you today?")
    
    # Display chat history
    for message in st.session_state.user_data["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle new input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to history
        st.session_state.user_data["messages"].append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Display assistant response
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator(prompt))
            # Ensure response is a string for history
            response_str = "".join(response) if isinstance(response, (list, tuple)) else response
            st.session_state.user_data["messages"].append({"role": "assistant", "content": response_str})
