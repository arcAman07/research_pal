"""Interactive shell for ResearchPal with enhanced UI and domain search."""

import os
import sys
import cmd
import asyncio
from typing import Optional, Dict, Any, List
import shlex
import json
import readline
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress
from rich.table import Table
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_pal.core.summarizer import PaperSummarizer
from research_pal.core.llm_interface import LLMInterface
from research_pal.db.chroma_manager import ChromaManager
from research_pal.utils.ui_themes import display_fancy_logo, get_fancy_prompt, set_theme, get_theme_color
from research_pal.utils.display import display_summary
from research_pal.utils.config import load_config

logger = logging.getLogger(__name__)
console = Console()

class InteractiveShell(cmd.Cmd):
    """Interactive shell for ResearchPal."""
    
    intro = "Welcome to the ResearchPal interactive shell. Type 'help' for available commands."
    
    def __init__(self, config_path: str = None, debug: bool = False, minimal: bool = False, theme: str = "minimal"):
        """Initialize the interactive shell."""
        super().__init__()
        
        # Store settings
        self.debug = debug
        self.minimal = minimal
        self.theme = theme

         # Additional context tracking
        self.paper_history = []  # Track recently opened papers
        self.max_history = 10    # Maximum number of papers to keep in history
        
        # Discussion history for the current paper
        self.discussion_history = []
        
        # Set theme
        set_theme(theme)
        
        # Set prompt
        self.prompt = get_fancy_prompt(theme)
        
        # Enable command history and tab completion
        readline.parse_and_bind("tab: complete")
        histfile = os.path.expanduser("~/.research_pal/history")
        os.makedirs(os.path.dirname(histfile), exist_ok=True)
        try:
            readline.read_history_file(histfile)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass
        
        # Load configuration
        self.config = load_config(config_path)
        
        # Set API keys from config to environment
        if self.config.get("openai_api_key"):
            os.environ["OPENAI_API_KEY"] = self.config["openai_api_key"]
        if self.config.get("google_api_key"):
            os.environ["GOOGLE_API_KEY"] = self.config["google_api_key"]
        
        # Set default model from config
        default_model = self.config.get("default_model")
        
        # Use theme from config if provided
        config_theme = self.config.get("theme")
        if config_theme and not theme:
            self.theme = config_theme
            set_theme(self.theme)
            self.prompt = get_fancy_prompt(self.theme)
        
        # Set default output token limit
        self.output_token_limit = self.config.get("output_token_limit", 4096)
        
        # Initialize components
        self.db_manager = ChromaManager(
            persist_directory=self.config.get("db_path", "~/.research_pal/chroma_db")
        )
        self.llm_interface = LLMInterface(default_model=default_model)
        self.summarizer = PaperSummarizer(
            llm_interface=self.llm_interface,
            db_manager=self.db_manager,
            output_token_limit=self.output_token_limit
        )
        
        # Current paper context
        self.current_paper_id = None
        self.current_paper = None
    
    # Method to track paper history
    def _add_to_paper_history(self, paper_id: str):
        """Add a paper to the history, maintaining the max size."""
        # Remove if already in history
        if paper_id in self.paper_history:
            self.paper_history.remove(paper_id)
        
        # Add to front of list
        self.paper_history.insert(0, paper_id)
        
        # Trim to max size
        if len(self.paper_history) > self.max_history:
            self.paper_history = self.paper_history[:self.max_history]
    
    # New method to show history
    def do_history(self, arg):
        """
        Show recently opened papers.
        
        Usage: history [number]
        """
        try:
            if arg:
                try:
                    count = int(arg)
                    papers_to_show = min(count, len(self.paper_history))
                except ValueError:
                    console.print("[red]Invalid number. Using default.[/red]")
                    papers_to_show = len(self.paper_history)
            else:
                papers_to_show = len(self.paper_history)
            
            if not self.paper_history:
                console.print("[yellow]No paper history available.[/yellow]")
                return
            
            console.print(f"\n[bold blue]Recently opened papers:[/bold blue]")
            
            # Create a table for history
            table = Table(title="Paper History")
            table.add_column("#", style=get_theme_color("accent"))
            table.add_column("ID", style=get_theme_color("primary"))
            table.add_column("Title", style="white")
            table.add_column("Domain", style=get_theme_color("secondary"))
            
            for i, paper_id in enumerate(self.paper_history[:papers_to_show]):
                # Try to get paper information
                try:
                    paper = self.summarizer.get_paper_summary(paper_id)
                    if paper:
                        title = paper.get("title", "Unknown Title")
                        domain = paper.get("domain", "Unknown")
                        table.add_row(
                            str(i+1),
                            paper_id,
                            title,
                            domain
                        )
                    else:
                        table.add_row(
                            str(i+1),
                            paper_id,
                            "Paper not found",
                            "N/A"
                        )
                except Exception:
                    table.add_row(
                        str(i+1),
                        paper_id,
                        "Error retrieving paper",
                        "N/A"
                    )
            
            console.print(table)
            console.print("\n[dim]To open a paper, use 'open <paper_id>'[/dim]")
        
        except Exception as e:
            if self.debug:
                console.print(f"[red]Error showing history: {str(e)}[/red]")
                import traceback
                console.print(traceback.format_exc())
            else:
                console.print(f"[red]Error showing history: {str(e)}[/red]")
    
    # New command to handle paper switching by number from history
    def do_switch(self, arg):
        """
        Switch to a paper from the history by number.
        
        Usage: switch <number>
        """
        try:
            if not arg:
                console.print("[red]No history number provided.[/red]")
                console.print("Usage: switch <number>")
                console.print("Use 'history' to see the list of recently opened papers.")
                return
            
            try:
                index = int(arg) - 1  # Convert to 0-based index
            except ValueError:
                console.print(f"[red]Invalid number: {arg}[/red]")
                return
            
            if not self.paper_history:
                console.print("[yellow]No paper history available.[/yellow]")
                return
            
            if index < 0 or index >= len(self.paper_history):
                console.print(f"[red]Invalid history number. Use a number between 1 and {len(self.paper_history)}.[/red]")
                return
            
            # Get the paper ID from history
            paper_id = self.paper_history[index]
            
            # Open that paper
            self.do_open(paper_id)
        
        except Exception as e:
            if self.debug:
                console.print(f"[red]Error switching papers: {str(e)}[/red]")
                import traceback
                console.print(traceback.format_exc())
            else:
                console.print(f"[red]Error switching papers: {str(e)}[/red]")
    
    def emptyline(self):
        """Do nothing on empty line."""
        pass
    
    def do_exit(self, arg):
        """Exit the interactive shell."""
        # Save command history
        histfile = os.path.expanduser("~/.research_pal/history")
        readline.write_history_file(histfile)
        
        console.print(f"[{get_theme_color('primary')}]Goodbye![/{get_theme_color('primary')}]")
        return True
    
    def do_quit(self, arg):
        """Exit the interactive shell."""
        return self.do_exit(arg)
    
    def default(self, line):
        """Handle unknown commands."""
        console.print(f"[red]Unknown command: {line}[/red]")
        console.print("Type 'help' for a list of available commands.")
    
    def do_theme(self, arg):
        """
        Change the UI theme.
        
        Usage: theme [cyberpunk|matrix|midnight|minimal|professional]
        """
        themes = ["cyberpunk", "matrix", "midnight", "minimal", "professional"]
        
        if not arg or arg not in themes:
            console.print(f"[red]Please specify a valid theme: {', '.join(themes)}[/red]")
            return
        
        # Update theme
        self.theme = arg
        set_theme(arg)
        self.prompt = get_fancy_prompt(arg)
        
        console.print(f"[green]Theme changed to: {arg}[/green]")
    
    def do_clear(self, arg):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_refresh(self, arg):
        """Refresh the display (show logo again)."""
        display_fancy_logo(console, animated=False, theme=self.theme)
    
    def do_search(self, arg):
        """
        Search for papers in the database.
        
        Usage: search <query> [-n <count>]
        
        Special search commands:
        - search domain:<domain_name> - Search papers by research domain
        - search title:<paper_title> - Search specifically for paper titles
        - search takeaway:<concept> - Search in paper takeaways
        """
        try:
            args = shlex.split(arg)
            count = 5
            
            # Parse arguments
            if "-n" in args:
                idx = args.index("-n")
                if idx + 1 < len(args):
                    try:
                        count = int(args[idx + 1])
                        args.pop(idx + 1)
                        args.pop(idx)
                    except ValueError:
                        console.print("[red]Invalid count value.[/red]")
                        return
            
            # Join remaining args as the query
            query = " ".join(args)
            if not query:
                console.print("[red]No search query provided.[/red]")
                return
            
            # Search for papers
            search_type = "general"
            display_query = query
            
            if query.lower().startswith("domain:"):
                search_type = "domain"
            elif query.lower().startswith("title:"):
                search_type = "title"
                # Handle title search by modifying the query for the vector search
                display_query = query
                # Strip "title:" from the query but enhance the query to focus on titles
                query = "title: " + query[6:]
            elif query.lower().startswith("takeaway:"):
                search_type = "takeaway"
                
            console.print(f"[bold blue]Searching for:[/bold blue] {display_query}")
            
            with console.status(f"[bold green]Searching database...[/bold green]", spinner="dots12"):
                results = self.summarizer.search_papers(query, n_results=count)
            
            # Display results
            if not results:
                console.print("[yellow]No results found.[/yellow]")
                return
            
            console.print(f"\n[bold green]Found {len(results)} results:[/bold green]\n")
            
            if search_type == "domain":
                # Create a table for domain-specific results
                table = Table(title=f"Papers in domain: {display_query.split(':', 1)[1].strip()}")
                table.add_column("ID", style=get_theme_color("primary"))
                table.add_column("Title", style="white")
                table.add_column("Domain", style=get_theme_color("accent"))
                
                for paper in results:
                    table.add_row(
                        paper.get("paper_id", ""),
                        paper.get("title", "Unknown Title"),
                        paper.get("domain", "Unknown")
                    )
                
                console.print(table)
            else:
                # Standard display
                for i, paper in enumerate(results):
                    title = paper.get("title", "Unknown Title")
                    paper_id = paper.get("paper_id", "")
                    domain = paper.get("domain", "Unknown")
                    summary = paper.get("summary", "")
                    
                    if search_type == "takeaway" and "takeaways" in paper:
                        # Highlight the matching takeaways
                        takeaways = paper.get("takeaways", [])
                        search_term = display_query.split(":", 1)[1].strip().lower() if ":" in display_query else display_query.lower()
                        
                        matching_takeaways = []
                        for takeaway in takeaways:
                            if search_term in takeaway.lower():
                                matching_takeaways.append(f"• [bold]{takeaway}[/bold]")
                            else:
                                matching_takeaways.append(f"• {takeaway}")
                        
                        content = "\n".join(matching_takeaways) if matching_takeaways else summary
                    else:
                        # Use summary for other search types
                        if len(summary) > 200:
                            summary = summary[:200] + "..."
                        content = summary
                    
                    panel = Panel(
                        Text(f"{content}", style="white"),
                        title=f"[bold cyan]{i+1}. {title}[/bold cyan] [dim]({domain})[/dim]",
                        subtitle=f"ID: {paper_id}",
                        border_style=get_theme_color("primary")
                    )
                    console.print(panel)
                    
                # Add hint about opening papers by ID
                console.print("\n[dim]To open a paper, use the 'open <paper_id>' command with the ID shown above.[/dim]")
        except Exception as e:
            if self.debug:
                console.print(f"[red]Error searching papers: {str(e)}[/red]")
                import traceback
                console.print(traceback.format_exc())
            else:
                console.print(f"[red]Error searching papers: {str(e)}[/red]")
                console.print("If this issue persists, try running with --debug for more information.")
    
    def do_domains(self, arg):
        """
        List all available research domains in the database.
        
        Usage: domains [-n <count>]
        """
        count = 20  # Default to showing 20 domains
        
        if arg:
            args = shlex.split(arg)
            if "-n" in args:
                idx = args.index("-n")
                if idx + 1 < len(args):
                    try:
                        count = int(args[idx + 1])
                    except ValueError:
                        console.print("[red]Invalid count value.[/red]")
                        return
        
        # Get all papers and extract unique domains
        with console.status(f"[bold green]Retrieving domains...[/bold green]", spinner="dots12"):
            try:
                # This is a simple implementation - in a real system we would 
                # have a more efficient way to get distinct domains
                results = self.summarizer.search_papers("", n_results=100)
                domains = {}
                
                for paper in results:
                    domain = paper.get("domain", "Unknown")
                    if domain in domains:
                        domains[domain] += 1
                    else:
                        domains[domain] = 1
                
                # Sort by frequency
                domain_list = sorted(domains.items(), key=lambda x: x[1], reverse=True)
            except Exception as e:
                console.print(f"[red]Error retrieving domains: {e}[/red]")
                return
        
        if not domain_list:
            console.print("[yellow]No domains found in the database.[/yellow]")
            return
        
        # Display domains
        table = Table(title="Research Domains in Database")
        table.add_column("Domain", style=get_theme_color("primary"))
        table.add_column("Paper Count", style=get_theme_color("secondary"))
        
        # Add rows for each domain
        for domain, count in domain_list[:count]:
            table.add_row(domain, str(count))
        
        console.print(table)
        console.print(f"\n[dim]Use 'search domain:<domain_name>' to find papers in a specific domain[/dim]")

    def do_open(self, arg):
        """
        Open a paper by ID and set it as the current context.
        
        Usage: open <paper_id>
        """
        paper_id = arg.strip()
        if not paper_id:
            console.print("[red]No paper ID provided.[/red]")
            console.print("Usage: open <paper_id>")
            console.print("To find paper IDs, use the 'search' command first.")
            return
        
        # Get paper from database
        try:
            with console.status(f"[bold green]Loading paper...[/bold green]", spinner="dots12"):
                paper = self.summarizer.get_paper_summary(paper_id)
            
            if not paper:
                console.print(f"[red]Paper with ID '{paper_id}' not found.[/red]")
                console.print("Use 'search' to find available papers.")
                return
            
            # Set as current paper
            self.current_paper_id = paper_id
            self.current_paper = paper
            
            # Add to history
            self._add_to_paper_history(paper_id)
            
            # Reset discussion history when changing papers
            self.discussion_history = []
            
            # Display paper summary
            title = paper.get("title", "Unknown Title")
            domain = paper.get("domain", "Unknown")
            console.print(f"\n[bold green]Opened paper:[/bold green] [cyan]{title}[/cyan] [dim]({domain})[/dim] (ID: {paper_id})\n")
            
            # Show brief summary
            summary = paper.get("summary", "")
            if summary:
                panel = Panel(
                    Text(summary[:300] + "..." if len(summary) > 300 else summary),
                    title=f"[bold cyan]Summary[/bold cyan]",
                    border_style=get_theme_color("secondary")
                )
                console.print(panel)
            
            console.print("\nUse 'show' command to view specific sections of the paper.")
        except Exception as e:
            if self.debug:
                console.print(f"[red]Error opening paper: {str(e)}[/red]")
                import traceback
                console.print(traceback.format_exc())
            else:
                console.print(f"[red]Error opening paper: {str(e)}[/red]")
                console.print("If this issue persists, try running with --debug for more information.")
    
    def do_show(self, arg):
        """
        Show a specific section of the current paper.
        
        Usage: show <section>
        Available sections: summary, takeaways, architecture, future, background, math, domain
        Use 'show all' to display the complete summary.
        """
        if not self.current_paper:
            console.print("[red]No paper currently open. Use 'open <paper_id>' first.[/red]")
            return
        
        section = arg.strip().lower()
        
        if not section:
            console.print("[red]No section specified.[/red]")
            console.print("Available sections: summary, takeaways, architecture, future, background, math, domain, all")
            return
        
        title = self.current_paper.get("title", "Unknown Title")
        
        if section == "all":
            # Display full summary
            display_summary(self.current_paper, theme=self.theme)
            return
        
        # Display specific section
        if section == "summary":
            content = self.current_paper.get("summary", "No summary available.")
            console.print(Panel(
                Text(content), 
                title=f"[bold cyan]Summary: {title}[/bold cyan]",
                border_style=get_theme_color("primary")
            ))
        
        elif section == "takeaways":
            takeaways = self.current_paper.get("takeaways", [])
            if isinstance(takeaways, str):
                takeaways = [takeaways]
            
            content = "\n".join([f"• {item}" for item in takeaways]) if takeaways else "No takeaways available."
            console.print(Panel(
                Text(content), 
                title=f"[bold cyan]Takeaways: {title}[/bold cyan]",
                border_style=get_theme_color("primary")
            ))
        
        elif section == "architecture":
            content = self.current_paper.get("architecture", "No architecture details available.")
            console.print(Panel(
                Text(content), 
                title=f"[bold cyan]Architecture: {title}[/bold cyan]",
                border_style=get_theme_color("primary")
            ))
        
        elif section == "future":
            future = self.current_paper.get("future_directions", [])
            if isinstance(future, str):
                future = [future]
            
            content = "\n".join([f"• {item}" for item in future]) if future else "No future directions available."
            console.print(Panel(
                Text(content), 
                title=f"[bold cyan]Future Directions: {title}[/bold cyan]",
                border_style=get_theme_color("primary")
            ))
        
        elif section == "background":
            content = self.current_paper.get("background", "No background information available.")
            console.print(Panel(
                Text(content), 
                title=f"[bold cyan]Background: {title}[/bold cyan]",
                border_style=get_theme_color("primary")
            ))
        
        elif section == "math":
            content = self.current_paper.get("math_formulations", "No mathematical formulations available.")
            console.print(Panel(
                Text(content), 
                title=f"[bold cyan]Mathematical Formulations: {title}[/bold cyan]",
                border_style=get_theme_color("primary")
            ))
            
        elif section == "domain":
            domain = self.current_paper.get("domain", "Unknown")
            
            # Show domain and related papers
            console.print(Panel(
                Text(f"Research Domain: [bold]{domain}[/bold]"), 
                title=f"[bold cyan]Domain Classification: {title}[/bold cyan]",
                border_style=get_theme_color("primary")
            ))
            
            # Optionally show related papers in the same domain
            if domain != "Unknown":
                console.print("\n[bold]Other papers in this domain:[/bold]")
                with console.status("[bold green]Finding related papers...[/bold green]", spinner="dots12"):
                    related = self.summarizer.search_papers(f"domain:{domain}", n_results=3)
                
                # Filter out the current paper
                related = [p for p in related if p.get("paper_id") != self.current_paper_id]
                
                if related:
                    for i, paper in enumerate(related):
                        console.print(f"  {i+1}. [cyan]{paper.get('title', 'Unknown')}[/cyan] (ID: {paper.get('paper_id', '')})")
                else:
                    console.print("  No other papers found in this domain.")
        
        else:
            console.print("[red]Unknown section.[/red]")
            console.print("Available sections: summary, takeaways, architecture, future, background, math, domain, all")
    
    def do_discuss(self, arg):
        """
        Start a discussion about the current paper with the LLM.
        
        Usage: discuss <question or topic>
        """
        if not self.current_paper:
            console.print("[red]No paper currently open. Use 'open <paper_id>' first.[/red]")
            console.print("You can find paper IDs using the 'search' command.")
            return
        
        question = arg.strip()
        if not question:
            console.print("[red]No question or topic provided.[/red]")
            console.print("Usage: discuss <question or topic>")
            console.print("Examples:")
            console.print("  discuss What are the key innovations in this paper?")
            console.print("  discuss How does this approach compare to previous methods?")
            console.print("  discuss What are the limitations of this method?")
            console.print("  discuss How could I implement this in PyTorch?")
            return
        
        try:
            # Get relevant information from paper
            title = self.current_paper.get("title", "Unknown Title")
            summary = self.current_paper.get("summary", "")
            problem_statement = self.current_paper.get("problem_statement", "")
            methodology = self.current_paper.get("methodology", "")
            takeaways = self.current_paper.get("takeaways", [])
            architecture = self.current_paper.get("architecture", "")
            background = self.current_paper.get("background", "")
            domain = self.current_paper.get("domain", "Unknown")
            math_formulations = self.current_paper.get("math_formulations", "")
            
            # Analyze the type of question to provide better context
            question_lower = question.lower()
            context_sections = []
            
            # Always include title, domain and summary
            context_sections.append(f"Title: {title}")
            context_sections.append(f"Domain: {domain}")
            context_sections.append(f"Summary: {summary}")
            
            # Add problem statement and methodology for most questions
            if problem_statement:
                context_sections.append(f"Problem Statement: {problem_statement}")
            if methodology:
                context_sections.append(f"Methodology: {methodology}")
            
            # Based on question type, add more specific context
            if any(term in question_lower for term in ["architecture", "model", "implement", "code", "network", "structure"]):
                if architecture:
                    context_sections.append(f"Architecture Details: {architecture}")
                # Include math formulations for implementation questions
                if math_formulations:
                    context_sections.append(f"Mathematical Formulations: {math_formulations}")
                    
            if any(term in question_lower for term in ["math", "equation", "formula", "derivation", "proof"]):
                if math_formulations:
                    context_sections.append(f"Mathematical Formulations: {math_formulations}")
                    
            if any(term in question_lower for term in ["background", "history", "related", "previous", "before"]):
                if background:
                    context_sections.append(f"Background: {background}")
                    
            if any(term in question_lower for term in ["takeaway", "finding", "conclusion", "result", "important"]):
                if isinstance(takeaways, list):
                    context_sections.append(f"Key Takeaways: {', '.join(takeaways)}")
                else:
                    context_sections.append(f"Key Takeaways: {takeaways}")
            
            # Prepare context for the LLM
            context = "\n\n".join(context_sections)
            
            # Create prompt for discussion
            system_message = """You are ResearchPal, an expert research assistant specializing in scientific literature analysis.
            You're discussing a specific research paper with the user. Use the provided context about the paper
            to answer their questions or discuss topics related to the paper.
            
            Be informative, precise, and helpful. Focus on the specific question.
            If you're unsure about something not covered in the context, acknowledge the limitation of your information.
            If the question requires technical details not present in the context, explain what would be needed.
            
            Format your response using Markdown for better readability. Use bullet points, headers, and other formatting
            as appropriate to organize your response.
            """
            
            prompt = f"""The user wants to discuss the following about the paper:
            
            {question}
            
            Here's the context about the paper:
            
            {context}
            
            Provide a thoughtful, accurate response based on the paper's contents. If you need more information that isn't
            provided in the context, please mention this limitation in your response. Format your response using Markdown.
            """
            
            # Query LLM
            console.print(f"\n[bold blue]Discussing:[/bold blue] {question}")
            
            with console.status(f"[bold green]Thinking...[/bold green]", spinner="dots12"):
                response = asyncio.run(self.llm_interface.query_model(
                    prompt=prompt,
                    system_message=system_message,
                    temperature=0.3
                ))
            
            # Display response
            console.print("\n[bold green]Response:[/bold green]")
            console.print(Markdown(response))
            
            # Save to discussion history (we could implement this later)
        
        except Exception as e:
            if self.debug:
                console.print(f"[red]Error in discussion: {str(e)}[/red]")
                import traceback
                console.print(traceback.format_exc())
            else:
                console.print(f"[red]Error generating response: {str(e)}[/red]")
                console.print("If this issue persists, try running with --debug for more information.")
    
    def do_add(self, arg):
        """
        Add information to the current paper.
        
        Usage: add <field> <content>
        Available fields: takeaways, future, notes, domain
        
        Example: add takeaways "The paper introduces a novel approach to XYZ"
        Example: add domain "Natural Language Processing"
        """
        if not self.current_paper:
            console.print("[red]No paper currently open. Use 'open <paper_id>' first.[/red]")
            return
        
        args = shlex.split(arg)
        if len(args) < 2:
            console.print("[red]Invalid arguments. Usage: add <field> <content>[/red]")
            console.print("Available fields: takeaways, future, notes, domain")
            return
        
        field = args[0].lower()
        content = " ".join(args[1:])
        
        # Map field names to database fields
        field_mapping = {
            "takeaways": "takeaways",
            "future": "future_ideas",
            "notes": "notes",
            "domain": "domain"
        }
        
        if field not in field_mapping:
            console.print(f"[red]Unknown field: {field}[/red]")
            console.print("Available fields: takeaways, future, notes, domain")
            return
        
        db_field = field_mapping[field]
        
        # Handle domain differently (it's a string, not a list)
        if field == "domain":
            # Update domain directly
            with console.status(f"[bold green]Updating domain...[/bold green]", spinner="dots12"):
                success = self.summarizer.update_paper_field(
                    paper_id=self.current_paper_id,
                    field=db_field,
                    value=content
                )
            
            if success:
                console.print(f"[green]Updated domain to:[/green] {content}")
                
                # Update current paper
                self.current_paper[db_field] = content
            else:
                console.print(f"[red]Failed to update domain.[/red]")
            return
        
        # For list fields
        current_value = self.current_paper.get(db_field, [])
        
        # Convert to list if string
        if isinstance(current_value, str):
            if current_value:
                current_value = [current_value]
            else:
                current_value = []
        
        # Add new content
        current_value.append(content)
        
        # Update database
        with console.status(f"[bold green]Updating database...[/bold green]", spinner="dots12"):
            success = self.summarizer.update_paper_field(
                paper_id=self.current_paper_id,
                field=db_field,
                value=current_value
            )
        
        if success:
            console.print(f"[green]Added to {field}:[/green] {content}")
            
            # Update current paper
            self.current_paper[db_field] = current_value
        else:
            console.print(f"[red]Failed to add content to {field}.[/red]")
    
    def do_summarize(self, arg):
        """
        Summarize a new paper.
        
        Usage: summarize <pdf_path> [options]
        
        Options:
        --code            Generate implementation code
        --blog            Generate blog post
        --blog-style      Path to a file containing sample blog writing style
        --model           Specify LLM model to use
        --token-limit     Set custom token limit
        --force           Re-summarize even if already in database
        --output          Specify path to save the summary
        """
        try:
            args = shlex.split(arg)
            if not args:
                console.print("[red]No PDF path provided.[/red]")
                return
            
            pdf_path = args[0]

            # Parse options (other option parsing code remains the same)
            force = "--force" in args
            
            # Parse options
            code = "--code" in args
            blog = "--blog" in args
            model = None
            blog_style_text = ""
            token_limit = None
            force = "--force" in args
            output_path = None
            
            if "--model" in args:
                idx = args.index("--model")
                if idx + 1 < len(args):
                    model = args[idx + 1]
            
            if "--token-limit" in args:
                idx = args.index("--token-limit")
                if idx + 1 < len(args):
                    try:
                        token_limit = int(args[idx + 1])
                    except ValueError:
                        console.print(f"[red]Invalid token limit: {args[idx + 1]}. Using default.[/red]")
            
            if "--blog-style" in args:
                idx = args.index("--blog-style")
                if idx + 1 < len(args):
                    style_path = args[idx + 1]
                    try:
                        with open(style_path, "r") as f:
                            blog_style_text = f.read()
                    except Exception as e:
                        console.print(f"[red]Failed to read blog style file: {e}[/red]")
                        return
            
            # Add handling for output path
            if "--output" in args:
                idx = args.index("--output")
                if idx + 1 < len(args):
                    output_path = args[idx + 1]
                    # Make sure directory exists
                    output_dir = os.path.dirname(output_path)
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)
            
            # Check if file exists
            if not os.path.exists(pdf_path):
                console.print(f"[red]PDF file not found: {pdf_path}[/red]")
                return
            
            # Check if this paper is already processed - FIXED VERSION
            if not force:
                paper_filename = os.path.basename(pdf_path)
                with console.status(f"[bold blue]Checking if already processed...[/bold blue]", spinner="dots12"):
                    # Search for papers with similar filename
                    existing_papers = self.summarizer.search_papers(paper_filename, n_results=5)
                    
                    # Check if any existing paper has the same filepath
                    for paper in existing_papers:
                        paper_filepath = paper.get("filepath", "")
                        paper_id = paper.get("paper_id", "")
                        
                        # Skip if paper_id is None or empty
                        if not paper_id:
                            continue
                            
                        # Compare normalized paths
                        if os.path.normpath(paper_filepath) == os.path.normpath(pdf_path):
                            console.print(f"[yellow]This paper has already been processed (ID: {paper_id}).[/yellow]")
                            console.print("Use the --force flag to reprocess it, or 'open' to view the existing summary.")
                            
                            # Ask if the user wants to open the existing paper
                            if console.input(f"Open existing summary? [y/N]: ").lower().strip() == "y":
                                self.do_open(paper_id)
                            return
            
            # Run summarization
            console.print(f"[bold blue]Processing paper:[/bold blue] {pdf_path}")
            
            try:
                with Progress() as progress:
                    task = progress.add_task("[green]Summarizing paper...", total=None)
                    
                    result = asyncio.run(self.summarizer.summarize_paper(
                        filepath=pdf_path,
                        generate_code=code,
                        generate_blog=blog,
                        blog_style_sample=blog_style_text,
                        model=model,
                        output_token_limit=token_limit
                    ))
                    
                    progress.update(task, completed=True)
                
                # Display summary
                display_summary(result, theme=self.theme)
                
                # Set as current paper
                self.current_paper_id = result["paper_id"]
                self.current_paper = result
                
                # Add to paper history
                self._add_to_paper_history(result["paper_id"])
                
                console.print(f"\n[bold green]Paper summarized and set as current paper.[/bold green]")
                console.print(f"[bold]Paper ID:[/bold] {result['paper_id']}")
                console.print(f"[bold]Domain:[/bold] {result.get('domain', 'Unknown')}")
                
                # Save to specified output path if provided
                if output_path:
                    with open(output_path, "w") as f:
                        # Write the paper summary as markdown
                        f.write(f"# {result['title']}\n\n")
                        f.write(f"**Domain:** {result.get('domain', 'Unknown')}\n\n")
                        f.write(f"**Paper ID:** {result['paper_id']}\n\n")
                        f.write("## Summary\n\n")
                        f.write(f"{result.get('summary', '')}\n\n")
                        
                        # Write takeaways
                        f.write("## Key Takeaways\n\n")
                        takeaways = result.get('takeaways', [])
                        if isinstance(takeaways, list):
                            for takeaway in takeaways:
                                f.write(f"- {takeaway}\n")
                        else:
                            f.write(f"{takeaways}\n")
                        
                        # Add more sections as needed
                        for section_title, section_key in [
                            ("Problem Statement", "problem_statement"),
                            ("Methodology", "methodology"),
                            ("Architecture", "architecture"),
                            ("Key Results", "key_results"),
                            ("Implications", "implications"),
                            ("Future Directions", "future_directions"),
                            ("Background", "background"),
                            ("Mathematical Formulations", "math_formulations"),
                        ]:
                            content = result.get(section_key, "")
                            if content:
                                f.write(f"\n## {section_title}\n\n")
                                f.write(f"{content}\n")
                    
                    console.print(f"\n[green]Summary saved to:[/green] {output_path}")
                
                # Save generated code if requested
                if code and "code_implementation" in result:
                    code_path = os.path.join(
                        os.path.expanduser(self.config.get("output_dir", ".")),
                        f"{os.path.splitext(os.path.basename(pdf_path))[0]}_implementation.py"
                    )
                    
                    os.makedirs(os.path.dirname(code_path), exist_ok=True)
                    
                    with open(code_path, "w") as f:
                        f.write(result["code_implementation"])
                    
                    console.print(f"\n[green]Implementation code saved to {code_path}[/green]")
                
                # Save generated blog if requested
                if blog and "blog_post" in result:
                    blog_path = os.path.join(
                        os.path.expanduser(self.config.get("output_dir", ".")),
                        f"{os.path.splitext(os.path.basename(pdf_path))[0]}_blog.md"
                    )
                    
                    os.makedirs(os.path.dirname(blog_path), exist_ok=True)
                    
                    with open(blog_path, "w") as f:
                        f.write(result["blog_post"])
                    
                    console.print(f"\n[green]Blog post saved to {blog_path}[/green]")
            
            except Exception as e:
                if self.debug:
                    console.print(f"\n[red]Error summarizing paper: {str(e)}[/red]")
                    import traceback
                    console.print(traceback.format_exc())
                else:
                    console.print(f"\n[red]Error summarizing paper: {str(e)}[/red]")
                    console.print("If this issue persists, try running with --debug for more information.")
        
        except Exception as e:
            if self.debug:
                console.print(f"[red]Error in summarize command: {str(e)}[/red]")
                import traceback
                console.print(traceback.format_exc())
            else:
                console.print(f"[red]Error in summarize command: {str(e)}[/red]")
                console.print("If this issue persists, try running with --debug for more information.")
    
    def do_generate(self, arg):
        """
        Generate code implementation or blog post for the current paper.
        
        Usage: generate code|blog [--blog-style <style_path>] [--model <model_name>]
        """
        if not self.current_paper:
            console.print("[red]No paper currently open. Use 'open <paper_id>' first.[/red]")
            return
        
        args = shlex.split(arg)
        if not args:
            console.print("[red]No generation type specified. Use 'generate code' or 'generate blog'.[/red]")
            return
        
        gen_type = args[0].lower()
        
        if gen_type not in ["code", "blog"]:
            console.print("[red]Invalid generation type. Use 'generate code' or 'generate blog'.[/red]")
            return
        
        # Get paper info
        paper_id = self.current_paper_id
        title = self.current_paper.get("title", "Unknown")
        architecture = self.current_paper.get("architecture", "")
        
        # Parse options
        model = None
        if "--model" in args:
            idx = args.index("--model")
            if idx + 1 < len(args):
                model = args[idx + 1]
        
        # Get blog style if applicable
        blog_style_text = ""
        if gen_type == "blog" and "--blog-style" in args:
            idx = args.index("--blog-style")
            if idx + 1 < len(args):
                style_path = args[idx + 1]
                try:
                    with open(style_path, "r") as f:
                        blog_style_text = f.read()
                except Exception as e:
                    console.print(f"[red]Failed to read blog style file: {e}[/red]")
                    return
        
        # Generate content
        if gen_type == "code":
            if not architecture:
                console.print("[yellow]Warning: No architecture details found for this paper. Code generation may be limited.[/yellow]")
            
            console.print("[bold blue]Generating code implementation...[/bold blue]")
            
            # Default to Gemini for code generation if no model specified
            if model is None:
                model = "gemini-1.5-flash-2.0"
            
            with console.status(f"[bold green]Generating code with {model}...[/bold green]", spinner="dots12"):
                code = asyncio.run(self.llm_interface.generate_code_implementation(
                    architecture_details=architecture,
                    paper_title=title,
                    model=model
                ))
            
            # Save code
            output_dir = os.path.expanduser(self.config.get("output_dir", "."))
            code_path = os.path.join(output_dir, f"{paper_id}_implementation.py")
            
            os.makedirs(os.path.dirname(code_path), exist_ok=True)
            
            with open(code_path, "w") as f:
                f.write(code)
            
            console.print(f"[green]Code implementation saved to:[/green] {code_path}")

            # Update paper in database
            self.summarizer.update_paper_field(
                paper_id=paper_id,
                field="code_implementation",
                value=code
            )
            
            # Update current paper
            self.current_paper["code_implementation"] = code
        
        elif gen_type == "blog":
            console.print("[bold blue]Generating blog post...[/bold blue]")
            
            with console.status(f"[bold green]Generating blog post...[/bold green]", spinner="dots12"):
                blog_post = asyncio.run(self.llm_interface.generate_blog_post(
                    paper_summary=self.current_paper,
                    paper_title=title,
                    blog_style_sample=blog_style_text,
                    model=model
                ))
            
            # Save blog post
            output_dir = os.path.expanduser(self.config.get("output_dir", "."))
            blog_path = os.path.join(output_dir, f"{paper_id}_blog.md")
            
            os.makedirs(os.path.dirname(blog_path), exist_ok=True)
            
            with open(blog_path, "w") as f:
                f.write(blog_post)
            
            console.print(f"\n[green]Blog post saved to {blog_path}[/green]")
            
            # Update paper in database
            self.summarizer.update_paper_field(
                paper_id=paper_id,
                field="blog_post",
                value=blog_post
            )
            
            # Update current paper
            self.current_paper["blog_post"] = blog_post
        
    # Enhanced do_help method for better command documentation

    # Enhanced do_help method for better command documentation

def do_help(self, arg):
    """Show help message."""
    if arg:
        # Show help for specific command
        try:
            # Get the method for the command
            func = getattr(self, 'do_' + arg, None)
            if func:
                # Extract the docstring
                doc = func.__doc__
                if doc:
                    # Format the docstring
                    console.print(f"\n[bold {get_theme_color('primary')}]Help for command: {arg}[/bold {get_theme_color('primary')}]\n")
                    # Split by lines and format
                    lines = doc.strip().split('\n')
                    description = lines[0].strip()
                    console.print(f"[bold]{description}[/bold]\n")
                    
                    # Process remaining lines for usage and examples
                    if len(lines) > 1:
                        for line in lines[1:]:
                            line = line.strip()
                            if line.startswith("Usage:"):
                                console.print(f"[bold {get_theme_color('secondary')}]{line}[/bold {get_theme_color('secondary')}]")
                            elif line.startswith("Example:") or line.startswith("Examples:"):
                                console.print(f"[bold {get_theme_color('accent')}]{line}[/bold {get_theme_color('accent')}]")
                            elif line:
                                console.print(line)
                else:
                    console.print(f"[yellow]No help available for '{arg}'.[/yellow]")
            else:
                console.print(f"[red]Unknown command: {arg}[/red]")
        except Exception as e:
            console.print(f"[red]Error displaying help: {str(e)}[/red]")
        return
    
    # Show general help - organized by categories
    console.print(f"\n[bold {get_theme_color('primary')}]ResearchPal Interactive Shell Commands:[/bold {get_theme_color('primary')}]\n")
    
    # Define command categories
    categories = {
        "Paper Management": [
            ("open <paper_id>", "Open a paper and set it as current context"),
            ("search <query> [-n <count>]", "Search for papers in the database"),
            ("search domain:<domain_name>", "Search for papers in a specific research domain"),
            ("search title:<paper_title>", "Search specifically for paper titles"),
            ("search takeaway:<concept>", "Search in paper takeaways"),
            ("domains [-n <count>]", "List all research domains in the database"),
            ("history [<count>]", "Show recently opened papers"),
            ("switch <number>", "Switch to a paper from history by number")
        ],
        "Paper Analysis": [
            ("show <section>", "Show a section of current paper (summary, takeaways, architecture, future, background, math, domain, all)"),
            ("discuss <question>", "Discuss the current paper with the AI assistant"),
            ("add <field> <content>", "Add information to the current paper (takeaways, future, notes, domain)")
        ],
        "Paper Processing": [
            ("summarize <pdf_path>", "Summarize a new paper"),
            ("summarize <pdf_path> --force", "Re-summarize even if already in database"),
            ("summarize <pdf_path> --code", "Generate implementation code while summarizing"),
            ("summarize <pdf_path> --blog", "Generate blog post while summarizing"),
            ("summarize <pdf_path> --token-limit <limit>", "Summarize with custom token limit"),
            ("generate code", "Generate code implementation for current paper"),
            ("generate blog", "Generate blog post for current paper")
        ],
        "Multi-Paper Comparison": [
            ("compare_add [<paper_id>]", "Add paper to comparison list (uses current paper if no ID provided)"),
            ("compare_remove <index>", "Remove paper from comparison list by index"),
            ("compare_list", "List papers in the comparison list"),
            ("compare_clear", "Clear the comparison list"),
            ("compare [aspect]", "Generate comparison of papers (aspects: general, methodology, results, architecture)")
        ],
        "Interface Control": [
            ("theme <theme_name>", "Change the UI theme (cyberpunk, matrix, midnight, minimal, professional)"),
            ("debug on|off", "Toggle debug mode for detailed error messages"),
            ("clear", "Clear the screen"),
            ("refresh", "Refresh the display (show logo)"),
            ("exit, quit", "Exit the interactive shell"),
            ("help [<command>]", "Show this help message or help for a specific command")
        ]
    }
    
    # Print commands by category
    for category, commands in categories.items():
        console.print(f"[bold {get_theme_color('accent')}]{category}:[/bold {get_theme_color('accent')}]")
        
        for cmd, desc in commands:
            console.print(f"  [bold {get_theme_color('secondary')}]{cmd:<45}[/bold {get_theme_color('secondary')}] {desc}")
        
        console.print("")
    
    console.print(f"[dim]Use 'help <command>' for more information on a specific command.[/dim]")
    
    def default(self, line):
        """Handle unknown commands."""
        console.print(f"[red]Unknown command: {line}[/red]")
        console.print("Type 'help' for a list of available commands.")

    def cmdloop(self, intro=None):
        """Override cmdloop to add global error handling."""
        try:
            # Use the original cmdloop method from cmd.Cmd
            super().cmdloop(intro)
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print("\n[yellow]Operation interrupted by user.[/yellow]")
            # Ask if user wants to exit
            if console.input("Exit ResearchPal? [y/N]: ").lower().strip() == "y":
                self.do_exit("")
            else:
                # Restart cmdloop
                self.cmdloop(intro="")
        except Exception as e:
            # Catch any other exceptions to prevent ugly stack traces
            if self.debug:
                console.print(f"[red]An unexpected error occurred: {str(e)}[/red]")
                import traceback
                console.print(traceback.format_exc())
            else:
                console.print(f"[red]An unexpected error occurred: {str(e)}[/red]")
                console.print("Run with --debug for more detailed error information.")
            
            # Restart cmdloop to keep the shell running
            self.cmdloop(intro="ResearchPal is recovering from an error. Type 'help' for available commands.")

    # Also add a new command to toggle debug mode
    def do_debug(self, arg):
        """
        Toggle debug mode to show detailed error messages.
        
        Usage: debug on|off
        """
        arg = arg.strip().lower()
        if arg == "on":
            self.debug = True
            console.print("[green]Debug mode enabled. Detailed error messages will be shown.[/green]")
        elif arg == "off":
            self.debug = False
            console.print("[green]Debug mode disabled. Errors will be shown in simplified form.[/green]")
        else:
            console.print(f"[yellow]Current debug status: {'Enabled' if self.debug else 'Disabled'}[/yellow]")
            console.print("Usage: debug on|off")

    def do_export(self, arg):
        """
        Export the current paper summary to a file.
        
        Usage: export <file_path>
        """
        if not self.current_paper:
            console.print("[red]No paper currently open. Use 'open <paper_id>' first.[/red]")
            return
        
        file_path = arg.strip()
        if not file_path:
            console.print("[red]No file path provided.[/red]")
            console.print("Usage: export <file_path>")
            return
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            with open(file_path, 'w') as f:
                # Write the paper summary as markdown
                f.write(f"# {self.current_paper.get('title', 'Unknown Title')}\n\n")
                f.write(f"**Domain:** {self.current_paper.get('domain', 'Unknown')}\n\n")
                f.write(f"**Paper ID:** {self.current_paper_id}\n\n")
                f.write("## Summary\n\n")
                f.write(f"{self.current_paper.get('summary', '')}\n\n")
                
                # Write takeaways
                f.write("## Key Takeaways\n\n")
                takeaways = self.current_paper.get('takeaways', [])
                if isinstance(takeaways, list):
                    for takeaway in takeaways:
                        f.write(f"- {takeaway}\n")
                else:
                    f.write(f"{takeaways}\n")
                
                # Add more sections as needed
                for section_title, section_key in [
                    ("Problem Statement", "problem_statement"),
                    ("Methodology", "methodology"),
                    ("Architecture", "architecture"),
                    ("Key Results", "key_results"),
                    ("Future Directions", "future_directions"),
                ]:
                    content = self.current_paper.get(section_key, "")
                    if content:
                        f.write(f"\n## {section_title}\n\n")
                        f.write(f"{content}\n")
            
            console.print(f"[green]Summary exported to:[/green] {file_path}")
        
        except Exception as e:
            if self.debug:
                console.print(f"[red]Error exporting summary: {str(e)}[/red]")
                import traceback
                console.print(traceback.format_exc())
            else:
                console.print(f"[red]Error exporting summary: {str(e)}[/red]")


def run_interactive_shell(config_path=None, debug=False, minimal=False, theme="minimal", animation=True):
    """Run the interactive shell."""
    # Check if we should show animation - respect both parameter and config
    config = load_config(config_path)
    disable_animations = config.get("disable_animations", False)
    show_animation = animation and not disable_animations
    
    # If no theme specified, use from config
    if config.get("theme") and theme == "minimal":
        theme = config.get("theme")
    
    # Display animated logo with fancier animation (or simple logo for minimal theme)
    display_fancy_logo(console, animated=show_animation, theme=theme)
    
    # Initialize and run the shell
    shell = InteractiveShell(config_path, debug=debug, minimal=minimal, theme=theme)
    shell.cmdloop()