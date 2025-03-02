from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from typing import Dict, Any, List

console = Console()

def get_theme_color(color_key, theme=None):
    """Get a color from the active theme."""
    # Import here to avoid circular imports
    from research_pal.utils.enhanced_display import get_theme_color as gtc
    return gtc(color_key)

def display_logo():
    """Display the ResearchPal logo."""
    # Import here to avoid circular imports
    from research_pal.utils.enhanced_display import display_fancy_logo
    display_fancy_logo(console, animated=False)

def display_summary(paper: Dict[str, Any], theme: str = None):
    """Display a formatted summary of a paper."""
    title = paper.get("title", "Unknown Title")
    domain = paper.get("domain", "Unknown")
    
    console.print(f"\n[bold blue]Paper Summary:[/bold blue] [cyan]{title}[/cyan] [dim]({domain})[/dim]\n")
    
    # Create sections
    sections = [
        ("Overview", paper.get("summary", "No overview available.")),
        ("Problem Statement", paper.get("problem_statement", "No problem statement available.")),
        ("Methodology", paper.get("methodology", "No methodology details available.")),
        ("Architecture", paper.get("architecture", "No architecture details available.")),
        ("Key Results", paper.get("key_results", "No results available.")),
        ("Implications", paper.get("implications", "No implications available.")),
        ("Novelty", paper.get("novelty", "No novelty assessment available.")),
        ("Related Work", paper.get("related_work", "No related work available."))
    ]
    
    # Display main sections
    for section_title, content in sections:
        if content and len(content.strip()) > 0:
            panel = Panel(
                Text(content),
                title=f"[bold cyan]{section_title}[/bold cyan]",
                expand=False,
                border_style=get_theme_color("primary", theme)
            )
            console.print(panel)
    
    # Display takeaways as a list
    takeaways = paper.get("takeaways", [])
    if takeaways:
        console.print(f"\n[bold {get_theme_color('primary', theme)}]Key Takeaways:[/bold {get_theme_color('primary', theme)}]")
        
        if isinstance(takeaways, list):
            for i, item in enumerate(takeaways):
                console.print(f"  [{get_theme_color('secondary', theme)}]{i+1}.[/{get_theme_color('secondary', theme)}] {item}")
        else:
            console.print(f"  • {takeaways}")
    
    # Display important ideas as a list
    important_ideas = paper.get("important_ideas", [])
    if important_ideas:
        console.print(f"\n[bold {get_theme_color('primary', theme)}]Important Ideas:[/bold {get_theme_color('primary', theme)}]")
        
        if isinstance(important_ideas, list):
            for i, item in enumerate(important_ideas):
                console.print(f"  [{get_theme_color('secondary', theme)}]{i+1}.[/{get_theme_color('secondary', theme)}] {item}")
        else:
            console.print(f"  • {important_ideas}")
    
    # Display limitations as a list
    limitations = paper.get("limitations", [])
    if limitations:
        console.print(f"\n[bold {get_theme_color('primary', theme)}]Limitations:[/bold {get_theme_color('primary', theme)}]")
        
        if isinstance(limitations, list):
            for i, item in enumerate(limitations):
                console.print(f"  [{get_theme_color('secondary', theme)}]{i+1}.[/{get_theme_color('secondary', theme)}] {item}")
        else:
            console.print(f"  • {limitations}")
    
    # Display practical applications as a list
    applications = paper.get("practical_applications", [])
    if applications:
        console.print(f"\n[bold {get_theme_color('primary', theme)}]Practical Applications:[/bold {get_theme_color('primary', theme)}]")
        
        if isinstance(applications, list):
            for i, item in enumerate(applications):
                console.print(f"  [{get_theme_color('secondary', theme)}]{i+1}.[/{get_theme_color('secondary', theme)}] {item}")
        else:
            console.print(f"  • {applications}")
    
    # Display future directions as a list
    future = paper.get("future_directions", [])
    if future:
        console.print(f"\n[bold {get_theme_color('primary', theme)}]Future Directions:[/bold {get_theme_color('primary', theme)}]")
        
        if isinstance(future, list):
            for i, item in enumerate(future):
                console.print(f"  [{get_theme_color('secondary', theme)}]{i+1}.[/{get_theme_color('secondary', theme)}] {item}")
        else:
            console.print(f"  • {future}")
    
    # Display domain information
    domain = paper.get("domain", "Unknown")
    if domain != "Unknown":
        console.print(f"\n[bold {get_theme_color('primary', theme)}]Research Domain:[/bold {get_theme_color('primary', theme)}] {domain}")
    
    # Display similar papers if available
    similar = paper.get("similar_papers", [])
    if similar:
        console.print(f"\n[bold {get_theme_color('primary', theme)}]Similar Papers:[/bold {get_theme_color('primary', theme)}]")
        
        table = Table(show_header=True, header_style=f"bold {get_theme_color('secondary', theme)}")
        table.add_column("Title")
        table.add_column("Authors")
        table.add_column("Year")
        
        for paper_ref in similar:
            if isinstance(paper_ref, dict):
                title = paper_ref.get("title", "Unknown")
                authors = paper_ref.get("authors", "")
                year = paper_ref.get("year", "")
                table.add_row(title, authors, str(year))
        
        console.print(table)

def format_code_for_display(code: str) -> str:
    """Format code for display with syntax highlighting."""
    # Basic formatting if no special formatting needed
    return code

def display_progress(current: int, total: int, description: str = "Processing", theme: str = None):
    """Display a progress bar."""
    percentage = int(100 * current / total)
    bar_length = 40
    filled_length = int(bar_length * current / total)
    
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    console.print(f"\r{description}: [{bar}] {percentage}% ({current}/{total})", end="")
    
    if current == total:
        console.print("")

def display_paper_list(papers: List[Dict[str, Any]], theme: str = None):
    """Display a list of papers in a nicely formatted table."""
    if not papers:
        console.print("[yellow]No papers to display.[/yellow]")
        return
    
    table = Table(title="Paper Collection", 
                 border_style=get_theme_color("primary", theme))
    
    table.add_column("ID", style=get_theme_color("accent", theme))
    table.add_column("Title", style="white")
    table.add_column("Domain", style=get_theme_color("secondary", theme))
    
    for paper in papers:
        table.add_row(
            paper.get("paper_id", ""),
            paper.get("title", "Unknown"),
            paper.get("domain", "Unknown")
        )
    
    console.print(table)