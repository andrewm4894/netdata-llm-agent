#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple CLI for interacting with the Netdata LLM Agent.
"""

import argparse
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from netdata_llm_agent.agent import NetdataLLMAgent

load_dotenv()


def parse_args():
    """Parse command-line arguments."""

    default_hosts_str = os.environ.get("NETDATA_URL_LIST", "http://localhost:19999")
    default_hosts = [
        host.strip() for host in default_hosts_str.split(",") if host.strip()
    ]

    parser = argparse.ArgumentParser(
        description="CLI for the Netdata LLM Agent Chat. "
        "Specify one or more Netdata host URLs and (optionally) a question to ask."
    )
    parser.add_argument(
        "--host",
        nargs="+",
        default=default_hosts,
        help="Netdata host URL(s) as a space-separated list. "
        "Defaults to the list from NETDATA_URL_LIST in the .env file or 'http://localhost:19999'.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="LLM model to use. Default is 'gpt-4o-mini'.",
    )
    parser.add_argument(
        "--question",
        type=str,
        help="Optional question to ask the agent. If provided, the agent will answer this question and exit.",
    )
    return parser.parse_args()


def print_and_save_message(message, chat_history, separator=True):
    """Print a message and add it to chat history."""
    if separator:
        print("-" * 100)
    print(message)
    if separator:
        print("-" * 100)
    chat_history.append("-" * 100)
    chat_history.append(message)
    chat_history.append("-" * 100)


def main():
    """Main function for the CLI."""

    args = parse_args()
    agent = NetdataLLMAgent(netdata_host_urls=args.host, model=args.model)

    # Initialize chat history
    chat_history = []

    if args.question:
        try:
            response = agent.chat(args.question, return_last=True, no_print=True)
            print_and_save_message(f"Agent: {response}\n", chat_history)
        except Exception as e:
            print_and_save_message(
                f"An error occurred while processing your question: {e}\n", chat_history
            )
        return

    welcome_message = "Welcome to the Netdata LLM Agent CLI!"
    welcome_message += "\nType your query about Netdata (e.g., charts, alarms, metrics) and press Enter."
    welcome_message += "\nType '/exit', '/quit' or '/bye' to end the session."
    welcome_message += "\nType '/save' to save the chat history to a file."
    welcome_message += "\nType '/reset' to clear chat history and restart the agent.\n"
    print_and_save_message(welcome_message, chat_history)

    while True:
        try:
            user_input = input("You: ").strip()
            chat_history.append(f"You: {user_input}")
        except (KeyboardInterrupt, EOFError):
            print_and_save_message("\nExiting...", chat_history)
            break

        if user_input.lower() in ("/exit", "/quit", "/bye"):
            print_and_save_message("Goodbye!", chat_history)
            break

        if user_input.lower() == "/reset":
            chat_history = []
            agent = NetdataLLMAgent(netdata_host_urls=args.host, model=args.model)
            print_and_save_message(
                "Chat history cleared and agent reinitialized!", chat_history
            )
            continue

        if user_input.lower() == "/save":
            os.makedirs("example_chats", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"example_chats/{timestamp}_{str(uuid.uuid4())[:8]}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for entry in chat_history:
                    f.write(f"{entry}\n")

            print_and_save_message(f"Chat history saved to: {filename}", chat_history)
            continue

        if not user_input:
            continue

        try:
            response = agent.chat(
                user_input, return_last=True, no_print=True, continue_chat=True
            )
            print_and_save_message(f"Agent: {response}\n", chat_history)

        except Exception as e:
            print_and_save_message(
                f"An error occurred while processing your request: {e}\n", chat_history
            )


if __name__ == "__main__":
    main()
