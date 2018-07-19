from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from SMARTDocsProject import settings
import datetime

now = datetime.datetime.now()


PRACTICE_DIARY_KEY = 'practice_diary'
INNER_INDIVIDUAL_TASK_KEY = 'inner_individual_task'
OUTER_INDIVIDUAL_TASK_KEY = 'outer_individual_task'
INNER_REPORT_TITLE_KEY = 'inner_report_title'
OUTER_REPORT_TITLE_KEY = 'outer_report_title'


def get_only_curators_q():
    return Q(groups__name='Curators')


def get_only_students_q():
    return Q(groups__name='Students')


def get_only_students_q_without_profile():
    return Q(groups__name='Students', student_profile=None)


def get_only_students_q_with_profile():
    return Q(groups__name='Students') & ~Q(student_profile=None)


def filled_docs_directory_path(instance, filename):
    return "filled_documents/{0}/{1}/{2}".format(instance.student.pk, now.year,
                                                     filename)


def avatars_directory(instance, filename):
    return "avatars/{0}/{1}".format(instance.student.pk, filename)


INNER_PRACTICE = 0
OUTER_PRACTICE = 1
BEFORE_GRAD_PRACTICE = 2

PRACTICE_TYPE = (
    (INNER_PRACTICE, 'Практика в лаборатории института'),
    (OUTER_PRACTICE, 'Практика на предприятии'),
    (BEFORE_GRAD_PRACTICE, 'Преддипломная практика'),
)

DOCUMENT_KEYS = (
    (PRACTICE_DIARY_KEY, 'Дневник практики'),
    (INNER_INDIVIDUAL_TASK_KEY, 'Индивидуальное задание (внутренняя практика)'),
    (OUTER_INDIVIDUAL_TASK_KEY, 'Индивидуальное задание (внешняя практика)'),
    (INNER_REPORT_TITLE_KEY, 'Титульный лист отчёта (внутренняя практика)'),
    (OUTER_REPORT_TITLE_KEY, 'Титульный лист отчёта (внешняя практика)'),
)

STANDBY = 0
ACCEPTED = 1
REJECTED = 2

DOCUMENT_STATUS = (
    (STANDBY, 'На проверке'),
    (ACCEPTED, 'Принят'),
    (REJECTED, 'Отклонен'),
)


class User(AbstractUser):
    middle_name = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to=avatars_directory, blank=True)

    def __str__(self):
        return "{} {} {}".format(self.first_name, self.last_name, self.middle_name)

    class Meta:
        verbose_name_plural = "Пользователи"


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, limit_choices_to=get_only_students_q_without_profile,
                                related_name='student_profile', unique=True)
    group = models.ForeignKey('StudyGroup', on_delete=models.CASCADE, related_name='group_student_profiles')

    def __str__(self):
        return "{} add. data".format(str(self.user))

    class Meta:
        verbose_name_plural = "Дополнительная информация студентов"

    def clean(self):
        if StudyGroup.objects.filter(group_student_profiles__user=self.user):
            raise ValidationError(message='Студент уже состоит в группе')


class CuratorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, limit_choices_to=get_only_curators_q,
                                related_name='curator_profile', unique=True)
    position = models.CharField(max_length=100, verbose_name="Должность")
    academic_title = models.CharField(max_length=100, verbose_name="Ученое звание", blank=True)

    def __str__(self):
        return "{} add. data".format(str(self.user))

    class Meta:
        verbose_name_plural = "Дополнительная информация кураторов"


class StudyGroup(models.Model):
    course = models.CharField(max_length=15, verbose_name="Курс группы")
    group_number = models.CharField(max_length=15, unique=True, verbose_name="Номер группы")

    def __str__(self):
        return "{}".format(self.group_number)

    class Meta:
        verbose_name_plural = "Студенческие группы"


class Practice(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование")
    type_of = models.SmallIntegerField(choices=PRACTICE_TYPE, default=0)
    curator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                limit_choices_to=get_only_curators_q, related_name='curator_practices',
                                verbose_name="Куратор")
    # pro_curator ??
    start_date = models.DateField(verbose_name="Дата начала практики")
    address = models.CharField(max_length=200, verbose_name="Адрес прохождения практики")
    end_date = models.DateField(verbose_name="Дата окончания практики")
    institute = models.CharField(max_length=200, verbose_name="Институт")
    speciality = models.CharField(max_length=200, verbose_name="Специальность/Направление подготовки", blank=True)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, through="StudentToPractice",
                                      related_name='student_practices')

    def __str__(self):
        return "{0}, куратор: {1} {2}".format(self.name, self.curator.first_name, self.curator.last_name)

    class Meta:
        verbose_name_plural = "Практики"


class StudentToPractice(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                limit_choices_to=get_only_students_q_with_profile,
                                related_name='student_relations',
                                verbose_name="Студент")
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name='practice_relations',
                                 verbose_name="Практика")
    is_active = models.BooleanField(default=True)

    def clean(self):
        active_practice = Practice.objects.filter(students=self.student, practice_relations__is_active=True)
        if active_practice and self.practice not in active_practice:
            raise ValidationError(message="Студент {} {} уже состоит в практике!".format(self.student.first_name,
                                                                                         self.student.last_name))

    def __str__(self):
        return "{}, студент: {} {}".format(self.practice.name, self.student.first_name, self.student.last_name)

    class Meta:
        verbose_name_plural = "Связи студентов к практикам"


class DocumentTemplate(models.Model):
    document_name = models.CharField(choices=DOCUMENT_KEYS, max_length=100, verbose_name="Уникальный ключ документа",
                                     unique=True)
    upload = models.FileField(upload_to='uploads/templates', unique=True, verbose_name="Файл загрузки")
    uploading_date = models.DateField(auto_now=True)

    def __str__(self):
        return "{}".format(self.document_name)

    class Meta:
        verbose_name_plural = "Шаблоны документов"


class Document(models.Model):
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE, related_name='filled',
                                 verbose_name='Шаблон')
    student = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.CASCADE,
                                limit_choices_to=get_only_students_q, related_name='student_documents',
                                verbose_name='Студент')
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name='practice_documents',
                                 verbose_name='Практика')
    upload = models.FileField(upload_to=filled_docs_directory_path, unique=True, verbose_name="Файл загрузки")
    uploading_date = models.DateField(auto_now=True)
    status = models.SmallIntegerField(choices=DOCUMENT_STATUS, default=0)

    def __str__(self):
        return "{0} {1}, от {2}".format(self.student.first_name, self.student.last_name, self.uploading_date)

    class Meta:
        verbose_name_plural = "Заполненные документы"
        unique_together = (("template", "student", "practice"),)
