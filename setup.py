from setuptools import setup, find_packages


def read_requirements(filename):
    """Read requirements from file, handling comments and empty lines."""
    with open(filename) as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#") and not line.startswith("-r")
        ]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Try to read from requirements.txt first, fall back to requirements.compile
try:
    requirements = read_requirements("requirements.txt")
except FileNotFoundError:
    requirements = read_requirements("requirements.compile")

setup(
    name="netdata-llm-agent",
    version="0.4.0",
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
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "netdata-llm-cli=netdata_llm_agent.cli:main",
            "netdata-llm-app=netdata_llm_agent.app:run_app",
        ],
    },
)
