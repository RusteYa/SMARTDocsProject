from django import template
from django.contrib.auth.models import Group
from main.models import PRACTICE_TYPE, DOCUMENT_KEYS, DOCUMENT_STATUS

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.filter(name='practice_status_str')
def practice_status_str(is_active):
    if is_active:
        return 'Активна'
    return 'Не активна'

@register.filter(name='practice_type_str')
def practice_type_str(type_of):
	for tup in PRACTICE_TYPE:
		if tup[0] == type_of:
			return tup[1]

@register.filter(name='doc_type_str')
def doc_type_str(type_of):
	for tup in DOCUMENT_KEYS:
		if tup[0] == type_of:
			return tup[1]

@register.filter(name='doc_status_str')
def doc_status_str(status):
	for tup in DOCUMENT_STATUS:
		if tup[0] == status:
			return tup[1]