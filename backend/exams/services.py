from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from django.db import transaction

from core.models import Student
from .models import Exam, ExamSet, Score


@dataclass
class ScoringResult:
    raw_score: int
    percent: float
    breakdown: List[Dict[str, str]]


def grade_answers(answers: Sequence[str], answer_key: Sequence[str]) -> ScoringResult:
    total = len(answer_key)
    correct = 0
    breakdown: List[Dict[str, str]] = []
    for idx, key in enumerate(answer_key):
        given = answers[idx] if idx < len(answers) else ''
        is_correct = given == key
        if is_correct:
            correct += 1
        breakdown.append({'item': idx + 1, 'answer': given, 'key': key, 'correct': is_correct})
    percent = (correct / total) * 100 if total else 0
    return ScoringResult(raw_score=correct, percent=percent, breakdown=breakdown)


@transaction.atomic
def upsert_score(*, exam: Exam, student: Student, set_code: str, answers: Sequence[str]) -> Score:
    exam_set = ExamSet.objects.get(exam=exam, set_code=set_code)
    result = grade_answers(answers, exam_set.answer_key)
    score, _ = Score.objects.update_or_create(
        exam=exam,
        student=student,
        defaults={
            'set_code': set_code,
            'raw_score': result.raw_score,
            'percent': result.percent,
            'breakdown': result.breakdown,
        },
    )
    return score


def recompute_exam_scores(exam: Exam) -> int:
    updated = 0
    for score in exam.scores.select_related('student').all():
        exam_set = exam.sets.get(set_code=score.set_code)
        result = grade_answers([b['answer'] for b in score.breakdown], exam_set.answer_key)
        Score.objects.filter(pk=score.pk).update(
            raw_score=result.raw_score,
            percent=result.percent,
            breakdown=result.breakdown,
        )
        updated += 1
    return updated
