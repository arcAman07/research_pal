# ResearchPal: AI-Powered Research Assistant

<div align="center">
  <img src="docs/images/researchpal_logo.svg" alt="ResearchPal Logo" width="300">
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python" alt="Python 3.8+">
    <img src="https://img.shields.io/badge/LLMs-GPT--4o%20%7C%20Gemini-green?style=flat-square" alt="LLMs">
    <img src="https://img.shields.io/badge/Status-Beta-orange?style=flat-square" alt="Status">
  </p>
  
  <h3>Your intelligent companion for scientific literature</h3>
</div>

## Overview

**ResearchPal** transforms how researchers interact with scientific literature by leveraging AI to extract, analyze, and organize research papers. It helps you understand papers faster, compare multiple works, generate code implementations, and discuss complex concepts with an AI assistant.

## Key Features

🔍 **Smart Paper Analysis**
- Extract and summarize research papers from PDFs
- Identify key takeaways, methodologies, and insights
- Classify papers into appropriate research domains
- Extract mathematical formulations and model architectures

🔎 **Advanced Search**
- Find papers by content, domain, title, or specific concepts
- Semantic search that understands meaning, not just keywords
- Browse papers by research domain

💬 **AI-Powered Discussion**
- Ask questions about papers and receive detailed answers
- Get explanations of complex concepts
- Explore implications and limitations of research

🔄 **Multi-Paper Comparison**
- Compare methodologies, results, and architectures across papers
- Generate comprehensive comparison reports
- Identify similarities and differences between approaches

💻 **Code Generation**
- Automatically implement paper architectures in Python
- Generate well-commented, working code
- Support for popular frameworks like PyTorch

📝 **Content Creation**
- Generate blog posts explaining papers in accessible language
- Create customized summaries with adjustable detail levels
- Export summaries to Markdown files

## Installation

### From PyPI (Recommended)

```bash
pip install research-pal
```

### From Source

```bash
git clone https://github.com/username/research-pal.git
cd research-pal
pip install -e .
```

## Getting Started

### 1. Configure API Keys

ResearchPal requires at least one of these API keys:
- [OpenAI API Key](https://platform.openai.com/account/api-keys) (for GPT models)
- [Google API Key](https://ai.google.dev/) (for Gemini models)

Run the configuration wizard:

```bash
research-pal configure
```

### 2. Launch the Interactive Shell

```bash
research-pal
```

### 3. Try Basic Commands

```bash
# Summarize a paper
summarize path/to/paper.pdf

# Search your paper collection
search neural networks

# Open a paper and discuss it
open abc123
discuss What are the key innovations in this paper?
```

## Command Reference

### Paper Management

| Command | Description |
|---------|-------------|
| `search <query> [-n <count>]` | Search for papers |
| `search domain:<domain>` | Search by research domain |
| `search title:<title>` | Search by paper title |
| `search takeaway:<concept>` | Search in paper takeaways |
| `open <paper_id>` | Open a paper |
| `history [<count>]` | Show recently opened papers |
| `switch <number>` | Switch to a paper from history |

### Paper Analysis

| Command | Description |
|---------|-------------|
| `show <section>` | Show a section of current paper |
| `show all` | Display full paper summary |
| `discuss <question>` | Discuss the current paper |
| `add <field> <content>` | Add info to current paper |

### Paper Processing

| Command | Description |
|---------|-------------|
| `summarize <pdf_path>` | Summarize a new paper |
| `summarize <pdf_path> --output <path>` | Save summary to path |
| `summarize <pdf_path> --force` | Re-summarize existing paper |
| `summarize <pdf_path> --code` | Generate implementation code |
| `summarize <pdf_path> --blog` | Generate blog post |
| `generate code` | Generate code for current paper |
| `generate blog` | Generate blog post for current paper |
| `export <file_path>` | Export current paper to file |

### Paper Comparison

| Command | Description |
|---------|-------------|
| `compare_add [<paper_id>]` | Add paper to comparison list |
| `compare_remove <index>` | Remove paper from comparison |
| `compare_list` | List papers for comparison |
| `compare_clear` | Clear comparison list |
| `compare [<aspect>]` | Generate comparison |

### Interface Control

| Command | Description |
|---------|-------------|
| `theme <theme_name>` | Change UI theme |
| `debug on\|off` | Toggle debug mode |
| `clear` | Clear screen |
| `exit`, `quit` | Exit the shell |
| `help [<command>]` | Show help |

## Examples

### Summarizing a Paper

```bash
> summarize ~/papers/transformer.pdf
```

![Summary Example](docs/images/summary_example.png)

### Saving a Summary to a Specific Location

```bash
> summarize path/to/paper.pdf --output ~/research/summaries/paper_summary.md
```

### Comparing Multiple Papers

```bash
> search title:Transformer
> open abc123
> compare_add
> search title:BERT
> open def456
> compare_add
> compare methodology
```

### Discussing a Paper

```bash
> open abc123
> discuss What are the key innovations in this paper?
```

### Finding Papers by Domain

```bash
> search domain:Computer Vision
```

## Advanced Settings

Configure ResearchPal's behavior:

```bash
research-pal configure
```

Options include:
- LLM model selection
- Output token limits
- Database location
- Output directory
- Theme preferences

## Development and Testing

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/username/research-pal.git
cd research-pal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest -v  # For verbose output
pytest --cov=research_pal  # For coverage information
```

## Documentation

Comprehensive documentation is available in the [docs](docs/) directory.

## Troubleshooting

See the [Troubleshooting Guide](docs/troubleshooting.md) for solutions to common issues.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Built with [OpenAI](https://openai.com/) and [Google Gemini](https://deepmind.google/technologies/gemini/) APIs
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Powered by [Rich](https://github.com/Textualize/rich) for terminal UI