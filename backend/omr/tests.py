from pathlib import Path

import cv2
import numpy as np
from django.test import TestCase

from .reader import process_scan


class OMRReaderTests(TestCase):
    def setUp(self):
        self.tmp_dir = Path('media/tests')
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.image_path = self.tmp_dir / 'scan__student-001__set-A.png'
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(str(self.image_path), image)
        answers_path = self.image_path.with_suffix('.json')
        answers_path.write_text('{"answers": ["A", "B", "C"]}', encoding='utf-8')

    def test_process_scan_reads_metadata(self):
        result = process_scan(str(self.image_path))
        self.assertEqual(result.student_number, '001')
        self.assertEqual(result.set_code, 'A')
        self.assertEqual(result.answers[:3], ['A', 'B', 'C'])
        self.assertGreater(result.confidence, 0)
