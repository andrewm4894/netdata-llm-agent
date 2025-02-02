from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="netdata-llm-agent",
    version="0.1.0",
    author="Andrew Maguire",
    author_email="andrewm4894@gmail.com",
    description="A language model agent that interacts with Netdata API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrewm4894/netdata-llm-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langgraph",
        "langchain-core",
        "langchain-openai",
        "langchain-anthropic",
        "langchain-ollama",
        "requests",
        "pandas",
        "markdownify",
        "streamlit",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "netdata-llm=netdata_llm_agent.cli:main",
            "netdata-llm-app=netdata_llm_agent.app:main",
        ],
    },
)
