from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions,generics
from .models import UserProfile,SavedJob,EducationEntry,WorkExperience,ResumeSummary
from .serializers import User_Registration_Serializer,User_Login_Serializer,UserProfileSerializer,ResumeSummarySerializer,WorkExperienceSerializer,EducationEntrySerializer
from users.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
import json
import requests
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from django.conf import settings
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from random import randint
from django.core.files import File
import glob
from .skill_utils import get_skills_for_role, analyze_skill_gap

INSTITUTION_API = "http://127.0.0.1:9000/api/Institution"

# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

#User Registration
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
    
#user login 
class User_Login_View(APIView):
    def post(self, request,format=None):
        serializer = User_Login_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token=get_tokens_for_user(user)
            return Response({
                'token': token,
                'msg': 'Login Success'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
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
class User_Profile_View(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            if UserProfile.objects.filter(user=request.user).exists():
                return Response({'error': 'User profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserProfileSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, context={'request': request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'User profile not found. Use POST to create.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# New: Job Listing & Application
# ===============================

class InstitutionJobListView(APIView):
    """
    Get list of jobs from the institution project
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            res = requests.get(f"{INSTITUTION_API}/jobs/")
            res.raise_for_status()
            jobs = res.json()
            return Response(jobs, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({'error': 'Could not connect to institution API', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
class InstitutionJobDetailView(APIView):
    """
    Get list of jobs from the institution project
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request,pk):
        try:
            res = requests.get(f"{INSTITUTION_API}/jobs/{pk}/")
            res.raise_for_status()
            jobs = res.json()
            return Response(jobs, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({'error': 'Could not connect to institution API', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class SaveJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        user = request.user
        saved, created = SavedJob.objects.get_or_create(user=user, job_id=job_id)
        if created:
            return Response({'msg': 'Job saved successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'msg': 'Job already saved'}, status=status.HTTP_200_OK)

# Unsave a job
class UnsaveJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, job_id):
        user = request.user
        deleted, _ = SavedJob.objects.filter(user=user, job_id=job_id).delete()
        if deleted:
            return Response({'msg': 'Job removed from saved list'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Job not found in saved list'}, status=status.HTTP_404_NOT_FOUND)

# Check if a job is saved
class IsJobSavedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, job_id):
        user = request.user
        is_saved = SavedJob.objects.filter(user=user, job_id=job_id).exists()
        return Response({'is_saved': is_saved}, status=status.HTTP_200_OK)

# List saved jobs
class SavedJobsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        saved_jobs = SavedJob.objects.filter(user=user).order_by('-saved_at')
        job_ids = [job.job_id for job in saved_jobs]

        # Fetch details from institution API
        saved_jobs_data = []
        for job_id in job_ids:
            try:
                res = requests.get(f"{INSTITUTION_API}/jobs/{job_id}/")
                if res.status_code == 200:
                    saved_jobs_data.append(res.json())
            except requests.exceptions.RequestException:
                continue  # skip if fetch fails

        return Response(saved_jobs_data, status=status.HTTP_200_OK)
#Apply for job
class ApplyToJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        user = request.user
        email = user.email
        resume_file = request.FILES.get("resume_file")

        if not resume_file:
            return Response({"error": "Resume file is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        profile_data = {
            "name": f"{profile.user.name}".strip(),
            "skills": profile.skills,
            "location": profile.location,
            "experience": profile.experience,
            "education": profile.education,
            "salary_expectation": profile.salary_expectation,
            "contact_number": profile.contact_number,
            "resume": request.build_absolute_uri(profile.resume.url) if profile.resume else None
        }

        data = {
            "email": email,
            "profile": json.dumps(profile_data),
        }

        files = {"resume_file": resume_file}

        try:
            response = requests.post(
                f"{INSTITUTION_API}/jobs/{job_id}/apply/",
                data=data,
                files=files
            )
            if response.status_code == 201:
                return Response({"msg": "Application sent."}, status=status.HTTP_201_CREATED)
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Institution server error", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        

class MyApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return Response({'error': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)

        user_email = request.user.email
        headers = {
            'Authorization': auth_header  # Forward the same token from frontend
        }

        try:
            res = requests.get(f"{INSTITUTION_API}/public-applications/?email={user_email}")
            res.raise_for_status()
            return Response(res.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({'error': 'Failed to fetch applications', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class HasAppliedProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        user_email = request.user.email
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header:
            return Response({"error": "Authorization header missing"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Forward request to institution
            institution_url = f"{INSTITUTION_API}/public-applications/check-applied/"
            params = {"email": user_email, "job_id": job_id}
            headers = {"Authorization": auth_header}

            response = requests.get(institution_url, headers=headers, params=params)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Failed to contact institution API", "details": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class ResumeSummaryView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ResumeSummarySerializer

    def get_object(self):
        profile = UserProfile.objects.get(user=self.request.user)
        obj, _ = ResumeSummary.objects.get_or_create(profile=profile)
        return obj


class WorkExperienceListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkExperienceSerializer

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        return WorkExperience.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(profile=profile)


class WorkExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkExperienceSerializer

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        return WorkExperience.objects.filter(profile=profile)


class EducationEntryListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EducationEntrySerializer

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        return EducationEntry.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(profile=profile)


class EducationEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EducationEntrySerializer

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        return EducationEntry.objects.filter(profile=profile)


class ScrapeJobsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # 1. Get user profile
            profile = UserProfile.objects.get(user=request.user)

            skill = profile.skills or ""
            location = profile.location or ""
            experience = profile.experience or "0"  # default to 0 years

            if not skill or not location:
                return Response({"error": "Skill and location must be provided in your profile."},
                                status=status.HTTP_400_BAD_REQUEST)

            print(f"Scraping for: Skill={skill}, Location={location}, Experience={experience}")

            # 2. URL generator
            def generate_url(page, skill, location, experience):
                base = f"https://www.naukri.com/{skill.replace(',', '-')}-jobs-in-{location}-experience"
                if page > 1:
                    base += f"-{page}"
                location_param_encoded = f"{location} experience".replace(" ", "%20")
                return f"{base}?k={skill}&l={location_param_encoded}&experience={experience}&nignbevent_src=jobsearchDeskGNB"

            def extract_rating(rating_a):
                if rating_a is None or rating_a.find('span', class_="main-2") is None:
                    return "None"
                return rating_a.find('span', class_="main-2").text

            def parse_job_data_from_soup(page_jobs, job_list):
                for job in page_jobs:
                    job = BeautifulSoup(str(job), 'html.parser')
                    job_title = job.find('div', class_="row1").a.text.strip() if job.find('div', class_="row1") else "N/A"
                    company_name = job.find('div', class_="row2").span.a.text.strip() if job.find('div', class_="row2") else "N/A"
                    rating = extract_rating(job.find('div', class_="row2").span)
                    
                    try:
                        job_details = job.find('div', class_="row3").find('div', class_="job-details")
                        experience = job_details.find('span', class_="exp-wrap").span.span.text.strip()
                        location = job_details.find('span', class_="loc-wrap ver-line").span.span.text.strip()
                    except Exception:
                        experience = "N/A"
                        location = "N/A"
                    
                    try:
                        salary = job_details.find('span', class_=lambda x: x and "sal" in x).text.strip()
                    except:
                        salary = "N/A"
                    
                    try:
                        min_requirements = job.find('div', class_="row4").span.text.strip()
                    except:
                        min_requirements = "N/A"


                    job_list.append([
                        job_title, company_name, rating, experience, location, salary, min_requirements
                    ])

            # 3. Start scraping
            options = webdriver.ChromeOptions()
            options.headless = True
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            job_list = []
            for page in range(1, 11):
                print(f"Scraping Page {page}")
                driver.get(generate_url(page, skill, location, experience))
                sleep(randint(4, 8))  # random delay
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_containers = soup.find_all("div", class_="srp-jobtuple-wrapper")
                parse_job_data_from_soup(job_containers, job_list)

            driver.quit()

            # 4. Save to Excel
            df = pd.DataFrame(job_list, columns=["Job Title", "Company Name", "Rating", "Experience", "Location", "Salary", "Minimum Requirements"])
            filename = f"Naukri_Jobs_{skill}_{location}_exp{experience}_{request.user.id}.xlsx"
            filepath = os.path.join("job_exports", filename)

            os.makedirs("job_exports", exist_ok=True)
            df.to_excel(filepath, index=False)
            with open(filepath, 'rb') as f:
                profile.scraped_file.save(filename, File(f), save=True)

            return Response({"message": "Scraping completed.", "file": filepath}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class JobRecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Keep the skills string intact (commas allowed)
        skills = profile.skills.strip().replace(' ', '').lower() if profile.skills else ''
        location = profile.location.strip().lower() if profile.location else ''
        experience = str(profile.experience or 0)

        # Log the matching values for debugging
        print("Skills:", skills)
        print("Location:", location)
        print("Experience:", experience)

        # Adjust to match your actual folder name
        scraped_folder = os.path.join(settings.BASE_DIR, 'job_exports')
        pattern = os.path.join(scraped_folder, f"Naukri_Jobs_{skills}_{location}_exp{experience}*.xlsx")

        print("Searching for file with pattern:", pattern)

        matching_files = glob.glob(pattern)
        if not matching_files:
            return Response({
                'error': f"Scraped job file not found for skill: {skills}, location: {location}, exp: {experience}"
            }, status=status.HTTP_404_NOT_FOUND)

        file_path = matching_files[0]
        print("Matched file:", file_path)

        try:
            df = pd.read_excel(file_path)
            df = df.fillna('')
            recommendations = df.head(10).to_dict(orient='records')  # Return top 10 jobs
            return Response({'recommendations': recommendations}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Failed to read Excel file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SkillGapAnalyzerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        desired_role = request.data.get("desired_role", "")
        
        if not desired_role:
            return Response({"error": "desired_role is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        user_skills_raw = user_profile.skills
        if not user_skills_raw:
            return Response({"error": "No skills found in user profile."}, status=status.HTTP_400_BAD_REQUEST)

        current_skills = [skill.strip().lower() for skill in user_skills_raw.split(',') if skill.strip()]
        required_skills = get_skills_for_role(desired_role)

        if not required_skills:
            return Response({"error": f"No skill data available for role: {desired_role}"}, status=status.HTTP_404_NOT_FOUND)

        missing_skills = analyze_skill_gap(current_skills, required_skills)

        return Response({
            "desired_role": desired_role,
            "required_skills": required_skills,
            "provided_skills": current_skills,
            "missing_skills": missing_skills,
            "total_missing": len(missing_skills),
        }, status=status.HTTP_200_OK)