import streamlit as st
from prompt import prompt
from persist import persist_data

def stick_header():
    # make header sticky.
    st.markdown(
        """
            <div class='fixed-header'/>
            <style>
                div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                    position: sticky;
                    top: 2.875rem;
                    background-color: #2D3748;
                    z-index: 999;
                }
                .fixed-header {
                    border-bottom: 2px solid white;
                }
            </style>
        """,
        unsafe_allow_html=True
    )

container =  st.container()

with container:
    st.markdown("# WikiSpeaks")
    stick_header()

# Initialize chat history
if "wikimsg" not in st.session_state:
    st.session_state.wikimsg = []

# Display chat messages from history on app rerun
for message in st.session_state.wikimsg:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if question := st.chat_input("Post your query!"):
# Display user message in chat message container
    st.chat_message("human").markdown(question)
# Add user message to chat history
    st.session_state.wikimsg.append({"role": "human", "content": question})

    with st.spinner("Please wait..."):
        persist_data(question)
        answer = prompt(question)

# Display assistant response in chat message container
    with st.chat_message("ai"):
        response = st.write_stream(answer)
# Add assistant response to chat history
    st.session_state.wikimsg.append({"role": "ai", "content": response})
