import streamlit as st
from netdata_llm_agent import NetdataLLMAgent

DEFAULT_NETDATA_URLS = [
    "http://localhost:19999/",
    "https://london3.my-netdata.io/",
    "https://bangalore.my-netdata.io/",
    "https://newyork.my-netdata.io/",
    "https://sanfrancisco.my-netdata.io/",
    "https://singapore.my-netdata.io/",
    "https://toronto.my-netdata.io/",
]


def init_session_state():
    """Initialize session state variables if not already set."""
    if "netdata_urls" not in st.session_state:
        st.session_state.netdata_urls = DEFAULT_NETDATA_URLS
    if "agent" not in st.session_state:
        st.session_state.agent = NetdataLLMAgent(st.session_state.netdata_urls)
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "reverse_chat" not in st.session_state:
        st.session_state.reverse_chat = False
    if "verbose_mode" not in st.session_state:
        st.session_state.verbose_mode = False


def sidebar_config():
    """Render and handle sidebar configuration."""
    st.sidebar.header("Configuration")

    netdata_url_input = st.sidebar.text_area(
        "Enter Netdata URLs (one per line):",
        value="\n".join(st.session_state.netdata_urls),
        height=150,
    )

    if st.sidebar.button("Update Netdata URLs"):
        new_urls = [
            url.strip() for url in netdata_url_input.splitlines() if url.strip()
        ]
        st.session_state.netdata_urls = new_urls
        st.session_state.agent = NetdataLLMAgent(new_urls)
        st.session_state.conversation = []
        st.rerun()

    st.sidebar.checkbox(
        "Reverse Chat Order",
        key="reverse_chat",
        help="Reverse the order of the chat messages.",
    )

    st.sidebar.checkbox(
        "Verbose Mode", key="verbose_mode", help="Toggle verbose output for debugging."
    )

    if st.sidebar.button("Clear Chat"):
        st.session_state.agent = NetdataLLMAgent(st.session_state.netdata_urls)
        st.session_state.conversation = []
        st.rerun()


def render_conversation():
    """Display the conversation history."""
    conv = st.session_state.conversation.copy()
    if st.session_state.reverse_chat:
        conv.reverse()
    for chat in conv:
        if chat["role"] == "user":
            with st.chat_message("user"):
                st.markdown(chat["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(chat["content"])


def chat_input():
    """Render the chat input form and return user input."""
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Enter your message:", key="input")
        send_pressed = st.form_submit_button("Send")
    return send_pressed, user_input


def main():
    """Main function to run the Streamlit app."""
    st.logo("./static/i-love-trouble.jpg", link="https://www.netdata.cloud/")
    st.title("Netdata LLM Agent Chat")

    init_session_state()
    sidebar_config()

    send_pressed, user_input = chat_input()

    if send_pressed and user_input:
        st.session_state.conversation.append({"role": "user", "content": user_input})
        continue_chat = len(st.session_state.conversation) > 1

        with st.spinner("Agent is thinking..."):
            try:
                if st.session_state.verbose_mode:
                    response = st.session_state.agent.chat(
                        user_input,
                        continue_chat=continue_chat,
                        return_thinking=True,
                        return_last=False,
                    )
                else:
                    response = st.session_state.agent.chat(
                        user_input,
                        continue_chat=continue_chat,
                        return_last=True,
                    )
            except Exception as e:
                response = f"Error: {e}"

        st.session_state.conversation.append({"role": "agent", "content": response})
        st.rerun()

    render_conversation()


if __name__ == "__main__":
    main()
