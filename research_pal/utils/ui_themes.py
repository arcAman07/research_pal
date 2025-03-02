# research_pal/utils/ui_themes.py
"""UI themes and enhanced display functionality for ResearchPal."""
import os
import sys
import random
import time
import threading
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.style import Style
from rich.layout import Layout
from rich.live import Live
from rich.columns import Columns
from rich.align import Align

# Simple logo (clean and modern with horizontal lines)
SIMPLE_LOGO = """
─────────────────────────────────────────────────────────────────────────
               _____                               _     _____      _    
              |  __ \\                             | |   |  __ \\    | |   
              | |__) |___  ___  ___  __ _ _ __ ___| |__ | |__) |_ _| |   
              |  _  // _ \\/ __|/ _ \\/ _` | '__/ __| '_ \\|  ___/ _` | |   
              | | \\ \\  __/\\__ \\  __/ (_| | | | (__| | | | |  | (_| | |   
              |_|  \\_\\___||___/\\___|\\___ |_|  \\___|_| |_|_|   \\__,_|_|   
                                                              
               Professional AI-Powered Research Assistant
─────────────────────────────────────────────────────────────────────────
"""

# Original holographic logo kept for backwards compatibility
HOLOGRAPHIC_LOGO = """
    ╭────────────────────────────────────────────────────────────────╮
    │                                                                │
    │   ██████╗ ████████╗███████╗████████╗ █████╗ ██████╗  ██████╗██╗  ██╗██████╗  █████╗ ██╗     │
    │   ██╔══██╗╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██║     │
    │   ██████╔╝   ██║   ███████╗   ██║   ███████║██████╔╝██║     ███████║██████╔╝███████║██║     │
    │   ██╔══██╗   ██║   ╚════██║   ██║   ██╔══██║██╔══██╗██║     ██╔══██║██╔═══╝ ██╔══██║██║     │
    │   ██║  ██║   ██║   ███████║   ██║   ██║  ██║██║  ██║╚██████╗██║  ██║██║     ██║  ██║███████╗│
    │   ╚═╝  ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝│
    │                                                                │
    ╰────────────────────────────────────────────────────────────────╯
"""

# Define CYBER_LOGO if it's referenced
CYBER_LOGO = HOLOGRAPHIC_LOGO  # Or create a different logo design

# Define these if they're referenced
DOCUMENT_ICON = "📄"
BRAIN_ICON = "🧠"
SEARCH_ICON = "🔍"
TIPS = [
    "Tip: Use 'generate code' to create implementation code for a paper.",
    "Tip: Try 'search domain:Computer Vision' to find papers in a specific domain.",
    "Tip: Change the theme with 'theme matrix' or 'theme cyberpunk'."
]

# Color themes
THEMES = {
    "cyberpunk": {
        "primary": "bright_cyan",
        "secondary": "magenta",
        "accent": "bright_yellow",
        "text": "bright_white",
        "dim": "dim cyan"
    },
    "matrix": {
        "primary": "bright_green",
        "secondary": "green",
        "accent": "bright_green",
        "text": "green",
        "dim": "dim green"
    },
    "midnight": {
        "primary": "bright_blue",
        "secondary": "blue",
        "accent": "bright_cyan",
        "text": "bright_white",
        "dim": "dim blue"
    },
    # New minimal theme with subdued colors
    "minimal": {
        "primary": "blue",
        "secondary": "grey62",
        "accent": "grey74",
        "text": "white",
        "dim": "grey42"
    },
    # New professional theme with even more subdued colors
    "professional": {
        "primary": "slate_blue",
        "secondary": "grey50",
        "accent": "slate_blue",
        "text": "grey93",
        "dim": "grey35"
    }
}

# Active theme (default)
active_theme = THEMES["minimal"]  # Changed default to minimal

def set_theme(theme_name):
    """Set the active color theme."""
    global active_theme
    if theme_name in THEMES:
        active_theme = THEMES[theme_name]

def get_theme_color(color_key, theme_name=None):
    """Get a color from the active theme or specified theme."""
    if theme_name and theme_name in THEMES:
        return THEMES[theme_name].get(color_key, "white")
    return active_theme.get(color_key, "white")

def create_gradient_text(text, colors=None):
    """Create text with gradient effect."""
    if colors is None:
        colors = [
            get_theme_color("primary"),
            get_theme_color("secondary"),
            get_theme_color("accent")
        ]
    
    styled_text = Text()
    
    for line_idx, line in enumerate(text.split('\n')):
        # Adjust color rotation based on line index
        offset = line_idx % 3
        
        for char_idx, char in enumerate(line):
            color_idx = (char_idx // 3 + offset) % len(colors)
            styled_text.append(char, Style(color=colors[color_idx]))
        
        styled_text.append("\n")
    
    return styled_text

def create_simple_text(text, color=None):
    """Create text with simple styling (no gradient)."""
    if color is None:
        color = get_theme_color("primary")
    
    styled_text = Text()
    styled_text.append(text, Style(color=color))
    return styled_text

def create_matrix_effect(console, duration=2):
    """Create a Matrix-like effect for startup."""
    width = console.width
    height = console.height
    
    chars = "01"
    
    # Clear the screen
    console.clear()
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Generate random characters
        lines = []
        for _ in range(height-1):
            line = ''.join(random.choice(chars) for _ in range(width))
            lines.append(line)
        
        # Display with color
        for i, line in enumerate(lines):
            brightness = 1.0 - (i / height)
            if brightness > 0.8:
                color = "bright_green"
            elif brightness > 0.5:
                color = "green"
            else:
                color = "dim green"
            
            console.print(line, style=color)
        
        time.sleep(0.1)
        console.clear()

class LogoAnimation:
    """Handles the animated display of the ResearchPal logo."""
    
    def __init__(self, console=None, theme="minimal"):
        """Initialize the logo animation."""
        self.console = console or Console()
        set_theme(theme)
        self.frame = 0
        self.max_frames = 20
        self.stop_event = threading.Event()
    
    def _render_frame(self):
        """Render a frame of the animation."""
        layout = Layout()
        
        # Use different logo based on theme
        if active_theme == THEMES["minimal"] or active_theme == THEMES["professional"]:
            logo_text = SIMPLE_LOGO
            styled_logo = create_simple_text(logo_text, get_theme_color("primary"))
        else:
            # Use different logo based on frame for animated themes
            if self.frame < self.max_frames // 2:
                logo_text = HOLOGRAPHIC_LOGO
            else:
                logo_text = CYBER_LOGO
            styled_logo = create_gradient_text(logo_text)
        
        # Create panels for icons - simplified for minimal theme
        if active_theme == THEMES["minimal"] or active_theme == THEMES["professional"]:
            icons = Text("PDF Processing | AI Analysis | Semantic Search", style=get_theme_color("secondary"))
        else:
            icons = Columns([
                Panel(DOCUMENT_ICON, border_style=get_theme_color("primary")),
                Panel(BRAIN_ICON, border_style=get_theme_color("secondary")),
                Panel(SEARCH_ICON, border_style=get_theme_color("accent"))
            ])
        
        # For simplified themes, just show the logo without much additional content
        if active_theme in [THEMES["minimal"], THEMES["professional"]]:
            # Just show the logo with minimal styling
            layout.update(styled_logo)
            return layout
        
        # Full fancy layout for other themes
        layout.split(
            Layout(name="logo", size=10),
            Layout(name="content")
        )
        
        layout["logo"].update(
            Panel(
                styled_logo,
                border_style=get_theme_color("primary"),
                title=f"[{get_theme_color('accent')}]ResearchPal[/{get_theme_color('accent')}]",
                subtitle=f"[{get_theme_color('dim')}]v1.0.0[/{get_theme_color('dim')}]"
            )
        )
        
        # Different content in different frames
        if self.frame % 3 == 0:
            layout["content"].update(
                Panel(
                    Align.center(Text("Your AI-powered research paper assistant", style=get_theme_color("text"))),
                    border_style=get_theme_color("secondary")
                )
            )
        elif self.frame % 3 == 1:
            layout["content"].update(
                Panel(
                    Align.center(Text(random.choice(TIPS), style=get_theme_color("text"))),
                    border_style=get_theme_color("secondary")
                )
            )
        else:
            layout["content"].update(
                Panel(
                    icons,
                    border_style=get_theme_color("secondary"),
                    title=f"[{get_theme_color('accent')}]Features[/{get_theme_color('accent')}]"
                )
            )
        
        return layout
    
    def animate(self, duration=3.0):
        """Run the animation for a specified duration."""
        start_time = time.time()
        end_time = start_time + duration
        
        # Clear screen
        self.console.clear()
        
        # Optional matrix effect - disabled for minimal theme
        if active_theme not in [THEMES["minimal"], THEMES["professional"]] and random.random() < 0.3:
            create_matrix_effect(self.console, duration=1.0)
        
        with Live(self._render_frame(), console=self.console, refresh_per_second=10) as live:
            while time.time() < end_time and not self.stop_event.is_set():
                self.frame = (self.frame + 1) % self.max_frames
                live.update(self._render_frame())
                time.sleep(0.1)
        
        # Final frame
        self.console.print(self._render_frame())
    
    def stop(self):
        """Stop the animation."""
        self.stop_event.set()

def display_fancy_logo(console=None, animated=True, theme="minimal"):
    """Display the fancy logo, either animated or static."""
    if console is None:
        console = Console()
    
    set_theme(theme)
    
    # For minimal theme, use a simpler display
    if theme in ["minimal", "professional"]:
        if animated:
            animation = LogoAnimation(console, theme)
            animation.animate(duration=1.0)  # Shorter duration for minimal theme
        else:
            logo_text = SIMPLE_LOGO
            styled_logo = create_simple_text(logo_text, get_theme_color("primary"))
            console.print(styled_logo)
            
            # Just show a simple tip without panel
            tip = "Type 'help' for available commands."
            console.print(Text(tip, style=get_theme_color("secondary")))
    else:
        # Original fancy display for other themes
        if animated:
            animation = LogoAnimation(console, theme)
            animation.animate()
        else:
            # Just show the logo without animation
            styled_logo = create_gradient_text(HOLOGRAPHIC_LOGO)
            console.print(Panel(
                styled_logo,
                border_style=get_theme_color("primary"),
                title=f"[{get_theme_color('accent')}]ResearchPal[/{get_theme_color('accent')}]",
                subtitle=f"[{get_theme_color('dim')}]v1.0.0[/{get_theme_color('dim')}]"
            ))
            
            tip = random.choice(TIPS)
            console.print(Panel(
                Text(tip, style=get_theme_color("text")),
                border_style=get_theme_color("secondary")
            ))

def get_fancy_prompt(theme_name=None):
    """Get a fancy prompt for the interactive shell based on the current theme."""
    if theme_name:
        set_theme(theme_name)
    
    primary = get_theme_color("primary")
    secondary = get_theme_color("secondary")
    text = get_theme_color("text")
    
    # Simpler prompt for minimal themes
    if active_theme in [THEMES["minimal"], THEMES["professional"]]:
        return f"[{primary}]rpal[/{primary}] [{secondary}]>[/{secondary}] "
    else:
        return f"[{primary}]research[/{primary}][{text}]pal[/{text}] [{secondary}]>[/{secondary}] "