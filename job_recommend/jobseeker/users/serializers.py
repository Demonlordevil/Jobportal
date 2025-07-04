from rest_framework import serializers
from .models import User,UserProfile,ResumeSummary,EducationEntry,WorkExperience
from rest_framework.authtoken.models import Token
from xml.dom import VALIDATION_ERR
from django.utils.encoding import smart_str, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
import requests

#user Registration
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
    
#user login 
class User_Login_Serializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']


#after Login view
class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    resume = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ['id','email', 'name', 'skills', 'location', 'experience', 'salary_expectation', 'education', 'contact_number', 'resume']

    def get_email(self, obj):
        return obj.user.email if obj.user else None

    def get_name(self, obj):
        return obj.user.name if obj.user else None

    def create(self, validated_data):
        # Automatically use the user from the request context
        user = self.context['request'].user
        return UserProfile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ResumeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeSummary
        fields = ['id', 'summary']

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'job_title', 'company', 'start_date', 'end_date', 'description']

class EducationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationEntry
        fields = ['id', 'institution', 'degree', 'field', 'start_year', 'end_year']

