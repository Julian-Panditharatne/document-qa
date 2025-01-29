import streamlit as st
import requests
import mimetypes
import base64
import magic  # Install using `pip install python-magic`


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
            mime = magic.Magic(mime=True)  # Create a magic instance
            for file in uploaded_files:
                try:
                    # Read file content
                    file_content = file.read()

                    # Identify file type using magic
                    file_type = mime.from_buffer(file_content)

                    # Base64 encode for transmission (optional)
                    if not file_type.startswith("text/"):  # Skip encoding for text files
                        encoded_data = base64.b64encode(file_content).decode("utf-8")
                        file_content = encoded_data
                    else:
                        # Process file (e.g., convert to base64)
                        file_content = file_content.decode('utf-8')  # Decode to handle potential encoding issues

                    # Create file metadata
                    file_metadata = {
                        "filename": file.name,
                        "content_type": file_type,
                        "size": len(file_content),  # Add file size for potential checks
                    }

                    # Append data (no metadata for now) to the list
                    file_data.append(file_content)
                except Exception as e:
                    st.error(f"Error processing file {file.name}: {e}")
                    
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
