from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.schemas import ComicResponse, PromptRequest


router = APIRouter()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


def generate_comic(request_data: PromptRequest):
    # Step 1: Generate 5-panel outline
    outlines = generate_outline(request_data)

    # Step 2: Generate detailed story
    stories = generate_story(outlines, request_data)

    # Step 3: Generate images
    image_paths = []

    for story in stories:
        image_path = generate_image(
            story.image_prompt,
            story.panel_number,
        )
        image_paths.append(image_path)

    # Step 4: Build comic layout
    layout = build_comic_layout(
        stories,
        image_paths,
    )

    # Step 5: Export PDF
    pdf_path = save_pdf(layout)

    return layout, pdf_path


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        request_data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        layout, pdf_path = generate_comic(request_data)

        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "layout": layout,
                "pdf_path": pdf_path,
            },
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/generate-comic/json", response_model=ComicResponse)
async def generate_comic_json(
    request_data: PromptRequest,
):
    try:
        layout, pdf_path = generate_comic(request_data)

        return ComicResponse(
            success=True,
            layout=layout,
            pdf_path=pdf_path,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    if "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    file_path = (
        BASE_DIR
        / "static"
        / "exports"
        / filename
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found.",
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
    )


@router.get("/export-success")
async def export_success(request: Request):
    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
        },
    )


@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    image_path = generate_image(
        prompt,
        1,
    )

    return {
        "success": True,
        "image_path": image_path,
    }


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ComicCraft",
    }