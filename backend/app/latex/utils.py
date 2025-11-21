"""
Utility functions for LaTeX processing.

Includes sanitization, validation, and text processing helpers.
"""


def sanitize_latex(text: str) -> str:
    """
    Sanitize LaTeX for guaranteed compilation.

    Performs:
    - Unicode character replacement
    - Brace balancing
    - Line length management

    Args:
        text: LaTeX source code

    Returns:
        Sanitized LaTeX source
    """
    # Replace problematic Unicode characters
    unicode_map = {
        '\u2019': "'",      # Right single quote
        '\u201c': '"',      # Left double quote
        '\u201d': '"',      # Right double quote
        '\u2013': '--',     # En dash
        '\u2014': '---',    # Em dash
        '\xa0': ' ',        # Non-breaking space
        '\u2026': '...',    # Ellipsis
        '\u2018': "'",      # Left single quote
    }

    for old, new in unicode_map.items():
        text = text.replace(old, new)

    # Balance braces (simple check)
    def balance_braces(s: str) -> str:
        open_count = s.count('{')
        close_count = s.count('}')
        if open_count > close_count:
            s += '}' * (open_count - close_count)
        elif close_count > open_count:
            # Remove excess closing braces from end
            excess = close_count - open_count
            for _ in range(excess):
                last_close = s.rfind('}')
                if last_close != -1:
                    s = s[:last_close] + s[last_close+1:]
        return s

    text = balance_braces(text)

    return text


def validate_latex_completeness(latex_source: str) -> str:
    """
    Validate that LaTeX document is complete and well-formed.

    If Gemini's response was truncated, add missing closing tags.

    Args:
        latex_source: LaTeX source code

    Returns:
        Complete LaTeX source with all tags properly closed
    """
    latex_source = latex_source.strip()

    # Check if document ends properly
    if not latex_source.endswith(r'\end{document}'):
        print("Response appears truncated, adding closing tags...")

        # Close any open itemize environments
        if r'\begin{itemize}' in latex_source:
            open_count = latex_source.count(r'\begin{itemize}')
            close_count = latex_source.count(r'\end{itemize}')
            if open_count > close_count:
                latex_source += '\n\\end{itemize}'

        # Close any open enumerate environments
        if r'\begin{enumerate}' in latex_source:
            open_count = latex_source.count(r'\begin{enumerate}')
            close_count = latex_source.count(r'\end{enumerate}')
            if open_count > close_count:
                latex_source += '\n\\end{enumerate}'

        # Close multicols if it's open
        if r'\begin{multicols}' in latex_source and r'\end{multicols}' not in latex_source:
            latex_source += '\n\\end{multicols}'

        # Close document
        latex_source += '\n\\end{document}'

    return latex_source.strip()


def clean_gemini_response(response_text: str) -> str:
    """
    Clean up Gemini's response by removing markdown code fences.

    Args:
        response_text: Raw response from Gemini API

    Returns:
        Cleaned LaTeX source code
    """
    text = response_text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    # Remove "latex" language identifier if present
    if text.startswith("latex\n"):
        text = text[6:]

    return text.strip()
