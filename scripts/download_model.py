#!/usr/bin/env python3
"""Download ML model from Hugging Face Hub at runtime"""
from huggingface_hub import snapshot_download
from pathlib import Path

def download_model():
    model_dir = Path("models/all-MiniLM-L6-v2")
    if not model_dir.exists():
        print("📥 Downloading model from Hugging Face...")
        snapshot_download(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            local_dir=model_dir,
            local_dir_use_symlinks=False
        )
        print("✅ Model downloaded successfully")
    else:
        print("✅ Model already exists")

if __name__ == "__main__":
    download_model()
