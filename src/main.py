import json
import re

import streamlit as st

if __name__ == "__main__" or __name__ == "src.main":
    from agent import create_agent_executor, tools
    from tools.google_calendar import USER_CONTEXT

    TOOL_MAP = {t.name: t for t in tools}
    MAX_HISTORY = 12

    def run_text_tool_call(answer: str):
        """
        Safety net: if the model printed a tool call as JSON text
        (e.g. {"name": "find_free_slots", "parameters": {...}}) instead of
        making a real tool call, execute it here. Returns the tool result or None.
        """
        match = re.search(r"\{.*\}", answer, re.S)
        if not match:
            return None
        try:
            call = json.loads(match.group(0))
            name = call["name"]
            args = call.get("parameters") or call.get("arguments") or {}
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
        if name not in TOOL_MAP:
            return None
        try:
            return TOOL_MAP[name].invoke(args)
        except Exception as e:
            return f"ERROR: {e}"

    def main():
        st.set_page_config(page_title="AI Calendar Agent", page_icon="📅")

        st.title("📅 AI Calendar Agent")
        st.caption("Schedule and manage your tasks using natural language.")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display past messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What would you like to schedule?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                recent = [
                    m["content"]
                    for m in st.session_state.messages
                    if m["role"] == "user"
                ][-3:]
                USER_CONTEXT["text"] = " ".join(recent)

                history = [
                    (m["role"], m["content"])
                    for m in st.session_state.messages[-MAX_HISTORY:]
                ]

                agent = create_agent_executor()

                with st.spinner("Thinking..."):
                    response = agent.invoke(
                        {"messages": history},
                        config={"recursion_limit": 10},
                    )
                    final_answer = response["messages"][-1].content

                    result = run_text_tool_call(final_answer)
                    if result is not None:
                        followup = history + [
                            ("assistant", final_answer),
                            (
                                "user",
                                f"Tool result: {result}\n"
                                "Answer my last question using this result, "
                                "in English, in one or two short sentences.",
                            ),
                        ]
                        response = agent.invoke(
                            {"messages": followup},
                            config={"recursion_limit": 10},
                        )
                        final_answer = response["messages"][-1].content

                st.markdown(final_answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": final_answer}
            )

    main()