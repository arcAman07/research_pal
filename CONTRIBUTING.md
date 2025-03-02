# Contributing to ResearchPal

First off, thank you for considering contributing to ResearchPal! 🎉 It's people like you that make ResearchPal such a great tool for researchers. 

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to [maintainers@researchpal.ai].

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for ResearchPal. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title** for the issue
* **Describe the exact steps to reproduce the problem** with as much detail as possible
* **Provide specific examples** such as the command you ran and the error message you received
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior
* **Explain which behavior you expected to see instead and why**
* **Include screenshots or animated GIFs** if applicable

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for ResearchPal, including completely new features and minor improvements to existing functionality.

* **Use a clear and descriptive title** for the issue
* **Provide a step-by-step description of the suggested enhancement** with as much detail as possible
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why
* **Explain why this enhancement would be useful** to most ResearchPal users

### Pull Requests

* Fill in the required template
* Follow the Python styleguide (PEP 8)
* Document new code based on the existing documentation style
* Include tests for new features
* End all files with a newline

## Development Setup

### Prerequisites
* Python 3.8+
* Git

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/research-pal.git
   cd research-pal
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* When only changing documentation, include `[docs]` in the commit title
* Consider starting the commit message with an applicable emoji:
  * 🎨 `:art:` when improving the format/structure of the code
  * 🐎 `:racehorse:` when improving performance
  * 🚱 `:non-potable_water:` when plugging memory leaks
  * 📝 `:memo:` when writing docs
  * 🐛 `:bug:` when fixing a bug
  * 🔥 `:fire:` when removing code or files
  * 💚 `:green_heart:` when fixing the CI build
  * ✅ `:white_check_mark:` when adding tests
  * 🔒 `:lock:` when dealing with security
  * ⬆️ `:arrow_up:` when upgrading dependencies
  * ⬇️ `:arrow_down:` when downgrading dependencies
  * 👕 `:shirt:` when removing linter warnings

### Python Styleguide

All Python code should adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/).

Additional style guidelines:
* Use type hints where appropriate
* Write docstrings for all classes and functions (Google style)
* Use f-strings for string formatting
* Limit line length to 88 characters
* Use double quotes for docstrings and single quotes for regular strings

### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown/) for documentation.
* Refer to classes, modules, functions, variables etc. using backticks.
* Include code examples when appropriate.
* Update the README.md with details of changes to the interface.

## Additional Notes

### Issue and Pull Request Labels

This repository uses the following labels to track issues and PRs:

| Label name | Description |
| --- | --- |
| `bug` | Indicates a confirmed bug or issue that needs to be fixed |
| `documentation` | Indicates a need for improvements or additions to documentation |
| `enhancement` | Indicates new feature requests or improvements to existing features |
| `help-wanted` | Indicates issues where community help is particularly welcome |
| `good-first-issue` | Indicates issues which are good for newcomers |

Thank you for your interest in contributing to ResearchPal!