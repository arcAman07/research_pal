"""Simple ASCII logo for ResearchPal - fallback for environments without rich formatting."""

# Simple ASCII logo for fallback
SIMPLE_LOGO = """
 ____                               _     ____       _ 
|  _ \ ___  ___  ___  __ _ _ __ ___| |__ |  _ \ __ _| |
| |_) / _ \/ __|/ _ \/ _` | '__/ __| '_ \| |_) / _` | |
|  _ <  __/\__ \  __/ (_| | | | (__| | | |  __/ (_| | |
|_| \_\___||___/\___|\__,_|_|  \___|_| |_|_|   \__,_|_|
                                                       
Your AI-powered research paper assistant
"""

def get_logo():
    """Return the simple ASCII logo."""
    return SIMPLE_LOGO

def display_logo():
    """Print the ASCII logo to the console."""
    print(SIMPLE_LOGO)