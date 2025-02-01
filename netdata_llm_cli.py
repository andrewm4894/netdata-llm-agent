#!/usr/bin/env python
"""
netdata_llm_cli.py

A simple CLI for interacting with the Netdata LLM Agent.
"""

import argparse
import os
from dotenv import load_dotenv
from netdata_llm_agent import NetdataLLMAgent

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
        default="gpt-4o",
        help="LLM model to use. Default is 'gpt-4o'.",
    )
    parser.add_argument(
        "--question",
        type=str,
        help="Optional question to ask the agent. If provided, the agent will answer this question and exit.",
    )
    return parser.parse_args()


def main():
    """Main function for the CLI."""

    args = parse_args()

    agent = NetdataLLMAgent(netdata_host_urls=args.host, model=args.model)

    if args.question:
        try:
            response = agent.chat(args.question, return_last=True, no_print=True)
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"An error occurred while processing your question: {e}\n")
        return

    print("Welcome to the Netdata LLM Agent CLI!")
    print(
        "Type your query about Netdata (e.g., charts, alarms, metrics) and press Enter."
    )
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            response = agent.chat(
                user_input, return_last=True, no_print=True, continue_chat=True
            )
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"An error occurred while processing your request: {e}\n")


if __name__ == "__main__":
    main()
