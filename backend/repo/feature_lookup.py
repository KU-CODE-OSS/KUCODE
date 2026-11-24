"""Read-only lookup over the feature-analysis snapshot."""
import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote, urlsplit


DEFAULT_DICTIONARY = 'spec_hierarchical'
DICTIONARIES = (
    DEFAULT_DICTIONARY,
    'spec_umap_hdbscan',
    'code_hierarchical',
    'code_umap_hdbscan',
)


class LookupFailure(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status = status
        self.code = code


def github_slug(value):
    """Build a case-insensitive lookup key, preserving spelling for source links."""
    if not value:
        return None
    try:
        url = urlsplit(value.strip())
    except ValueError:
        return None
    if (
        url.scheme not in ('http', 'https')
        or url.netloc.lower() != 'github.com'
        or url.query or url.fragment
    ):
        return None
    slug = url.path.strip('/')
    if slug.lower().endswith('.git'):
        slug = slug[:-4]
    if not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', slug):
        return None
    if slug.split('/')[1] in ('.', '..'):
        return None
    return slug


@lru_cache(maxsize=2)
def load_snapshot(path):
    with Path(path).open(encoding='utf-8') as snapshot:
        return FeatureSnapshot(json.load(snapshot))


class FeatureSnapshot:
    def __init__(self, data):
        if data['schemaVersion'] != 'feature-api-snapshot-v1':
            raise ValueError('Unsupported feature snapshot schema')
        self.run = data['run']
        self.units = data['units']
        self.repositories = data['repositories']
        self.students = data['students']
        self.dictionaries = data['dictionaries']
        self.repository_aliases = defaultdict(set)
        self.contributions = defaultdict(dict)
        self.assignments = {}
        self.source_links = {}

        for repo_id, repo in self.repositories.items():
            for url in [repo['repoUrl'], *repo['aliases']]:
                slug = github_slug(url)
                if slug:
                    self.repository_aliases[slug.casefold()].add(repo_id)
            for unit_id in repo['unitIds']:
                if self.units[unit_id]['source']['codebaseId'] != repo_id:
                    raise ValueError('Feature snapshot repository membership is inconsistent')

        for unit_id, unit in self.units.items():
            source = unit['source']
            slug = github_slug(source['repoUrl'])
            if not slug or not re.fullmatch(r'[0-9a-fA-F]{40}', source['commit']):
                raise ValueError('Invalid source repository or commit in feature snapshot')
            if not 1 <= source['startLine'] <= source['endLine']:
                raise ValueError('Invalid source line range in feature snapshot')
            self.source_links[unit_id] = (
                f'https://github.com/{slug}/blob/{source["commit"]}/'
                f'{quote(source["path"], safe="/")}#L{source["startLine"]}-L{source["endLine"]}'
            )
            for contributor in unit['contributors']:
                share = contributor['lineShare']
                if share > 0:
                    for student_id in set(contributor['studentIds']):
                        shares = self.contributions[student_id]
                        shares[unit_id] = min(1.0, shares.get(unit_id, 0) + share)

        for name, dictionary in self.dictionaries.items():
            assignments = {}
            for entry in dictionary['entries']:
                for unit_id in entry['memberUnitIds']:
                    if unit_id in assignments:
                        raise ValueError('Multiple feature assignments for a code block')
                    assignments[unit_id] = entry
            unassigned = set(dictionary['unassignedUnitIds'])
            if assignments.keys() & unassigned or assignments.keys() | unassigned != self.units.keys():
                raise ValueError('Incomplete feature dictionary assignments')
            self.assignments[name] = assignments

    def repository_key(self, repository):
        # Codebase IDs are based on the representative GitHub repository's numeric ID.
        if re.fullmatch(r'[0-9]+', str(repository.pk)):
            codebase_id = f'cb_{repository.pk}'
            if codebase_id in self.repositories:
                return codebase_id

        aliases = set()
        url_slug = github_slug(repository.url)
        if url_slug:
            aliases.update(self.repository_aliases.get(url_slug.casefold(), ()))
        if repository.owner_github_id and repository.name:
            slug = f'{repository.owner_github_id}/{repository.name}'.casefold()
            aliases.update(self.repository_aliases.get(slug, ()))
        if len(aliases) > 1:
            raise LookupFailure(409, 'ambiguous_repository', '이 레포가 여러 분석 대상과 일치합니다.')
        if not aliases:
            raise LookupFailure(404, 'repository_not_analyzed', '이 레포의 기능 분석 결과가 아직 없습니다.')
        return aliases.pop()

    def evidence(self, unit_id, student_id, needs_review=False):
        unit = self.units[unit_id]
        source = unit['source']
        line_share = self.contributions.get(student_id, {}).get(unit_id, 0.0)
        return {
            'unitId': unit_id,
            'title': unit['title'],
            'purpose': unit['purpose'],
            'kind': unit['kind'],
            'function': source['qualifiedName'],
            'sourceUrl': self.source_links[unit_id],
            'studentLineShare': line_share if student_id else None,
            'needsReview': needs_review,
            **{key: source[key] for key in (
                'codebaseId', 'repoUrl', 'commit', 'path', 'startLine', 'endLine', 'language'
            )},
        }

    def features(self, *, repository, student_id, dictionary, scope, limit, offset):
        if dictionary not in self.assignments:
            raise LookupFailure(503, 'dictionary_unavailable', '지정한 기능 사전을 사용할 수 없습니다.')
        if scope == 'contributed' and student_id not in self.students:
            raise LookupFailure(404, 'student_not_analyzed', '이 학생의 기여 분석 결과가 아직 없습니다.')

        repository_key = self.repository_key(repository) if repository else None
        if repository_key:
            repo = self.repositories[repository_key]
            selected = set(repo['unitIds'])
        else:
            repo = None
            selected = set(self.contributions.get(student_id, {}))
        if scope == 'contributed':
            selected.intersection_update(self.contributions.get(student_id, {}))

        assignments = self.assignments[dictionary]
        groups = defaultdict(list)
        unassigned = []
        for unit_id in sorted(selected):
            entry = assignments.get(unit_id)
            if entry:
                groups[entry['id']].append(unit_id)
            else:
                unassigned.append(self.evidence(unit_id, student_id))

        features = []
        for members in groups.values():
            entry = assignments[members[0]]
            suspect = set(entry['suspectUnitIds'])
            features.append({
                **{key: entry[key] for key in ('id', 'name', 'definition', 'status', 'mixedScope', 'reviewFlags')},
                'dictionaryBlockCount': len(entry['memberUnitIds']),
                'blockCount': len(members),
                'repositoryCount': len({self.units[unit]['source']['codebaseId'] for unit in members}),
                'observedTitles': sorted({self.units[unit]['title'] for unit in members}),
                'evidence': [self.evidence(unit, student_id, unit in suspect) for unit in members],
            })
        features.sort(key=lambda feature: (-feature['repositoryCount'], -feature['blockCount'], feature['id']))

        return {
            'run': self.run,
            'dictionary': dictionary,
            'dictionaryStatus': self.dictionaries[dictionary]['status'],
            'repository': {
                'id': str(repository.pk),
                'codebaseId': repository_key,
                'analyzedRepoUrl': repo['repoUrl'],
                'analyzedBlockCount': len(repo['unitIds']),
            } if repository else None,
            'studentId': student_id,
            'scope': scope,
            'summary': {
                'selectedBlockCount': len(selected),
                'assignedBlockCount': len(selected) - len(unassigned),
                'unassignedBlockCount': len(unassigned),
                'repositoryCount': len({self.units[unit]['source']['codebaseId'] for unit in selected}),
                'featureCount': len(features),
            },
            'totalFeatures': len(features),
            'limit': limit,
            'offset': offset,
            'hasMore': offset + limit < len(features),
            'features': features[offset:offset + limit],
            'unassigned': unassigned,
        }
