#!/usr/bin/python
"""
Test suite for ClassifierAnalyzer.
"""

import filecmp
import logging
import os
import pandas
from pandas.util.testing import assert_frame_equal
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d
import unittest


from ClassifierAnalyzerTestData import RANDOM_10_TEST_CASE, RANDOM_100_TEST_CASE
from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import make_test_suite, MedInfoTestCase
from medinfo.common.Util import log
from medinfo.ml.ListPredictor import ListPredictor
from medinfo.ml.ClassifierAnalyzer import ClassifierAnalyzer
from medinfo.ml.SupervisedClassifier import SupervisedClassifier

class TestClassifierAnalyzer(MedInfoTestCase):
    def setUp(self):
        log.level = logging.ERROR
        # Use simple classifier and test case for testing non-ROC analyses.
        X = RANDOM_10_TEST_CASE['X']
        y = RANDOM_10_TEST_CASE['y']
        self._list_classifier = ListPredictor([0, 1])
        self._lc_analyzer = ClassifierAnalyzer(self._list_classifier, X, y)

        # Use ml classifier and complex test case.
        X = RANDOM_100_TEST_CASE['X']
        y = RANDOM_100_TEST_CASE['y']
        # Generate train/test split.
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=123456789)
        # Train logistic regression model.
        hyperparams = {
            'algorithm': SupervisedClassifier.REGRESS_AND_ROUND,
            'random_state': 123456789
        }
        self._ml_classifier = SupervisedClassifier([0, 1], hyperparams)
        self._ml_classifier.train(X_train, column_or_1d(y_train))
        self._ml_analyzer = ClassifierAnalyzer(self._ml_classifier, X_test, y_test)


    def tearDown(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        # Clean up the actual report file.
        try:
            actual_report_name = 'actual-list-classifier.report'
            actual_report_path = '/'.join([test_dir, actual_report_name])
            os.remove(actual_report_path)
        except OSError:
            pass

        # Clean up the actual precision-recall plot.
        try:
            actual_plot_name = 'actual-precision-recall-plot.png'
            actual_plot_path = '/'.join([test_dir, actual_plot_name])
            os.remove(actual_plot_path)
        except OSError:
            pass

        # Clean up the actual roc plot.
        try:
            actual_plot_name = 'actual-roc-plot.png'
            actual_plot_path = '/'.join([test_dir, actual_plot_name])
            os.remove(actual_plot_path)
        except OSError:
            pass

        # Clean up the actual precision at k plot.
        try:
            actual_plot_name = 'actual-precision-at-k-plot.png'
            actual_plot_path = '/'.join([test_dir, actual_plot_name])
            os.remove(actual_plot_path)
        except OSError:
            pass

    def _assert_fuzzy_equality(self, expected, actual):
        abs_diff = actual - expected
        rel_diff = (abs_diff) / expected
        self.assertTrue(rel_diff < 0.1)

    def test_score_accuracy(self):
        # Test accuracy.
        expected_accuracy = RANDOM_10_TEST_CASE['accuracy']
        actual_accuracy = self._lc_analyzer.score()
        self.assertEqual(expected_accuracy, actual_accuracy)

        # Test accuracy.
        expected_accuracy = RANDOM_100_TEST_CASE['accuracy']
        actual_accuracy = self._ml_analyzer.score()
        self.assertEqual(expected_accuracy, actual_accuracy)

        # Test bootstrapped CIs.
        actual_accuracy, actual_lower_ci, actual_upper_ci = self._ml_analyzer.score(ci=0.95, n_bootstrap_iter=1000)
        self.assertEqual(expected_accuracy, actual_accuracy)
        expected_lower_ci = RANDOM_100_TEST_CASE['ci']['accuracy']['lower']
        self.assertEqual(expected_lower_ci, actual_lower_ci)
        expected_upper_ci = RANDOM_100_TEST_CASE['ci']['accuracy']['upper']
        self.assertEqual(expected_upper_ci, actual_upper_ci)

    def test_score_recall(self):
        # Test recall.
        expected_recall = RANDOM_10_TEST_CASE['recall']
        actual_recall = self._lc_analyzer.score(metric=ClassifierAnalyzer.RECALL_SCORE)
        self.assertEqual(expected_recall, actual_recall)

        # Test recall.
        expected_recall = RANDOM_100_TEST_CASE['recall']
        actual_recall = self._ml_analyzer.score(metric=ClassifierAnalyzer.RECALL_SCORE)
        self.assertEqual(expected_recall, actual_recall)

        # Test bootstrapped CIs.
        actual_recall, actual_lower_ci, actual_upper_ci = self._ml_analyzer.score(metric=ClassifierAnalyzer.RECALL_SCORE, ci=0.95, n_bootstrap_iter=1000)
        self.assertEqual(expected_recall, actual_recall)
        expected_lower_ci = RANDOM_100_TEST_CASE['ci']['recall']['lower']
        self.assertEqual(expected_lower_ci, actual_lower_ci)
        expected_upper_ci = RANDOM_100_TEST_CASE['ci']['recall']['upper']
        self.assertEqual(expected_upper_ci, actual_upper_ci)

    def test_score_precision(self):
        # Test precision.
        expected_precision = RANDOM_10_TEST_CASE['precision']
        actual_precision = self._lc_analyzer.score(metric=ClassifierAnalyzer.PRECISION_SCORE)
        self.assertEqual(expected_precision, actual_precision)

        # Test precision.
        expected_precision = RANDOM_100_TEST_CASE['precision']
        actual_precision = self._ml_analyzer.score(metric=ClassifierAnalyzer.PRECISION_SCORE)
        self.assertEqual(expected_precision, actual_precision)

        # Test bootstrapped CIs.
        actual_precision, actual_lower_ci, actual_upper_ci = self._ml_analyzer.score(metric=ClassifierAnalyzer.PRECISION_SCORE, ci=0.95, n_bootstrap_iter=1000)
        self.assertEqual(expected_precision, actual_precision)
        expected_lower_ci = RANDOM_100_TEST_CASE['ci']['precision']['lower']
        self.assertEqual(expected_lower_ci, actual_lower_ci)
        expected_upper_ci = RANDOM_100_TEST_CASE['ci']['precision']['upper']
        self.assertEqual(expected_upper_ci, actual_upper_ci)

    def test_score_f1(self):
        # Test F1 score.
        expected_f1 = RANDOM_10_TEST_CASE['f1']
        actual_f1 = self._lc_analyzer.score(metric=ClassifierAnalyzer.F1_SCORE)
        self.assertEqual(expected_f1, actual_f1)

        # Test f1.
        expected_f1 = RANDOM_100_TEST_CASE['f1']
        actual_f1 = self._ml_analyzer.score(metric=ClassifierAnalyzer.F1_SCORE)
        self.assertEqual(expected_f1, actual_f1)

        # Test bootstrapped CIs.
        actual_f1, actual_lower_ci, actual_upper_ci = self._ml_analyzer.score(metric=ClassifierAnalyzer.F1_SCORE, ci=0.95, n_bootstrap_iter=1000)
        self.assertEqual(expected_f1, actual_f1)
        expected_lower_ci = RANDOM_100_TEST_CASE['ci']['f1']['lower']
        self.assertEqual(expected_lower_ci, actual_lower_ci)
        expected_upper_ci = RANDOM_100_TEST_CASE['ci']['f1']['upper']
        self.assertEqual(expected_upper_ci, actual_upper_ci)

    def test_score_average_precision(self):
        # Test average precision.
        expected_average_precision = RANDOM_100_TEST_CASE['average_precision']
        actual_average_precision = self._ml_analyzer.score(metric=ClassifierAnalyzer.AVERAGE_PRECISION_SCORE)
        self.assertEqual(expected_average_precision, actual_average_precision)

        # Test bootstrapped CIs.
        actual_average_precision, actual_lower_ci, actual_upper_ci = self._ml_analyzer.score(metric=ClassifierAnalyzer.AVERAGE_PRECISION_SCORE, ci=0.95, n_bootstrap_iter=1000)
        self.assertEqual(expected_average_precision, actual_average_precision)
        expected_lower_ci = RANDOM_100_TEST_CASE['ci']['average_precision']['lower']
        self.assertEqual(expected_lower_ci, actual_lower_ci)
        expected_upper_ci = RANDOM_100_TEST_CASE['ci']['average_precision']['upper']
        self.assertEqual(expected_upper_ci, actual_upper_ci)

    def test_score_roc_auc(self):
        # Test roc_auc.
        expected_roc_auc = RANDOM_100_TEST_CASE['roc_auc']
        actual_roc_auc = self._ml_analyzer.score(metric=ClassifierAnalyzer.ROC_AUC_SCORE)
        self.assertEqual(expected_roc_auc, actual_roc_auc)

        # Test bootstrapped CIs.
        actual_roc_auc, actual_lower_ci, actual_upper_ci = self._ml_analyzer.score(metric=ClassifierAnalyzer.ROC_AUC_SCORE, ci=0.95, n_bootstrap_iter=1000)
        self.assertEqual(expected_roc_auc, actual_roc_auc)
        expected_lower_ci = RANDOM_100_TEST_CASE['ci']['roc_auc']['lower']
        self.assertEqual(expected_lower_ci, actual_lower_ci)
        expected_upper_ci = RANDOM_100_TEST_CASE['ci']['roc_auc']['upper']
        self.assertEqual(expected_upper_ci, actual_upper_ci)

    def test_score_precision_at_k(self):
        # Test precision at K.
        prev_precision = 1.0
        for k in range(1, 20):
            actual_precision_at_k = self._ml_analyzer.score(metric=ClassifierAnalyzer.PRECISION_AT_K_SCORE, k=k)
            expected_precision_at_k = RANDOM_100_TEST_CASE['precision_at_k'][k]
            self.assertEqual(expected_precision_at_k, actual_precision_at_k)

        # Test bootstrapped CIs.
        actual_precision_at_k, actual_lower_ci, actual_upper_ci = self._ml_analyzer.score(metric=ClassifierAnalyzer.PRECISION_AT_K_SCORE, k=10, ci=0.95, n_bootstrap_iter=1000)
        expected_precision_at_k = RANDOM_100_TEST_CASE['precision_at_k'][10]
        self.assertEqual(expected_precision_at_k, actual_precision_at_k)
        expected_lower_ci = RANDOM_100_TEST_CASE['ci']['precision_at_k']['lower'][10]
        self.assertEqual(expected_lower_ci, actual_lower_ci)
        expected_upper_ci = RANDOM_100_TEST_CASE['ci']['precision_at_k']['upper'][10]
        self.assertEqual(expected_upper_ci, actual_upper_ci)

    def test_score_percent_predictably_positive(self):
        # Test roc_auc.
        expected_ppp = RANDOM_100_TEST_CASE['percent_predictably_positive']
        actual_ppp = self._ml_analyzer.score(metric=ClassifierAnalyzer.PERCENT_PREDICTABLY_POSITIVE)
        self.assertEqual(expected_ppp, actual_ppp)

        # Test bootstrapped CIs.
        actual_ppp, actual_lower_ci, actual_upper_ci = self._ml_analyzer.score(metric=ClassifierAnalyzer.PERCENT_PREDICTABLY_POSITIVE, ci=0.95, n_bootstrap_iter=1000)
        self.assertEqual(expected_ppp, actual_ppp)
        expected_lower_ci = RANDOM_100_TEST_CASE['ci']['percent_predictably_positive']['lower']
        self.assertEqual(expected_lower_ci, actual_lower_ci)
        expected_upper_ci = RANDOM_100_TEST_CASE['ci']['percent_predictably_positive']['upper']
        self.assertEqual(expected_upper_ci, actual_upper_ci)

    def test_plot_precision_recall_curve(self):
        # Compute precision-recall curve.
        precision_recall_curve = self._ml_analyzer.compute_precision_recall_curve()

        # Build paths for expected and actual plots.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        actual_plot_name = 'actual-precision-recall-plot.png'
        actual_plot_path = '/'.join([test_dir, actual_plot_name])

        self._ml_analyzer.plot_precision_recall_curve('Precision-Recall Curve', actual_plot_path)

        # Not sure how to validate this at the moment, so just validate
        # that it actually passes.
        self.assertTrue(True)

    def test_plot_roc_curve(self):
        # Compute ROC curve.
        roc_curve = self._ml_analyzer.compute_roc_curve()

        # Build paths for expected and actual plots.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        actual_plot_name = 'actual-roc-plot.png'
        actual_plot_path = '/'.join([test_dir, actual_plot_name])

        self._ml_analyzer.plot_roc_curve('ROC', actual_plot_path)

        # Not sure how to validate this at the moment, so just validate
        # that it actually passes.
        self.assertTrue(True)

    def test_plot_precision_at_k_curve(self):
        # Compute precision_recall_curve.
        k_vals, precision_vals = self._ml_analyzer.compute_precision_at_k_curve()

        # Build paths for expected and actual plots.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        actual_plot_name = 'actual-precision-at-k-plot.png'
        actual_plot_path = '/'.join([test_dir, actual_plot_name])

        self._ml_analyzer.plot_precision_at_k_curve('Precision at K', actual_plot_path)

        # Not sure how to validate this at the moment, so just validate
        # that it actually passes.
        self.assertTrue(True)

    def test_build_report(self):
        # Build report.
        expected_report = RANDOM_100_TEST_CASE['report']
        actual_report = self._ml_analyzer.build_report()[0]
        log.debug('expected_report: %s' % expected_report)
        log.debug('actual_report: %s' % actual_report)
        assert_frame_equal(expected_report, actual_report)

        # Build bootstrapped report.
        expected_report = RANDOM_100_TEST_CASE['ci']['report']
        actual_report = self._ml_analyzer.build_report(ci=0.95)[0]
        assert_frame_equal(expected_report, actual_report)

        # Build paths for expected and actual report.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        actual_report_name = 'actual-list-classifier.report'
        actual_report_path = '/'.join([test_dir, actual_report_name])

        # Write the report.
        self._ml_analyzer.write_report(actual_report_path)

        # Not sure how to validate this at the moment, so just validate
        # that it actually passes.
        self.assertTrue(True)

if __name__ == '__main__':
    suite = make_test_suite(TestClassifierAnalyzer)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
