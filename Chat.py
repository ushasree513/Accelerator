import requests
import streamlit as st

api_url = "https://api.langflow.astra.datastax.com/lf/a4a1bb07-f60a-4d47-ba9c-fa70dc6f603b/api/v1/run/696810d5-6526-4272-a734-a6e4f5739705"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer AstraCS:DUtgjqmHJHPZxTkmjurxUuIC:23712c069a37c11b02b4ec09ce13ad4b0ab0553b92d042ec7f90b1a4fe3b8ab1"
}

def send_request(input_value, stream="false", method="POST"):
    """Sends a request to the API with a JSON body and processes the JSON response.

    Args:
        input_value (str): The user input to send to the API.
        stream (str, optional): The stream value (default: "false").
        method (str, optional): The HTTP method (default: "POST").

    Returns:
        dict or None: The JSON response from the API, or None on error.
    """
    # JSON payload for the request
    json_payload = {
        "input_value": input_value,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "ChatInput-8RV6X": {
                "background_color": "white",
                "chat_icon": "",
                "files": "",
                "sender": "User",
                "sender_name": "User",
                "session_id": "",
                "should_store_message": True,
                "text_color": "Red"
            },
            "ParseData-fS7ix": {"sep": "\n", "template": "{text}"},
            "Prompt-XzjEZ": {
                "context": "",
                "question": "",
                "template": "Memory : {Memory}\n---\n{context}\n\n---\n\nGiven the context above, answer the question as best as possible based on the context.\n\nQuestion: {context} + {question}\n\nAnswer: ",
                "Memory": ""
            },
            "SplitText-GzUt3": {"chunk_overlap": 200, "chunk_size": 1000, "separator": "\n"},
            "OpenAIModel-Rt5J9": {
                "api_key": "Open_AI_Key",
                "input_value": "",
                "json_mode": False,
                "max_tokens": None,
                "model_kwargs": {},
                "model_name": "gpt-4o-mini",
                "openai_api_base": "",
                "output_schema": {},
                "seed": 1,
                "stream": False,
                "system_message": "",
                "temperature": 0.1
            },
            "ChatOutput-Ej2y2": {
                "background_color": "",
                "chat_icon": "",
                "data_template": "{text}",
                "input_value": "",
                "sender": "Machine",
                "sender_name": "AI",
                "session_id": "",
                "should_store_message": True,
                "text_color": ""
            },
            "OpenAIEmbeddings-ECHhD": {
                "chunk_size": 1000,
                "model": "text-embedding-3-small",
                "tiktoken_enable": True,
                "tiktoken_model_name": ""
            }
        }
    }

    try:
        # Sending the HTTP request
        response = requests.request(method, api_url, headers=headers, json=json_payload)
        #print (json_payload.context)
        response.raise_for_status()  # Raise an exception for error HTTP statuses
        return response.json()  # Assuming the API always returns JSON

    except requests.exceptions.RequestException as e:
        st.error(f"Error sending request: {e}")
        return None

def handle_json_response(response):
    """Process the JSON response."""
    if isinstance(response, str):
        return response

    response_text = response.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "")
    if not response_text:
        st.error("API response is missing 'text' field.")
    return response_text

# Streamlit app setup
st.set_page_config(page_title="API Chatbot", page_icon="")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input and stream value
if prompt := st.chat_input(placeholder="Enter your message"):
    stream_value = "false"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = send_request(prompt, stream_value, method="POST")

            if response:
                response_text = handle_json_response(response)
                st.markdown(f"**Assistant:**\n{response_text}")
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error("Failed to get a response from the API.")