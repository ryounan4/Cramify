"""
Gemini API client for LaTeX generation.

Handles all communication with Gemini AI API.
"""

import os
import base64
import requests
from typing import List
from dotenv import load_dotenv

from .prompts import LATEX_SYSTEM_PROMPT, CONDENSATION_PROMPT_TEMPLATE
from .utils import clean_gemini_response, validate_latex_completeness

load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY', '')
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"


def gemini_generate_latex(
    images: List[bytes],
    filenames: List[str],
    api_key: str = API_KEY
) -> str:
    """
    Send all PDF images to Gemini Flash and get back complete LaTeX source.

    Args:
        images: List of PNG image bytes (from all PDFs)
        filenames: Source filenames for context
        api_key: Gemini API key

    Returns:
        Complete LaTeX document source

    Raises:
        requests.HTTPError: If API call fails
        ValueError: If API key is missing
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set. Add it to .env or environment variables.")

    # Build request parts
    parts = []

    # Add context about source files
    file_list = "\n".join([f"- {fn}" for fn in set(filenames)])  # Deduplicate filenames
    parts.append({"text": f"SOURCE FILES:\n{file_list}\n\nNow processing {len(images)} pages from these lecture slides..."})

    # Add all images
    for img_bytes in images:
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": img_b64
            }
        })

    # API request payload
    payload = {
        "system_instruction": {
            "parts": [{"text": LATEX_SYSTEM_PROMPT}]
        },
        "contents": [{"role": "user", "parts": parts}],
        "generation_config": {
            "temperature": 0.2,  # Low temperature for consistency
            "max_output_tokens": 8192,
        }
    }

    print(f"Sending {len(images)} images to Gemini Flash...")

    response = requests.post(
        f"{API_URL}?key={api_key}",
        json=payload,
        timeout=120  # 2 minute timeout for large batches
    )
    response.raise_for_status()

    data = response.json()
    latex_source = data["candidates"][0]["content"]["parts"][0]["text"]

    # Clean up markdown code fences and validate completeness
    latex_source = clean_gemini_response(latex_source)
    latex_source = validate_latex_completeness(latex_source)

    return latex_source


def condense_to_two_pages(
    latex_source: str,
    current_pages: int,
    api_key: str = API_KEY
) -> str:
    """
    Ask Gemini to condense content from 3+ pages down to exactly 2 pages.

    Strategy: Remove lower-priority items while keeping all essential content.

    Args:
        latex_source: Current LaTeX source (3+ pages)
        current_pages: Number of pages in current PDF
        api_key: Gemini API key

    Returns:
        Condensed LaTeX source targeting 2 pages

    Raises:
        requests.HTTPError: If API call fails
        ValueError: If API key is missing
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set.")

    instruction = CONDENSATION_PROMPT_TEMPLATE.format(current_pages=current_pages)

    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": instruction},
                {"text": f"\n\nCURRENT LATEX SOURCE:\n\n{latex_source}"}
            ]
        }],
        "generation_config": {
            "temperature": 0.2,
            "max_output_tokens": 8192,
        }
    }

    print(f"Asking Gemini to condense from {current_pages} pages to 2 pages...")

    response = requests.post(
        f"{API_URL}?key={api_key}",
        json=payload,
        timeout=120
    )
    response.raise_for_status()

    data = response.json()
    condensed_latex = data["candidates"][0]["content"]["parts"][0]["text"]

    # Clean up and validate
    condensed_latex = clean_gemini_response(condensed_latex)
    condensed_latex = validate_latex_completeness(condensed_latex)

    return condensed_latex
