# ============================================================================
# 🐺 FENRIR V2 - COLAB SECTION 1: ENVIRONMENT SETUP
# ============================================================================
# Runtime > Change runtime type > A100 GPU, High-RAM
# Then run this cell
# ============================================================================

# Check GPU
!nvidia-smi

# Install Ollama
!curl -fsSL https://ollama.com/install.sh | sh

# Install Python packages
!pip install -q yfinance requests pandas finnhub-python

# Start Ollama server in background
import subprocess
subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import time
time.sleep(5)  # Wait for server to start

# Pull base model
!ollama pull llama3.1:8b

print("✅ Section 1 Complete - Environment Ready")
print("🐺 A100 GPU active, Ollama running")
