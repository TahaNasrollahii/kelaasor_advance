from django.contrib import admin
from .models import Category, Instructor, Course, Chapter, Video, Attachment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'expertise']
    search_fields = ['user__mobile', 'user__full_name', 'expertise']
    ordering = ['user']


class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ['title', 'video_file', 'order', 'duration', 'is_free']
    readonly_fields = ['duration']


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1
    fields = ['title', 'file']


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ['title', 'order']
    inlines = [VideoInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'course__title']
    inlines = [VideoInline]
    ordering = ['course', 'order']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'order', 'is_free', 'created_at']
    list_filter = ['chapter__course', 'is_free']
    search_fields = ['title', 'chapter__title', 'chapter__course__title']
    ordering = ['chapter', 'order']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'uploaded_at']
    search_fields = ['title', 'course__title']
    list_filter = ['course']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'price', 'course_type', 'is_active', 'start_date']
    list_filter = ['category', 'is_active', 'course_type']
    search_fields = ['title', 'slug', 'description', 'instructors__user__full_name']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['start_date']
    inlines = [ChapterInline, AttachmentInline]
    filter_horizontal = ['instructors']
