from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="research-pal",
    version="0.1.0",
    author="ResearchPal Contributors",
    author_email="amananytime07@gmail.com",
    description="AI-powered research assistant for scientific literature",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/researchpal/research-pal",
    project_urls={
        "Bug Tracker": "https://github.com/researchpal/research-pal/issues",
        "Documentation": "https://docs.researchpal.ai",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "research-pal=research_pal.cli.main:main",
        ],
    },
    include_package_data=True,
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-cov>=4.1.0",
            "pre-commit>=3.3.2",
            "flake8>=6.0.0",
            "black>=23.3.0",
            "mypy>=1.3.0",
        ],
    },
)