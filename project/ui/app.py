import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from agents.router_agent import route_query
import openai
from dotenv import load_dotenv
from project.feedback.logger import log_feedback

load_dotenv()

st.title("Enterprise AI Search (RAG Demo)")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize session 
if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False
if 'last_query' not in st.session_state:
    st.session_state['last_query'] = ''
if 'last_doc_id' not in st.session_state:
    st.session_state['last_doc_id'] = 'N/A'
if 'last_answer' not in st.session_state:
    st.session_state['last_answer'] = ''

query = st.text_input("Ask a question:")

if st.button("Submit"):
    # Route the query through agent
    agent_output = route_query(query)
    st.write("**Agent Output:**")
    st.write(agent_output)

    # Send to GPT-4 API
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
        st.session_state['last_answer'] = answer
    else:
        st.info("Set your OPENAI_API_KEY in the .env file to enable GPT-4 answers.")
        st.session_state['last_answer'] = agent_output
    st.session_state['submitted'] = True
    st.session_state['last_query'] = query
    st.session_state['last_doc_id'] = "N/A"  # Replace with actual doc_id if available

# This asks for feedback after the question is answered
if st.session_state.get('submitted', False) and st.session_state.get('last_answer', ''):
    st.write("---")
    st.write("### Was this answer helpful?")
    with st.form("feedback_form"):
        rating = st.radio("Your rating:", ["👍", "👎"], horizontal=True)
        comment = st.text_input("Additional comments (optional):", key="feedback_comment")
        submitted_feedback = st.form_submit_button("Submit Feedback")
        if submitted_feedback:
            rating_value = 1 if rating == "👍" else 0
            log_feedback(st.session_state['last_query'], st.session_state['last_doc_id'], rating_value, comment)
            st.success("Thank you for your feedback!")
            st.session_state['submitted'] = False  # Hide feedback after submission