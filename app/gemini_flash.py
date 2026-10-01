import json

from google import genai
from google.genai import types

from app.config import settings
from app.schemas import PanelOutline, PromptRequest


def extract_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return json.loads(text)


def demo_outline(request: PromptRequest):
    character = request.character_name
    setting = request.setting

    return [
        PanelOutline(
            panel_number=1,
            title="The Beginning",
            scene_description=(
                f"{character} starts an ordinary day in {setting}."
            ),
            image_prompt=(
                f"Comic panel, {character} in {setting}, "
                f"establishing shot, {request.art_style}, "
                f"{request.tone} mood."
            ),
        ),
        PanelOutline(
            panel_number=2,
            title="A Strange Discovery",
            scene_description=(
                f"{character} discovers something unusual "
                f"while exploring {setting}."
            ),
            image_prompt=(
                f"Comic panel, {character} discovering something mysterious "
                f"in {setting}, expressive face, {request.art_style}."
            ),
        ),
        PanelOutline(
            panel_number=3,
            title="The Challenge",
            scene_description=(
                f"{character} faces an unexpected challenge."
            ),
            image_prompt=(
                f"Comic panel, {character} facing a challenge, "
                f"dynamic action scene, {request.art_style}."
            ),
        ),
        PanelOutline(
            panel_number=4,
            title="The Turning Point",
            scene_description=(
                f"{character} finds a clever way to solve the problem."
            ),
            image_prompt=(
                f"Comic panel, {character} solving the problem, "
                f"dramatic lighting, {request.art_style}."
            ),
        ),
        PanelOutline(
            panel_number=5,
            title="A New Beginning",
            scene_description=(
                f"{character} finishes the adventure with a hopeful ending."
            ),
            image_prompt=(
                f"Comic panel, {character} smiling after the adventure, "
                f"beautiful {setting}, positive ending, "
                f"{request.art_style}."
            ),
        ),
    ]


def generate_outline(request: PromptRequest):
    if not settings.gemini_api_key:
        return demo_outline(request)

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    prompt = f"""
Create a short 5-panel comic outline.

User story:
{request.story_prompt}

Character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Return exactly 5 panels.

For every panel return these fields:

panel_number
title
scene_description
image_prompt

Return ONLY valid JSON array.
Do not add markdown.
"""

    response = client.models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
        ),
    )

    data = extract_json(response.text)

    return [
        PanelOutline(**item)
        for item in data
    ]