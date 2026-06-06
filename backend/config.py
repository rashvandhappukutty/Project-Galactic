# backend/config.py
import os

DB_PATH = "galactic_twin.db"
DATASETS_DIR = "datasets"

# Fallback path if backend is run from a subfolder
if not os.path.exists(DATASETS_DIR) and os.path.exists(os.path.join("..", DATASETS_DIR)):
    DATASETS_DIR = os.path.join("..", DATASETS_DIR)
