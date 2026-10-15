"""Verify the explanatory case, including its deliberate identity-check limitation."""
import csv
from collections import Counter
import io
import json
from pathlib import Path
import unittest
from dataqmonitor.demo import demo, DEMO_AT
from dataqmonitor.engine import analyze

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'dataqmonitor/fixtures'

class CaseStudyTests(unittest.TestCase):
    def test_fictional_manifest_is_a_declared_population(self):
        manifest = json.loads((ROOT/'examples/expected-deliveries.json').read_text())
        self.assertIs(manifest['synthetic'], True)
        expected = {'D' + str(i).zfill(3) for i in range(1, 13)}
        self.assertEqual(set(manifest['expected_record_ids']), expected)
        self.assertEqual(manifest['required_count'], 12)
        config = json.loads((FIXTURES/'config.json').read_text())
        self.assertEqual(config['expected_rows'], manifest['required_count'])
        before = list(csv.DictReader(io.StringIO((FIXTURES/'broken.csv').read_text())))
        after = list(csv.DictReader(io.StringIO((FIXTURES/'healthy.csv').read_text())))
        ids = Counter(row['record_id'] for row in before)
        self.assertEqual(len(before), 8)
        self.assertEqual(ids['D006'], 2)
        self.assertEqual(expected-set(ids), {'D008','D009','D010','D011','D012'})
        self.assertEqual({row['record_id'] for row in after}, expected)

    def test_case_table_counts_match_reports(self):
        broken, healthy = demo('broken'), demo('healthy')
        self.assertEqual((broken['status'], healthy['status']), ('attention','ok'))
        c = broken['checks']['completeness']['evidence']
        self.assertEqual((c['observed_records'],c['expected_rows'],c['present_required_cells'],c['all_required_cells']), (7,12,39,40))
        self.assertEqual(broken['checks']['freshness']['evidence']['fresh_rows'],5)
        self.assertEqual(broken['checks']['availability']['evidence']['successful_attempts'],2)
        self.assertEqual(broken['checks']['consistency']['evidence']['rows_passing_rules'],5)
        self.assertTrue(all(check['value']==100 for check in healthy['checks'].values()))

    def test_count_can_pass_without_matching_expected_identities(self):
        text = (FIXTURES/'healthy.csv').read_text().replace('D012,','X012,')
        config = json.loads((FIXTURES/'config.json').read_text())
        report = analyze(text,config,attempts_csv=(FIXTURES/'healthy_attempts.csv').read_text(),at=DEMO_AT)
        self.assertEqual(report['checks']['completeness']['status'],'ok')
        self.assertEqual(report['status'],'ok')
        self.assertNotIn('D012', {row['record_id'] for row in csv.DictReader(io.StringIO(text))})
