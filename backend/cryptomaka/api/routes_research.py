"""
Research publication and academic paper generator API routes.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(prefix="/research", tags=["research"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_GEN_DIR = PROJECT_ROOT / "research" / "paper_generator"


@router.get("/paper/metadata")
def get_paper_metadata():
    """Returns metadata and document structure of the academic paper."""
    from research.paper_generator.academic_paper_generator import (
        DEFAULT_PDF_OUTPUT,
        DEFAULT_TEX_OUTPUT,
        AcademicPaperGenerator,
    )

    # Ensure files exist
    generator = AcademicPaperGenerator()
    if not DEFAULT_PDF_OUTPUT.exists():
        generator.generate_pdf()
    if not DEFAULT_TEX_OUTPUT.exists():
        generator.generate_latex()

    return {
        "title": "CryptoMAKA: A Rigorous Evaluation Framework for Lightweight Three-Party Mutual Authentication and Key Agreement Protocols in Cloud-IoT Networks",
        "authors": "Research Evaluation & Verification Group, CryptoMAKA Laboratory",
        "target_format": "IEEE / ACM Camera-Ready 2-Column Preprint",
        "formats_available": ["pdf", "tex"],
        "sections": [
            "I. Introduction",
            "II. Protocol Architectures & Normalization",
            "III. Threat Model & Adversarial Penetration Suite",
            "IV. Formal Protocol Verification (ProVerif 2.05)",
            "V. Cyber-Physical IoT Wireless & Energy Modeling",
            "VI. Discussion & Conclusion",
            "References",
        ],
        "pdf_size_bytes": os.path.getsize(DEFAULT_PDF_OUTPUT) if DEFAULT_PDF_OUTPUT.exists() else 0,
        "tex_size_bytes": os.path.getsize(DEFAULT_TEX_OUTPUT) if DEFAULT_TEX_OUTPUT.exists() else 0,
        "features": [
            "Dynamically incorporates live ProVerif 2.05 formal verification theorems",
            "Includes cyber-physical LPWAN & cellular IoT latency/energy simulations",
            "Camera-ready typography with running headers and page numbers (Page X of Y)",
            "Dual export: PDF binary + full standalone IEEEtran LaTeX source (.tex)",
        ],
    }


@router.get("/paper/download")
def download_academic_paper(format: str = Query(default="pdf", pattern="^(pdf|tex)$")):
    """
    Downloads the dynamically compiled academic research manuscript
    in Camera-Ready PDF format or standalone IEEEtran LaTeX (.tex) format.
    """
    from research.paper_generator.academic_paper_generator import (
        DEFAULT_PDF_OUTPUT,
        DEFAULT_TEX_OUTPUT,
        AcademicPaperGenerator,
    )

    generator = AcademicPaperGenerator()

    if format == "pdf":
        pdf_path = generator.generate_pdf()
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename="CryptoMAKA_Academic_Manuscript.pdf",
        )
    elif format == "tex":
        tex_path = generator.generate_latex()
        return FileResponse(
            path=str(tex_path),
            media_type="application/x-tex",
            filename="CryptoMAKA_Academic_Manuscript.tex",
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: 'pdf', 'tex'")
