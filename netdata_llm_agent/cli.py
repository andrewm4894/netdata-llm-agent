#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple CLI for interacting with the Netdata LLM Agent.
"""

import argparse
import os
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from netdata_llm_agent.agent import NetdataLLMAgent
from enum import Enum

load_dotenv()

SEPARATOR_TEXT = "─" * 50 + "  \n"

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
        console.print(SEPARATOR_TEXT, style="dim")

    if is_markdown:
        console.print(Markdown(message))
    else:
        console.print(message)

    if separator:
        console.print(SEPARATOR_TEXT, style="dim")

    chat_history.append(SEPARATOR_TEXT)
    chat_history.append(message + '\n')
    chat_history.append(SEPARATOR_TEXT)


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


class Command(Enum):
    EXIT = ["/exit", "/quit", "/bye"]
    RESET = "/reset"
    SAVE = "/save"
    SAVE_GOOD = "/good"
    SAVE_BAD = "/bad"

class ChatCLI:
    def __init__(self, agent):
        self.agent = agent
        self.chat_history = ChatHistory()
        self.console = Console()

    def handle_command(self, user_input):
        """Handle CLI commands and return True if command was handled."""
        if user_input.lower() in Command.EXIT.value:
            self._handle_exit()
            return True

        if user_input.lower() == Command.RESET.value:
            self._handle_reset()
            return True

        if user_input.lower() in [Command.SAVE.value, Command.SAVE_GOOD.value, Command.SAVE_BAD.value]:
            self._handle_save(user_input.lower())
            return True

        return False

    def _handle_exit(self):
        self.console.print("[yellow]Goodbye![/yellow]")
        self.chat_history.add_message("Goodbye!")

    def _handle_reset(self):
        self.chat_history.clear()
        self.agent = NetdataLLMAgent(netdata_host_urls=self.agent.netdata_host_urls, model=self.agent.model)
        self.console.print("[green]Chat history cleared and agent reinitialized![/green]")
        self.chat_history.add_message("Chat history cleared and agent reinitialized!")

    def _handle_save(self, command):
        os.makedirs("example_chats", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chat_title = get_chat_title(self.agent, self.chat_history.messages)

        prefix = ""
        if command in [Command.SAVE_GOOD.value, Command.SAVE_BAD.value]:
            prefix = f"{command[1:]}_"

        filename = f"example_chats/{prefix}{timestamp}__{chat_title}.md"
        self.chat_history.save_to_file(filename)

        save_message = f"Chat history saved to: {filename}"
        self.console.print(f"[blue]{save_message}[/blue]")
        self.chat_history.add_message(save_message, quiet=True)

    def add_user_message(self, message):
        """Add a user message to the chat history."""
        self.chat_history.add_message(f"You: {message}\n", separator=True, quiet=True)

    def add_agent_message(self, message):
        """Add an agent message to the chat history."""
        self.chat_history.add_message(f"Agent: {message}\n", is_markdown=True)


class ChatHistory:
    def __init__(self):
        self.messages = []
        self.console = Console()

    def add_message(self, message, separator=True, is_markdown=False, quiet=False):
        """
        Add a message to chat history and optionally print it.

        Args:
            message: The message to add
            separator: Whether to print separator lines
            is_markdown: Whether to render the message as markdown
            quiet: If True, don't print the message (just add to history)
        """
        if not quiet:
            if separator:
                self.console.print(SEPARATOR_TEXT, style="dim")

            if is_markdown:
                self.console.print(Markdown(message))
            else:
                self.console.print(message)

            if separator:
                self.console.print(SEPARATOR_TEXT, style="dim")

        self.messages.extend([
            SEPARATOR_TEXT if separator else "",
            message + '\n',
            ""
        ])

    def clear(self):
        """Clear the chat history."""
        self.messages.clear()

    def save_to_file(self, filename):
        """Save chat history to a file."""
        with open(filename, "w", encoding="utf-8") as f:
            for entry in self.messages:
                if entry:
                    f.write(f"{entry}\n")


def main():
    """Main function for the CLI."""
    args = parse_args()
    agent = NetdataLLMAgent(netdata_host_urls=args.host, model=args.model)
    cli = ChatCLI(agent)

    if args.question:
        try:
            response = agent.chat(args.question, return_last=True, no_print=True)
            cli.add_agent_message(response)
        except Exception as e:
            error_msg = f"An error occurred while processing your question: {e}\n"
            console.print(f"[red]{error_msg}[/red]")
            cli.chat_history.add_message(error_msg)
        return

    welcome_message = """# Welcome to the Netdata LLM Agent CLI!

- Type your query about Netdata (e.g., charts, alarms, metrics) and press Enter
- Type `/exit`, `/quit` or `/bye` to end the session
- Type `/save` to save the chat history to a file
- Type `/good` to save with good_ prefix, `/bad` to save with bad_ prefix (useful for debugging in langsmith)
- Type `/reset` to clear chat history and restart the agent
"""
    cli.chat_history.add_message(welcome_message, is_markdown=True)

    while True:
        try:
            user_input = cli.console.input("[bold green]You:[/bold green] ").strip()
            cli.add_user_message(user_input)
        except (KeyboardInterrupt, EOFError):
            cli.chat_history.add_message("\nExiting...")
            break

        if not user_input:
            continue

        if cli.handle_command(user_input):
            if user_input.lower() in Command.EXIT.value:
                break
            continue

        try:
            response = agent.chat(
                user_input, return_last=True, no_print=True, continue_chat=True
            )
            cli.add_agent_message(response)
        except Exception as e:
            error_msg = f"An error occurred while processing your request: {e}\n"
            console.print(f"[red]{error_msg}[/red]")
            cli.chat_history.add_message(error_msg)


if __name__ == "__main__":
    main()
