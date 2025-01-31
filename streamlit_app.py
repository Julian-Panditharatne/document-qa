import streamlit as st
import requests
from openai import OpenAI

gpt_Key = st.secrets["API_KEYS"]["Personal_GPT_Key"]
client = OpenAI(api_key=gpt_Key)
file_data = []

def main():
    MAKE_COM_WEBHOOK_URL = "https://hook.us2.make.com/pxjavgk8qa3pmenqucl2cp2t7feh3h61"
    other_hook = "https://hook.us2.make.com/q7m1xgm52ugdzsx73lcrwv838on5glum"
    MAKE_COM_RESPONSE_URL = MAKE_COM_WEBHOOK_URL

    # Show title and description.
    st.title("💬 Documents Question Answering")
    st.write(
        "Upload documents below and ask a question about them – GPT will answer! "
    )
    
    # Let the user upload files via `st.file_uploader`.
    uploaded_files = st.file_uploader("Upload Documents", accept_multiple_files=True)

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask questions about the documents!",
        placeholder="Can you give me a short summary of these documents?",
        disabled=not uploaded_files
    )

    if st.button("Submit"):
        if uploaded_files:
            for file in uploaded_files:
                # Upload the file to OpenAI so that it can be stored in the following vector store
                f = client.files.create(
                    file=file,
                    purpose="assistants"
                    )
                # Add the file's id to file_data
                file_data.append(f.id)
                # Attach the file to the vector store assigned to assistant
                vector_store_file = client.beta.vector_stores.files.create(
                    vector_store_id="vs_cjcLeqY3t0N2j1x3hXMo6vDG",
                    file_id=f.id
                    )
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
            
            # Delete all the files from OpenAI once user's questions are answered
            #[client.files.delete(f) for f in file_data]
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with Make.com: {e}")

if __name__ == "__main__":
    main()
