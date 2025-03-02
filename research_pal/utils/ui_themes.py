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

# Holographic-style logo with enhanced visuals
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
    }
}

# Active theme (default)
active_theme = THEMES["cyberpunk"]

def set_theme(theme_name):
    """Set the active color theme."""
    global active_theme
    if theme_name in THEMES:
        active_theme = THEMES[theme_name]

def get_theme_color(color_key):
    """Get a color from the active theme."""
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
    
    def __init__(self, console=None, theme="cyberpunk"):
        """Initialize the logo animation."""
        self.console = console or Console()
        set_theme(theme)
        self.frame = 0
        self.max_frames = 20
        self.stop_event = threading.Event()
    
    def _render_frame(self):
        """Render a frame of the animation."""
        layout = Layout()
        
        # Use different logo based on frame
        if self.frame < self.max_frames // 2:
            logo_text = HOLOGRAPHIC_LOGO
        else:
            logo_text = CYBER_LOGO
        
        # Apply wave effect based on frame number
        wave_offset = self.frame % 5
        
        styled_logo = create_gradient_text(logo_text)
        
        # Create panels for icons
        icons = Columns([
            Panel(DOCUMENT_ICON, border_style=get_theme_color("primary")),
            Panel(BRAIN_ICON, border_style=get_theme_color("secondary")),
            Panel(SEARCH_ICON, border_style=get_theme_color("accent"))
        ])
        
        # Display everything
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
                    Align.center(Text(f"Your AI-powered research paper assistant", style=get_theme_color("text"))),
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
        
        # Optional matrix effect
        if random.random() < 0.3:  # 30% chance
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

def display_fancy_logo(console=None, animated=True, theme="cyberpunk"):
    """Display the fancy logo, either animated or static."""
    if console is None:
        console = Console()
    
    set_theme(theme)
    
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
    
    return f"[{primary}]research[/{primary}][{text}]pal[/{text}] [{secondary}]>[/{secondary}] "