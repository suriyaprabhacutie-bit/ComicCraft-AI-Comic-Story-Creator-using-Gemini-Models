from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient

from app.config import BASE_DIR, settings


def create_demo_image(prompt: str, panel_number: int) -> str:
    output_dir = BASE_DIR / "static" / "panels"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"panel_{panel_number}.png"
    output_path = output_dir / filename

    image = Image.new(
        "RGB",
        (1024, 1024),
        "white",
    )

    draw = ImageDraw.Draw(image)

    # Border
    draw.rectangle(
        (20, 20, 1004, 1004),
        outline="black",
        width=8,
    )

    # Title
    title = f"COMICCRAFT - PANEL {panel_number}"

    draw.text(
        (50, 50),
        title,
        fill="black",
    )

    # Prompt text
    lines = wrap(prompt, width=55)

    y_position = 150

    for line in lines[:15]:
        draw.text(
            (60, y_position),
            line,
            fill="black",
        )

        y_position += 40

    # Simple placeholder illustration
    draw.ellipse(
        (350, 400, 674, 724),
        outline="black",
        width=8,
    )

    draw.text(
        (420, 530),
        "AI IMAGE",
        fill="black",
    )

    image.save(output_path)

    return f"/static/panels/{filename}"


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    if (
        settings.image_provider.lower() == "huggingface"
        and settings.hf_api_key
    ):
        try:
            client = InferenceClient(
                token=settings.hf_api_key
            )

            image = client.text_to_image(
                prompt,
                model=settings.hf_image_model,
            )

            output_dir = (
                BASE_DIR
                / "static"
                / "panels"
            )

            output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            filename = f"panel_{panel_number}.png"

            output_path = (
                output_dir / filename
            )

            image.save(output_path)

            return f"/static/panels/{filename}"

        except Exception as error:
            print(
                f"Hugging Face image generation failed: {error}"
            )

            if not settings.use_demo_fallback:
                raise

    if settings.use_demo_fallback:
        return create_demo_image(
            prompt,
            panel_number,
        )

    raise RuntimeError(
        "Image generation is not configured. "
        "Add HF_API_KEY or enable USE_DEMO_FALLBACK."
    )