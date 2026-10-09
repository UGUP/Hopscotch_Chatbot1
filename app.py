import os 
from dotenv import load_dotenv
from pathlib import Path
import streamlit as st
from openai import OpenAI


st.set_page_config(page_title="Hopscotch Return Policy Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Hopscotch Chatbot")
st.caption("This chatbot is designed to answer questions about Hopscotch's return policy. It is powered by OpenRouter and OpenAI's GPT-4 model.")

# Load environment variables from .env file
load_dotenv()

# Get the OpenRouter API key from environment variables
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    st.error("OpenRouter API key not found. Please set it in the .env file.")
    st.stop()

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

# Hardcording the model to openai/gpt-4.o-mini
model = "openai/gpt-4o-mini"

# Creation of Sytem prompt for the chatbot
POLICY = (PATH := Path(__file__).parent / "hopscotch_policy.md").read_text(ENCODING := "utf-8")
SYSTEM_PROMPT = f"""You are a helpful and friendly AI assistant. You will answer questions based on the following policy: {POLICY}
Rules:
- Answer ONLY from the policy above. Never invent rules.
- If you need the delivery date, the item's condition, or the order value, ask for it.
- For ANY Section 4 case (child safety, skin reaction/allergy, order above INR 5,000,
  unclear facts, or uncertainty between defect and misuse) do NOT decide. Tell the
  customer their case will be passed to a human agent.
- For defect claims, ask the customer for photo evidence.
"""

# Memory to store the conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [{ "role" : "system", "content": SYSTEM_PROMPT }]


# create sidebar 
with st.sidebar:
    if st.button("Clear Conversation"):
        st.session_state.conversation_history = [{ "role" : "system", "content": SYSTEM_PROMPT }]
        st.success("Conversation cleared.")
        st.rerun()
    with st.expander("Conversation History list that we resend every turn"):
        st.write(f"Number of Messages in the conversation history: {len(st.session_state.conversation_history)}")
        st.json(st.session_state.conversation_history, expanded=True)
    st.markdown("Example prompts")
    st.code("I bought a dress 10 days ago, never worn, tags on — can I return it?", language=None)
    st.code("The sole of my son's sneakers peeled off after 3 weeks of school", language=None)
    st.code("A button came off and my toddler nearly put it in his mouth", language=None)
    st.code("My order was ₹7,200, I want a refund", language=None)

## render history of conversations and skip system messages
for m in st.session_state.conversation_history:
    if(m["role"] != "system"):
        with st.chat_message(m.get("role", "Unable to determine role")):
            st.markdown(m.get("content", ""))


# one loop iteration : new user message -> send to model -> get response -> display response
if prompt := st.chat_input("Ask me anything about Hopscotch's return policy"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    st.session_state.conversation_history.append({ "role" : "user", "content" : prompt })

    # Send the conversation history to the model and get the response
    with st.spinner("Waiting for Hopscotch's AI assistant to respond..."):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=st.session_state.conversation_history,
                temperature=0.3,  # Lower temperature for more deterministic responses
            )
        
            # Extract the assistant's reply from the response
            assistant_reply = response.choices[0].message.content
            # Display assistant response in chat message container
            st.chat_message("assistant").markdown(assistant_reply)
            st.session_state.conversation_history.append({ "role" : "assistant", "content" : assistant_reply })
        except Exception as e:
            st.error(f"Error occurred while fetching response: {e}")