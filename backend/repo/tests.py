import json
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import RequestFactory, TestCase
from django.utils.timezone import now as timezone_now
from rest_framework.test import APIRequestFactory

from account.models import Student
from course.models import Course, Course_project
from repo.api.views import (
    GenerateRepoSummaryAPIView,
    RepoSummaryAnalyzer,
    repository_summary_fingerprint,
    repository_summary_refresh_priority,
    repository_summary_status,
    remove_repository,
    repo_account_read_db,
)
from repo.models import Repo_commit, Repository


class RepoAccountReadDbTimestampTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.student = Student.objects.create(
            id="timestamp-student", name="Timestamp Student", github_id="test-user",
        )
        self.repo = Repository.objects.create(
            id="timestamp-repo", name="Timestamp Repo", owner_github_id="test-user",
            star_count=0, fork_count=0,
        )

    def add_commit(self, timestamp, author="test-user", repo=None):
        return Repo_commit.objects.create(
            repo=repo or self.repo,
            sha=f"commit-{Repo_commit.objects.count()}",
            repo_url="https://github.com/test-user/test-repo",
            owner_github_id="test-user",
            author_github_id=author,
            added_lines=3,
            deleted_lines=2,
            last_update=timestamp,
        )

    def read_profile(self):
        request = self.factory.post(
            "/repo/repo_account_read_db",
            json.dumps({"uuid": "empty", "student_num": self.student.id}),
            content_type="application/json",
        )
        with patch("repo.api.views.datetime", wraps=datetime) as clock:
            clock.now.return_value = datetime(2026, 8, 26, 12)
            response = repo_account_read_db(request)
        self.assertEqual(response.status_code, 200, response.content)
        return json.loads(response.content)

    def test_mixed_dates_skip_invalid_values_without_losing_totals(self):
        for value in (
            "2026-08-25T10:00:00Z", "2026-08-24T11:00:00Z",
            "Unknown", None, "", "not-a-date", "2026-02-30T00:00:00Z",
        ):
            self.add_commit(value)
        self.add_commit("2026-08-26T00:00:00Z", author="another-user")

        data = self.read_profile()

        self.assertEqual(data["monthly_commits"]["total_count"], [
            ["2026-03", 0], ["2026-04", 0], ["2026-05", 0],
            ["2026-06", 0], ["2026-07", 0], ["2026-08", 2],
        ])
        self.assertEqual(data["monthly_commits"]["added_lines"], [
            ["2026-03", 0], ["2026-04", 0], ["2026-05", 0],
            ["2026-06", 0], ["2026-07", 0], ["2026-08", 6],
        ])
        self.assertEqual(data["monthly_commits"]["deleted_lines"], [
            ["2026-03", 0], ["2026-04", 0], ["2026-05", 0],
            ["2026-06", 0], ["2026-07", 0], ["2026-08", 4],
        ])
        self.assertEqual(data["monthly_commits"]["changed_lines"], [
            ["2026-03", 0], ["2026-04", 0], ["2026-05", 0],
            ["2026-06", 0], ["2026-07", 0], ["2026-08", 10],
        ])
        self.assertEqual(data["repositories"][0]["monthly_commits"], [["2026-08", 2]])
        self.assertEqual(data["repositories"][0]["user_commit_count"], 7)
        self.assertEqual(data["total_stats"]["all_total_commits"], 8)
        self.assertEqual(data["total_stats"]["owner_total_commits"], 7)
        self.assertEqual(data["total_stats"]["owner_total_changed_lines"], 35)
        self.assertEqual(data["heatmap"]["Tue"]["10"], 1)
        self.assertEqual(data["heatmap"]["Mon"]["11"], 1)
        self.assertEqual(sum(sum(hours.values()) for hours in data["heatmap"].values()), 2)

    def test_all_invalid_dates_return_empty_charts(self):
        for value in ("Unknown", None, "", "bad-date"):
            self.add_commit(value)

        data = self.read_profile()

        self.assertEqual(data["repositories"][0]["monthly_commits"], [])
        self.assertEqual(data["repositories"][0]["user_commit_count"], 4)
        self.assertEqual(data["monthly_commits"]["total_count"], [
            ["2026-03", 0], ["2026-04", 0], ["2026-05", 0],
            ["2026-06", 0], ["2026-07", 0], ["2026-08", 0],
        ])
        self.assertEqual(sum(sum(hours.values()) for hours in data["heatmap"].values()), 0)

    def test_repository_window_uses_latest_valid_user_commit(self):
        for value in ("2020-08-01T10:00:00Z", "2020-07-01T10:00:00Z",
                      "2018-01-01T00:00:00Z", "Unknown"):
            self.add_commit(value)
        self.add_commit("2026-08-25T00:00:00Z", author="another-user")

        data = self.read_profile()

        self.assertEqual(data["monthly_commits"]["total_count"], [
            ["2020-03", 0], ["2020-04", 0], ["2020-05", 0],
            ["2020-06", 0], ["2020-07", 1], ["2020-08", 1],
        ])
        self.assertEqual(data["repositories"][0]["monthly_commits"],
                         [["2020-07", 1], ["2020-08", 1]])

    def test_contributor_repository_and_repository_without_commits(self):
        contributed_repo = Repository.objects.create(
            id="contributed-repo", name="Contributed Repo", owner_github_id="another-user",
            contributors="test-user", star_count=0, fork_count=0,
        )
        self.add_commit("Unknown", repo=contributed_repo)
        self.add_commit("2026-08-25T10:00:00Z", repo=contributed_repo)

        data = self.read_profile()
        repos = {repo["id"]: repo for repo in data["repositories"]}

        self.assertEqual(repos[self.repo.id]["monthly_commits"], [])
        self.assertEqual(repos[contributed_repo.id]["monthly_commits"], [["2026-08", 1]])
        self.assertEqual(data["total_stats"]["contributor_total_commits"], 2)
        self.assertEqual(data["monthly_commits"]["total_count"], [
            ["2026-03", 0], ["2026-04", 0], ["2026-05", 0],
            ["2026-06", 0], ["2026-07", 0], ["2026-08", 1],
        ])


class RepositorySummaryLiveReportTests(TestCase):
    def test_course_link_keeps_repository_when_public_listing_drops_it(self):
        repo = Repository.objects.create(
            id="course-retained", owner_github_id="owner", name="Course Repo",
            summary='{"project_summary": {}}',
        )
        course = Course.objects.create(
            course_id="COSE100", year=2026, semester=2, name="Course", prof="Professor",
        )
        Course_project.objects.create(
            course=course, course_year=2026, course_semester=2,
            repo=repo, repo_name=repo.name,
        )

        result = remove_repository("owner", Repository(id=repo.id))

        self.assertEqual(result["status"], "Skipped")
        repo.refresh_from_db()
        self.assertEqual(repo.github_availability, "not_listed")
        self.assertEqual(repo.summary, '{"project_summary": {}}')

    def test_source_fingerprint_ignores_crawl_time_but_tracks_changes(self):
        repo = Repository.objects.create(
            id="fingerprint-repo", owner_github_id="owner", name="repo",
            description="Original", language_bytes={"Python": 10},
            updated_at="2026-09-01T00:00:00Z", pushed_at="2026-09-01T00:00:00Z",
        )
        original = repository_summary_fingerprint(repo, RepoSummaryAnalyzer.MODEL)
        repo.crawled_date = "2026-09-18T00:00:00Z"
        self.assertEqual(repository_summary_fingerprint(repo, RepoSummaryAnalyzer.MODEL), original)
        repo.description = "Changed"
        self.assertNotEqual(repository_summary_fingerprint(repo, RepoSummaryAnalyzer.MODEL), original)

    def test_summary_status_distinguishes_missing_legacy_stale_and_limited(self):
        repo = Repository.objects.create(
            id="status-repo", owner_github_id="owner", name="repo",
        )
        self.assertEqual(repository_summary_status(repo), "missing")
        repo.summary = '{"project_summary": {}}'
        self.assertEqual(repository_summary_status(repo), "legacy")
        repo.summary_source_fingerprint = repository_summary_fingerprint(repo, RepoSummaryAnalyzer.MODEL)
        repo.summary_source_kind = "database"
        self.assertEqual(repository_summary_status(repo), "limited")
        repo.pushed_at = "2026-09-18T00:00:00Z"
        self.assertEqual(repository_summary_status(repo), "stale")

    def test_github_fetch_failure_does_not_call_openai(self):
        analyzer = RepoSummaryAnalyzer.__new__(RepoSummaryAnalyzer)
        analyzer._fetch_summary_context = Mock(return_value={
            "error": "GitHub REST crawler request failed: 401",
            "http_status": 401,
        })
        analyzer.openai_client = SimpleNamespace(responses=SimpleNamespace(create=Mock()))

        result = analyzer.analyze_repository({
            "owner_github_id": "owner", "name": "repo", "description": "",
            "language_bytes": {},
        })

        self.assertFalse(result["success"])
        self.assertIn("401", result["error"])
        analyzer.openai_client.responses.create.assert_not_called()

    def test_unavailable_github_uses_saved_description_only(self):
        analyzer = RepoSummaryAnalyzer.__new__(RepoSummaryAnalyzer)
        analyzer._fetch_summary_context = Mock(return_value={
            "error": "GitHub REST crawler request failed: 404", "http_status": 404,
        })
        analyzer._analyze_with_llm = Mock(return_value={
            "success": True,
            "structured_summary": {"project_summary": {}, "user_content": {}},
            "usage": analyzer.empty_usage(), "cost_usd": 0.0,
        })

        result = analyzer.analyze_repository({
            "owner_github_id": "owner", "name": "repo", "description": "Known purpose",
            "language_bytes": {"Python": 100},
        })

        self.assertTrue(result["success"])
        self.assertEqual(result["source_kind"], "database")
        self.assertEqual(analyzer._analyze_with_llm.call_args.args[1], {})

    def test_unavailable_github_without_description_is_insufficient(self):
        analyzer = RepoSummaryAnalyzer.__new__(RepoSummaryAnalyzer)
        analyzer._fetch_summary_context = Mock(return_value={
            "error": "GitHub REST crawler request failed: 404", "http_status": 404,
        })
        analyzer._analyze_with_llm = Mock()
        result = analyzer.analyze_repository({
            "owner_github_id": "owner", "name": "repo", "description": None,
            "language_bytes": {"Python": 100},
        })
        self.assertFalse(result["success"])
        self.assertIn("insufficient_data", result["error"])
        analyzer._analyze_with_llm.assert_not_called()

    def test_empty_tech_stack_is_valid_when_evidence_is_missing(self):
        RepoSummaryAnalyzer.validate_structured_summary({
            "project_summary": {
                "primary_language": "Unknown", "purpose": "Purpose unclear",
                "tech_stack": [], "key_functionalities": [], "scale": "small",
            },
            "user_content": {"description": "Evidence is limited."},
        })

    def test_prompt_uses_saved_languages(self):
        analyzer = RepoSummaryAnalyzer.__new__(RepoSummaryAnalyzer)
        prompt = analyzer._create_analysis_prompt({
            "owner_github_id": "owner", "name": "repo", "description": "Known purpose",
            "language_bytes": {"Python": 100},
        }, {}, "", {})
        self.assertIn("'Python': 100", prompt)
        self.assertIn("저장된 DB 정보만 사용", prompt)

    def test_summary_context_uses_fastapi_crawler_without_github_header(self):
        analyzer = RepoSummaryAnalyzer.__new__(RepoSummaryAnalyzer)
        response = Mock(status_code=200)
        response.json.return_value = {
            "files": [{"path": "app.py", "size": 10}],
            "directories": [],
            "readme_content": "README",
            "key_files": {},
        }

        with patch("repo.api.views.requests.get", return_value=response) as get:
            context = analyzer._fetch_summary_context("owner", "repo")

        self.assertEqual(context["readme_content"], "README")
        get.assert_called_once_with(
            f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/summary-context",
            params={"github_id": "owner", "repo_name": "repo"},
            timeout=120,
        )

    def test_llm_request_uses_gpt_5_4_nano_and_returns_usage(self):
        response = SimpleNamespace(
            id="response-test",
            model="gpt-5.4-nano-2026-03-17",
            output_text=json.dumps({
                "project_summary": {
                    "primary_language": "Python",
                    "purpose": "Test purpose",
                    "tech_stack": ["Python"],
                    "key_functionalities": ["Test feature"],
                    "scale": "small",
                },
                "user_content": {"description": "Test description"},
            }),
            usage=SimpleNamespace(
                input_tokens=100,
                input_tokens_details=SimpleNamespace(cached_tokens=0),
                output_tokens=50,
                output_tokens_details=SimpleNamespace(reasoning_tokens=10),
                total_tokens=150,
            ),
        )
        analyzer = RepoSummaryAnalyzer.__new__(RepoSummaryAnalyzer)
        analyzer.openai_client = SimpleNamespace(
            responses=SimpleNamespace(create=Mock(return_value=response))
        )

        result = analyzer._analyze_with_llm(
            {"owner_github_id": "owner", "name": "repo", "description": ""},
            {},
            "README",
            {},
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["response_id"], "response-test")
        self.assertEqual(result["response_model"], "gpt-5.4-nano-2026-03-17")
        self.assertEqual(result["usage"]["reasoning_tokens"], 10)
        analyzer.openai_client.responses.create.assert_called_once_with(
            model="gpt-5.4-nano",
            input=analyzer._create_analysis_prompt(
                {"owner_github_id": "owner", "name": "repo", "description": ""},
                {},
                "README",
                {},
            ),
            reasoning={"effort": "low"},
            text=analyzer.SUMMARY_TEXT_CONFIG,
            max_output_tokens=1200,
            store=False,
        )

    def test_usage_and_cost_include_cached_and_reasoning_details(self):
        response = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=1200,
                input_tokens_details=SimpleNamespace(cached_tokens=200),
                output_tokens=400,
                output_tokens_details=SimpleNamespace(reasoning_tokens=100),
                total_tokens=1600,
            )
        )

        usage = RepoSummaryAnalyzer.usage_from_response(response)

        self.assertEqual(usage, {
            "input_tokens": 1200,
            "cached_input_tokens": 200,
            "output_tokens": 400,
            "reasoning_tokens": 100,
            "total_tokens": 1600,
        })
        self.assertEqual(RepoSummaryAnalyzer.calculate_cost_usd(usage), 0.000704)

    def test_llm_rejects_incomplete_summary_instead_of_marking_success(self):
        response = SimpleNamespace(
            id="response-invalid",
            model="gpt-5.4-nano",
            output_text=json.dumps({"project_summary": {"purpose": "Only one field"}}),
            usage=None,
        )
        analyzer = RepoSummaryAnalyzer.__new__(RepoSummaryAnalyzer)
        analyzer.openai_client = SimpleNamespace(
            responses=SimpleNamespace(create=Mock(return_value=response))
        )

        result = analyzer._analyze_with_llm(
            {"owner_github_id": "owner", "name": "repo", "description": ""},
            {}, "README", {},
        )

        self.assertFalse(result["success"])
        self.assertIn("unexpected top-level structure", result["error"])

    def test_live_report_samples_missing_repositories_without_saving(self):
        for index in range(3):
            Repository.objects.create(
                id=f"summary-missing-{index}",
                name=f"Summary Missing {index}",
                owner_github_id=f"owner-{index}",
                star_count=0,
                fork_count=0,
            )
        Repository.objects.create(
            id="summary-existing",
            name="Summary Existing",
            owner_github_id="existing-owner",
            summary='{"project_summary": {}}',
            star_count=0,
            fork_count=0,
        )

        class FakeAnalyzer:
            MODEL = RepoSummaryAnalyzer.MODEL
            PRICING_VERSION = RepoSummaryAnalyzer.PRICING_VERSION
            INPUT_USD_PER_MILLION = RepoSummaryAnalyzer.INPUT_USD_PER_MILLION
            CACHED_INPUT_USD_PER_MILLION = RepoSummaryAnalyzer.CACHED_INPUT_USD_PER_MILLION
            OUTPUT_USD_PER_MILLION = RepoSummaryAnalyzer.OUTPUT_USD_PER_MILLION
            empty_usage = RepoSummaryAnalyzer.empty_usage

            def analyze_repository(self, repo_data):
                return {
                    "success": True,
                    "structured_summary": {"project_summary": {"purpose": repo_data["name"]}},
                    "usage": {
                        "input_tokens": 100,
                        "cached_input_tokens": 0,
                        "output_tokens": 50,
                        "reasoning_tokens": 10,
                        "total_tokens": 150,
                    },
                    "cost_usd": 0.0000825,
                    "response_id": f"response-{repo_data['id']}",
                    "response_model": RepoSummaryAnalyzer.MODEL,
                }

        request = APIRequestFactory().post(
            "/api/repo/generate_repo_summary/",
            {
                "filter": "missing_summary",
                "sample_size": 2,
                "sample_seed": 7,
                "test_report": True,
                "save": False,
            },
            format="json",
            HTTP_X_KUOSS_SUMMARY_TOKEN="test-openai-key",
        )
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-openai-key"}), patch(
            "repo.api.views.RepoSummaryAnalyzer", FakeAnalyzer
        ):
            response = GenerateRepoSummaryAPIView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["test_report"])
        self.assertFalse(response.data["summaries_saved"])
        self.assertEqual(response.data["eligible_repository_count"], 3)
        self.assertEqual(response.data["sample_repository_count"], 2)
        self.assertEqual(response.data["processed"], 2)
        self.assertEqual(response.data["saved"], 0)
        self.assertEqual(response.data["usage"]["input_tokens"], 200)
        self.assertEqual(response.data["actual_cost_usd"], 0.000165)
        self.assertEqual(response.data["projected_eligible_cost_usd"], 0.0002475)
        self.assertFalse(
            Repository.objects.filter(
                id__startswith="summary-missing-", summary__isnull=False
            ).exists()
        )

    def test_live_report_rejects_missing_authorization_token(self):
        request = APIRequestFactory().post(
            "/api/repo/generate_repo_summary/",
            {"test_report": True, "sample_size": 1},
            format="json",
        )
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-openai-key"}):
            response = GenerateRepoSummaryAPIView.as_view()(request)

        self.assertEqual(response.status_code, 403)

    def test_needs_refresh_saves_only_missing_or_changed_sources(self):
        ready = Repository.objects.create(id="c-ready", name="Ready", owner_github_id="owner")
        ready.summary = '{"old": true}'
        ready.summary_source_fingerprint = repository_summary_fingerprint(ready, RepoSummaryAnalyzer.MODEL)
        ready.save(update_fields=["summary", "summary_source_fingerprint"])
        stale = Repository.objects.create(id="b-stale", name="Stale", owner_github_id="owner")
        stale.summary = '{"old": true}'
        stale.summary_source_fingerprint = "old-fingerprint"
        stale.save(update_fields=["summary", "summary_source_fingerprint"])
        missing = Repository.objects.create(id="a-missing", name="Missing", owner_github_id="owner")

        class FakeAnalyzer:
            MODEL = RepoSummaryAnalyzer.MODEL
            PRICING_VERSION = RepoSummaryAnalyzer.PRICING_VERSION
            INPUT_USD_PER_MILLION = RepoSummaryAnalyzer.INPUT_USD_PER_MILLION
            CACHED_INPUT_USD_PER_MILLION = RepoSummaryAnalyzer.CACHED_INPUT_USD_PER_MILLION
            OUTPUT_USD_PER_MILLION = RepoSummaryAnalyzer.OUTPUT_USD_PER_MILLION
            empty_usage = RepoSummaryAnalyzer.empty_usage

            def analyze_repository(self, repo_data):
                return {
                    "success": True,
                    "structured_summary": {"project_summary": {"purpose": repo_data["name"]}},
                    "source_kind": "database", "usage": self.empty_usage(), "cost_usd": 0.0,
                }

        request = APIRequestFactory().post(
            "/api/repo/generate_repo_summary/",
            {"filter": "needs_refresh", "sample_size": 2, "save": True},
            format="json", HTTP_X_KUOSS_SUMMARY_TOKEN="test-openai-key",
        )
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-openai-key"}), patch(
            "repo.api.views.RepoSummaryAnalyzer", FakeAnalyzer
        ):
            response = GenerateRepoSummaryAPIView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["eligible_repository_count"], 2)
        self.assertEqual(response.data["saved"], 2)
        ready.refresh_from_db()
        stale.refresh_from_db()
        missing.refresh_from_db()
        self.assertEqual(ready.summary, '{"old": true}')
        for repo in (stale, missing):
            self.assertEqual(repo.summary_source_fingerprint,
                             repository_summary_fingerprint(repo, RepoSummaryAnalyzer.MODEL))
            self.assertIsNotNone(repo.summary_generated_at)
            self.assertEqual(repo.summary_source_kind, "database")
            self.assertIsNone(repo.summary_last_error)

    def test_failed_refresh_preserves_previous_summary(self):
        repo = Repository.objects.create(
            id="stale-failure", name="Failure", owner_github_id="owner",
            summary='{"old": true}', summary_source_fingerprint="old-fingerprint",
        )

        class FailingAnalyzer:
            MODEL = RepoSummaryAnalyzer.MODEL
            PRICING_VERSION = RepoSummaryAnalyzer.PRICING_VERSION
            INPUT_USD_PER_MILLION = RepoSummaryAnalyzer.INPUT_USD_PER_MILLION
            CACHED_INPUT_USD_PER_MILLION = RepoSummaryAnalyzer.CACHED_INPUT_USD_PER_MILLION
            OUTPUT_USD_PER_MILLION = RepoSummaryAnalyzer.OUTPUT_USD_PER_MILLION
            empty_usage = RepoSummaryAnalyzer.empty_usage

            def analyze_repository(self, repo_data):
                return {
                    "success": False, "structured_summary": None,
                    "error": "GitHub API 요청 실패: 401",
                    "usage": self.empty_usage(), "cost_usd": 0.0,
                }

        request = APIRequestFactory().post(
            "/api/repo/generate_repo_summary/",
            {"filter": "needs_refresh", "sample_size": 1, "save": True},
            format="json", HTTP_X_KUOSS_SUMMARY_TOKEN="test-openai-key",
        )
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-openai-key"}), patch(
            "repo.api.views.RepoSummaryAnalyzer", FailingAnalyzer
        ):
            response = GenerateRepoSummaryAPIView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["saved"], 0)
        repo.refresh_from_db()
        self.assertEqual(repo.summary, '{"old": true}')
        self.assertEqual(repo.summary_source_fingerprint, "old-fingerprint")
        self.assertIsNotNone(repo.summary_last_attempt_at)
        self.assertIn("401", repo.summary_last_error)

    def test_refresh_priority_is_missing_legacy_stale_then_failed(self):
        missing = Repository.objects.create(
            id="z-missing", name="Missing", owner_github_id="owner",
        )
        legacy = Repository.objects.create(
            id="a-legacy", name="Legacy", owner_github_id="owner",
            summary='{"old": true}',
        )
        stale = Repository.objects.create(
            id="b-stale", name="Stale", owner_github_id="owner",
            summary='{"old": true}', summary_source_fingerprint="old-fingerprint",
            summary_generated_at=timezone_now() - timedelta(days=2),
        )
        failed = Repository.objects.create(
            id="a-failed", name="Failed", owner_github_id="owner",
            summary_last_error="GitHub API request failed",
            summary_last_attempt_at=timezone_now() - timedelta(days=1),
        )

        ordered = sorted(
            [failed, stale, legacy, missing],
            key=lambda repo: repository_summary_refresh_priority(
                repo, RepoSummaryAnalyzer.MODEL
            ),
        )

        self.assertEqual(
            [repo.id for repo in ordered],
            ["z-missing", "a-legacy", "b-stale", "a-failed"],
        )

    def test_attempt_cutoff_prevents_same_run_failure_retry(self):
        repo = Repository.objects.create(
            id="one-attempt", name="One Attempt", owner_github_id="owner",
        )
        attempt_before = timezone_now().timestamp()

        class FailingAnalyzer:
            MODEL = RepoSummaryAnalyzer.MODEL
            PRICING_VERSION = RepoSummaryAnalyzer.PRICING_VERSION
            INPUT_USD_PER_MILLION = RepoSummaryAnalyzer.INPUT_USD_PER_MILLION
            CACHED_INPUT_USD_PER_MILLION = RepoSummaryAnalyzer.CACHED_INPUT_USD_PER_MILLION
            OUTPUT_USD_PER_MILLION = RepoSummaryAnalyzer.OUTPUT_USD_PER_MILLION
            empty_usage = RepoSummaryAnalyzer.empty_usage

            def analyze_repository(self, repo_data):
                return {
                    "success": False, "structured_summary": None,
                    "error": "temporary failure",
                    "usage": self.empty_usage(), "cost_usd": 0.0,
                }

        def make_request():
            return APIRequestFactory().post(
                "/api/repo/generate_repo_summary/",
                {
                    "filter": "needs_refresh", "sample_size": 500,
                    "save": True, "attempt_before": attempt_before,
                },
                format="json", HTTP_X_KUOSS_SUMMARY_TOKEN="test-openai-key",
            )

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-openai-key"}), patch(
            "repo.api.views.RepoSummaryAnalyzer", FailingAnalyzer
        ):
            first = GenerateRepoSummaryAPIView.as_view()(make_request())
            second = GenerateRepoSummaryAPIView.as_view()(make_request())

        self.assertEqual(first.data["sample_repository_count"], 1)
        self.assertEqual(first.data["failed"], 1)
        self.assertEqual(second.data["eligible_repository_count"], 1)
        self.assertEqual(second.data["selectable_repository_count"], 0)
        self.assertEqual(second.data["sample_repository_count"], 0)
        repo.refresh_from_db()
        self.assertIsNone(repo.summary)
        self.assertEqual(repo.summary_last_error, "temporary failure")
