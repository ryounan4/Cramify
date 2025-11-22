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
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


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

    # Retry logic for blocked responses
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.post(
            f"{API_URL}?key={api_key}",
            json=payload,
            timeout=240  # 2 minute timeout for large batches
        )
        response.raise_for_status()

        data = response.json()

        # Check if response was blocked or has unexpected structure
        if "candidates" not in data or len(data["candidates"]) == 0:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1}: No candidates, retrying...")
                continue
            raise ValueError(f"Gemini API error: No candidates after {max_retries} attempts")

        candidate = data["candidates"][0]

        # Check if content was blocked by safety filters
        if "content" not in candidate:
            finish_reason = candidate.get("finishReason", "UNKNOWN")
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1}: Response blocked ({finish_reason}), retrying...")
                continue
            raise ValueError(f"Gemini blocked response after {max_retries} attempts. Reason: {finish_reason}")

        # Success. Extract the LaTeX
        latex_source = candidate["content"]["parts"][0]["text"]

        # Clean up markdown code fences and validate completeness
        latex_source = clean_gemini_response(latex_source)
        latex_source = validate_latex_completeness(latex_source)

        return latex_source


def fix_latex_errors(
    latex_source: str,
    errors: List[str],
    compilation_log: str,
    api_key: str = API_KEY
) -> str:
    """
    Ask Gemini to fix LaTeX compilation errors.

    Args:
        latex_source: Current LaTeX source that failed to compile
        errors: List of error messages from LaTeX compiler
        compilation_log: Full compilation log
        api_key: Gemini API key

    Returns:
        Fixed LaTeX source

    Raises:
        requests.HTTPError: If API call fails
        ValueError: If API key is missing
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set.")

    # Extract the most relevant part of the log (last 1000 chars)
    log_excerpt = compilation_log[-1000:] if len(compilation_log) > 1000 else compilation_log

    error_summary = "\n".join(errors[:5])  # First 5 errors

    instruction = f"""The LaTeX code you generated has compilation errors. Please fix them and return the corrected complete LaTeX document.

COMPILATION ERRORS:
{error_summary}

RELEVANT LOG EXCERPT:
{log_excerpt}

Please:
1. Identify and fix all syntax errors
2. Ensure all math expressions are properly wrapped in $ or $$ delimiters
3. Escape special characters correctly (%, &, _, etc.)
4. Make sure all environments are properly closed
5. Return the COMPLETE corrected LaTeX document (not just the fixes)

CURRENT LATEX SOURCE:
"""

    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": instruction},
                {"text": latex_source}
            ]
        }],
        "generation_config": {
            "temperature": 0.2,
            "max_output_tokens": 8192,
        }
    }

    print(f"Asking Gemini to fix {len(errors)} LaTeX errors...")

    response = requests.post(
        f"{API_URL}?key={api_key}",
        json=payload,
        timeout=240
    )
    response.raise_for_status()

    data = response.json()

    # Check for blocked responses
    if "candidates" not in data or len(data["candidates"]) == 0:
        raise ValueError("Gemini API error: No candidates in response")

    candidate = data["candidates"][0]
    if "content" not in candidate:
        raise ValueError(f"Gemini blocked response. Reason: {candidate.get('finishReason', 'UNKNOWN')}")

    fixed_latex = candidate["content"]["parts"][0]["text"]

    # Clean up and validate
    fixed_latex = clean_gemini_response(fixed_latex)
    fixed_latex = validate_latex_completeness(fixed_latex)

    return fixed_latex


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
        timeout=240
    )
    response.raise_for_status()

    data = response.json()
    condensed_latex = data["candidates"][0]["content"]["parts"][0]["text"]

    # Clean up and validate
    condensed_latex = clean_gemini_response(condensed_latex)
    condensed_latex = validate_latex_completeness(condensed_latex)

    return condensed_latex
