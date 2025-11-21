# Use official Python 3.11 slim image (secure base from Docker Hub)
FROM python:3.11-slim

# Install LaTeX - all packages needed for template in prompts.py:
# - texlive-latex-base: article class, inputenc, fontenc, amsmath, amssymb
# - texlive-latex-extra: geometry, multicol, enumitem, titlesec, mathtools
# - texlive-fonts-recommended: standard fonts for better compatibility
# - texlive-science: siunitx package
# - lmodern: Latin Modern fonts
# - latexmk: LaTeX compilation tool
# - ghostscript: PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    lmodern \
    latexmk \
    ghostscript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create non-root user for security (don't run as root)
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Railway uses PORT env variable)
EXPOSE 8080

# Start gunicorn with Railway's PORT and increased timeout for AI processing
CMD gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 300 app.api:app
