#!/usr/bin/env python3
"""
Example script demonstrating how to use ResearchPal to analyze a paper.
"""
import os
import asyncio
import argparse
from rich.console import Console

from research_pal.core.summarizer import PaperSummarizer
from research_pal.core.llm_interface import LLMInterface
from research_pal.db.chroma_manager import ChromaManager
from research_pal.utils.display import display_summary

# Set up console for rich output
console = Console()

async def analyze_paper(pdf_path, generate_code=False, generate_blog=False, output_token_limit=4096):
    """Analyze a research paper."""
    # Ensure file exists
    if not os.path.exists(pdf_path):
        console.print(f"[red]Error: File {pdf_path} not found.[/red]")
        return
    
    # Initialize components
    llm_interface = LLMInterface()
    db_manager = ChromaManager()
    
    # Create summarizer
    summarizer = PaperSummarizer(
        llm_interface=llm_interface,
        db_manager=db_manager,
        output_token_limit=output_token_limit
    )
    
    # Display processing message
    console.print(f"[bold blue]Processing paper:[/bold blue] {pdf_path}")
    
    # Process paper
    with console.status("[bold green]Analyzing paper...[/bold green]"):
        result = await summarizer.summarize_paper(
            filepath=pdf_path,
            generate_code=generate_code,
            generate_blog=generate_blog
        )
    
    # Display results
    console.print("\n[bold green]Analysis complete![/bold green]")
    display_summary(result)
    
    # Save generated content if requested
    if generate_code and "code_implementation" in result:
        output_path = f"{os.path.splitext(pdf_path)[0]}_implementation.py"
        with open(output_path, "w") as f:
            f.write(result["code_implementation"])
        console.print(f"\n[green]Implementation code saved to {output_path}[/green]")
    
    if generate_blog and "blog_post" in result:
        output_path = f"{os.path.splitext(pdf_path)[0]}_blog.md"
        with open(output_path, "w") as f:
            f.write(result["blog_post"])
        console.print(f"\n[green]Blog post saved to {output_path}[/green]")
    
    return result

def main():
    """Main entry point."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Analyze a research paper using ResearchPal")
    parser.add_argument("pdf_path", help="Path to the PDF file to analyze")
    parser.add_argument("--code", action="store_true", help="Generate implementation code")
    parser.add_argument("--blog", action="store_true", help="Generate blog post")
    parser.add_argument("--token-limit", type=int, default=4096, help="Output token limit")
    args = parser.parse_args()
    
    # Run analysis
    asyncio.run(analyze_paper(
        args.pdf_path,
        generate_code=args.code,
        generate_blog=args.blog,
        output_token_limit=args.token_limit
    ))

if __name__ == "__main__":
    main()