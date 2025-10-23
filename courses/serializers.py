from rest_framework import serializers
from .models import Category, Instructor, Course, Chapter, Video, Attachment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class InstructorSerializer(serializers.ModelSerializer):
    user_mobile = serializers.CharField(source='user.mobile', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Instructor
        fields = ['id', 'user', 'user_mobile', 'user_full_name', 'bio', 'expertise', 'avatar']

class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'title', 'file', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        try:
            return obj.file.url
        except Exception:
            return None

class VideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'chapter', 'title', 'video_file', 'video_url', 'duration', 'order', 'is_free', 'created_at']

    def get_video_url(self, obj):
        try:
            return obj.video_file.url
        except Exception:
            return None

class ChapterSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'course', 'title', 'order', 'videos']

class CourseListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    instructors = InstructorSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'category', 'price',
            'course_type', 'is_active', 'instructors', 'image'
        ]

class CourseDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    instructors = InstructorSerializer(many=True, read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id','title','slug','description','image','category','price',
            'course_type','start_date','registration_deadline','access_duration_days',
            'is_active','instructors','chapters','attachments','created_at'
        ]
