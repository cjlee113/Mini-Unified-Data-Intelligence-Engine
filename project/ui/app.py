import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from agents.router_agent import route_query
import openai
from dotenv import load_dotenv
from project.feedback.logger import log_feedback, log_query_audit
from dashboards.metrics import get_all_metrics

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
    start_time = time.time()
    agent_output, tool_name = route_query(query)
    duration = time.time() - start_time
    log_query_audit(query, tool_name, agent_output, duration)
    st.write("**Agent Output:**")
    st.write(agent_output)

    # If OpenAI API key is set, send to GPT-4
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        with st.spinner("Generating answer with GPT-4..."):
            prompt = f"User question: {query}\n\nAgent context: {agent_output}\n\nAnswer the user's question using the context above."
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.2,
            )
            answer = response.choices[0].message["content"]
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

# Sidebar dashboard
with st.sidebar:
    st.header("📊 System Metrics")
    metrics = get_all_metrics()
    st.subheader("Query Count Per Day")
    st.bar_chart(metrics['query_count_per_day'])
    st.subheader("Tool Usage")
    st.bar_chart(metrics['tool_usage_stats'])
    st.subheader("Average Query Time")
    avg_time = metrics['average_query_time']
    if avg_time is not None:
        st.write(f"{avg_time:.2f} seconds")