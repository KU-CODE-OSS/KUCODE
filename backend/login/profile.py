"""Resolve a profile target using the verified account and stored student IDs."""
import json

from account.models import Student
from login.models import Student as LoginStudent


def profile_student(request, legacy_uid):
    own_id = getattr(request, 'member_student_id', None)
    if own_id is not None:
        return Student.objects.get(pk=own_id)
    if getattr(request, 'is_admin', False):
        data = json.loads(request.body or b'{}') if request.method == 'POST' else request.GET
        target = data.get('student_id') or data.get('student_num')
        if target and target != 'empty':
            return Student.objects.get(pk=target)
    return Student.objects.get(pk=LoginStudent.objects.get(member_id=legacy_uid).pk)
