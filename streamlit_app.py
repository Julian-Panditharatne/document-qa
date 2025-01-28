import streamlit as st
import requests
from flask import Flask, request, jsonify
from threading import Thread
import json

def main():
    MAKE_COM_WEBHOOK_URL = "https://hook.us2.make.com/6m3voepa1225gxksxocis3ow8oyygutp"
    other_hook = "https://hook.us2.make.com/q7m1xgm52ugdzsx73lcrwv838on5glum"
    MAKE_COM_RESPONSE_URL = MAKE_COM_WEBHOOK_URL

    # Show title and description.
    st.title("💬 Files Question Answering")
    st.write(
        "Upload files below and ask a question about them – GPT will answer! "
    )

    # Let the user upload files via `st.file_uploader`.
    uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask questions about the files!",
        placeholder="Can you give me a short summary of these files?",
        disabled=not uploaded_files
    )

    if st.button("Submit"):
        file_data = []
        if uploaded_files:
            for file in uploaded_files:
                # Process file (e.g., convert to base64)
                file_data.append(file.read().decode('utf-8'))  # Decode to handle potential encoding issues

        data = {
            "text_input": question,
            "file_data": file_data
        }

        try:
            response = requests.post(MAKE_COM_WEBHOOK_URL, json=data)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Send a request to Make.com to get the LLM response
            response = requests.get(MAKE_COM_RESPONSE_URL)
            response.raise_for_status() 

            gpt_response = response.text 

            st.success("Data sent to Make.com successfully!")
            st.write("### GPT Response")
            st.write(gpt_response)
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with Make.com: {e}")

if __name__ == "__main__":
    main()
