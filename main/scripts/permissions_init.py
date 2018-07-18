from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from main.models import User


def run():
    students, created = Group.objects.get_or_create(name='Students')
    curators, created = Group.objects.get_or_create(name='Curators')
    deanery_workers, created = Group.objects.get_or_create(name='Deanery_Workers')

    ct = ContentType.objects.get_for_model(User)

    students_permissions = Permission.objects.create(codename='student_permissions',
                                                     name='Permissions for all Students',
                                                     content_type=ct)
    curators_permissions = Permission.objects.create(codename='curator_permissions',
                                                     name='Permissions for all Curators',
                                                     content_type=ct)
    deanery_workers_permissions = Permission.objects.create(codename='deanery_worker_permissions',
                                                            name='Permissions for all Deanery Workers',
                                                            content_type=ct)

    students.permissions.add(students_permissions)
    curators.permissions.add(curators_permissions)
    deanery_workers.permissions.add(deanery_workers_permissions)
