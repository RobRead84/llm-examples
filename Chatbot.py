import streamlit as st
from openai import OpenAI
from langflow.load import run_flow_from_json

st.title("💬 Firehills Eco system agent")
st.caption("🚀 A Streamlit chatbot powered by Firehills")

# Set up API key input in the sidebar
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password", key="openai_api_key")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

# Define Langflow configuration
TWEAKS = {
  "ChatInput-M6iQR": {},
  "Prompt-LF2aH": {},
  "SplitText-tupJH": {},
  "ChatOutput-GEz6P": {},
  "OpenAIEmbeddings-4iBwL": {},
  "File-u2CTZ": {},
  "OpenAIModel-uYwgQ": {},
  "AstraDB-s4pvI": {},
  "AstraDB-TGYg1": {},
  "parser-sfG9k": {}
}

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Type in the name of the organisation you would like to map?"}]

# Display existing chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle chat input
if prompt := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    
    try:
        # Run the Langflow flow with the user's input
        result = run_flow_from_json(
            flow="Firehills Eco System Agent.json",
            input_value=prompt,
            session_id=st.session_state.get("session_id", ""),  # Use existing session_id if available
            fallback_to_env_vars=True,
            tweaks=TWEAKS
        )
        
        # Process the Langflow result
        if result and isinstance(result, dict) and "response" in result:
            msg = result["response"]
        else:
            # Fallback to OpenAI if Langflow doesn't return expected format
            client = OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=st.session_state.messages
            )
            msg = response.choices[0].message.content
            
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
        
    except Exception as e:
        st.error(f"Error processing your request: {str(e)}")