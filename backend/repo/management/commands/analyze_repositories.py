# repo/management/commands/analyze_repositories.py

from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json


class Command(BaseCommand):
    help = "레포지토리 배치 분석을 실행합니다"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="한 번에 처리할 레포지토리 수 (기본값: 50)",
        )
        parser.add_argument(
            "--filter",
            type=str,
            default="missing_summary",
            choices=["missing_summary", "outdated", "all"],
            help="필터 조건 (기본값: missing_summary)",
        )
        parser.add_argument(
            "--student-ids",
            type=str,
            help="특정 학생 ID들 (쉼표로 구분, 예: 1,2,3,4,5)",
        )
        parser.add_argument(
            "--host",
            type=str,
            default="http://localhost:8000",
            help="API 서버 호스트 (기본값: http://localhost:8000)",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        filter_type = options["filter"]
        student_ids_str = options["student_ids"]
        host = options["host"]

        # 학생 ID 파싱
        student_ids = []
        if student_ids_str:
            try:
                student_ids = [int(id.strip()) for id in student_ids_str.split(",")]
            except ValueError:
                self.stdout.write(
                    self.style.ERROR("학생 ID는 숫자여야 합니다. 예: 1,2,3,4,5")
                )
                return

        # API 요청 데이터 구성
        request_data = {"filter": filter_type, "batch_size": batch_size}

        if student_ids:
            request_data["student_ids"] = student_ids

        # API 호출
        api_url = f"{host}/api/repo/generate_repo_summary_batch/"

        self.stdout.write(f"배치 분석 시작...")
        self.stdout.write(f"API URL: {api_url}")
        self.stdout.write(f"요청 데이터: {json.dumps(request_data, indent=2)}")

        try:
            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                json=request_data,
                timeout=3600,  # 1시간 타임아웃
            )

            if response.status_code == 200:
                result = response.json()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"배치 분석 완료\n"
                        f"  - 성공: {result.get('processed', 0)}개\n"
                        f"  - 실패: {result.get('failed', 0)}개\n"
                        f"  - 전체: {result.get('total_requested', 0)}개"
                    )
                )

                # 실패한 레포지토리 출력
                failed_repos = result.get("failed_repositories", [])
                if failed_repos:
                    self.stdout.write(
                        self.style.WARNING(
                            f"\n실패한 레포지토리 ({len(failed_repos)}개):"
                        )
                    )
                    for repo in failed_repos[:5]:  # 최대 5개만 출력
                        self.stdout.write(f"  - {repo['repository']}: {repo['error']}")

                    if len(failed_repos) > 5:
                        self.stdout.write(f"  ... 및 {len(failed_repos) - 5}개 더")

            else:
                error_data = (
                    response.json()
                    if response.headers.get("content-type") == "application/json"
                    else response.text
                )
                self.stdout.write(
                    self.style.ERROR(
                        f"API 호출 실패 (HTTP {response.status_code}):\n{error_data}"
                    )
                )

        except requests.exceptions.Timeout:
            self.stdout.write(self.style.ERROR("요청 타임아웃 (1시간 초과)"))
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.ERROR(f"서버 연결 실패: {api_url}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"예기치 못한 오류: {str(e)}"))
