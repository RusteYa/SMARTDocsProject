import datetime
import locale
import pymorphy2
from docxtpl import DocxTemplate
from .models import *

print(locale.locale_alias)

locale.setlocale(locale.LC_ALL, 'ru_RU.ISO8859-5')
morph = pymorphy2.MorphAnalyzer()

FACULTY_MAX_LEN = 65
PRACTICE_TYPE_MAX_LEN = 80
EXECUTOR_MAX_LEN = 50
DAY_MAX_LEN = 5
MONTH_MAX_LEN = 15
YEAR_MAX_LEN = 6
CURATOR_MAX_LEN = 60
PRACTICE_TYPE_SECOND_MAX_LEN = 30
PRACTICE_PLACE_MAX_LEN = 35

FACULTY_IND_MAX_LEN = 50
SPECIALTY_MAX_LEN = 35
EXECUTOR_FULL_MAX_LEN = 60
FIO_BRIEF_MAX_LEN = 25
CURATOR_COMPANY_OFFICE_MAX_LEN = 26
CURATOR_COMPANY_FIO_BRIEF_MAX_LEN = 20

CURATOR_COMPANY_TITLE_MAX_LEN = 67
CURATOR_TITLE_MAX_LEN = 67
EXECUTOR_TITLE_MAX_LEN = 40
PRACTICE_PLACE_TITLE_MAX_LEN = 65

practice_types = {
    0: 'учебная',
    1: 'производственная',
    2: 'преддипломная'
}


class Field:
    def __init__(self, name, value, max_len):
        self.name = name
        self.value = str(value)
        self.max_len = max_len


def generate_practice_diary(fio, group, faculty_data, practice_type_num, practice_start_date, practice_end_date,
                            curator_fio, curator_office, practice_place, works_content):
    practice_type_data = practice_types[practice_type_num]
    if faculty_data.__len__() <= FACULTY_MAX_LEN \
            and practice_type_data.__len__() <= PRACTICE_TYPE_MAX_LEN \
            and fio.__len__() + group.__len__() + 2 <= EXECUTOR_MAX_LEN \
            and curator_fio.__len__() + curator_office.__len__() + 2 <= CURATOR_MAX_LEN \
            and practice_type_data.__len__() <= PRACTICE_TYPE_SECOND_MAX_LEN \
            and practice_place.__len__() <= PRACTICE_PLACE_MAX_LEN:
        print(practice_start_date.strftime("%B"))
        print(morph.parse(practice_start_date.strftime("%B"))[0])
        practice_start_date_month_gent = morph.parse(practice_start_date.strftime("%B"))[0].inflect({'gent'}).word
        practice_end_date_month_gent = morph.parse(practice_end_date.strftime("%B"))[0].inflect({'gent'}).word
        practice_type_data_gent = morph.parse(practice_type_data)[0].inflect({'gent'}).word
        executor = '{fio}, {group}'.format(fio=fio, group=group)
        curator = '{fio}, {office}'.format(fio=curator_fio, office=curator_office)

        fields = [
            Field(name='executor', value=executor, max_len=EXECUTOR_MAX_LEN),
            Field(name='faculty', value=faculty_data, max_len=FACULTY_MAX_LEN),
            Field(name='practice_type', value=practice_type_data, max_len=PRACTICE_TYPE_MAX_LEN),
            Field(name='practice_start_date_day', value=practice_start_date.day, max_len=DAY_MAX_LEN),
            Field(name='practice_start_date_month', value=practice_start_date_month_gent, max_len=MONTH_MAX_LEN),
            Field(name='practice_start_date_year', value=practice_start_date.year, max_len=YEAR_MAX_LEN),
            Field(name='practice_end_date_day', value=practice_end_date.day, max_len=DAY_MAX_LEN),
            Field(name='practice_end_date_month', value=practice_end_date_month_gent, max_len=MONTH_MAX_LEN),
            Field(name='practice_end_date_year', value=practice_end_date.year, max_len=YEAR_MAX_LEN),
            Field(name='curator', value=curator, max_len=CURATOR_MAX_LEN),
            Field(name='current_year', value=datetime.datetime.now().year, max_len=YEAR_MAX_LEN),
            Field(name='practice_type_gent', value=practice_type_data_gent, max_len=PRACTICE_TYPE_SECOND_MAX_LEN),
            Field(name='practice_place', value=practice_place, max_len=PRACTICE_PLACE_MAX_LEN),
        ]

        template = DocumentTemplate.objects.get(document_name=PRACTICE_DIARY_KEY)
        doc = DocxTemplate(template.upload.path)

        context = generate_filled_fields_value(fields)
        context['tabel_contents'] = works_content

        doc.render(context)

        return doc, template


def generate_ind_task(fio, group, faculty_data, practice_start_date, practice_end_date, specialty,
                      curator_academic_tittle, curator_fio, curator_office, practice_place,
                      course, works_content, template, practice_type_num,
                      curator_company_fio="",
                      curator_company_office=""):
    practice_type_data = morph.parse(practice_types[practice_type_num])[0].inflect({'accs'}).word
    if faculty_data.__len__() <= FACULTY_IND_MAX_LEN \
            and practice_type_data.__len__() <= PRACTICE_TYPE_MAX_LEN \
            and fio.__len__() + group.__len__() + 10 <= EXECUTOR_FULL_MAX_LEN \
            and practice_place.__len__() <= PRACTICE_PLACE_MAX_LEN \
            and specialty.__len__() <= SPECIALTY_MAX_LEN \
            and curator_company_office.__len__() <= CURATOR_COMPANY_OFFICE_MAX_LEN:
        practice_end_date_month_gent = morph.parse(practice_end_date.strftime("%B"))[0].inflect({'gent'}).word
        executor_full = '{fio}, {course} курс, {group}'.format(fio=fio, course=course, group=group)
        curator_full = '{fio}, {office}'.format(fio=curator_fio, office=curator_office) if (
                curator_academic_tittle is None or curator_academic_tittle == "") else '{fio}, {office}, {academic_tittle}'.format(
            fio=curator_fio, office=curator_office, academic_tittle=curator_academic_tittle)
        curator_company_fio_brief = fio_abbreviate(curator_company_fio)
        fio_brief = fio_abbreviate(fio)

        fields = [
            Field(name='executor_full', value=executor_full, max_len=EXECUTOR_FULL_MAX_LEN),
            Field(name='faculty', value=faculty_data, max_len=FACULTY_IND_MAX_LEN),
            Field(name='specialty', value=specialty, max_len=SPECIALTY_MAX_LEN),
            Field(name='practice_start_date_day', value=practice_start_date.day, max_len=DAY_MAX_LEN),
            Field(name='practice_end_date_day', value=practice_end_date.day, max_len=DAY_MAX_LEN),
            Field(name='practice_end_date_month', value=practice_end_date_month_gent, max_len=MONTH_MAX_LEN),
            Field(name='practice_end_date_year', value=practice_end_date.year, max_len=YEAR_MAX_LEN),
            Field(name='practice_place', value=practice_place, max_len=PRACTICE_PLACE_MAX_LEN),
            Field(name='curator_company_office', value=curator_company_office, max_len=CURATOR_COMPANY_OFFICE_MAX_LEN),
            Field(name='curator_company_fio_brief', value=curator_company_fio_brief,
                  max_len=CURATOR_COMPANY_FIO_BRIEF_MAX_LEN),
            Field(name='fio_brief', value=fio_brief, max_len=FIO_BRIEF_MAX_LEN),
        ]

        doc = DocxTemplate(template.upload.path)

        context = generate_filled_fields_value(fields)
        context['curator_full'] = "__{curator_full}__".format(curator_full=curator_full)
        context['practice_type'] = practice_type_data
        context['tabel_contents'] = works_content

        doc.render(context)

        return doc, template


def generate_company_ind_task(fio, group, faculty_data, practice_type_num, course, practice_start_date,
                              practice_end_date, curator_fio,
                              curator_office, practice_place, curator_company_fio, curator_company_office,
                              curator_academic_tittle, specialty, works_content):
    template = DocumentTemplate.objects.get(document_name=OUTER_INDIVIDUAL_TASK_KEY)
    return generate_ind_task(
        fio=fio, group=group, faculty_data=faculty_data, practice_type_num=practice_type_num, course=course,
        practice_start_date=practice_start_date, practice_end_date=practice_end_date,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        curator_company_fio=curator_company_fio, curator_company_office=curator_company_office,
        curator_academic_tittle=curator_academic_tittle, specialty=specialty, works_content=works_content,
        template=template
    )


def generate_lab_ind_task(fio, group, faculty_data, practice_type_num, course, practice_start_date, practice_end_date,
                          curator_fio,
                          curator_office, practice_place, curator_academic_tittle, specialty, works_content):
    template = DocumentTemplate.objects.get(document_name=INNER_INDIVIDUAL_TASK_KEY)
    return generate_ind_task(
        fio=fio, group=group, faculty_data=faculty_data, practice_type_num=practice_type_num, course=course,
        practice_start_date=practice_start_date, practice_end_date=practice_end_date,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        curator_academic_tittle=curator_academic_tittle, specialty=specialty, works_content=works_content,
        template=template
    )


def generate_title(fio, group, faculty_data, curator_academic_tittle, curator_fio, curator_office, practice_place,
                   template,
                   practice_type_num, curator_company_fio="", curator_company_office=""):
    practice_type_data = practice_types[practice_type_num]
    if faculty_data.__len__() <= FACULTY_MAX_LEN \
            and practice_type_data.__len__() <= PRACTICE_TYPE_MAX_LEN \
            and fio.__len__() + group.__len__() + 10 <= EXECUTOR_FULL_MAX_LEN \
            and practice_type_data.__len__() <= PRACTICE_TYPE_SECOND_MAX_LEN \
            and practice_place.__len__() <= PRACTICE_PLACE_MAX_LEN \
            and curator_company_office.__len__() <= CURATOR_COMPANY_OFFICE_MAX_LEN:
        executor = '{fio}, {group}'.format(fio=fio, group=group)
        curator_full = '{fio}, {office}'.format(fio=curator_fio, office=curator_office) if (
                curator_academic_tittle is None or curator_academic_tittle == "") else '{fio}, {office}, {academic_tittle}'.format(
            fio=curator_fio, office=curator_office, academic_tittle=curator_academic_tittle)
        curator_company = '{fio}, {office}'.format(fio=curator_company_fio, office=curator_company_office)
        practice_type_data_gent = morph.parse(practice_type_data)[0].inflect({'gent'}).word

        fields = [
            Field(name='executor', value=executor, max_len=EXECUTOR_TITLE_MAX_LEN),
            Field(name='practice_place', value=practice_place, max_len=PRACTICE_PLACE_TITLE_MAX_LEN),
            Field(name='curator_company', value=curator_company, max_len=CURATOR_COMPANY_TITLE_MAX_LEN),
            Field(name='curator_full', value=curator_full, max_len=CURATOR_TITLE_MAX_LEN)
        ]

        doc = DocxTemplate(template.upload.path)

        context = generate_filled_fields_value(fields)
        context['company'] = practice_place
        context['faculty'] = faculty_data
        context['practice_type_gent'] = practice_type_data_gent.upper()

        doc.render(context)

        return doc, template


def generate_company_title(fio, group, faculty_data, curator_fio, curator_office, practice_place, curator_company_fio,
                           curator_company_office, curator_academic_tittle, practice_type_num):
    template = DocumentTemplate.objects.get(document_name=OUTER_REPORT_TITLE_KEY)
    return generate_title(
        fio=fio, group=group, faculty_data=faculty_data,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        curator_company_fio=curator_company_fio, curator_company_office=curator_company_office,
        curator_academic_tittle=curator_academic_tittle, practice_type_num=practice_type_num,
        template=template
    )


def generate_lab_title(fio, group, faculty_data, curator_fio, curator_office, practice_place, curator_academic_tittle,
                       practice_type_num):
    template = DocumentTemplate.objects.get(document_name=INNER_REPORT_TITLE_KEY)
    return generate_title(
        fio=fio, group=group, faculty_data=faculty_data,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        curator_academic_tittle=curator_academic_tittle, practice_type_num=practice_type_num,
        template=template
    )


def generate_filled_fields_value(fields):
    context = {}
    for field in fields:
        context[field.name] = "_" * ((field.max_len - field.value.__len__()) // 2) + field.value + "_" * (
                (field.max_len - field.value.__len__()) // 2)
    return context


def fio_abbreviate(fio):
    if fio is not None and fio != "":
        strs = fio.split(" ")
        fio = '%s ' % strs[0]
        fio += '. '.join([x[0] for x in strs[1:strs.__len__()] if x.__len__() > 0]) + '. '
        return fio
    else:
        return ""


if __name__ == '__main__':
    fio = "Ямиков Рустем Рафикович"
    group = "11-601"
    course = 2
    specialty = "программная инженерия"
    faculty_data = "Высшая школа ИТИС"
    practice_type_num = 0
    practice_start_date = datetime.date(2018, 7, 6)
    practice_end_date = datetime.date(2018, 7, 19)
    curator_fio = "Абрамский Михаил Михайлович"
    curator_office = "старший преподаватель"
    curator_academic_tittle = "доктор наук"
    curator_company_fio = "Абрамский2 Михаил Михайлович"
    curator_company_office = "ведущий разработчик"
    practice_place = "кафедра программной инженерии"
    works_content = [
        {'date': '16.07.2018', 'work': 'Аналитика проектной работы'},
        {'date': '7.07.2018', 'work': 'Начало разработки'},
        {'date': '7.07.2018', 'work': 'Продолжение разработки'},
        {'date': '6.07.2018', 'work': 'Аналитика проектной работы'},
        {'date': '7.07.2018', 'work': 'Начало разработки'},
        {'date': '7.07.2018', 'work': 'Продолжение разработки'},
        {'date': '6.07.2018', 'work': 'Аналитика проектной работы'},
        {'date': '7.07.2018', 'work': 'Начало разработки'},
        {'date': '7.07.2018', 'work': 'Продолжение разработки'},
        {'date': '6.07.2018', 'work': 'Аналитика проектной работы'},
        {'date': '7.07.2018', 'work': 'Начало разработки'},
        {'date': '7.07.2018', 'work': 'Продолжение разработки'},
    ]
    ind_task_works_content = [
        {'num': '1',
         'work': 'Ознакомление со спецификой работы организации, ее структурой, работой отдела/подразделения, в котором проводится практика',
         'start_date': '6.07.2018', 'end_date': '8.07.2018'},
        {'num': '2',
         'work': 'Ознакомление с корпоративной политикой, нормативной базой, должностными инструкциями, технологией получения и выполнения задач, информационной политикой и особенностями рабочей коммуникации.',
         'start_date': '9.07.2018', 'end_date': '10.2018'},
        {'num': '3',
         'work': 'Приобретение первоначальных навыков работы на определенной позиции, выполнение базовых задач, поставленных руководителем практики',
         'start_date': '11.07.2018', 'end_date': '14.07.2018'},
        {'num': '4',
         'work': 'Выполнение дополнительных задач, поставленных руководителем практики',
         'start_date': '15.07.2018', 'end_date': '17.07.2018'},
        {'num': '5',
         'work': 'Осуществление систематизации и анализа работы в форме отчёта по практике.',
         'start_date': '18.07.2018', 'end_date': '19.07.2018'},
    ]

    doc, templ = generate_practice_diary(
        fio=fio, group=group, faculty_data=faculty_data, practice_type_num=practice_type_num,
        practice_start_date=practice_start_date, practice_end_date=practice_end_date,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        works_content=works_content
    )
    doc.save("static/docs/Dnevnik_praktiki_generated.docx")

    doc, templ = generate_company_ind_task(
        fio=fio, group=group, faculty_data=faculty_data, course=course,
        practice_start_date=practice_start_date, practice_end_date=practice_end_date,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        curator_company_fio=curator_company_fio, curator_company_office=curator_company_office,
        curator_academic_tittle=curator_academic_tittle, specialty=specialty, works_content=ind_task_works_content,
        practice_type_num=practice_type_num
    )
    doc.save("static/docs/ind_zadanie_na_uchebnuyu_i_proizvodstvennuyu_praktiki_v_kompanii_generated.docx")

    doc, templ = generate_lab_ind_task(
        fio=fio, group=group, faculty_data=faculty_data, course=course,
        practice_start_date=practice_start_date, practice_end_date=practice_end_date,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        curator_academic_tittle=curator_academic_tittle, specialty=specialty, works_content=ind_task_works_content,
        practice_type_num=practice_type_num
    )
    doc.save("static/docs/ind_zadanie_na_uchebnuyu_i_proizvodstvennuyu_praktiki_v_lab_ITIS_generated.docx")

    doc = generate_company_title(
        fio=fio, group=group, faculty_data=faculty_data,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        curator_academic_tittle=curator_academic_tittle, curator_company_fio=curator_company_fio,
        curator_company_office=curator_company_office, practice_type_num=practice_type_num
    )
    doc.save("static/docs/Titul_otcheta_praktiki_ot_kompanii-partnera_generated.docx")

    doc = generate_lab_title(
        fio=fio, group=group, faculty_data=faculty_data,
        curator_fio=curator_fio, curator_office=curator_office, practice_place=practice_place,
        curator_academic_tittle=curator_academic_tittle, practice_type_num=practice_type_num
    )
    doc.save("static/docs/Titul_otcheta_po_praktike_v_lab_ITISa_generated.docx")
