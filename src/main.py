import streamlit as st

if __name__ == "__main__" or __name__ == "src.main":
    from agent import create_agent_executor

    def main():
        st.set_page_config(page_title="AI Calendar Agent", page_icon="📅")

        st.title("📅 AI Calendar Agent")
        st.caption("Schedule and manage your tasks using natural language.")

        # Initialize the agent once and store it in session state
        if "agent_executor" not in st.session_state:
            st.session_state.agent_executor = create_agent_executor()

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display past messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle user input
        if prompt := st.chat_input("What would you like to schedule?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Invoke the agent using the new messages format
                response = st.session_state.agent_executor.invoke({"messages": [("user", prompt)]})
                
                # Extract the final answer from the messages list
                final_answer = response["messages"][-1].content
                st.markdown(final_answer)
                
            st.session_state.messages.append({"role": "assistant", "content": final_answer})

    main()