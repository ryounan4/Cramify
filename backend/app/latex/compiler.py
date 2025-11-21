import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

from .utils import sanitize_latex
from .pdf_processing import count_pdf_pages

# Compile LaTeX source to PDF using latexmk
def compile_latex(latex_source: str, output_dir: Path = None, retry: bool = True) -> Dict:
    """
    Compile LaTeX source to PDF using latexmk.

    Args:
        latex_source: Complete LaTeX document source
        output_dir: Directory to save output (default: temp directory)
        retry: If True, retry with aggressive sanitization on failure

    Returns:
        {
            "success": bool,
            "pdf_bytes": bytes | None,
            "pdf_path": str | None,
            "tex_path": str | None,
            "log": str,
            "errors": List[str],
            "page_count": int
        }
    """
    # First sanitization pass
    latex_source = sanitize_latex(latex_source)

    # Use provided output_dir or create temp
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        tmpdir = str(output_dir)
        cleanup = False
    else:
        tmpdir = tempfile.mkdtemp()
        cleanup = True

    try:
        tex_path = Path(tmpdir) / 'cheatsheet.tex'
        tex_path.write_text(latex_source, encoding='utf-8')

        print(f"Compiling LaTeX...")

        # Compile with latexmk
        try:
            result = subprocess.run(
                [
                    'latexmk',
                    '-pdf',
                    '-halt-on-error',
                    '-interaction=nonstopmode',
                    '-no-shell-escape',  # Security: disable shell access
                    'cheatsheet.tex'
                ],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=30
            )
            log = result.stdout + '\n' + result.stderr
        except subprocess.TimeoutExpired as e:
            log = f"TIMEOUT after 30 seconds\nstdout: {e.stdout}\nstderr: {e.stderr}"
            print(f"Compilation timed out")
            result = None

        pdf_path = Path(tmpdir) / 'cheatsheet.pdf'

        if pdf_path.exists():
            pdf_bytes = pdf_path.read_bytes()
            page_count = count_pdf_pages(pdf_bytes)
            return {
                "success": True,
                "pdf_bytes": pdf_bytes,
                "pdf_path": str(pdf_path),
                "tex_path": str(tex_path),
                "log": log,
                "errors": [],
                "page_count": page_count
            }

        # Parse errors
        errors = [line for line in log.split('\n') if line.startswith('! ')]

        # Aggressive retry
        if retry and (errors or result is None):
            print("First compilation failed, retrying with aggressive sanitization...")

            # Aggressive sanitization: ASCII only + remove comments
            aggressive = latex_source.encode('ascii', 'ignore').decode('ascii')
            aggressive = re.sub(r'(?<!\\)%.*$', '', aggressive, flags=re.MULTILINE)

            tex_path.write_text(aggressive, encoding='utf-8')

            try:
                result_retry = subprocess.run(
                    [
                        'latexmk',
                        '-pdf',
                        '-halt-on-error',
                        '-interaction=nonstopmode',
                        '-no-shell-escape',
                        'cheatsheet.tex'
                    ],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                retry_success = True
                retry_log = result_retry.stdout + result_retry.stderr
            except subprocess.TimeoutExpired as e:
                retry_success = False
                retry_log = f"RETRY TIMEOUT after 30 seconds\nstdout: {e.stdout or ''}\nstderr: {e.stderr or ''}"
                print(f"Retry also timed out")

            if retry_success and (Path(tmpdir) / 'cheatsheet.pdf').exists():
                pdf_bytes = (Path(tmpdir) / 'cheatsheet.pdf').read_bytes()
                page_count = count_pdf_pages(pdf_bytes)
                return {
                    "success": True,
                    "pdf_bytes": pdf_bytes,
                    "pdf_path": str(Path(tmpdir) / 'cheatsheet.pdf'),
                    "tex_path": str(tex_path),
                    "log": retry_log,
                    "errors": [],
                    "page_count": page_count
                }

        return {
            "success": False,
            "pdf_bytes": None,
            "pdf_path": None,
            "tex_path": str(tex_path),
            "log": log,
            "errors": errors,
            "page_count": 0
        }

    finally:
        # Clean up temp directory if we created it
        if cleanup:
            import shutil
            try:
                shutil.rmtree(tmpdir)
            except:
                pass
