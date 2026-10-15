"""Narrow regressions accepted in the second pre-edit stress review."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from dataqmonitor._support import check, json_object
from dataqmonitor.__main__ import main
from dataqmonitor.demo import demo
from dataqmonitor.report import as_text, as_html

class ReviewRegressionTests(unittest.TestCase):
    def test_excessive_config_nesting_is_an_input_error(self):
        text = '{"x":' + '[' * 100000 + '0' + ']' * 100000 + '}'
        with self.assertRaisesRegex(ValueError, 'nesting'):
            json_object(text)
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            path.write_text(text)
            csv = Path(directory) / 'input.csv'
            csv.write_text('record_id,predicted_label,actual_label\na,x,x\n')
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = main(['check', str(csv), '--config', str(path), '--format', 'json'])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(stdout.getvalue())['error']['code'], 'INVALID_INPUT')
            self.assertIn('nesting', json.loads(stdout.getvalue())['error']['message'])
            self.assertEqual(stderr.getvalue(), '')

    def test_human_reports_preserve_serialized_check_precision(self):
        report = demo('healthy')
        report['checks']['precision_example'] = check('Boundary example', 94.996, '%', {}, 'Observed', minimum=95)
        for render in (as_text, as_html):
            self.assertIn('94.996 %', render(report))
        self.assertEqual(report['checks']['precision_example']['status'], 'attention')
