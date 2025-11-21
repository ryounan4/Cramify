"""
Cramify LaTeX Pipeline - Streamlined 2-Page Cheat Sheet Generator

This module orchestrates the complete pipeline:
  1. Convert PDFs to images
  2. Send to Gemini for LaTeX generation (targeting ~3 pages)
  3. Compile and check page count
  4. Condense to exactly 2 pages if needed
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict

from .latex import (
    pdf_to_images,
    gemini_generate_latex,
    condense_to_two_pages,
    compile_latex,
)

logger = logging.getLogger(__name__)

# Configuration
API_KEY = os.getenv('GEMINI_API_KEY', '')


def generate_cheatsheet(
    pdf_files: List[bytes],
    filenames: List[str],
    api_key: str = API_KEY,
    output_dir: Path = None
) -> Dict:
    """
    Complete pipeline: PDFs → 2-page LaTeX cheat sheet.

    Args:
        pdf_files: List of PDF file bytes (up to 10 recommended)
        filenames: Corresponding filenames for context
        api_key: Gemini API key
        output_dir: Optional directory to save outputs

    Returns:
        {
            "success": bool,
            "pdf_bytes": bytes | None,
            "pdf_path": str | None,
            "latex_source": str,
            "tex_path": str | None,
            "metadata": {
                "input_pdfs": int,
                "total_pages": int,
                "output_pages": int,
                "processing_time_sec": float,
                "compilation_log": str
            }
        }
    """
    start_time = time.time()
    logger.info(f"STAGE 1 START: Converting {len(pdf_files)} PDFs to images...")

    # Stage 1: Convert all PDFs to images
    all_images = []
    page_count = 0

    for i, pdf_bytes in enumerate(pdf_files):
        logger.info(f"STAGE 1: Converting PDF {i+1}/{len(pdf_files)} ({len(pdf_bytes)} bytes)")
        images = pdf_to_images(pdf_bytes)
        all_images.extend(images)
        page_count += len(images)
        logger.info(f"STAGE 1: PDF {i+1} converted to {len(images)} pages")

    logger.info(f"STAGE 1 COMPLETE: Converted {page_count} total pages from {len(pdf_files)} PDFs")

    # Stage 2: Single Gemini call to generate comprehensive LaTeX
    logger.info(f"STAGE 2 START: Calling Gemini API with {len(all_images)} images")
    try:
        latex_source = gemini_generate_latex(all_images, filenames, api_key)
        logger.info(f"STAGE 2 COMPLETE: Received {len(latex_source)} characters of LaTeX")
    except Exception as e:
        logger.error(f"STAGE 2 FAILED: Gemini API error: {str(e)}")
        return {
            "success": False,
            "pdf_bytes": None,
            "pdf_path": None,
            "latex_source": "",
            "tex_path": None,
            "error": f"Gemini API error: {str(e)}",
            "metadata": {
                "input_pdfs": len(pdf_files),
                "total_pages": page_count,
                "output_pages": 0,
                "processing_time_sec": time.time() - start_time,
                "compilation_log": ""
            }
        }

    # Stage 3: Compile initial version
    logger.info(f"STAGE 3 START: Compiling initial LaTeX")
    result = compile_latex(latex_source, output_dir=output_dir)

    if not result["success"]:
        elapsed = time.time() - start_time
        logger.error(f"STAGE 3 FAILED: Compilation failed after {elapsed:.1f}s")
        if result["errors"]:
            logger.error(f"STAGE 3: First 3 errors: {result['errors'][:3]}")
        return {
            "success": False,
            "pdf_bytes": None,
            "pdf_path": None,
            "latex_source": latex_source,
            "tex_path": result["tex_path"],
            "metadata": {
                "input_pdfs": len(pdf_files),
                "total_pages": page_count,
                "output_pages": 0,
                "processing_time_sec": time.time() - start_time,
                "compilation_log": result["log"]
            }
        }

    # Stage 4: Check page count and condense if needed
    actual_pages = result["page_count"]
    logger.info(f"STAGE 3 COMPLETE: Initial compilation succeeded with {actual_pages} page(s)")

    if actual_pages > 2:
        logger.info(f"STAGE 4 START: Condensing {actual_pages} pages down to 2 pages...")
        try:
            latex_source = condense_to_two_pages(latex_source, actual_pages, api_key)
            logger.info(f"STAGE 4: Received condensed LaTeX, recompiling...")

            # Recompile condensed version
            result = compile_latex(latex_source, output_dir=output_dir)

            if result["success"]:
                final_pages = result["page_count"]
                logger.info(f"STAGE 4 COMPLETE: Condensed to {final_pages} page(s)")
            else:
                logger.warning(f"STAGE 4: Condensed version failed to compile, using original")
                # Fall back to original if condensation fails
                result = compile_latex(latex_source, output_dir=output_dir)

        except Exception as e:
            logger.error(f"STAGE 4 FAILED: Condensation error: {e}")
            logger.info(f"STAGE 4: Using original {actual_pages}-page version")

    elapsed = time.time() - start_time

    if result["success"]:
        final_pages = result["page_count"]
        pdf_size = len(result["pdf_bytes"]) if result["pdf_bytes"] else 0
        logger.info(f"FINAL SUCCESS: Generated cheat sheet in {elapsed:.1f}s ({final_pages} pages, {pdf_size} bytes)")
        if final_pages != 2:
            logger.warning(f"FINAL: Output is {final_pages} pages (target was 2)")
    else:
        logger.error(f"FINAL FAILURE: Final compilation failed after {elapsed:.1f}s")

    return {
        "success": result["success"],
        "pdf_bytes": result["pdf_bytes"],
        "pdf_path": result["pdf_path"],
        "latex_source": latex_source,
        "tex_path": result["tex_path"],
        "metadata": {
            "input_pdfs": len(pdf_files),
            "total_pages": page_count,
            "output_pages": result["page_count"] if result["success"] else 0,
            "processing_time_sec": elapsed,
            "compilation_log": result["log"]
        }
    }


def generate_from_paths(
    pdf_paths: List[str],
    output_dir: str = "output",
    api_key: str = API_KEY
) -> Dict:
    """
    Convenience function to generate cheat sheet from PDF file paths.

    Args:
        pdf_paths: List of PDF file paths
        output_dir: Directory to save outputs
        api_key: Gemini API key

    Returns:
        Result dictionary from generate_cheatsheet()
    """
    pdf_files = []
    filenames = []

    for path in pdf_paths:
        pdf_path = Path(path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        pdf_files.append(pdf_path.read_bytes())
        filenames.append(pdf_path.name)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    result = generate_cheatsheet(pdf_files, filenames, api_key, output_path)

    # Also save LaTeX source
    if result["latex_source"]:
        tex_output = output_path / "cheatsheet.tex"
        tex_output.write_text(result["latex_source"], encoding='utf-8')
        print(f" Saved LaTeX source: {tex_output}")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python latex_pipeline.py <pdf1> [pdf2] [pdf3] ...")
        print("\nExample:")
        print("  python latex_pipeline.py lecture1.pdf lecture2.pdf lecture3.pdf")
        sys.exit(1)

    pdf_paths = sys.argv[1:]

    print(f" Cramify LaTeX Pipeline")
    print(f"   Processing {len(pdf_paths)} PDF(s)")
    print()

    try:
        result = generate_from_paths(pdf_paths)

        if result["success"]:
            print()
            print(f" Summary:")
            print(f" Input PDFs: {result['metadata']['input_pdfs']}")
            print(f" Input pages: {result['metadata']['total_pages']}")
            print(f" Output pages: {result['metadata']['output_pages']}")
            print(f" Time: {result['metadata']['processing_time_sec']:.1f}s")
            print(f" Output: {result['pdf_path']}")
        else:
            print()
            print(f" Failed to generate cheat sheet")
            if "error" in result:
                print(f"   Error: {result['error']}")
            sys.exit(1)

    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
