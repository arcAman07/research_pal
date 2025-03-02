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
│   ├── test_chroma_manager.py
│   └── test_config.py
├── docs/                     # Documentation
│   ├── docs.md               # Full documentation
│   ├── index.md              # Documentation index (added)
│   └── images/               # Images for docs
│       └── researchpal_logo.svg  # Logo (added)
├── examples/                 # Example scripts
│   ├── analyze_paper.py
│   └── batch_processing.py
├── setup.py                  # Package setup
├── pyproject.toml            # Project config
├── requirements.txt          # Dependencies
├── CONTRIBUTING.md           # Contribution guide
├── README.md                 # Project readme (updated)
└── LICENSE                   # License file