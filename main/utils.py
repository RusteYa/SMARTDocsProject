from django.db.utils import IntegrityError

from .docs_generator import *
from .models import *
from django.core.files import File
import os

PRACTICE_TYPE = {
    0: 'Внутренняя',
    1: 'Производственная',
}


def get_temporary_save_path(student, document_type):
    return "tmp/{}_{}_{}.docx".format(document_type, student.first_name, student.last_name)


def get_practice(practice_id, student):
    practice = Practice.objects.get(id=practice_id)
    state = StudentToPractice.objects.get(practice=practice, student=student)
    return practice, state


def diary_adapter(json_data, student, practice):
    fio = "{} {} {}".format(student.last_name, student.first_name, student.middle_name)
    curator = practice.curator
    curator_fio = "{} {} {}".format(curator.last_name, curator.first_name, curator.middle_name)
    group = student.student_profile.group
    doc, template = generate_practice_diary(fio, group.group_number, practice.institute,
                                            practice.type_of,
                                            practice.start_date, practice.end_date, curator_fio,
                                            curator.curator_profile.position, practice.name, json_data.get('works'))

    return doc, template


def ind_task_adapter(json_data, student, practice):
    fio = "{} {} {}".format(student.last_name, student.first_name, student.middle_name)
    curator = practice.curator
    curator_fio = "{} {} {}".format(curator.last_name, curator.first_name, curator.middle_name)
    group = student.student_profile.group

    if practice.type_of == INNER_PRACTICE:
        doc, template = generate_lab_ind_task(fio, group.group_number, practice.institute,
                                              practice.type_of, group.course, practice.start_date,
                                              practice.end_date, curator_fio, curator.curator_profile.position,
                                              practice.name,
                                              curator.curator_profile.academic_title, practice.speciality,
                                              json_data.get('works'))

    if practice.type_of == OUTER_PRACTICE or practice.type_of == BEFORE_GRAD_PRACTICE:
        doc, template = generate_company_ind_task(fio, group.group_number, practice.institute, practice.type_of,
                                                  group.course, practice.start_date,
                                                  practice.end_date, curator_fio, curator.curator_profile.position,
                                                  practice.name, json_data.get('curator_fio'),
                                                  json_data.get('curator_office'),
                                                  curator.curator_profile.academic_title, practice.speciality,
                                                  json_data.get('works'))
    return doc, template


def title_adapter(student, practice, json_data=None):
    fio = "{} {} {}".format(student.last_name, student.first_name, student.middle_name)
    curator = practice.curator
    curator_fio = "{} {} {}".format(curator.last_name, curator.first_name, curator.middle_name)
    group = student.student_profile.group

    if practice.type_of == INNER_PRACTICE:
        doc, template = generate_lab_title(fio, group.group_number, practice.institute, curator_fio, curator.curator_profile.position,
                                           practice.name, curator.curator_profile.academic_title, practice.type_of)

    if practice.type_of == OUTER_PRACTICE or practice.type_of == BEFORE_GRAD_PRACTICE:
        doc, template = generate_company_title(fio, group.group_number, practice.institute, curator_fio, curator.curator_profile.position,
                                               practice.name, json_data.get('curator_fio'),
                                               json_data.get('curator_office'), curator.curator_profile.academic_title,
                                               practice.type_of)

    return doc, template


def save_doc(document, tmp_path, owner, practice, template):
    earlier_documents = Document.objects.filter(template=template, student=owner, practice=practice)
    for earlier_document in earlier_documents:
        if earlier_document.status == 2:
            earlier_document.delete()
        elif earlier_document:
            raise IntegrityError


    print(settings.MEDIA_URL, settings.MEDIA_ROOT)
    print(tmp_path)
    document.save(tmp_path)

    reopen = open(tmp_path, "rb")
    django_file = File(reopen)

    entry = Document()
    entry.template = template
    entry.student = owner
    entry.practice = practice
    entry.upload.save("{}_{}_{}.docx".format(owner.first_name, owner.last_name, str(template)), django_file, save=True)

    reopen.close()
    os.remove(tmp_path)
    return entry
