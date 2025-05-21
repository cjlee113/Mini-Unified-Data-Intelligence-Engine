import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from agents.router_agent import route_query
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.title("Enterprise AI Search (RAG Demo)")

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

query = st.text_input("Ask a question:")

if st.button("Submit"):
    # Route the query through your agent
    agent_output = route_query(query)
    st.write("**Agent Output:**")
    st.write(agent_output)

    # If OpenAI API key is set, send to GPT-4
    if OPENAI_API_KEY:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        with st.spinner("Generating answer with GPT-4..."):
            prompt = f"User question: {query}\n\nAgent context: {agent_output}\n\nAnswer the user's question using the context above."
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.2,
            )
            answer = response.choices[0].message.content
        st.write("**GPT-4 Answer:**")
        st.write(answer)
    else:
        st.info("Set your OPENAI_API_KEY in the .env file to enable GPT-4 answers.")