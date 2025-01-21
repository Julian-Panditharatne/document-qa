import streamlit as st
import requests
from flask import Flask, request, jsonify
from threading import Thread
import json

# Flask app setup
app = Flask(__name__)

@app.route("/receive_response", methods=["POST"])
def receive_response():
    try:
        # Parse the request data
        data = request.get_json()
        llm_response = data.get("llm_response", "No response received.")
        
        # Update Streamlit session state
        st.session_state["llm_response"] = llm_response
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask in a separate thread
def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)

# Start Flask server in a thread
if "flask_thread" not in st.session_state:
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    st.session_state["flask_thread"] = flask_thread

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

            """# Send a request to Make.com to get the LLM response
            response = requests.get(MAKE_COM_RESPONSE_URL)
            response.raise_for_status() 

            gpt_response = response.text 

            st.success("Data sent to Make.com successfully!")
            st.write("### GPT Response")
            st.write(gpt_response)"""
            if "llm_response" not in st.session_state:
                st.session_state["llm_response"] = ""
    
            st.success("Data sent to Make.com successfully!")
            st.write("### GPT Response")
            st.write(st.session_state["llm_response"])
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with Make.com: {e}")



if __name__ == "__main__":
    main()
