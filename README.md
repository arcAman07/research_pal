# ResearchPal 🔬📑

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/LLMs-GPT--4o%20%7C%20Gemini-green?style=for-the-badge" alt="LLMs">
  <img src="https://img.shields.io/badge/Status-Beta-orange?style=for-the-badge" alt="Status">
</div>

<p align="center">
  <img src="docs/images/researchpal_logo.svg" alt="ResearchPal Logo" width="300">
</p>

**ResearchPal** is your AI-powered research assistant for scientific literature. It helps you process, understand, and extract insights from research papers with ease.

## ✨ Features

- 📄 **Extract and summarize research papers** from PDFs
- 🔍 **Search your paper collection** by content, domain, and more
- 💡 **Generate key takeaways** and important insights automatically
- 🧠 **Discuss papers** with an AI assistant to deepen understanding
- 🧮 **Extract mathematical formulations** and model architectures
- 💻 **Generate implementation code** for described architectures
- 📝 **Create blog posts** explaining papers in accessible language
- 🌐 **Domain classification** to organize your research collection
- 📊 **Interactive interface** with customizable themes

## 🚀 Quick Start

### Installation

```bash
pip install research-pal
```

### API Keys
ResearchPal uses LLMs for analysis. You'll need at least one of these API keys:
- OpenAI API Key (for GPT models)
- Google API Key (for Gemini models)

### Basic Usage

Launch the interactive shell:
```bash
research-pal
```

Or configure your settings first:
```bash
research-pal configure
```

## 🧰 Commands

### Interactive Shell Commands

| Command | Description |
|---------|-------------|
| `search <query> [-n <count>]` | Search for papers in the database |
| `search domain:<domain_name>` | Search for papers in a specific research domain |
| `open <paper_id>` | Open a paper and set it as current context |
| `show <section>` | Show a section of current paper (summary, takeaways, etc.) |
| `discuss <question>` | Discuss the current paper with the AI assistant |
| `summarize <pdf_path>` | Summarize a new paper |
| `summarize <pdf_path> [--token-limit <limit>]` | Summarize with custom token limit |
| `generate code\|blog` | Generate code implementation or blog post |
| `theme <theme_name>` | Change the UI theme (cyberpunk, matrix, midnight) |

## 📚 Examples

### Summarize a paper
```bash
> summarize path/to/paper.pdf
```

### Generate implementation code
```bash
> summarize path/to/paper.pdf --code
```

### Generate a blog post
```bash
> summarize path/to/paper.pdf --blog
```

### Search for papers in a specific domain
```bash
> search domain:Reinforcement Learning
```

### Discuss a paper with the AI assistant
```bash
> open 8f7e9a1b2c
> discuss What are the limitations of this approach?
```

## 🧩 Advanced Settings

You can customize ResearchPal's behavior by editing your configuration:

```bash
research-pal configure
```

Options include:
- Default LLM model selection
- Output token limits
- Database location
- Output directory for generated files
- Theme preferences

## 🏗️ Project Structure

```
research_pal/
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
└── utils/              # Utilities
    ├── __init__.py
    ├── display.py      # Display functions
    └── enhanced_display.py # Advanced UI
```

## 📋 Requirements

- Python 3.8+
- Required packages:
  - rich
  - click
  - httpx
  - tenacity
  - chromadb
  - pdfminer.six
  - pyyaml

## 🤝 Contributing

Contributions are welcome! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Built with [OpenAI](https://openai.com/) and [Google Gemini](https://deepmind.google/technologies/gemini/) APIs
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Powered by [Rich](https://github.com/Textualize/rich) for terminal UI