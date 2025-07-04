from django.shortcuts import render 
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import InstitutionProfile,JobPost,JobApplication,SavedApplication
from rest_framework import status,permissions,generics
from .serializers import User_Registration_Serializer , UserLoginSerializer , InstitutionProfileSerializer,JobPostSerializer,JobApplicationSerializer
from django.contrib.auth import authenticate
from users.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
import json

#generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class User_Registration_View(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = User_Registration_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # ✅ Important fix
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({
            'token': token,
            'msg': 'Registration Success'
        }, status=status.HTTP_201_CREATED)
    
class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token=get_tokens_for_user(user)
            return Response({'token':token,'msg':'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
        


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract the refresh token from the request body
            refresh_token = request.data.get("refresh")
            
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Create a RefreshToken object from the provided refresh token
            token = RefreshToken(refresh_token)
            
            # Blacklist the refresh token to invalidate it
            token.blacklist()
            
            return Response({"msg": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        
        except TokenError as e:
            # Catching errors related to invalid token format
            return Response({"error": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # General exception handling for any unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
#user profile view
class Institution_Profile_View(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Attempt to get the institution profile associated with the logged-in user
            institution_profile = InstitutionProfile.objects.get(user=request.user)
            serializer = InstitutionProfileSerializer(institution_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InstitutionProfile.DoesNotExist:
            return Response({'error': 'Institution profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            # Check if the user already has an institution profile
            if InstitutionProfile.objects.filter(user=request.user).exists():
                return Response({'error': 'Institution profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Pass data and context to the serializer
            serializer = InstitutionProfileSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Save the profile
                serializer.save()  # Ensuring the profile is linked to the current logged-in user
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            # Attempt to update the existing institution profile
            institution_profile = InstitutionProfile.objects.get(user=request.user)
            serializer = InstitutionProfileSerializer(institution_profile, data=request.data, context={'request': request}, partial=True)
            if serializer.is_valid():
                serializer.save()  # Saving the updated data
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except InstitutionProfile.DoesNotExist:
            return Response({'detail': 'Institution profile not found. Use POST to create.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#job creation
class JobPostCreateView(generics.CreateAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            profile = InstitutionProfile.objects.get(user=self.request.user)
        except InstitutionProfile.DoesNotExist:
            raise PermissionDenied("You must be an institution to create a job post.")
        serializer.save(posted_by=profile)

# Update/delete requires auth and institution ownership
class JobPostUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobPost.objects.filter(posted_by__user=self.request.user)

# Public job list view (no authentication required)
class PublicJobListView(generics.ListAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer
    permission_classes = [AllowAny]

# Public job detail view (no authentication required)
class PublicJobDetailView(generics.RetrieveAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views
        instance.views = instance.views + 1
        instance.save(update_fields=['views'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


#institution job posted
class InstitutionJobListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the institution profile for the authenticated user
            profile = InstitutionProfile.objects.get(user=request)

            # Get job posts posted by this institution
            jobs = JobPost.objects.filter(posted_by=profile)

            # Serialize the job posts
            serializer = JobPostSerializer(jobs, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except InstitutionProfile.DoesNotExist:
            return Response({'error': 'Institution profile not found'}, status=status.HTTP_404_NOT_FOUND)
        


class ApplyToJobView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, job_id):
        try:
            job = JobPost.objects.get(id=job_id)
        except JobPost.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        email = request.data.get("email")
        resume_file = request.FILES.get("resume_file")
        profile_data = request.data.get("profile")

        if not email or not resume_file or not profile_data:
            return Response({"error": "Email, resume, and profile are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile_data = json.loads(profile_data)
        except json.JSONDecodeError:
            return Response({"error": "Invalid profile format."}, status=status.HTTP_400_BAD_REQUEST)

        if JobApplication.objects.filter(job=job, email=email).exists():
            return Response({"error": "Already applied."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = JobApplicationSerializer(data={
            "job": job.id,
            "email": email,
            "resume_link": resume_file,
            "profile_data": profile_data,
        })

        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Application submitted successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstitutionJobApplicationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            institution_profile = InstitutionProfile.objects.get(user=request.user)
            jobs_posted = JobPost.objects.filter(posted_by=institution_profile)
            applications = JobApplication.objects.filter(job__in=jobs_posted)

            # Filter by status if provided
            status_filter = request.query_params.get('status')
            if status_filter:
                applications = applications.filter(status__iexact=status_filter)

            serializer = JobApplicationSerializer(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except InstitutionProfile.DoesNotExist:
            return Response(
                {"error": "Institution profile not found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )

            
class UpdateApplicationStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, app_id):
        try:
            application = JobApplication.objects.get(id=app_id)
            status_choice = request.data.get("status")

            if status_choice not in dict(JobApplication.STATUS_CHOICES):
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

            application.status = status_choice
            application.status_updated_at = timezone.now()

            if status_choice == "Accepted":
                job = application.job
                now = timezone.now()

                if not job.hire_date:
                    job.hire_date = now
                    if job.created_at:
                        job.time_to_hire = now - job.created_at
                    job.save(update_fields=["hire_date", "time_to_hire"])

                if job.created_at:
                    application.time_to_hire = now - job.created_at

            application.save()

            return Response({"msg": f"Application {status_choice}"}, status=status.HTTP_200_OK)

        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

class PublicApplicationsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get("email")
        applications = JobApplication.objects.filter(email=email)
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    

class SaveApplicationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, app_id):
        try:
            institution = InstitutionProfile.objects.get(user=request.user)
            application = JobApplication.objects.get(id=app_id)

            if application.job.posted_by != institution:
                return Response({"error": "Not authorized to save this application."}, status=status.HTTP_403_FORBIDDEN)

            _, created = SavedApplication.objects.get_or_create(
                institution=institution, application=application
            )
            msg = "Application saved." if created else "Application already saved."
            return Response({"msg": msg}, status=status.HTTP_200_OK)

        except InstitutionProfile.DoesNotExist:
            return Response({"error": "Institution profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)


class UnsaveApplicationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, app_id):
        try:
            institution = InstitutionProfile.objects.get(user=request.user)
            saved = SavedApplication.objects.get(institution=institution, application__id=app_id)
            saved.delete()
            return Response({"msg": "Application unsaved."}, status=status.HTTP_200_OK)
        except InstitutionProfile.DoesNotExist:
            return Response({"error": "Institution profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except SavedApplication.DoesNotExist:
            return Response({"error": "Application not saved."}, status=status.HTTP_404_NOT_FOUND)


class IsApplicationSavedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, app_id):
        try:
            institution = InstitutionProfile.objects.get(user=request.user)
            is_saved = SavedApplication.objects.filter(institution=institution, application__id=app_id).exists()
            return Response({"saved": is_saved}, status=status.HTTP_200_OK)
        except InstitutionProfile.DoesNotExist:
            return Response({"error": "Institution profile not found."}, status=status.HTTP_404_NOT_FOUND)


class SavedApplicationsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            institution = InstitutionProfile.objects.get(user=request.user)
            saved_apps = SavedApplication.objects.filter(institution=institution).select_related('application')
            applications = [s.application for s in saved_apps]
            serializer = JobApplicationSerializer(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InstitutionProfile.DoesNotExist:
            return Response({"error": "Institution profile not found."}, status=status.HTTP_404_NOT_FOUND)

class PerformanceDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            institution = InstitutionProfile.objects.get(user=request.user)
        except InstitutionProfile.DoesNotExist:
            return Response({"error": "Institution profile not found"}, status=404)

        job_data = []
        jobs = JobPost.objects.filter(posted_by=institution)

        for job in jobs:
            applications = JobApplication.objects.filter(job=job)
            accepted_apps = applications.filter(status="Accepted")

            time_to_hire_days_list = []
            for app in accepted_apps:
                if job.created_at and app.status_updated_at:
                    delta_days = (app.status_updated_at - job.created_at).days
                    time_to_hire_days_list.append(delta_days)

            avg_time_to_hire = (
                sum(time_to_hire_days_list) / len(time_to_hire_days_list)
                if time_to_hire_days_list else None
            )

            job_data.append({
                "job_title": job.title,
                "views": job.views,
                "applications": applications.count(),
                "time_to_hire_days": round(avg_time_to_hire, 2) if avg_time_to_hire is not None else None,
            })

        return Response(job_data)


class CheckAppliedInstitutionView(APIView):
    def get(self, request):
        email = request.GET.get("email")
        job_id = request.GET.get("job_id")

        if not email or not job_id:
            return Response({"error": "Missing email or job_id"}, status=status.HTTP_400_BAD_REQUEST)

        has_applied = JobApplication.objects.filter(email=email, job_id=job_id).exists()
        return Response({"has_applied": has_applied}, status=status.HTTP_200_OK)