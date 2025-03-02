# ResearchPal Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Command Reference](#command-reference)
5. [Interactive Shell](#interactive-shell)
6. [API Reference](#api-reference)
7. [Project Structure](#project-structure)
8. [Development Guide](#development-guide)
9. [Customization](#customization)
10. [Troubleshooting](#troubleshooting)

## Introduction

ResearchPal is an AI-powered research assistant that helps you process, understand, and extract insights from scientific papers. It leverages large language models (LLMs) like GPT-4o and Gemini to provide intelligent analysis of research literature.

### Key Features

- PDF processing and text extraction
- Automatic summarization of papers
- Key takeaway extraction
- Mathematical formulation identification
- Code implementation generation
- Blog post creation
- Interactive AI-powered discussions about papers
- Research domain classification
- Vector database for semantic search

## Installation

### Prerequisites

- Python 3.8 or higher
- API keys for LLM providers (OpenAI and/or Google)

### pip Installation

```bash
pip install research-pal
```

### From Source

```bash
git clone https://github.com/username/research-pal.git
cd research-pal
pip install -e .
```

## Configuration

ResearchPal requires configuration before first use. You can run the configuration wizard with:

```bash
research-pal configure
```

This will guide you through setting up:
- API keys (OpenAI, Google)
- Default LLM model selection
- Database location
- Output settings
- UI theme preference
- Token limits

### Configuration File

Configuration is stored in `~/.research_pal/config.yaml`. You can edit this file directly if needed:

```yaml
openai_api_key: "sk-..."
google_api_key: "AIza..."
default_model: "gpt-4o-mini"
output_token_limit: 4096
db_path: "~/.research_pal/chroma_db"
output_dir: "~/research_output"
```

## Command Reference

### Main Commands

| Command | Description |
|---------|-------------|
| `research-pal` | Launch the interactive shell |
| `research-pal configure` | Run configuration wizard |
| `research-pal shell` | Launch the interactive shell (explicit) |
| `research-pal version` | Display version information |
| `research-pal test <file_path>` | Test file processing |
| `research-pal test --test-api` | Test API connectivity |

### Command Options

| Option | Description |
|--------|-------------|
| `--debug` | Enable debug logging |
| `--theme` | Select UI theme (cyberpunk, matrix, midnight) |
| `--config-path` | Specify custom config path |
| `--minimal` | Use minimal UI |
| `--no-animation` | Disable startup animation |

## Interactive Shell

The interactive shell is the primary interface for ResearchPal. It provides a command-line interface with rich formatting and visualization capabilities.

### Shell Commands

#### Paper Search and Management

| Command | Description |
|---------|-------------|
| `search <query> [-n <count>]` | Search for papers in the database |
| `search domain:<domain_name>` | Search for papers in a specific research domain |
| `search title:<paper_title>` | Search specifically for paper titles |
| `search takeaway:<concept>` | Search in paper takeaways |
| `domains [-n <count>]` | List all research domains in the database |
| `open <paper_id>` | Open a paper and set it as current context |

#### Paper Analysis

| Command | Description |
|---------|-------------|
| `show <section>` | Show a section of current paper |
| `show all` | Display the complete paper summary |
| `show summary` | Show paper summary |
| `show takeaways` | Show key takeaways |
| `show architecture` | Show architecture details |
| `show future` | Show future research directions |
| `show background` | Show background information |
| `show math` | Show mathematical formulations |
| `show domain` | Show domain classification |
| `discuss <question>` | Discuss the current paper with the AI assistant |

#### Content Generation

| Command | Description |
|---------|-------------|
| `summarize <pdf_path>` | Summarize a new paper |
| `summarize <pdf_path> --code` | Summarize and generate code implementation |
| `summarize <pdf_path> --blog` | Summarize and generate blog post |
| `summarize <pdf_path> --token-limit <limit>` | Summarize with custom token limit |
| `generate code` | Generate code implementation for current paper |
| `generate blog` | Generate blog post for current paper |
| `add <field> <content>` | Add information to the current paper |

#### Interface Control

| Command | Description |
|---------|-------------|
| `theme <theme_name>` | Change the UI theme |
| `clear` | Clear the screen |
| `refresh` | Refresh the display (show logo) |
| `exit` or `quit` | Exit the interactive shell |
| `help` | Show help message |
| `help <command>` | Show help for specific command |

### Examples

#### Summarizing a Paper

```
> summarize ~/papers/transformer.pdf
```

This will process the paper, generate a comprehensive summary, and store it in the database.

#### Advanced Summarization Options

```
> summarize ~/papers/transformer.pdf --code --blog --token-limit 8000 --model gpt-4o
```

This will:
- Process the paper
- Generate a comprehensive summary
- Generate implementation code
- Create a blog post
- Use a token limit of 8000
- Use the GPT-4o model

#### Discussing a Paper

```
> open f7a2b3c4d5
> discuss What are the key innovations in this paper?
```

#### Adding Information

```
> add takeaways "The paper introduces a novel approach to attention mechanisms"
> add domain "Natural Language Processing"
```

## API Reference

ResearchPal is designed to be usable not only as a standalone application but also as a library in your Python code.

### Core Components

#### PaperSummarizer

The `PaperSummarizer` class is the central component for paper analysis.

```python
from research_pal.core.summarizer import PaperSummarizer
from research_pal.core.llm_interface import LLMInterface
from research_pal.db.chroma_manager import ChromaManager

# Initialize components
llm_interface = LLMInterface(default_model="gpt-4o-mini")
db_manager = ChromaManager(persist_directory="~/my_papers_db")
summarizer = PaperSummarizer(
    llm_interface=llm_interface,
    db_manager=db_manager,
    output_token_limit=4096
)

# Summarize a paper
import asyncio
result = asyncio.run(summarizer.summarize_paper(
    filepath="path/to/paper.pdf",
    generate_code=True,
    generate_blog=True
))

# Search for papers
papers = summarizer.search_papers("attention mechanisms", n_results=5)

# Get a specific paper
paper = summarizer.get_paper_summary("paper_id_here")
```

#### LLMInterface

The `LLMInterface` class handles interactions with LLM APIs.

```python
from research_pal.core.llm_interface import LLMInterface
import asyncio

# Initialize
llm = LLMInterface(default_model="gemini-1.5-flash")

# Query model
response = asyncio.run(llm.query_model(
    prompt="Explain transformer architecture",
    system_message="You are a helpful AI assistant",
    temperature=0.3,
    max_tokens=1000
))

# Generate code implementation
code = asyncio.run(llm.generate_code_implementation(
    architecture_details="Transformer with 8 attention heads...",
    paper_title="Attention Is All You Need"
))
```

#### ChromaManager

The `ChromaManager` class handles database operations.

```python
from research_pal.db.chroma_manager import ChromaManager

# Initialize
db = ChromaManager(persist_directory="~/my_research_db")

# Add a paper
db.add_paper(
    paper_id="unique_id",
    title="Paper Title",
    filepath="/path/to/paper.pdf",
    summary="This paper introduces...",
    takeaways=["First takeaway", "Second takeaway"],
    domain="Computer Vision"
)

# Get a paper
paper = db.get_paper("unique_id")

# Search papers
results = db.search_papers("neural networks", n_results=5)

# Search by domain
cv_papers = db.search_by_domain("Computer Vision", n_results=10)
```

### Helper Functions

#### Display Utilities

```python
from research_pal.utils.display import display_summary, display_paper_list
from rich.console import Console

console = Console()

# Display a paper summary
display_summary(paper, theme="cyberpunk")

# Display a list of papers
display_paper_list(papers, theme="matrix")
```

## Project Structure

ResearchPal follows a modular architecture to enhance maintainability and extensibility.

### Directory Structure

```
research_pal/
├── __init__.py
├── cli/                # Command-line interface
│   ├── __init__.py
│   ├── interactive.py  # Interactive shell
│   └── main.py         # Entry point
├── core/               # Core functionality
│   ├── __init__.py
│   ├── llm_interface.py # LLM API interactions
│   ├── pdf_processor.py # PDF extraction
│   ├── prompts.py      # System prompts
│   └── summarizer.py   # Paper summarization
├── db/                 # Database management
│   ├── __init__.py
│   └── chroma_manager.py # Vector database
├── utils/              # Utilities
│   ├── __init__.py
│   ├── config.py       # Configuration handling
│   ├── display.py      # Display functions
│   └── enhanced_display.py # Advanced UI
└── tests/              # Test suite
    ├── __init__.py
    ├── test_llm_interface.py
    ├── test_pdf_processor.py
    └── test_summarizer.py
```

### Key Files and Their Functions

#### CLI Components

- **main.py**: Main entry point with CLI commands
- **interactive.py**: Interactive shell implementation

#### Core Components

- **llm_interface.py**: Handles interactions with LLM APIs
- **pdf_processor.py**: Extracts text and metadata from PDFs
- **summarizer.py**: Coordinates the paper analysis process
- **prompts.py**: Contains system prompts for LLM interactions

#### Database Components

- **chroma_manager.py**: Manages vector database operations

#### Utility Components

- **config.py**: Handles loading and saving configuration
- **display.py**: Basic display functions
- **enhanced_display.py**: Rich UI components

### Dependencies

ResearchPal relies on the following key libraries:

| Library | Purpose |
|---------|---------|
| **rich** | Terminal UI and formatting |
| **click** | Command-line interface |
| **chromadb** | Vector database for paper storage |
| **httpx** | Async HTTP requests to LLM APIs |
| **tenacity** | Retry logic for API requests |
| **pdfminer.six** | PDF text extraction |
| **pyyaml** | Configuration file handling |

## Development Guide

This section provides guidance for developers who want to contribute to ResearchPal.

### Setting Up a Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/username/research-pal.git
   cd research-pal
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

Run the test suite to ensure everything is working correctly:

```bash
pytest
```

For more detailed test output:

```bash
pytest -v
```

For code coverage information:

```bash
pytest --cov=research_pal
```

### Development Workflow

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests

3. Run the test suite to ensure your changes don't break existing functionality:
   ```bash
   pytest
   ```

4. Run linting to ensure code quality:
   ```bash
   flake8 research_pal
   ```

5. Commit your changes using conventional commit messages:
   ```bash
   git commit -m "feat: add new feature"
   ```

6. Push your branch and create a pull request

### Adding New Features

#### Adding a New Command

To add a new command to the interactive shell:

1. Add a `do_commandname` method to the `InteractiveShell` class in `interactive.py`:
   ```python
   def do_newcommand(self, arg):
       """
       Command documentation.
       
       Usage: newcommand <arguments>
       """
       # Your command implementation here
   ```

2. Update the `do_help` method to include your new command

#### Supporting a New LLM Provider

To add support for a new LLM provider:

1. Add the provider's configuration to the `model_configs` dictionary in `LLMInterface.__init__`
2. Create a new method `query_newprovider` similar to `query_openai` or `query_google`
3. Update the `_select_provider` and `query_model` methods to handle the new provider

### Code Style Guidelines

ResearchPal follows these code style guidelines:

- PEP 8 for general Python style
- Google-style docstrings
- Type hints for all function parameters and return values
- Line length limit of 88 characters
- Use of f-strings for string formatting
- Comprehensive error handling

Example:

```python
def process_data(data: List[str], max_items: int = 10) -> Dict[str, Any]:
    """
    Process the input data and return results.
    
    Args:
        data: List of strings to process
        max_items: Maximum number of items to process
        
    Returns:
        Dictionary containing processed results
        
    Raises:
        ValueError: If data is empty or max_items is less than 1
    """
    if not data:
        raise ValueError("Input data cannot be empty")
    if max_items < 1:
        raise ValueError(f"max_items must be positive, got {max_items}")
        
    results = {}
    # ... implementation ...
    return results
```

## Customization

ResearchPal offers several customization options to adapt to your specific needs and preferences.

### UI Themes

ResearchPal comes with three built-in themes:
- **Cyberpunk**: Cyan and magenta color scheme (default)
- **Matrix**: Green-focused theme
- **Midnight**: Blue-focused dark theme

Change the theme using the `theme` command in the interactive shell:
```
> theme matrix
```

Or set it when starting ResearchPal:
```bash
research-pal --theme midnight
```

### Custom Prompts

You can customize the system prompts used for LLM interactions by modifying the prompt templates in `prompts.py`. This allows you to adjust how ResearchPal analyzes papers based on your specific fields or preferences.

For example, to customize the summarization prompt for papers in a specific field:

```python
# Custom prompt for physics papers
PHYSICS_PAPER_PROMPT = """You are ResearchPal, an expert in physics research papers.
... custom prompt specific to physics papers ...
"""

# Use it in your code
if paper_domain == "Physics":
    system_message = PHYSICS_PAPER_PROMPT
else:
    system_message = DEFAULT_PAPER_PROMPT
```

### Blog Generation Styling

When generating blog posts, you can provide a sample of your writing style to make the generated content match your style. Create a text file with a sample of your writing and use it with the `--blog-style` parameter:

```bash
research-pal summarize paper.pdf --blog --blog-style my_writing_sample.txt
```

Or in the interactive shell:
```
> generate blog --blog-style my_writing_sample.txt
```

### Database Customization

You can customize the database location to store papers in different collections or to share databases with colleagues:

```python
from research_pal.db.chroma_manager import ChromaManager

# Create a custom database
team_db = ChromaManager(persist_directory="/shared/team_papers_db")

# Add papers to this specific database
team_db.add_paper(...)
```

### Output Token Limits

You can adjust the output token limit to control the verbosity of generated content:

```bash
research-pal summarize paper.pdf --token-limit 8000
```

This is particularly useful for very complex papers that might need more detailed analysis.

### Adding Custom Commands

For advanced users, you can extend ResearchPal with custom commands by subclassing the `InteractiveShell` class:

```python
from research_pal.cli.interactive import InteractiveShell

class CustomShell(InteractiveShell):
    def do_custom_command(self, arg):
        """My custom command."""
        # Implementation here
        print("Custom command executed!")

# Use your custom shell
if __name__ == "__main__":
    shell = CustomShell()
    shell.cmdloop()
```

## Troubleshooting

This section covers common issues and their solutions.

### API Key Issues

**Problem**: `OpenAI API key not found` or `Google API key not found` errors

**Solution**:
1. Run `research-pal configure` to set up your API keys
2. Ensure the correct API keys are in your configuration file
3. Check that the environment variables `OPENAI_API_KEY` or `GOOGLE_API_KEY` are set correctly if you're using them

### PDF Processing Issues

**Problem**: ResearchPal cannot properly extract text from some PDFs

**Solution**:
1. Ensure the PDF is not scanned or image-based; ResearchPal works best with digital PDFs
2. Try preprocessing the PDF with OCR software if it's scanned
3. Check that the PDF isn't password-protected

**Problem**: Mathematical formulas are not extracted correctly

**Solution**:
1. ResearchPal has limited support for LaTeX extraction; complex formulas might be processed imperfectly
2. For papers with critical mathematical content, verify the extracted formulations

### Database Issues

**Problem**: `ChromaDB connection error` or similar database errors

**Solution**:
1. Check that the database directory path in your configuration is valid and accessible
2. Ensure you have write permissions to the database directory
3. Try running `research-pal` with administrator privileges if necessary
4. If the database is corrupted, you may need to delete it and start fresh

### API Rate Limiting

**Problem**: Receiving rate limit errors from OpenAI or Google APIs

**Solution**:
1. Process fewer papers at once
2. Increase the retry delay in `llm_interface.py`
3. Consider using a different model with higher rate limits
4. Upgrade your API plan with the provider

### Memory Issues

**Problem**: Running out of memory when processing large papers

**Solution**:
1. Adjust the chunk size in your config file to process smaller pieces at a time
2. Close other memory-intensive applications
3. Use a machine with more RAM
4. Try a different model that requires less memory

### Installation Problems

**Problem**: Package installation fails with dependency errors

**Solution**:
1. Update pip: `pip install --upgrade pip`
2. Ensure you have the required Python version (3.8+)
3. Install dependencies manually first: `pip install rich click httpx tenacity chromadb pdfminer.six pyyaml`
4. Try creating a fresh virtual environment

### Debug Mode

For persistent issues, run ResearchPal in debug mode to get more detailed logs:

```bash
research-pal --debug
```

This will provide verbose logging information that can help diagnose problems.

### Reporting Issues

If you encounter a bug or persistent issue, please report it on the GitHub repository with:
1. A detailed description of the problem
2. Steps to reproduce the issue
3. Your environment details (OS, Python version, etc.)
4. Any relevant error messages or logs

## Conclusion

ResearchPal is designed to transform how researchers interact with scientific literature. By leveraging the power of AI, it helps you process, understand, and extract insights from papers with unprecedented efficiency.

We hope this documentation helps you make the most of ResearchPal. For any questions not covered here, please reach out to the community on GitHub or Discord.

Happy researching!

---

*© 2025 ResearchPal Contributors. Licensed under MIT.*