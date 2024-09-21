from flask_app import generate_response, get_user_profile
import streamlit as st

st.title("Medical Chatbot")

# Set a default model
if "hf_model" not in st.session_state:
    st.session_state["hf_model"] = "DialogGPT-MedDialog-large"

# Store SLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User-provided prompt
if prompt := st.chat_input("Say something"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            user_id = "default_user"
            user_profile = get_user_profile(user_id)
            response = generate_response(prompt, user_profile)
            print(response)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)