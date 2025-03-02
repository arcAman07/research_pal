# ResearchPal Setup and Testing Guide

This guide provides detailed steps to set up, test, and use ResearchPal locally.

## 1. Initial Setup

### Clone the repository (if installing from source)

```bash
git clone https://github.com/username/research-pal.git
cd research-pal
```

### Set up a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Linux/macOS:
source venv/bin/activate
# For Windows:
# venv\Scripts\activate
```

### Install the package

#### Option 1: Install from source (for development)

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

#### Option 2: Install from PyPI (for regular usage)

```bash
pip install research-pal
```

### Setting up API Keys

ResearchPal requires at least one of the following API keys:

1. **OpenAI API Key** (for GPT models): Get one from https://platform.openai.com/account/api-keys
2. **Google API Key** (for Gemini models): Get one from https://ai.google.dev/

You can configure these keys in any of these ways:

#### Method 1: Using environment variables

```bash
# For Linux/macOS:
export OPENAI_API_KEY="your_openai_key_here"
export GOOGLE_API_KEY="your_google_key_here"

# For Windows Command Prompt:
# set OPENAI_API_KEY=your_openai_key_here
# set GOOGLE_API_KEY=your_google_key_here

# For Windows PowerShell:
# $env:OPENAI_API_KEY="your_openai_key_here"
# $env:GOOGLE_API_KEY="your_google_key_here"
```

#### Method 2: Using the configuration utility

```bash
research-pal configure
```

Follow the prompts to enter your API keys and set other preferences.

#### Method 3: Create a .env file (for development)

```bash
# Create a .env file in the project root:
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "GOOGLE_API_KEY=your_google_key_here" >> .env

# For use with the python-dotenv package (already included in requirements)
```

## 2. Testing the Installation

### Verify command availability

```bash
research-pal --version
```

You should see the version number of ResearchPal.

### Run the test suite

```bash
# Make sure you're in the project root
cd research-pal

# Run tests
pytest

# For more detailed output
pytest -v

# For coverage information
pytest --cov=research_pal
```

### Test the API connectivity

```bash
research-pal test --test-api
```

This will check if your API keys are working properly.

## 3. Testing Each Major Feature

### Interactive Shell

```bash
# Launch the interactive shell
research-pal
```

You should see the ResearchPal logo and a prompt.

### Setting a theme

```bash
# Inside the interactive shell
theme matrix

# Or try other themes
theme cyberpunk
theme midnight
```

### Processing a Paper

For this test, you'll need a PDF file of a research paper. You can use any research paper in PDF format.

```bash
# Inside the interactive shell
summarize path/to/your/paper.pdf
```

The system will process the paper and display a summary. This may take a few minutes depending on the paper length.

### Generating Code Implementation

```bash
# After summarizing a paper
generate code

# Or during summarization
summarize path/to/your/paper.pdf --code
```

### Creating a Blog Post

```bash
# After summarizing a paper
generate blog

# Or during summarization
summarize path/to/your/paper.pdf --blog
```

### Searching Papers

After you've summarized at least one paper:

```bash
# Search by text
search neural networks

# Search by domain
search domain:Computer Vision

# Limit number of results
search transformer -n 3
```

### Opening a Paper

```bash
# Open a paper using its ID (from search results)
open 8f7e9a1b2c  # Replace with an actual paper ID from your database
```

### Displaying Paper Sections

After opening a paper:

```bash
# Show the whole paper
show all

# Show specific sections
show summary
show takeaways
show architecture
show future
show domain
```

### Discussing a Paper

After opening a paper:

```bash
# Ask a question about the paper
discuss What are the key innovations in this paper?
discuss How does this compare to previous approaches?
discuss What are the limitations of this method?
```

### Adding Information to a Paper

After opening a paper:

```bash
# Add a new takeaway
add takeaways "The paper introduces a novel approach to attention mechanisms"

# Add a future research direction
add future "Extending the approach to multi-modal data could be promising"

# Update the domain
add domain "Natural Language Processing"
```

### Listing Available Domains

```bash
# List all domains in your database
domains

# Limit the number of domains shown
domains -n 5
```

### Batch Processing (Using Example Script)

If you want to process multiple papers at once, you can use the batch processing script:

```bash
# Make sure you're in the project root
cd research-pal

# Run the batch processing script
python -m research_pal.examples.batch_processing path/to/papers/directory --limit 3
```

## 4. Advanced Usage

### Using Custom Output Directories

During configuration or with command options:

```bash
# During summarization, specify custom token limit
summarize path/to/paper.pdf --token-limit 8000

# Specify a custom model (if you have access)
summarize path/to/paper.pdf --model gpt-4o
```

### Using as a Library in Python Code

You can also use ResearchPal programmatically in your Python code:

```python
import asyncio
from research_pal.core.summarizer import PaperSummarizer
from research_pal.core.llm_interface import LLMInterface
from research_pal.db.chroma_manager import ChromaManager

async def analyze_paper(pdf_path):
    # Initialize components
    llm_interface = LLMInterface()
    db_manager = ChromaManager()
    summarizer = PaperSummarizer(
        llm_interface=llm_interface,
        db_manager=db_manager
    )
    
    # Process paper
    result = await summarizer.summarize_paper(
        filepath=pdf_path,
        generate_code=True
    )
    
    # Use the results
    print(f"Paper ID: {result['paper_id']}")
    print(f"Title: {result['title']}")
    print(f"Domain: {result['domain']}")
    
    # Return the full result
    return result

# Run the async function
if __name__ == "__main__":
    asyncio.run(analyze_paper("path/to/paper.pdf"))
```

## 5. Project Structure Clarification

The project has the following structure:

```
research_pal/                 # GitHub repository root
├── research_pal/             # Python package directory
│   ├── __init__.py           # Package initialization
│   ├── cli/                  # Command-line interface
│   │   ├── __init__.py
│   │   ├── interactive.py    # Interactive shell
│   │   └── main.py           # Entry point
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── llm_interface.py  # LLM API interactions
│   │   ├── pdf_processor.py  # PDF extraction
│   │   ├── prompts.py        # System prompts
│   │   └── summarizer.py     # Paper summarization
│   ├── db/                   # Database management
│   │   ├── __init__.py
│   │   └── chroma_manager.py # Vector database
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── config.py         # Configuration handling
│       ├── display.py        # Display functions
│       └── ui_themes.py      # Advanced UI
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Test fixtures
│   ├── data/                 # Test data
│   │   └── sample_paper.pdf
│   ├── test_llm_interface.py
│   ├── test_pdf_processor.py
│   ├── test_summarizer.py
│   └── test_chroma_manager.py
├── docs/                     # Documentation
│   ├── docs.md               # Full documentation
│   ├── index.md              # Documentation index
│   └── images/               # Images for docs
│       └── researchpal_logo.svg  # Logo
├── examples/                 # Example scripts
│   ├── analyze_paper.py
│   └── batch_processing.py
├── setup.py                  # Package setup
├── pyproject.toml            # Project config
├── requirements.txt          # Dependencies
├── CONTRIBUTING.md           # Contribution guide
├── README.md                 # Project readme
└── LICENSE                   # License file
```

## 6. Common Issues and Troubleshooting

### API Key Issues

If you encounter API key errors:

1. Verify that your API keys are correctly set in the environment or configuration file
2. Check if your API keys have sufficient permissions and credit
3. Run `research-pal test --test-api` to verify API connectivity

### PDF Processing Issues

If PDF extraction isn't working as expected:

1. Ensure the PDF is not scanned (OCR-based PDFs may have extraction issues)
2. Check that the PDF is not password-protected
3. For large PDFs, try increasing chunk size in the configuration

### Database Issues

If you encounter ChromaDB errors:

1. Check the configured database path to ensure it's valid and writable
2. Try clearing the database directory and starting fresh
3. Ensure you have the correct version of ChromaDB installed

### Memory Issues

If the system runs out of memory:

1. Try processing papers with a smaller token limit
2. Use a model with lower memory requirements (e.g., switch from gpt-4o to gpt-4o-mini)
3. Process larger papers in batches

## 7. Adding Your Own Features

If you want to extend ResearchPal:

1. **Add a new command**: Add a `do_commandname` method to the `InteractiveShell` class in `interactive.py`
2. **Support a new LLM provider**: Add provider configuration to `LLMInterface.__init__`
3. **Implement custom display**: Extend the display functions in `display.py`
4. **Add a new theme**: Add a theme dictionary to `THEMES` in `ui_themes.py`

## 8. Future Development Ideas

Here are some ideas for future contributions:

1. Multi-paper comparison feature
2. Citation network analysis
3. Web-based user interface
4. Reference manager integration (Zotero, Mendeley)
5. Automated literature review generation
6. Collaborative features for teams