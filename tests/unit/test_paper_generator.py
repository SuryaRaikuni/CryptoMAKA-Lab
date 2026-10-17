"""
Unit tests for the Academic Paper Generator (PDF & LaTeX).
"""

import os

import pytest

from research.paper_generator.academic_paper_generator import (
    AcademicPaperGenerator,
)


@pytest.fixture
def generator():
    return AcademicPaperGenerator()


def test_generate_pdf(generator, tmp_path):
    """Ensure PDF generation produces a non-empty, valid PDF file."""
    output_pdf = tmp_path / "test_manuscript.pdf"
    path = generator.generate_pdf(output_pdf)
    assert path.is_file()
    assert os.path.getsize(path) > 5000

    # Verify PDF magic header (%PDF)
    with open(path, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"


def test_generate_latex(generator, tmp_path):
    """Ensure LaTeX generation produces a valid IEEEtran .tex document."""
    output_tex = tmp_path / "test_manuscript.tex"
    path = generator.generate_latex(output_tex)
    assert path.is_file()
    content = path.read_text(encoding="utf-8")

    assert r"\documentclass[journal,10pt,twocolumn]{IEEEtran}" in content
    assert r"\begin{document}" in content
    assert r"\end{document}" in content
    assert r"Ju \& Park" in content or "Ju-Park" in content
    assert "ML-KEM-768" in content
    assert r"\begin{table}" in content
    assert r"\bibitem{jupark2023}" in content
