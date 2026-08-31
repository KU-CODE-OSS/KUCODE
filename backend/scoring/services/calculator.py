import math
import statistics


LANGUAGE_COEFFICIENTS = {
    "javascript": 1.00,
    "typescript": 1.00,
    "html": 1.00,
    "css": 1.00,
    "vue": 1.00,
    "java": 1.10,
    "kotlin": 1.10,
    "php": 1.10,
    "sql": 1.10,
    "c#": 1.10,
    "r": 1.15,
    "julia": 1.15,
    "python": 1.20,
    "jupyter notebook": 1.20,
    "c": 1.30,
    "c++": 1.30,
    "rust": 1.30,
}


def clamp(value, minimum=0.0, maximum=100.0):
    return max(minimum, min(maximum, float(value)))


def percentile(values, quantile):
    ordered = sorted(float(value) for value in values if value is not None)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def normalize_log(value, reference):
    value = max(0.0, float(value or 0))
    reference = float(reference or 0)
    if value == 0 or reference <= 0:
        return 0.0
    return clamp(math.log1p(value) / math.log1p(reference) * 100.0)


def weighted_available(components):
    available = [(float(value), float(weight)) for value, weight in components if value is not None]
    weight_sum = sum(weight for _, weight in available)
    if weight_sum <= 0:
        return None
    return clamp(sum(value * weight for value, weight in available) / weight_sum)


def churn_rate(added_lines, deleted_lines):
    added_lines = max(0, int(added_lines or 0))
    deleted_lines = max(0, int(deleted_lines or 0))
    total = added_lines + deleted_lines
    return None if total == 0 else deleted_lines / total


def churn_score(rate, mean=0.20, stddev=0.15):
    if rate is None:
        return None
    stddev = float(stddev or 0)
    if stddev <= 0:
        raise ValueError("churn stddev must be positive")
    exponent = -((float(rate) - float(mean)) ** 2) / (2 * stddev**2)
    return clamp(100.0 * math.exp(exponent))


def productivity_score(
    commit_count,
    added_lines,
    deleted_lines,
    commit_reference,
    line_reference,
    churn_mean=0.20,
    churn_stddev=0.15,
):
    commit_component = normalize_log(commit_count, commit_reference)
    line_component = normalize_log(
        max(0, int(added_lines or 0)) + max(0, int(deleted_lines or 0)),
        line_reference,
    )
    rate = churn_rate(added_lines, deleted_lines)
    churn_component = churn_score(rate, churn_mean, churn_stddev)
    score = weighted_available(
        [(commit_component, 0.4), (line_component, 0.4), (churn_component, 0.2)]
    )
    return score or 0.0, {
        "commit": commit_component,
        "changed_lines": line_component,
        "churn_rate": rate,
        "churn": churn_component,
    }


def gini_coefficient(values):
    values = [max(0.0, float(value or 0)) for value in values]
    if not values or sum(values) == 0:
        return None
    values.sort()
    count = len(values)
    weighted_sum = sum((index + 1) * value for index, value in enumerate(values))
    return (2 * weighted_sum) / (count * sum(values)) - (count + 1) / count


def collaboration_score(
    merged_pr_count,
    unmerged_pr_count,
    contributor_contributions,
    issue_count,
    pr_reference,
    team_size_reference=4,
    issue_cap=5,
):
    pr_weighted = max(0, merged_pr_count or 0) + 0.4 * max(0, unmerged_pr_count or 0)
    pr_component = normalize_log(pr_weighted, pr_reference)

    contribution_values = [value for value in contributor_contributions if (value or 0) > 0]
    contributor_count = len(contribution_values)
    contributor_count_component = clamp(
        contributor_count / max(1, int(team_size_reference or 1)) * 100.0
    )
    gini = gini_coefficient(contribution_values)
    equality_component = None if gini is None else clamp((1.0 - gini) * 100.0)
    contributor_component = weighted_available(
        [(contributor_count_component, 0.5), (equality_component, 0.5)]
    )
    if contributor_component is None:
        contributor_component = 0.0

    issue_component = clamp(max(0, issue_count or 0) / max(1, issue_cap) * 100.0)
    base_score = weighted_available(
        [(pr_component, 0.4), (contributor_component, 0.4), (issue_component, 0.2)]
    ) or 0.0
    issue_bonus_rate = min(0.20, issue_component / 100.0 * 0.20)
    score = clamp(base_score + base_score * issue_bonus_rate)
    return score, {
        "pr_weighted_count": pr_weighted,
        "pr": pr_component,
        "contributor_count": contributor_count,
        "contributor_count_score": contributor_count_component,
        "gini": gini,
        "contribution_equality": equality_component,
        "contributors": contributor_component,
        "issues": issue_component,
        "issue_bonus": base_score * issue_bonus_rate,
    }


def issue_resolution_score(average_days, reference_days):
    if average_days is None or reference_days is None:
        return None
    average_days = max(0.0, float(average_days))
    reference_days = max(0.0, float(reference_days))
    if average_days == 0:
        return 100.0
    if reference_days == 0:
        return None
    return clamp(100.0 * reference_days / (reference_days + average_days))


def pr_merge_score(merged_count, closed_unmerged_count):
    denominator = max(0, merged_count or 0) + max(0, closed_unmerged_count or 0)
    if denominator == 0:
        return None
    return clamp(max(0, merged_count or 0) / denominator * 100.0)


def cicd_score(workflow_count, workflow_commit_count, has_snapshot=True, workflow_reference=2, update_reference=3):
    if not has_snapshot:
        return None
    workflow_count = max(0, workflow_count or 0)
    workflow_commit_count = max(0, workflow_commit_count or 0)
    exists = 1.0 if workflow_count > 0 else 0.0
    return clamp(
        100.0
        * (
            0.5 * exists
            + 0.3 * min(1.0, workflow_count / max(1, workflow_reference))
            + 0.2 * min(1.0, workflow_commit_count / max(1, update_reference))
        )
    )


def problem_solving_score(
    average_issue_resolution_days,
    issue_resolution_reference_days,
    merged_pr_count,
    closed_unmerged_pr_count,
    workflow_count,
    workflow_commit_count,
    has_snapshot=True,
):
    issue_component = issue_resolution_score(
        average_issue_resolution_days, issue_resolution_reference_days
    )
    pr_component = pr_merge_score(merged_pr_count, closed_unmerged_pr_count)
    cicd_component = cicd_score(
        workflow_count, workflow_commit_count, has_snapshot=has_snapshot
    )
    score = weighted_available(
        [(issue_component, 0.30), (pr_component, 0.30), (cicd_component, 0.25)]
    )
    return score, {
        "issue_resolution": issue_component,
        "pr_merge": pr_component,
        "cicd": cicd_component,
        "repeated_file": None,
    }


def language_difficulty_multiplier(language_bytes, coefficients=None):
    coefficients = coefficients or LANGUAGE_COEFFICIENTS
    if not isinstance(language_bytes, dict):
        return 1.0, {"language_coefficients": {}, "unmapped_languages": []}
    positive = {
        str(language): max(0.0, float(byte_count or 0))
        for language, byte_count in language_bytes.items()
        if float(byte_count or 0) > 0
    }
    total = sum(positive.values())
    if total <= 0:
        return 1.0, {"language_coefficients": {}, "unmapped_languages": []}

    details = {}
    unmapped = []
    weighted = 0.0
    for language, byte_count in positive.items():
        coefficient = float(coefficients.get(language.lower(), 1.0))
        ratio = byte_count / total
        weighted += ratio * coefficient
        details[language] = {"ratio": ratio, "coefficient": coefficient}
        if language.lower() not in coefficients:
            unmapped.append(language)
    return clamp(weighted, 0.90, 1.50), {
        "language_coefficients": details,
        "unmapped_languages": unmapped,
    }


def project_score(productivity, collaboration, problem_solving, difficulty_multiplier):
    components = [
        (clamp(productivity) * difficulty_multiplier, 0.45),
        (clamp(collaboration) * difficulty_multiplier, 0.35),
        (problem_solving, 0.20),
    ]
    return weighted_available(components) or 0.0


def personal_multiplier(contribution_share, team_size):
    team_size = max(1, int(team_size or 1))
    contribution_share = clamp(contribution_share, 0.0, 1.0)
    return clamp(contribution_share / (1.0 / team_size), 0.0, 1.30)


def activity_score(commit_count, changed_lines):
    return math.log1p(max(0, commit_count or 0)) + math.log1p(max(0, changed_lines or 0))


def collaboration_stability(scores):
    scores = [float(score) for score in scores if score is not None]
    if not scores:
        return None
    deviation = statistics.pstdev(scores) if len(scores) > 1 else 0.0
    return clamp(100.0 - deviation)


def difficulty_weighted_average(score_and_multiplier):
    values = [
        (float(score), float(multiplier))
        for score, multiplier in score_and_multiplier
        if score is not None and multiplier is not None and multiplier > 0
    ]
    denominator = sum(multiplier for _, multiplier in values)
    if denominator <= 0:
        return None
    return clamp(sum(score * multiplier for score, multiplier in values) / denominator)


def prototype_student_overall(project_scores, collaboration_scores):
    project_scores = [float(score) for score in project_scores if score is not None]
    if not project_scores:
        return 0.0, {"project_average": 0.0, "collaboration_stability": None}
    project_average = statistics.fmean(project_scores)
    stability = collaboration_stability(collaboration_scores)
    # Growth is intentionally excluded. Normalize the remaining 60:15 weights to 80:20.
    overall = weighted_available([(project_average, 0.60), (stability, 0.15)]) or 0.0
    return overall, {
        "project_average": project_average,
        "collaboration_stability": stability,
        "effective_weights": {"project_average": 0.80, "collaboration_stability": 0.20},
    }


def cohort_parameters(repository_metrics):
    commit_values = [row.get("commit_count", 0) for row in repository_metrics]
    line_values = [row.get("changed_lines", 0) for row in repository_metrics]
    pr_values = [row.get("pr_weighted_count", 0) for row in repository_metrics]
    churn_values = [row.get("churn_rate") for row in repository_metrics if row.get("churn_rate") is not None]
    issue_days = [
        value
        for row in repository_metrics
        for value in row.get("closed_issue_resolution_days", [])
        if value is not None
    ]
    churn_mean = statistics.fmean(churn_values) if churn_values else 0.20
    churn_stddev = statistics.pstdev(churn_values) if len(churn_values) > 1 else 0.15
    if churn_stddev <= 0:
        churn_stddev = 0.15
    return {
        "commit_p95": percentile(commit_values, 0.95),
        "changed_lines_p95": percentile(line_values, 0.95),
        "pr_weighted_p95": percentile(pr_values, 0.95),
        "churn_mean": churn_mean,
        "churn_stddev": churn_stddev,
        "issue_resolution_median_days": statistics.median(issue_days) if issue_days else None,
    }
