from django.contrib import admin

# Register your models here.
from .models import Lead,Teacher,Note,Group

admin.site.register(Lead)
admin.site.register(Teacher)
admin.site.register(Group)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'text', 'created_at')
    list_filter = ('teacher', 'created_at')
    search_fields = ('text',)