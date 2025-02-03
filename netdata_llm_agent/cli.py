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
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from netdata_llm_agent.agent import NetdataLLMAgent

load_dotenv()

console = Console()


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


def print_and_save_message(message, chat_history, separator=True, is_markdown=False):
    """Print a message and add it to chat history."""
    if separator:
        console.print("─" * 75, style="dim")
        console.print()  # Add newline after separator

    if is_markdown:
        console.print(Markdown(message))
    else:
        console.print(message)

    if separator:
        console.print()  # Add newline before separator
        console.print("─" * 75, style="dim")
        console.print()  # Add newline after separator

    chat_history.append("─" * 75)
    chat_history.append("")  # Add newline in saved history
    chat_history.append(message)
    chat_history.append("")  # Add newline in saved history
    chat_history.append("─" * 75)
    chat_history.append("")  # Add newline in saved history


def get_chat_title(agent, chat_history):
    """
    Get a short descriptive title for the chat from the agent.

    Args:
        agent: The NetdataLLMAgent instance
        chat_history: A list of strings representing the chat history

    Returns:
        A string representing the title of the chat
    """
    try:
        prompt = """Based on the chat history above, generate a very short (3-5 words) title that describes

        the main topic discussed. Return ONLY the title, no quotes or extra text."""

        chat_summary = "\n".join(
            line for line in chat_history
            if not line.startswith("─") and not line.startswith("Chat history saved")
        )

        title = agent.chat(
            chat_summary + "\n" + prompt,
            return_last=True,
            no_print=True,
            continue_chat=False
        )

        clean_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        clean_title = clean_title.strip().replace(" ", "_")
        return clean_title
    except Exception as e:
        console.print(f"[yellow]Could not generate title: {e}[/yellow]")
        return "untitled_chat"


def main():
    """Main function for the CLI."""

    args = parse_args()
    agent = NetdataLLMAgent(netdata_host_urls=args.host, model=args.model)

    chat_history = []

    if args.question:
        try:
            response = agent.chat(args.question, return_last=True, no_print=True)
            print_and_save_message(f"Agent: {response}\n", chat_history, is_markdown=True)
        except Exception as e:
            console.print(f"[red]An error occurred while processing your question: {e}[/red]\n")
            chat_history.append(f"An error occurred while processing your question: {e}\n")
        return

    welcome_message = """# Welcome to the Netdata LLM Agent CLI!

- Type your query about Netdata (e.g., charts, alarms, metrics) and press Enter
- Type `/exit`, `/quit` or `/bye` to end the session
- Type `/save` to save the chat history to a file
- Type `/good` to save with good_ prefix, `/bad` to save with bad_ prefix (useful for debugging in langsmith)
- Type `/reset` to clear chat history and restart the agent
"""
    print_and_save_message(welcome_message, chat_history, is_markdown=True)

    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ").strip()
            chat_history.append(f"\nYou: {user_input}")
        except (KeyboardInterrupt, EOFError):
            print_and_save_message("\nExiting...", chat_history)
            break

        if user_input.lower() in ("/exit", "/quit", "/bye"):
            console.print("[yellow]Goodbye![/yellow]")
            chat_history.append("Goodbye!")
            break

        if user_input.lower() == "/reset":
            chat_history = []
            agent = NetdataLLMAgent(netdata_host_urls=args.host, model=args.model)
            console.print("[green]Chat history cleared and agent reinitialized![/green]")
            chat_history.append("Chat history cleared and agent reinitialized!")
            continue

        if user_input.lower() in ("/save", "/good", "/bad"):
            os.makedirs("example_chats", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            chat_title = get_chat_title(agent, chat_history)

            prefix = ""
            if user_input.lower() in ("/good", "/bad"):
                prefix = f"{user_input[1:]}_"

            filename = f"example_chats/{prefix}{chat_title}_{timestamp}_{str(uuid.uuid4())[:8]}.md"

            with open(filename, "w", encoding="utf-8") as f:
                for entry in chat_history:
                    f.write(f"{entry}\n")

            console.print(f"[blue]Chat history saved to: {filename}[/blue]")
            chat_history.append(f"Chat history saved to: {filename}")
            continue

        if not user_input:
            continue

        try:
            response = agent.chat(
                user_input, return_last=True, no_print=True, continue_chat=True
            )
            print_and_save_message(f"Agent: {response}\n", chat_history, is_markdown=True)

        except Exception as e:
            error_msg = f"An error occurred while processing your request: {e}\n"
            console.print(f"[red]{error_msg}[/red]")
            chat_history.append(error_msg)


if __name__ == "__main__":
    main()
