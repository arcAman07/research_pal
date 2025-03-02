#!/usr/bin/env python3
"""
Example script demonstrating how to batch process multiple papers with ResearchPal.
"""
import os
import asyncio
import argparse
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, TaskID

from research_pal.core.summarizer import PaperSummarizer
from research_pal.core.llm_interface import LLMInterface
from research_pal.db.chroma_manager import ChromaManager

console = Console()

async def process_paper(pdf_path: str, summarizer: PaperSummarizer, 
                       progress: Progress, task_id: TaskID) -> Dict[str, Any]:
    """Process a single paper and update progress."""
    try:
        # Process the paper
        result = await summarizer.summarize_paper(filepath=pdf_path)
        
        # Update progress
        progress.update(task_id, advance=1)
        
        return result
    except Exception as e:
        console.print(f"[red]Error processing {pdf_path}: {e}[/red]")
        progress.update(task_id, advance=1)
        return None

async def batch_process(directory: str, output_dir: str = None, limit: int = None) -> List[Dict[str, Any]]:
    """
    Process all PDF files in a directory.
    
    Args:
        directory: Directory containing PDF files
        output_dir: Directory to save output files (optional)
        limit: Maximum number of papers to process (optional)
        
    Returns:
        List of processing results
    """
    # Validate and normalize directory paths
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        console.print(f"[red]Error: {directory} is not a valid directory.[/red]")
        return []
    
    if output_dir:
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    
    # Find all PDF files
    pdf_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                if f.lower().endswith('.pdf')]
    
    if limit and limit > 0:
        pdf_files = pdf_files[:limit]
    
    if not pdf_files:
        console.print(f"[yellow]No PDF files found in {directory}[/yellow]")
        return []
    
    console.print(f"[bold blue]Found {len(pdf_files)} PDF files to process[/bold blue]")
    
    # Initialize components
    llm_interface = LLMInterface()
    db_manager = ChromaManager()
    summarizer = PaperSummarizer(
        llm_interface=llm_interface,
        db_manager=db_manager
    )
    
    # Process files with progress tracking
    results = []
    with Progress() as progress:
        task = progress.add_task("[green]Processing papers...", total=len(pdf_files))
        
        # Create tasks for each paper
        tasks = [
            process_paper(pdf_path, summarizer, progress, task)
            for pdf_path in pdf_files
        ]
        
        # Run all tasks
        results = await asyncio.gather(*tasks)
    
    # Filter out None results (failed processing)
    results = [r for r in results if r]
    
    # Display summary
    console.print(f"\n[bold green]Processed {len(results)} papers successfully[/bold green]")
    
    # Print summary of papers
    for result in results:
        title = result.get("title", "Unknown Title")
        domain = result.get("domain", "Unknown")
        console.print(f"✓ [cyan]{title}[/cyan] ([blue]{domain}[/blue])")
    
    return results

def main():
    """Main entry point."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Batch process research papers with ResearchPal")
    parser.add_argument("directory", help="Directory containing PDF files to process")
    parser.add_argument("--output", help="Directory to save output files")
    parser.add_argument("--limit", type=int, help="Maximum number of papers to process")
    args = parser.parse_args()
    
    # Run batch processing
    asyncio.run(batch_process(
        directory=args.directory,
        output_dir=args.output,
        limit=args.limit
    ))

if __name__ == "__main__":
    main()