from django.contrib import admin
from main.forms import MyUserAdmin
from main.models import *

admin.site.register(User, MyUserAdmin)
admin.site.register(StudentProfile)
admin.site.register(CuratorProfile)
admin.site.register(Practice)
admin.site.register(StudyGroup)
admin.site.register(StudentToPractice)
admin.site.register(DocumentTemplate)
admin.site.register(Document)
