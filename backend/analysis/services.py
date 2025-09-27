from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import List

from exams.models import Exam


@dataclass
class ItemAnalytics:
    item: int
    difficulty: float
    discrimination_index: float
    point_biserial: float


@dataclass
class ExamAnalytics:
    exam_id: int
    kr20: float
    average_score: float
    average_percent: float
    item_stats: List[ItemAnalytics]


def _difficulty(correct_counts: List[int], total_students: int) -> List[float]:
    if total_students == 0:
        return [0.0 for _ in correct_counts]
    return [count / total_students for count in correct_counts]


def _discrimination_index(item_matrix: List[List[bool]], totals: List[int]) -> List[float]:
    if not totals:
        return [0.0 for _ in range(len(item_matrix[0]) if item_matrix else 0)]
    paired = list(zip(totals, item_matrix))
    paired.sort(key=lambda x: x[0])
    n = len(paired)
    slice_size = max(1, math.floor(n * 0.27))
    bottom = paired[:slice_size]
    top = paired[-slice_size:]
    results: List[float] = []
    for idx in range(len(item_matrix[0])):
        top_correct = sum(1 for _, answers in top if answers[idx])
        bottom_correct = sum(1 for _, answers in bottom if answers[idx])
        results.append(
            (top_correct / slice_size if slice_size else 0) - (bottom_correct / slice_size if slice_size else 0)
        )
    return results


def _point_biserial(item_matrix: List[List[bool]], totals: List[int]) -> List[float]:
    if not totals:
        return [0.0 for _ in range(len(item_matrix[0]) if item_matrix else 0)]
    avg_total = mean(totals)
    sd_total = pstdev(totals) or 1.0
    n = len(totals)
    results: List[float] = []
    for idx in range(len(item_matrix[0])):
        correct_totals = [totals[i] for i in range(n) if item_matrix[i][idx]]
        incorrect_totals = [totals[i] for i in range(n) if not item_matrix[i][idx]]
        p = len(correct_totals) / n if n else 0
        q = 1 - p
        if not correct_totals or not incorrect_totals or p in {0, 1}:
            results.append(0.0)
            continue
        mean_correct = mean(correct_totals)
        mean_incorrect = mean(incorrect_totals)
        r_pb = ((mean_correct - mean_incorrect) / sd_total) * math.sqrt(p * q)
        results.append(r_pb)
    return results


def compute_exam_analytics(exam: Exam) -> ExamAnalytics:
    scores = list(exam.scores.all())
    breakdowns = [score.breakdown for score in scores]
    totals = [score.raw_score for score in scores]
    if not breakdowns:
        return ExamAnalytics(
            exam_id=exam.id,
            kr20=0.0,
            average_score=0.0,
            average_percent=0.0,
            item_stats=[],
        )

    num_items = len(breakdowns[0])
    total_students = len(breakdowns)
    correct_counts = [0 for _ in range(num_items)]
    item_matrix: List[List[bool]] = [[False] * num_items for _ in range(total_students)]

    for student_idx, items in enumerate(breakdowns):
        for item in items:
            index = int(item['item']) - 1
            is_correct = bool(item['correct'])
            if is_correct:
                correct_counts[index] += 1
            item_matrix[student_idx][index] = is_correct

    difficulty = _difficulty(correct_counts, total_students)
    discrimination = _discrimination_index(item_matrix, totals)
    point_biserial = _point_biserial(item_matrix, totals)

    p_q_sum = sum(p * (1 - p) for p in difficulty)
    variance_total = pstdev(totals) ** 2 or 1.0
    kr20 = (num_items / (num_items - 1)) * (1 - (p_q_sum / variance_total)) if num_items > 1 else 0.0

    item_stats = [
        ItemAnalytics(item=index + 1, difficulty=difficulty[index], discrimination_index=discrimination[index], point_biserial=point_biserial[index])
        for index in range(num_items)
    ]

    return ExamAnalytics(
        exam_id=exam.id,
        kr20=round(kr20, 4),
        average_score=round(mean(totals), 2),
        average_percent=round(mean(score.percent for score in scores), 2),
        item_stats=item_stats,
    )
