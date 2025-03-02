# research_pal/cli/main.py
#!/usr/bin/env python3
"""
ResearchPal: Main entry point for the CLI application.
Provides a unified interface for working with research papers.
"""
import os
import sys
import click
import asyncio
from typing import Optional, List, Dict, Any
import logging
from rich.console import Console
from rich.logging import RichHandler
import yaml
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_pal.core.summarizer import PaperSummarizer
from research_pal.core.llm_interface import LLMInterface
from research_pal.db.chroma_manager import ChromaManager
from research_pal.cli.interactive import InteractiveShell, run_interactive_shell
from research_pal.utils.ui_themes import display_fancy_logo, get_fancy_prompt, set_theme
from research_pal.utils.config import CONFIG_PATH, load_config, save_config, DEFAULT_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("research_pal")
console = Console()

def check_environment():
    """Check if environment is properly set up."""
    # Check if required environment variables are set
    api_keys = {
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY")
    }
    
    missing_keys = [k for k, v in api_keys.items() if not v]
    
    if missing_keys:
        # Try to load from config
        config = load_config()
        for key in missing_keys:
            key_lower = key.lower()
            if config.get(key_lower):
                os.environ[key] = config[key_lower]
                missing_keys.remove(key)
    
    # Still missing keys?
    if missing_keys:
        console.print(f"[yellow]Warning: The following API keys are missing: {', '.join(missing_keys)}[/yellow]")
        console.print("[yellow]Some features may not work properly. Run 'research-pal configure' to set them up.[/yellow]")
        return False
    
    return True

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug logging.')
@click.option('--theme', type=click.Choice(['cyberpunk', 'matrix', 'midnight', 'minimal', 'professional']), 
              default='minimal', help='Choose UI color theme.')
@click.pass_context
def cli(ctx, debug, theme):
    """ResearchPal: A CLI tool for managing research papers."""
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Store debug flag and theme in context
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['THEME'] = theme
    
    # Set theme globally
    set_theme(theme)

@cli.command()
@click.option('--config-path', '-c', default=CONFIG_PATH, help='Path to configuration file.')
@click.pass_context
def configure(ctx, config_path):
    """Configure ResearchPal settings."""
    # Load existing config if available
    config = load_config(config_path)
    
    # Display logo first
    display_fancy_logo(console, theme=ctx.obj['THEME'], animated=False)
    
    # Prompt for configuration values
    console.print("\n[bold]ResearchPal Configuration[/bold]\n")
    
    console.print("[bold]API Keys:[/bold]")
    openai_api_key = click.prompt("OpenAI API Key", default=config.get("openai_api_key", ""))
    google_api_key = click.prompt("Google AI API Key (for Gemini Flash)", default=config.get("google_api_key", ""))
    
    console.print("\n[bold]LLM Settings:[/bold]")
    default_model = click.prompt("Default LLM Model", 
                                default=config.get("default_model", DEFAULT_CONFIG["default_model"]),
                                type=click.Choice(["gpt-4o-mini", "gpt-4o", "gemini-1.5-flash", "gemini-1.5-pro"]))
    
    output_token_limit = click.prompt("Default Output Token Limit", 
                                     default=config.get("output_token_limit", 4096),
                                     type=int)
    
    console.print("\n[bold]Database Settings:[/bold]")
    db_path = click.prompt("Database Path", default=config.get("db_path", DEFAULT_CONFIG["db_path"]))
    
    console.print("\n[bold]Output Settings:[/bold]")
    output_dir = click.prompt("Default Output Directory", default=config.get("output_dir", DEFAULT_CONFIG["output_dir"]))
    
    console.print("\n[bold]UI Settings:[/bold]")
    theme = click.prompt("UI Theme", 
                         default=config.get("theme", ctx.obj['THEME']),
                         type=click.Choice(["cyberpunk", "matrix", "midnight", "minimal", "professional"]))
    
    disable_animations = click.confirm("Disable animations?", 
                                      default=config.get("disable_animations", config.get("theme") in ["minimal", "professional"]))
    
    # Update config
    config.update({
        "openai_api_key": openai_api_key,
        "google_api_key": google_api_key,
        "default_model": default_model,
        "output_token_limit": output_token_limit,
        "db_path": db_path,
        "output_dir": output_dir,
        "theme": theme,
        "disable_animations": disable_animations
    })
    
    # Save config
    save_config(config, config_path)
    console.print(f"\n[green]Configuration saved to {config_path}[/green]")
    
    # Set environment variables right away for current session
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
    
    # Ask user if they want to enter the shell
    if click.confirm("\nDo you want to enter the interactive shell now?", default=True):
        ctx.invoke(shell, config_path=config_path, minimal=(theme in ["minimal", "professional"]))

@cli.command()
@click.option('--config-path', '-c', default=CONFIG_PATH, help='Path to configuration file.')
@click.option('--minimal/--no-minimal', default=None, help='Use minimal UI design.')
@click.option('--no-animation/--animation', default=None, help='Disable startup animation.')
@click.pass_context
def shell(ctx, config_path, minimal, no_animation):
    """Start the interactive shell."""
    # Check environment setup
    check_environment()
    
    # Load config to check for user preferences
    config = load_config(config_path)
    
    # Set minimal mode based on theme if not explicitly specified
    if minimal is None:
        minimal = config.get("theme") in ["minimal", "professional"]
    
    # Use config's animation setting if not specified in command
    if no_animation is None:
        no_animation = config.get("disable_animations", False)
    
    # Pass debug flag, theme, and animation settings to the shell
    debug = ctx.obj.get('DEBUG', False)
    theme = ctx.obj.get('THEME', config.get("theme", "minimal"))
    animation = not no_animation
    
    # Run the interactive shell
    run_interactive_shell(
        config_path=config_path, 
        debug=debug, 
        minimal=minimal,
        theme=theme,
        animation=animation
    )

@cli.command()
@click.pass_context
def run(ctx):
    """Default command, starts the interactive shell."""
    ctx.invoke(shell)

@cli.command()
def version():
    """Display the version information."""
    from importlib.metadata import version as get_version
    
    try:
        version = get_version("research-pal")
    except:
        version = "1.0.0"  # Default if not installed as package
    
    console.print(f"[bold]ResearchPal[/bold] version [cyan]{version}[/cyan]")
    console.print("Your AI-powered research paper assistant")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--test-api', is_flag=True, help='Test API connectivity with minimal processing.')
@click.pass_context
def test(ctx, file_path, test_api):
    """Test file processing and API connectivity."""
    # Display logo
    display_fancy_logo(console, theme=ctx.obj['THEME'], animated=False)
    
    if test_api:
        console.print("[bold]Testing API Connectivity...[/bold]")
        
        async def test_apis():
            llm_interface = LLMInterface()
            
            # Test OpenAI API
            console.print("\n[bold]Testing OpenAI API...[/bold]")
            try:
                response = await llm_interface.query_openai(
                    prompt="Say 'Hello from GPT' if you can read this.",
                    max_tokens=20
                )
                console.print(f"[green]Success! Response: {response}[/green]")
            except Exception as e:
                console.print(f"[red]Failed to connect to OpenAI API: {e}[/red]")
            
            # Test Google/Gemini API
            console.print("\n[bold]Testing Google API (Gemini)...[/bold]")
            try:
                response = await llm_interface.query_google(
                    prompt="Say 'Hello from Gemini' if you can read this.",
                    max_tokens=20
                )
                console.print(f"[green]Success! Response: {response}[/green]")
            except Exception as e:
                console.print(f"[red]Failed to connect to Google API: {e}[/red]")
        
        asyncio.run(test_apis())
    else:
        # Test file processing
        console.print(f"[bold]Testing file processing for: {file_path}[/bold]")
        
        from research_pal.core.pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        
        try:
            with console.status("[bold green]Processing file...[/bold green]"):
                result = processor.extract_and_chunk(file_path)
            
            console.print(f"[green]Successfully processed file![/green]")
            console.print(f"[bold]Metadata:[/bold] {result['metadata']}")
            console.print(f"[bold]Extracted {result['chunk_count']} chunks[/bold]")
            console.print(f"[bold]Found {len(result.get('highlighted_text', []))} highlighted sections[/bold]")
            console.print(f"[bold]Detected {len(result.get('figures_tables', []))} figures/tables[/bold]")
            
            # Show sample content
            if result['chunks']:
                console.print("\n[bold]Sample content (first 300 chars):[/bold]")
                console.print(result['chunks'][0][:300] + "...")
            
        except Exception as e:
            console.print(f"[red]Error processing file: {e}[/red]")
    
    # Ask user if they want to enter the shell
    if click.confirm("\nDo you want to enter the interactive shell now?", default=True):
        ctx.invoke(shell)

def main():
    """Main entry point."""
    # If run directly without arguments, launch the shell
    if len(sys.argv) == 1:
        sys.argv.append("shell")
    cli(obj={})

if __name__ == "__main__":
    main()