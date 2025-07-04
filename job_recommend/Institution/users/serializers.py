from rest_framework import serializers
from users.models import User,InstitutionProfile,JobPost,JobApplication
from rest_framework.authtoken.models import Token
from xml.dom import VALIDATION_ERR
from django.utils.encoding import smart_str, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.conf import settings

#Institution Register
class User_Registration_Serializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name','password','password2','tc']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password Doesn't Match")
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
#institution Login  
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']

#after login       
class InstitutionProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    logo = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = InstitutionProfile
        fields = ['id', 'email', 'name', 'location', 'contact_number', 'description', 'website', 'logo']

    def get_email(self, obj):
        return obj.user.email if obj.user else None

    def get_name(self, obj):
        return obj.user.name if obj.user else None

    def create(self, validated_data):
        user = self.context['request'].user  # Get the current logged-in user
        return InstitutionProfile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

#job post 
class JobPostSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='posted_by.user.name', read_only=True)
    logo = serializers.SerializerMethodField()
    website = serializers.CharField(source='posted_by.website', read_only=True)
    company_description = serializers.CharField(source='posted_by.description', read_only=True)
    time_to_hire = serializers.SerializerMethodField()


    class Meta:
        model = JobPost
        fields = [
            'id', 'company_name', 'logo', 'website', 'company_description',
            'title', 'description', 'requirements', 'location', 'salary_range',
            'application_deadline','no_opening', 'is_open', 'created_at', 'updated_at','time_to_hire'
        ]
    def get_time_to_hire(self, obj):
        return obj.time_to_hire
    
    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.posted_by.logo and request:
            return request.build_absolute_uri(obj.posted_by.logo.url)
        return None


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.SerializerMethodField()
    applied_at_formatted = serializers.SerializerMethodField()
    time_to_hire_days = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()  # New field added

    class Meta:
        model = JobApplication
        fields = '__all__'  # keep all model fields + new SerializerMethodFields
        # Note: '__all__' will include model fields, 
        # but SerializerMethodFields are included automatically.

    def get_job_title(self, obj):
        return obj.job.title if obj.job else None

    def get_applied_at_formatted(self, obj):
        if obj.applied_at:
            return obj.applied_at.strftime("%Y-%m-%d %H:%M")
        return None

    def get_time_to_hire_days(self, obj):
        if obj.time_to_hire:
            return obj.time_to_hire.days
        return None

    def get_company_name(self, obj):
        if obj.job and obj.job.posted_by and obj.job.posted_by.user:
            return obj.job.posted_by.user.name
        return None

    
class PerformanceMetricsSerializer(serializers.Serializer):
    job_title = serializers.CharField()
    views = serializers.IntegerField()
    applications = serializers.IntegerField()
    time_to_hire_days = serializers.FloatField(allow_null=True)