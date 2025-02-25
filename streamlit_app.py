import streamlit as st
import requests
import json
from openai import OpenAI

gpt_Key = st.secrets["API_KEYS"]["Personal_GPT_Key"]
client = OpenAI(api_key=gpt_Key)

# Variables that will retain their values throughout runs in a session
if 'file_data' not in st.session_state:
    st.session_state['file_data'] = []
if 'data' not in st.session_state:
    st.session_state['data'] = {}
if 'disable_que' not in st.session_state:
    st.session_state['disable_que'] = True
if 'up_files' not in st.session_state:
    st.session_state['up_files'] = 1
if 'gpt_response' not in st.session_state:
    st.session_state['gpt_response'] = {}

def main():
    MAKE_COM_WEBHOOK_URL = "https://hook.us2.make.com/pxjavgk8qa3pmenqucl2cp2t7feh3h61"
    
    # Show title and description.
    st.title("💬 Documents Question Answering")
    st.write(
        "Upload documents below and ask a question about them – GPT will answer! "
    )
   
    
    def upload_processing():
        """
        Function for embedding the files in vector space and collecting the file IDs
        """
        if st.session_state[st.session_state['up_files']]:
            with st.spinner("Processing files, please wait..."):
                for file in st.session_state[st.session_state['up_files']]:
                    # Upload the file to OpenAI so that it can be stored in the following vector store
                    f = client.files.create(
                        file=file,
                        purpose="assistants"
                        )
                    # Add the file's id to file_data
                    st.session_state['file_data'].append(f.id)
                    # Attach the file to the vector store assigned to assistant
                    vector_store_file = client.beta.vector_stores.files.create_and_poll(
                        vector_store_id="vs_cjcLeqY3t0N2j1x3hXMo6vDG",
                        file_id=f.id
                        )
            st.success('Files processed.', icon="✅")
            st.session_state['disable_que'] = False # Enable chat input

    def submission():
        """
        Function for making POST requests to Make webhook and getting response from it and displaying it.
        """
        st.session_state['data'] = {
            "text_input": st.session_state['que'],
            "file_data": st.session_state['file_data']
        }

        try:
            response = requests.post(MAKE_COM_WEBHOOK_URL, json=st.session_state['data'])

            if response.status_code == 200:
                resp_text = response.text
                resp_text = resp_text.replace('```', '').removeprefix('json')
                resp_dict = json.loads(resp_text)
                st.session_state['gpt_response'] = f"""{resp_dict["answer"] }\nSources: {resp_dict["sources"]}"""
                # Seperate the IDs and use them to get the images' byte arrays from open AI.
                visuals = resp_dict["visualization_file_id"]
                viz_bytes = []
                if visuals and visuals != '': # Make sure visuals is not the None value and is not the empty string.
                    visual_IDs_list = visuals.split(", ")
                    viz_bytes = [client.files.content(viz) for viz in visual_IDs_list] 

                st.success("Data sent to Make.com successfully!")
                st.write("### GPT Response")
                st.write(st.session_state["gpt_response"])
                if viz_bytes != []: # Display the images of any charts/graphs if there were any.
                    st.image(viz_bytes, use_container_width=True)
            else:
                response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with Make.com: {e}")

        # Delete all the files from OpenAI once user's question is answered
        deletion = [client.files.delete(f) for f in st.session_state['file_data']]
        st.session_state['file_data'].clear()
    
        st.session_state['up_files'] += 1 # Clear the file uploader.
        st.session_state['disable_que'] = True # Disable the chat input until files are uploaded again.

    with st.container():
        # Let the user upload files via `st.file_uploader`.
        st.file_uploader("Upload Documents", on_change=upload_processing, accept_multiple_files=True, key=st.session_state['up_files'])
        
        # Ask the user for a question via `st.chat_input`.
        st.chat_input(
            placeholder="""Now ask a question about the documents!""",
            on_submit=submission,
            disabled=st.session_state['disable_que'],
            key='que'
        )

if __name__ == "__main__":
    main()
