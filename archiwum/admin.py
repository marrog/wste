from archiwum.models import *
from django.contrib import admin
from django.contrib.sites.models import Site
from django.conf import settings

admin.site.register((Subject, Student, Instructor, Dean, DocumentPublic, Document))
admin.site.register((Lesson, Grade))

class StudentgroupAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Studentgroup, StudentgroupAdmin)

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('number','slug')
    prepopulated_fields = {'slug': ('number',)}

admin.site.register(Semester, SemesterAdmin)

class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(DocumentCategory, DocumentCategoryAdmin)

class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(DocumentType, DocumentTypeAdmin)

class NewsAdmin(admin.ModelAdmin):
    readonly_fields = ('author',)
    def save_model(self,request,obj,form,change):
        obj.author = request.user
        obj.save()

admin.site.register(News, NewsAdmin)

