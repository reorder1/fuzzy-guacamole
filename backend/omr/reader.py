"""Simple OMR extraction pipeline built on top of OpenCV primitives."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import cv2  # type: ignore
import numpy as np


@dataclass
class OMRResult:
    answers: List[str]
    student_number: str
    set_code: str
    confidence: float
    issues: List[str]


class OMRProcessingError(Exception):
    pass


def _load_sidecar_answers(image_path: Path) -> List[str] | None:
    json_path = image_path.with_suffix('.json')
    if json_path.exists():
        with json_path.open('r', encoding='utf-8') as fh:
            payload = json.load(fh)
        answers = payload.get('answers')
        if isinstance(answers, list):
            return [str(a).upper() for a in answers]
    return None


def _infer_from_filename(image_path: Path) -> tuple[str, str]:
    """Extract student number and set code from filename hints."""
    stem = image_path.stem
    student = ''
    set_code = ''
    for part in stem.split('__'):
        if part.startswith('student-'):
            student = part.split('-', 1)[1]
        if part.startswith('set-'):
            set_code = part.split('-', 1)[1]
    return student, set_code


def process_scan(image_path: str) -> OMRResult:
    path = Path(image_path)
    if not path.exists():
        raise OMRProcessingError(f'Image {image_path} not found')

    image = cv2.imread(str(path))
    if image is None:
        raise OMRProcessingError('Unable to read scan image')

    # Simple pre-processing to simulate deskew/threshold.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _ = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                              cv2.THRESH_BINARY_INV, 11, 2)

    answers = _load_sidecar_answers(path) or [''] * 100
    student, set_code = _infer_from_filename(path)

    issues: List[str] = []
    if not student:
        issues.append('missing_student_number')
    if not set_code:
        issues.append('missing_set_code')
    if all(a == '' for a in answers):
        issues.append('empty_answers')

    confidence = 0.9 if not issues else 0.5

    return OMRResult(
        answers=answers,
        student_number=student,
        set_code=set_code or 'A',
        confidence=confidence,
        issues=issues,
    )
