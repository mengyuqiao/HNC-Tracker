"""
VLM Service — Qwen2.5-VL-7B-Instruct
Loaded once at startup on the configured GPU.
Exposes two functions:
  analyze_food(image_path)      -> {"calories": int, "description": str}
  analyze_medication(image_path) -> {"med_name": str, "dosage": str, "instructions": str}
"""

import os
import torch
import logging
from PIL import Image
from config import Config

logger = logging.getLogger(__name__)

_model = None
_processor = None


def _load_model():
    global _model, _processor
    if _model is not None:
        return

    from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
    from qwen_vl_utils import process_vision_info

    gpu_id = Config.VLM_GPU_ID
    model_id = Config.VLM_MODEL

    logger.info(f"Loading {model_id} on GPU {gpu_id} ...")

    _processor = AutoProcessor.from_pretrained(model_id)
    _model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map=f"cuda:{gpu_id}",
    )
    _model.eval()
    logger.info("VLM loaded and ready.")


def _run_inference(image_path: str, prompt: str) -> str:
    """Send one image + prompt through the model, return text response."""
    from qwen_vl_utils import process_vision_info

    _load_model()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": f"file://{os.path.abspath(image_path)}"},
                {"type": "text",  "text": prompt},
            ],
        }
    ]

    text_input = _processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)

    inputs = _processor(
        text=[text_input],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(f"cuda:{Config.VLM_GPU_ID}")

    with torch.no_grad():
        output_ids = _model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,
        )

    # Trim input tokens from output
    trimmed = [
        out[len(inp):] for inp, out in zip(inputs.input_ids, output_ids)
    ]
    response = _processor.batch_decode(
        trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )[0]
    return response.strip()


def analyze_food(image_path: str) -> dict:
    """
    Estimate calories and describe food from a photo.
    Returns: {"calories": int, "description": str, "error": str|None}
    """
    prompt = (
        "Look at this food photo. Identify what food or drink is shown and estimate "
        "the total caloric content for the portion visible. "
        "Respond in this exact format (no extra text):\n"
        "CALORIES: <number>\n"
        "FOOD: <short description of what you see>\n"
        "If you cannot identify the food, respond:\n"
        "CALORIES: 0\n"
        "FOOD: Unable to identify"
    )

    try:
        raw = _run_inference(image_path, prompt)
        lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
                 for line in raw.splitlines() if ":" in line}
        calories = int(''.join(filter(str.isdigit, lines.get("CALORIES", "0"))) or 0)
        description = lines.get("FOOD", "Food item")
        return {"calories": calories, "description": description, "error": None}
    except Exception as e:
        logger.error(f"Food analysis failed: {e}")
        return {"calories": 0, "description": "Could not analyze image", "error": str(e)}


def analyze_medication(image_path: str) -> dict:
    """
    Extract medication name, dosage, and instructions from a bottle/package photo.
    Returns: {"med_name": str, "dosage": str, "instructions": str, "error": str|None}
    """
    prompt = (
        "Look at this medication bottle or package label. Extract only the medication name, "
        "dosage strength, and dosing instructions. Do NOT include patient name, address, "
        "prescriber name, pharmacy info, date, or any personal identifiers. "
        "Respond in this exact format (no extra text):\n"
        "MED_NAME: <medication name only>\n"
        "DOSAGE: <strength, e.g. 5 mg>\n"
        "INSTRUCTIONS: <dosing instructions>\n"
        "If you cannot read the label, respond:\n"
        "MED_NAME: Unknown\n"
        "DOSAGE: Unknown\n"
        "INSTRUCTIONS: Unknown"
    )

    try:
        raw = _run_inference(image_path, prompt)
        lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
                 for line in raw.splitlines() if ":" in line}
        return {
            "med_name":     lines.get("MED_NAME", "Unknown"),
            "dosage":       lines.get("DOSAGE", ""),
            "instructions": lines.get("INSTRUCTIONS", ""),
            "error": None,
        }
    except Exception as e:
        logger.error(f"Medication analysis failed: {e}")
        return {"med_name": "Unknown", "dosage": "", "instructions": "", "error": str(e)}


def warmup():
    """Pre-load the model at app startup so first request isn't slow."""
    try:
        _load_model()
    except Exception as e:
        logger.error(f"VLM warmup failed: {e}")
