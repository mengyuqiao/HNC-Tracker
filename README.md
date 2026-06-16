# HNC Tracker

A mobile web application for AI-assisted nutrition and pain medication tracking in head and neck cancer (HNC) patients undergoing radiation therapy. Built for a feasibility study evaluating real-time monitoring of the pain-nutrition relationship during treatment.

## Demo

https://github.com/mengyuqiao/HNC-Tracker/display.mp4

## Overview

HNC patients face high rates of malnutrition (50–80%) and pain during radiotherapy. Uncontrolled pain directly limits food intake, accelerating nutritional decline. This app tracks both together, using an on-device vision-language model (VLM) to minimize patient burden — no manual data entry required.

**Patient-facing app:**
- Photo-based food logging with AI calorie estimation
- Medication photo logging with AI OCR (reads bottle label automatically)
- Pain rating (0–9 scale) before and after each dose
- 60-minute follow-up check-in to measure medication effectiveness

**Clinician dashboard:**
- Real-time overview of all enrolled patients
- Flags for low caloric intake (<50% of goal) and high pain (≥7/9)
- Longitudinal charts: daily calories and pain before/after medication
- Full medication and food log tables

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask, SQLAlchemy |
| Database | SQLite |
| AI / VLM | Qwen2.5-VL-7B-Instruct (HuggingFace) |
| Frontend | Jinja2 templates, vanilla JS, Chart.js |
| Serving | Flask dev server + gunicorn |
| Tunnel | ngrok (external access without VPN) |
| Environment | Conda |

## Requirements

- Ubuntu server with NVIDIA GPU (≥16GB VRAM recommended)
- CUDA 12.x driver
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [ngrok account](https://ngrok.com) (free tier works)

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/hnc-tracker.git
cd hnc-tracker
```

**2. Run the setup script**
```bash
bash setup_hnc_tracker.sh
```

This creates a conda environment named `hnc-tracker` and installs all dependencies including PyTorch (CUDA 12.4), Flask, and Qwen2.5-VL.

**3. Configure environment**

Edit `.env` to match your setup:
```bash
SECRET_KEY=your-long-random-secret
VLM_GPU_ID=0          # which GPU to load the VLM on
VLM_MODEL=Qwen/Qwen2.5-VL-7B-Instruct
SUPPORT_PHONE=607-555-0100
FOLLOWUP_DELAY_MINUTES=60
```

**4. Set up ngrok**
```bash
ngrok config add-authtoken YOUR_NGROK_TOKEN
```

## Running

```bash
bash run.sh
```

This launches a tmux session with three panes:

```
┌─────────────────────┬──────────────────────┐
│                     │  ngrok               │
│  Flask app + logs   │  (public URL here)   │
│                     ├──────────────────────┤
│                     │  tail -f log file    │
└─────────────────────┴──────────────────────┘
```

- **Left** — Flask app output and VLM loading progress
- **Top right** — ngrok public URL for external access
- **Bottom right** — live log tail

Detach from tmux without stopping the app: `Ctrl+B` then `D`

Re-attach later: `tmux attach -t hnc`

## Accessing the App

Once running, check the top-right ngrok pane for your public URL:

| Interface | URL |
|---|---|
| Patient app | `https://xxxx.ngrok-free.dev` |
| Clinician dashboard | `https://xxxx.ngrok-free.dev/clinician/login` |
| Local (on server) | `http://localhost:5000` |

> **Note:** The ngrok URL changes on every restart with the free plan.

## Default Credentials

The database is seeded with demo data on first run.

**Demo patients:**

| Name | Enrollment Code | Calorie Goal |
|---|---|---|
| John Smith (DOB 03/14/1958) | `472910` | 2000 cal |
| Maria Garcia (DOB 07/22/1965) | `835621` | 1800 cal |

**Clinician login:**

| Username | Password |
|---|---|
| `admin` | `admin123` |

> ⚠️ Change the default clinician password before use with real patients. Update `seed_db()` in `app.py`.

## Project Structure

```
hnc-tracker/
├── app.py                  # Flask app and all routes
├── vlm_service.py          # Qwen2.5-VL model loader and inference
├── database.py             # SQLAlchemy models (Patient, FoodLog, MedLog, Clinician)
├── config.py               # Settings loaded from .env
├── run.sh                  # Startup script (tmux + ngrok)
├── setup_hnc_tracker.sh    # One-time environment setup
├── .env                    # Environment variables (not committed)
├── templates/
│   ├── base.html
│   ├── patient/            # 10 patient-facing screens
│   └── clinician/          # 3 clinician screens
├── static/
│   ├── css/style.css       # Colorblind-accessible design system
│   └── js/
│       ├── camera.js       # Mobile camera capture
│       └── app.js
├── uploads/                # Temporary image storage (auto-cleaned)
├── logs/                   # Timestamped log files
└── instance/
    └── hnc_tracker.db      # SQLite database
```

## Patient Flow

```
Welcome → Enter 6-digit code → Confirm identity → Home
  ├── Log a meal → Take photo → AI estimates calories → Confirm portion → Saved
  └── Log medicine → Take photo → AI reads label → Confirm med → Rate pain (0–9)
        └── [60 min later] Follow-up check-in → Rate pain again → Delta recorded
```

## Clinician Flow

```
Login → Dashboard (all patients, flags for low cal / high pain)
  └── Patient detail → Calorie chart (14 days) + Pain timeline + Med log table
```

## Colorblind Accessibility

The UI avoids red entirely. Color coding uses:
- 🔵 **Blue** (`#1a4a6b`) — primary actions
- 🟢 **Green** (`#2a7d4f`) — success, adequate intake
- 🟠 **Amber** (`#d4860a`) — warnings, low intake
- 🟤 **Orange-brown** (`#b84a00`) — severe pain (instead of red)

## IRB and Privacy Notes

- All image analysis is performed on the server (no third-party cloud processing of patient photos)
- Images are deleted from disk immediately after VLM inference
- Medication label OCR is prompted to exclude patient name, prescriber, and pharmacy information
- Patient login uses enrollment codes only — no passwords stored
- HIPAA-compliant storage is planned for the production deployment

## Research Context

This application supports a feasibility study targeting 20 HNC patients over 6–7 weeks of radiation therapy. Outcome measures include engagement metrics, System Usability Scale (SUS), and post-study acceptability surveys.

**Target journal:** JMIR Research Protocols / BMC Health Services Research

## License

For research use only. Not approved for clinical deployment without IRB approval and appropriate data security review.
