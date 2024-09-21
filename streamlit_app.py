import streamlit as st
from streamlit_option_menu import option_menu

from flask_app import (call_external_api, generate_response, get_user_profile,
                       update_medical_database)

with st.sidebar:
    selected = option_menu(
        menu_title="Medical Chatbot",
        options=["About", "Chat", "Update", "External API"],
        icons=["calendar", "chat-dots", "database", "box-arrow-up-left"],
        menu_icon="capsule",
    )

if selected == "About":
    st.markdown(
        """
    ### This is a Medical Chatbot
    Built using [DialoGPT-large](https://huggingface.co/microsoft/DialoGPT-large) by Microsoft which was fine-tuned on [MedDialog](https://huggingface.co/datasets/bigbio/meddialog) dataset.

    Key features:
    - You can chat with it.
    - You can find out about a disease. Just type the disease name in the Chat section (Eg. headache)
    - You can even update description about a disease.
    - You can call an external medical API to retrieve additional information.
    """
    )

if selected == "Update":
    condition = st.text_input(
        "Condition you want to update", placeholder="Enter condition"
    )
    description = st.text_input(
        "Description of the condition", placeholder="Enter description"
    )

    if st.button("Update"):
        info = update_medical_database(condition, description)
        "Updated" if info else "Condition does not exist in the database"

if selected == "External API":
    query = st.text_input("Topic you want to search about", placeholder="Enter topic")

    if st.button("Search"):
        result = call_external_api(query)
        st.markdown(
            f"""Here are the results about {query}:

        {result["research"]}
        """
        )

if selected == "Chat":
    # Set a default model
    if "hf_model" not in st.session_state:
        st.session_state["hf_model"] = "DialoGPT-MedDialog-large"

    # Store SLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "How may I help you?"}
        ]

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

                if isinstance(response, str):
                    st.write(response)
                else:
                    st.write(response[-1]["content"])

        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
