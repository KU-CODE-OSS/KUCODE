import json
from datetime import datetime
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from account.models import Student
from repo.api.views import repo_account_read_db
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

        self.assertEqual(data["monthly_commits"]["total_count"], [["2026-08", 2]])
        self.assertEqual(data["monthly_commits"]["added_lines"], [["2026-08", 6]])
        self.assertEqual(data["monthly_commits"]["deleted_lines"], [["2026-08", 4]])
        self.assertEqual(data["monthly_commits"]["changed_lines"], [["2026-08", 10]])
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
        self.assertEqual(data["monthly_commits"]["total_count"], [])
        self.assertEqual(sum(sum(hours.values()) for hours in data["heatmap"].values()), 0)

    def test_repository_window_uses_latest_valid_user_commit(self):
        for value in ("2020-08-01T10:00:00Z", "2020-07-01T10:00:00Z",
                      "2018-01-01T00:00:00Z", "Unknown"):
            self.add_commit(value)
        self.add_commit("2026-08-25T00:00:00Z", author="another-user")

        data = self.read_profile()

        self.assertEqual(data["monthly_commits"]["total_count"], [])
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
