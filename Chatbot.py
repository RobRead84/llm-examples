from openai import OpenAI
import streamlit as st

st.title("💬 Firehills Eco system agent")
st.caption("🚀 A Streamlit chatbot powered by Firehills")
from langflow.load import run_flow_from_json
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

result = run_flow_from_json(flow="Firehills Eco System Agent.json",
                            input_value="message",
                            session_id="", # provide a session id if you want to use session state
                            fallback_to_env_vars=True, # False by default
                            tweaks=TWEAKS)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Type in the name of the organisation you would like to map?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
