from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from .forms import *
from .models import *
from .utils import *
import json
import os


# Create your views here.


@permission_required('main.student_permissions')
@login_required(login_url='/app/user/login/')
def student_diary(request, practice_id):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user

        practice, is_active = get_practice(practice_id, user)

        if not is_active:
            messages.add_message(request, messages.INFO, 'Практика уже окончена')
            return render(request, 'main/html/student_practice_diary.html',
                          {"doc_type": "practice", "page_title": "Дневник практики"})

        doc, template = diary_adapter(data, user, practice)

        path = get_temporary_save_path(user, 'practice_diary')

        try:
            entry = save_doc(doc, path, user, practice, template)
        except IntegrityError:
            content = {"message": "Вы уже создали этот документ. Дождитесь решения деканата."}
            return HttpResponse(json.dumps(content), content_type="application/json")

        response = HttpResponse(json.dumps({}), content_type='application/json')

        return response

    if request.method == "GET":
        return render(request, 'main/html/student/fill_document.html',
                      {"doc_type": "practice", "page_title": "Дневник практики"})


@permission_required('main.student_permissions')
@login_required(login_url='/app/user/login/')
def student_ind_task(request, practice_id):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user

        practice, is_active = get_practice(practice_id, user)

        if not is_active:
            messages.add_message(request, messages.INFO, 'Практика уже окончена')
            return render(request, 'main/html/student/fill_document.html',
                          {"doc_type": "ind_task", "outer_practice": practice.type_of == OUTER_PRACTICE,
                           "page_title": "Индивидуальное задание"})

        doc, template = ind_task_adapter(data, user, practice)

        path = get_temporary_save_path(user, 'individual_task')

        try:
            entry = save_doc(doc, path, user, practice, template)
        except IntegrityError:
            content = {"message": "Вы уже создали этот документ. Дождитесь решения деканата."}
            return HttpResponse(json.dumps(content), content_type="application/json")

        response = HttpResponse(json.dumps({}), content_type='application/json')

        return response

    if request.method == "GET":
        practice = Practice.objects.get(id=practice_id)
        return render(request, 'main/html/student/fill_document.html',
                      {"doc_type": "ind_task", "outer_practice": practice.type_of == OUTER_PRACTICE,
                       "page_title": "Индивидуальное задание"})


@permission_required('main.student_permissions')
@login_required(login_url='/app/user/login/')
def student_title(request, practice_id):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user

        practice, is_active = get_practice(practice_id, user)

        if not is_active:
            messages.add_message(request, messages.INFO, 'Практика уже окончена')
            return render(request, 'main/html/student/fill_document.html',
                          {"doc_type": "title", "page_title": "Титульный лист"})

        doc, template = title_adapter(user, practice, data)

        path = get_temporary_save_path(user, 'individual_task')

        try:
            entry = save_doc(doc, path, user, practice, template)
        except IntegrityError:
            content = {"message": "Вы уже создали этот документ. Дождитесь решения деканата."}
            return HttpResponse(json.dumps(content), content_type="application/json")

        response = HttpResponse(json.dumps({}), content_type='application/json')

        return response

    if request.method == "GET":
        practice = Practice.objects.get(id=practice_id)
        return render(request, 'main/html/student/fill_document.html',
                      {"doc_type": "title", "outer_practice": practice.type_of == OUTER_PRACTICE,
                       "page_title": "Титульный лист", "practice": practice})


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def get_groups(request):
    groups = StudyGroup.objects.all()
    content = {"groups": groups}
    return HttpResponse(json.dumps(content), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def get_practices(request):
    practices = Practice.objects.all()
    practice_list = []
    for practice in practices:
        practice_list.append()
    content = {"practices": practices}
    return HttpResponse(json.dumps(content), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def get_practice_view(request, practice_id):
    try:
        practice = Practice.objects.get(id=practice_id)
        practice_dict = {}
        practice_dict['name'] = practice.name
        practice_dict['curator'] = practice.curator.id
        practice_dict['type_of'] = practice.type_of
        practice_dict['address'] = practice.address
        practice_dict['institute'] = practice.institute
        practice_dict['speciality'] = practice.speciality
        practice_dict['start_date'] = practice.start_date.strftime('%d.%m.%Y')
        practice_dict['end_date'] = practice.end_date.strftime('%d.%m.%Y')
    except Exception:
        return HttpResponse(json.dumps({"message": "Данной практики не существует"}), content_type="application/json")
    return HttpResponse(json.dumps({"practice": practice_dict}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def all_practices(request):
    return render(request, "main/html/deanery/practices.html", {"practices": Practice.objects.all(), "page_title": "Список практик"})


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def create_practice(request):
    if request.method == "POST":
        practice = Practice()
        json_data = json.loads(request.body)
        practice_id = json_data.get('practice_id')
        if (practice_id):
            try:
                practice = Practice.objects.get(id=practice_id)
            except:
                return HttpResponse(json.dumps({"message": "Такой практики не существует."}), content_type="application/json")
        practice.type_of = json_data.get("type_of")
        practice.curator = User.objects.get(id=json_data.get("curator"))
        practice.address = json_data.get("address")
        practice.institute = json_data.get("institute")
        practice.speciality = json_data.get("speciality")
        start_date = json_data.get("start_date").split('.')
        start_date.reverse()
        practice.start_date = '-'.join(start_date)
        end_date = json_data.get("end_date").split('.')
        end_date.reverse()
        practice.end_date = '-'.join(end_date)
        practice.name = json_data.get("name")

        practice.save()
        return HttpResponse(json.dumps({}), content_type="application/json")

    if request.method == "GET":
        return render(request, "main/html/deanery/create_practice.html", {"practices": Practice.objects.all(), "practice_type_choices": PRACTICE_TYPE, "curators": User.objects.filter(groups__name="Curators"), "page_title": "Создать"})


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def delete_practice(request, practice_id):
    try:
        practice = Practice.objects.get(id=practice_id)
    except Exception:
        return HttpResponse(json.dumps({"message": "Данной практики не существует"}), content_type="application/json")
    try:
        practice.delete()
    except Exception:
        return HttpResponse(json.dumps({"message": "Удаление не удалось"}), content_type="application/json")
    return HttpResponse(json.dumps({"message": "Удаление успешно завершено"}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def get_group(request, group_id):
    try:
        group = StudyGroup.objects.get(id=group_id)
    except Exception:
        return HttpResponse(json.dumps({"message": "Данной практики не существует"}), content_type="application/json")
    return HttpResponse(json.dumps({"group": group}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def create_group(request, old_group_id=None):
    if request.method == "POST":
        group = StudyGroup()
        if old_group_id:
            try:
                group = StudyGroup.objects.get(id=old_group_id)
            except Exception:
                return HttpResponse(json.dumps({"message": "Данной группы не существует"}),
                                    content_type="application/json")

        json_data = json.loads(request.body)
        group.group_number = json_data.get("group_number")
        group.course = json_data.get("course")

        group.save()
        return HttpResponse(json.dumps({"message": "Операция успешно проведена."}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def delete_group(request, group_id):
    try:
        group = StudyGroup.objects.get(id=group_id)
    except Exception:
        return HttpResponse(json.dumps({"message": "Данной группы не существует"}), content_type="application/json")
    try:
        group.delete()
    except Exception:
        return HttpResponse(json.dumps({"message": "Удаление не удалось"}), content_type="application/json")
    return HttpResponse(json.dumps({"message": "Удаление успешно завершено"}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def get_students(request, practice_id):
    try:
        relations = StudentToPractice.objects.filter(practice__id=practice_id, is_active=True)
    except:
        return HttpResponse(json.dumps({"message": "Данной практики не существует"}), content_type="application/json")
    students = []
    for relation in relations:
        student = relation.student
        students.append({
            name: student.__str__(),
            group: {
                number: student.student_profile.group.group_number,
                course: student.student_profile.group.course
            }
        })

@login_required(login_url='/app/user/login/')
def get_student_info(request, student_id):
    try:
        student = User.objects.get(id=student_id)
    except Exception:
        return HttpResponse(json.dumps({"message": "Студент не найден"}), content_type="application/json")
    relations = StudentToPractice.objects.filter(student=student)
    practices = []
    for relation in relations:
        practice = Practice.objects.get(student=student, practice_relations=relation)
        practice.is_active = relation.is_active
        practices.append(practice)
    student.practices = practices
    return HttpResponse(json.dumps({"student": student}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def change_student_group(request, student_id, group_id):
    try:
        profile = StudentProfile.objects.get(user__id=student_id)
    except Exception:
        return HttpResponse(json.dumps({"message": "Студент не найден"}), content_type="application/json")

    try:
        group = User.objects.get(id=group_id)
    except Exception:
        return HttpResponse(json.dumps({"message": "Такой группы не существует"}), content_type="application/json")

    profile.group = group
    profile.save()
    return HttpResponse(json.dumps({"message": "Операция успешно проведена."}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def change_student_to_practice_relation_status(request, relation_id):
    status = json.loads(request.body).get("is_active")
    try:
        relation = StudentToPractice.objects.get(id=relation_id)
    except Exception:
        return HttpResponse(json.dumps({"message": "Связь не найдена"}), content_type="application/json")
    relation.is_active = status
    relation.save()
    return HttpResponse(json.dumps({"message": "Статус успешно обновлен"}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def delete_student_to_practice_relation_status(request, relation_id):
    try:
        relation = StudentToPractice.objects.get(id=relation_id)
    except Exception:
        return HttpResponse(json.dumps({"message": "Связь не найдена"}), content_type="application/json")
    relation.delete()
    return HttpResponse(json.dumps({"message": "Статус успешно обновлен"}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def add_student_to_practice_relation(request):
    json_data = json.loads(request.body)
    try:
        student = User.objects.get(id=json_data.get("student_id"))
    except Exception:
        return HttpResponse(json.dumps({"message": "Студент не найден"}), content_type="application/json")
    try:
        practice = Practice.objects.get(id=json_data.get("practice_id"))
    except Exception:
        return HttpResponse(json.dumps({"message": "Данной практики не существует"}), content_type="application/json")

    relation = StudentToPractice()
    relation.student = student
    relation.practice = practice
    relation.is_active = True
    relation.save()
    return HttpResponse(json.dumps({"message": "Операция успешно проведена."}), content_type="application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def append_students_to_group(request):
    json_data = json.loads(request.body)
    try:
        group = StudyGroup.objects.get(id=json_data.get("group_id"))
    except Exception:
        return HttpResponse(json.dumps({"message": "Такой группы не существует"}), content_type="application/json")
    messages = []
    for id in json_data.get("students"):
        try:
            student = User.objects.get(id=id)
        except Exception:
            messages.append({"message": "Студент {} не был найден".format(id)})
            continue
        try:
            profile = StudentProfile.objects.get(user=student)
        except Exception:
            messages.append({"message": "У студента {} {} не настроен профиль".format(student.first_name,
                                                                                      student.last_name)})
            continue
        profile.group = group
        profile.save()
    messages.append({"message": "Операция успешно завершена"})
    return HttpResponse(json.dumps(messages), "application/json")


@permission_required('main.deanery_worker_permissions')
@login_required(login_url='/app/user/login/')
def append_students_to_practice(request):
    json_data = json.loads(request.body)
    try:
        practice = Practice.objects.get(id=json_data.get("practice_id"))
    except Exception:
        return HttpResponse(json.dumps({"message": "Такой практики не существует"}), content_type="application/json")
    messages = []
    for id in json_data.get("students"):
        try:
            student = User.objects.get(id=id)
        except Exception:
            messages.append({"message": "Студент {} не был найден".format(id)})
            continue

        if StudentToPractice.objects.filter(student=student, is_active=True):
            messages.append({"message": "У студента {} {} были обнаружены активные практики.".format(student.first_name,
                                                                                                     student.last_name)})

        relation = StudentToPractice()
        relation.student = student
        relation.practice = practice
        relation.is_active = True
        relation.save()

    messages.append({"message": "Операция успешно завершена"})
    return HttpResponse(json.dumps(messages), "application/json")


@login_required(login_url='/app/user/login/')
@permission_required('main.deanery_worker_permissions')
def change_document_status(request):
    json_data = json.loads(request.body)
    try:
        document = Document.objects.get(id=json_data.get("document_id"))
    except:
        return HttpResponse(json.dumps({"message": "Документ не найден"}), content_type="application/json")
    document.status = json_data.get("status")
    document.save()
    return HttpResponse(json.dumps({"message": "Операция завершена"}), content_type="application/json")


@login_required(login_url='/app/user/login/')
def main_redirect(request):
    user = request.user
    if user.has_perm('main.student_permissions'):
        practices = Practice.objects.filter(students=user)
        for practice in practices:
            practice.documents = Document.objects.filter(student=user, practice=practice)
            relation = StudentToPractice.objects.get(student=user, practice=practice)
            practice.is_active = relation.is_active
        return render(request, 'main/html/student/practices.html',
                      {"practices": practices, "page_title": "Список практик"})

    if user.has_perm('main.deanery_worker_permissions'):
        practices = Practice.objects.filter(practice_documents__status=0)
        for practice in practices:
            practice.documents = Document.objects.filter(practice=practice, status=0)
            for document in practice.documents:
                document.student.group = StudyGroup.objects.get(group_student_profiles__user=document.student)
        return render(request, 'main/html/deanery/documents.html', {"practices": practices, "page_title": "Новые документы"})

    return HttpResponseRedirect('/app/user/login/')


def new_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/app/user/main/')
            else:
                raise Http404
        else:
            messages.add_message(request, messages.INFO, 'Неверное имя пользователя или пароль.')
            messages.get_messages(request)
            return render(request, 'main/html/login.html', {"page_title": "Вход"})

    if request.method == "GET":
        return render(request, 'main/html/login.html', {"page_title": "Вход"})


def new_logout(request):
    logout(request)
    return HttpResponseRedirect('/app/user/login/')
