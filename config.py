import os
from dotenv import load_dotenv

load_dotenv()

# Absolute path to the project root (where config.py lives)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

    # Always use an absolute path for SQLite so it works regardless of cwd
    _instance_dir = os.path.join(BASE_DIR, 'instance')
    os.makedirs(_instance_dir, exist_ok=True)   # create instance/ if missing
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(_instance_dir, 'hnc_tracker.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max image upload
    VLM_GPU_ID = int(os.environ.get('VLM_GPU_ID', 4))
    VLM_MODEL = os.environ.get('VLM_MODEL', 'Qwen/Qwen2.5-VL-7B-Instruct')
    SUPPORT_PHONE = os.environ.get('SUPPORT_PHONE', '607-555-0100')
    # Follow-up check-in delay in minutes after medication log
    FOLLOWUP_DELAY_MINUTES = 60