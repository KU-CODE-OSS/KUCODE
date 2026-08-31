from django.test import SimpleTestCase

from scoring.services.calculator import (
    activity_score,
    churn_score,
    cohort_parameters,
    collaboration_score,
    gini_coefficient,
    language_difficulty_multiplier,
    normalize_log,
    personal_multiplier,
    problem_solving_score,
    productivity_score,
    project_score,
    prototype_student_overall,
)


class CalculatorTests(SimpleTestCase):
    def test_log_normalization_hits_reference_and_caps(self):
        self.assertAlmostEqual(normalize_log(10, 10), 100.0)
        self.assertAlmostEqual(normalize_log(100, 10), 100.0)
        self.assertAlmostEqual(normalize_log(0, 10), 0.0)

    def test_churn_score_peaks_at_configured_mean(self):
        self.assertAlmostEqual(churn_score(0.20), 100.0)
        self.assertLess(churn_score(0.0), 100.0)
        self.assertLess(churn_score(0.60), churn_score(0.35))

    def test_productivity_redistributes_missing_churn_weight(self):
        score, details = productivity_score(10, 0, 0, 10, 100)
        self.assertEqual(details["churn"], None)
        self.assertAlmostEqual(score, 50.0)

    def test_gini_is_zero_for_equal_contributions(self):
        self.assertAlmostEqual(gini_coefficient([5, 5, 5, 5]), 0.0)
        self.assertGreater(gini_coefficient([20, 0, 0, 0]), 0.7)

    def test_collaboration_applies_issue_bonus_and_caps(self):
        score, details = collaboration_score(
            merged_pr_count=10,
            unmerged_pr_count=0,
            contributor_contributions=[5, 5, 5, 5],
            issue_count=5,
            pr_reference=10,
        )
        self.assertEqual(score, 100.0)
        self.assertGreater(details["issue_bonus"], 0)

    def test_problem_solving_redistributes_missing_components(self):
        score, details = problem_solving_score(
            average_issue_resolution_days=None,
            issue_resolution_reference_days=None,
            merged_pr_count=1,
            closed_unmerged_pr_count=1,
            workflow_count=0,
            workflow_commit_count=0,
            has_snapshot=True,
        )
        self.assertIsNone(details["issue_resolution"])
        self.assertAlmostEqual(score, 50 * 0.30 / 0.55)

    def test_language_only_difficulty_uses_byte_weighted_average(self):
        multiplier, details = language_difficulty_multiplier({"Python": 75, "JavaScript": 25})
        self.assertAlmostEqual(multiplier, 1.15)
        self.assertEqual(details["unmapped_languages"], [])

    def test_unknown_language_defaults_to_neutral(self):
        multiplier, details = language_difficulty_multiplier({"ShaderLab": 10})
        self.assertEqual(multiplier, 1.0)
        self.assertEqual(details["unmapped_languages"], ["ShaderLab"])

    def test_project_and_personal_scores_are_capped(self):
        self.assertEqual(project_score(100, 100, 100, 1.3), 100.0)
        self.assertEqual(personal_multiplier(1.0, 4), 1.3)

    def test_activity_score_is_monotonic(self):
        self.assertGreater(activity_score(10, 100), activity_score(5, 100))
        self.assertAlmostEqual(activity_score(0, 0), 0.0)

    def test_student_overall_excludes_growth_and_normalizes_remaining_weights(self):
        overall, details = prototype_student_overall([80, 80], [50, 50])
        self.assertAlmostEqual(overall, 84.0)
        self.assertEqual(details["effective_weights"]["project_average"], 0.80)
        self.assertNotIn("growth", details)

    def test_cohort_parameters_use_p95_and_defaults_for_single_churn(self):
        parameters = cohort_parameters(
            [
                {
                    "commit_count": 10,
                    "changed_lines": 100,
                    "pr_weighted_count": 2,
                    "churn_rate": 0.2,
                    "closed_issue_resolution_days": [2, 4],
                },
                {
                    "commit_count": 20,
                    "changed_lines": 200,
                    "pr_weighted_count": 4,
                    "churn_rate": None,
                    "closed_issue_resolution_days": [],
                },
            ]
        )
        self.assertAlmostEqual(parameters["commit_p95"], 19.5)
        self.assertAlmostEqual(parameters["issue_resolution_median_days"], 3.0)
        self.assertAlmostEqual(parameters["churn_stddev"], 0.15)
