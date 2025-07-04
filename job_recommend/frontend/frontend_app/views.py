import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import json

# ======================= PUBLIC VIEWS =======================
def home(request):
    return render(request, 'user/home.html')

def about(request):
    return render(request, 'user/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        full_message = f"From: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                settings.EMAIL_HOST_USER,     # From
                ['adityatanvoji@gmail.com'],    # To
                fail_silently=False,
            )
            messages.success(request, "Message sent successfully!")
        except Exception as e:
            messages.error(request, f"Failed to send message: {e}")

    return render(request, 'user/contact.html')


def industries(request):
    return render(request, 'user/industries.html')


# ======================= USER VIEWS =========================
def register_user(request):
    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'name': request.POST.get('name'),
            'password': request.POST.get('password'),
            'password2': request.POST.get('password2'),
            'tc': True
        }

        try:
            response = requests.post(settings.API_BASE_URL_USER + 'register/', data=data)

            if response.status_code == 201:
                messages.success(request, 'Registration Successful. Please login.')
                return redirect('login_user')

            try:
                # Try to parse JSON error
                errors = response.json()
                if errors:
                    first_value = list(errors.values())[0]
                    error_msg = first_value[0] if isinstance(first_value, list) else str(first_value)
                else:
                    error_msg = 'Registration failed. No error message provided.'

            except ValueError:
                # Response wasn't JSON — show raw text instead
                error_msg = f"Error: {response.text}"

            messages.error(request, error_msg)

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Connection error: {str(e)}")

    return render(request, 'user/user_register.html')

def jobseeker_contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        full_message = f"From: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                settings.EMAIL_HOST_USER,     # From
                ['adityatanvoji@gmail.com'],    # To
                fail_silently=False,
            )
            messages.success(request, "Message sent successfully!")
        except Exception as e:
            messages.error(request, f"Failed to send message: {e}")

    return render(request, 'jobseeker/contact.html')

def jobseeker_about(request):
    return render(request, 'jobseeker/about.html')

def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            # Send login request to the API
            response = requests.post(settings.API_BASE_URL_USER + 'login/', data={'email': email, 'password': password})

            # Print the entire response content to debug
           # print("Response Content:", response.text)

            if response.status_code == 200:
                # Attempt to extract token from the nested response
                response_data = response.json()
               # print("Response JSON:", response_data)  # Debug print
                token = response_data.get('token', {}).get('access')  # Access token from the nested 'token' dictionary

                if token:
                    # Store the token in session
                    request.session['user_token'] = token
                    #print("Token stored in session:", token)  # Debug print
                    
                    # Use token to fetch user profile
                    profile_response = requests.get(settings.API_BASE_URL_USER + 'profile/',
                                                    headers={'Authorization': f'Bearer {token}'})
                    
                    if profile_response.status_code == 200:
                        # Redirect to institution dashboard if profile exists
                        return redirect('dashboard_user')
                    else:
                        # Redirect to profile creation if profile doesn't exist
                        return redirect('create_user_profile')
                else:
                    messages.error(request, "Token not found in the response.")
            else:
                messages.error(request, "Invalid login credentials or API error.")
        except requests.exceptions.RequestException as e:
            # Handle potential request errors
            messages.error(request, f"Error connecting to the server: {str(e)}")
        
    return render(request, 'user/user_login.html')


def create_user_profile(request):
    # ✅ Correct session key (case-sensitive)
    token = request.session.get('user_token')
    if not token:
        return redirect('login_user')

    if request.method == 'POST':
        data = {
            'skills': request.POST.get('skills'),
            'location': request.POST.get('location'),
            'experience': request.POST.get('experience'),
            'education': request.POST.get('education'),
            'salary_expectation': request.POST.get('salary_expectation'),
            'contact_number': request.POST.get('contact_number'),
        }

        # ✅ Handle optional resume upload
        files = {'resume': request.FILES['resume']} if 'resume' in request.FILES else {}

        try:
            response = requests.post(
                settings.API_BASE_URL_USER + 'profile/',
                data=data,
                files=files,
                headers={'Authorization': f'Bearer {token}'}
            )

            if response.status_code == 201:
                return redirect('dashboard_user')
            else:
                messages.error(request, f"Failed to create profile: {response.text}")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error connecting to server: {str(e)}")

    return render(request, 'jobseeker/create_jobseeker_profile.html')


def view_user_profile(request):
    token = request.session.get('user_token')
    if not token:
        return redirect('login_user')

    response = requests.get(settings.API_BASE_URL_USER + 'profile/',
                            headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 200:
        profile = response.json()

        # Modify the resume URL if it exists
        resume_path = profile.get('resume')
        if resume_path:
            if resume_path.startswith('/'):
                resume_path = resume_path[1:]  # Remove leading slash if present
            profile['resume'] = f'{settings.API_BASE_URL}/{resume_path}'  # Use dynamic API_BASE_URL from settings

        return render(request, 'jobseeker/profile.html', {'profile': profile})
    else:
        return redirect('create_user_profile')


    

def edit_user_profile(request):
    token = request.session.get('user_token')
    if not token:
        return redirect('login_user')

    if request.method == 'POST':
        data = {
            'skills': request.POST.get('skills'),
            'location': request.POST.get('location'),
            'experience': request.POST.get('experience'),
            'education': request.POST.get('education'),
            'salary_expectation': request.POST.get('salary_expectation'),
            'contact_number': request.POST.get('contact_number'),
        }
        files = {'resume': request.FILES['resume']} if 'resume' in request.FILES else {}

        response = requests.put(settings.API_BASE_URL_USER + 'profile/',
                                data=data,
                                files=files,
                                headers={'Authorization': f'Bearer {token}'})
        if response.status_code == 200:
            messages.success(request, "Profile updated successfully.")
            return redirect('view_user_profile')
        else:
            messages.error(request, f"Update failed: {response.text}")

    # GET request: fetch profile to pre-fill form
    response = requests.get(settings.API_BASE_URL_USER + 'profile/',
                            headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 200:
        profile = response.json()
        return render(request, 'jobseeker/edit_profile.html', {'profile': profile})
    else:
        return redirect('create_user_profile')


def dashboard_user(request):
    token = request.session.get('user_token')
    
    if not token:
        return redirect('login_user')  # Redirect to login if token doesn't exist

    # Fetch institution profile data using the stored token
    response = requests.get(settings.API_BASE_URL_USER + 'profile/',
                            headers={'Authorization': f'Bearer {token}'})
    
    if response.status_code == 200:
        # Profile data fetched successfully, passing it to the template
        profile = response.json()
        resume_path = profile.get('resume')
        if resume_path:
            if resume_path.startswith('/'):
                resume_path = resume_path[1:]  # Remove leading slash if present
            profile['resume'] = f'{settings.API_BASE_URL}/{resume_path}'
        return render(request, 'jobseeker/dashboard.html', {'profile': profile})
    else:
        # If the profile data fetching fails, show an error and redirect
        messages.error(request, "Unable to fetch profile data. Please try again.")
        return redirect('create_user_profile')
    
def jobseeker_tools(request):
    return render(request, 'jobseeker/tools.html')

def recommendations_view(request):
    token = request.session.get('user_token')
    if not token:
        return redirect('login_user')

    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        # ✅ Call the scraper endpoint first
        scrape_response = requests.get(settings.API_BASE_URL_USER + 'scrape-jobs/', headers=headers)
        if scrape_response.status_code != 200:
            messages.warning(request, "Job scraping failed or partially completed.")

        # ✅ Then call the recommendations endpoint
        response = requests.get(settings.API_BASE_URL_USER + 'recommendations/', headers=headers)

        if response.status_code == 200:
            recommendations = response.json().get('recommendations', [])
        else:
            recommendations = []
            messages.error(request, "Failed to fetch recommendations.")

    except requests.exceptions.RequestException as e:
        recommendations = []
        messages.error(request, f"Error fetching data: {str(e)}")

    return render(request, 'jobseeker/recommendations.html', {'recommendations': recommendations})

def job_list(request):
    try:
        res = requests.get(f"{settings.API_BASE_URL_USER}jobs/")
        res.raise_for_status()
        jobs = res.json()
    except requests.exceptions.RequestException:
        jobs = []
    return render(request, 'jobseeker/job_list.html', {'jobs': jobs})

def saved_jobs_view(request):
    token = request.session.get('user_token')
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    saved_jobs = []
    error = None

    # Fetch saved jobs list from your API
    try:
        res = requests.get(f"{settings.API_BASE_URL_USER}saved-jobs/", headers=headers)
        res.raise_for_status()
        saved_jobs = res.json()  # List of saved job dicts
    except requests.exceptions.RequestException:
        error = "Failed to fetch saved jobs."

    return render(request, 'jobseeker/saved_jobs.html', {
        'saved_jobs': saved_jobs,
        'error': error,
    })


def job_detail(request, job_id):
    import requests
    from django.conf import settings
    from django.shortcuts import render, redirect

    token = request.session.get('user_token')
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    job = None
    is_saved = False
    is_applied = False
    error = None

    # Fetch job detail
    try:
        res = requests.get(f"{settings.API_BASE_URL_USER}jobs/{job_id}/", headers=headers)
        res.raise_for_status()
        job = res.json()
    except requests.exceptions.RequestException as e:
        error = "Failed to fetch job details."
        print("Job detail fetch error:", e)

    # Handle save/unsave POST request
    if request.method == 'POST' and token:
        try:
            action = request.POST.get('action')
            if action == 'save':
                response = requests.post(f"{settings.API_BASE_URL_USER}save-job/{job_id}/", headers=headers)
                response.raise_for_status()
            elif action == 'unsave':
                response = requests.delete(f"{settings.API_BASE_URL_USER}unsave-job/{job_id}/", headers=headers)
                response.raise_for_status()

            return redirect('job-detail', job_id=job_id)

        except Exception as e:
            error = "Failed to update saved status."
            print("Save/Unsave error:", e)

    # Check saved and applied status
    if token:
        try:
            # Check if job is saved
            saved_res = requests.get(f"{settings.API_BASE_URL_USER}saved-jobs/{job_id}/", headers=headers)
            if saved_res.status_code == 200:
                is_saved = saved_res.json().get("is_saved", False)

            # Check if job is applied
            applied_res = requests.get(f"{settings.API_BASE_URL_USER}check-applied/{job_id}/", headers=headers)
            if applied_res.status_code == 200:
                is_applied = applied_res.json().get("has_applied", False)

        except Exception as e:
            print("Status check error:", e)

    return render(request, 'jobseeker/job_detail.html', {
        'job': job,
        'job_id': job_id,
        'is_saved': is_saved,
        'is_applied': is_applied,
        'error': error
    })


def apply_job_with_profile(request, job_id):
    token = request.session.get('user_token')
    if not token:
        return redirect('login_user')

    response = requests.get(
        settings.API_BASE_URL_USER + 'profile/',
        headers={'Authorization': f'Bearer {token}'}
    )
    if response.status_code == 200:
        profile = response.json()

        # Fix resume URL
        resume_path = profile.get('resume')
        if resume_path:
            if resume_path.startswith('/'):
                resume_path = resume_path[1:]
            profile['resume'] = f"{settings.API_BASE_URL}/{resume_path}"
    else:
        return redirect('create_user_profile')

    return render(request, 'jobseeker/apply_job_form.html', {
        'profile': profile,
        'job_id': job_id
    })


def submit_application(request, job_id):
    if request.method == "POST":
        token = request.session.get("user_token")
        if not token:
            messages.error(request, "You must be logged in to apply.")
            return redirect('login')

        resume_file = request.FILES.get("resume_file")
        if not resume_file:
            messages.error(request, "Please upload your resume.")
            return redirect('apply-job-form', job_id=job_id)

        headers = {"Authorization": f"Bearer {token}"}
        files = {"resume_file": resume_file}

        try:
            response = requests.post(
                f"{settings.API_BASE_URL_USER}jobs/{job_id}/apply/",
                headers=headers,
                files=files
            )
            if response.status_code == 201:
                messages.success(request, "Application submitted successfully.")
            else:
                error_msg = response.json().get("error", "Something went wrong.")
                messages.error(request, error_msg)
        except Exception as e:
            messages.error(request, f"Server error: {str(e)}")

        return redirect('job-detail', job_id=job_id)

def my_applications_view(request):
    token = request.session.get('user_token')  # Get token from session
    if not token:
        return redirect('login_user')

    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(f"{settings.API_BASE_URL_USER}my-applications/", headers=headers)
        if response.status_code == 200:
            applications = response.json()
        else:
            applications = []
            # Optionally log or show an error message
    except requests.exceptions.RequestException as e:
        applications = []
        # Optionally log error or show message

    return render(request, 'jobseeker/my_applications.html', {'applications': applications})


def skill_gap_analyzer_view(request):
    token = request.session.get('user_token')  # JWT token saved in session during login
    if not token:
        return redirect('login_user')  # Redirect if user not authenticated

    result = None
    error_msg = None

    if request.method == 'POST':
        desired_role = request.POST.get('desired_role', '').strip()
        if desired_role:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }
            payload = {'desired_role': desired_role}

            try:
                response = requests.post(
                    f"{settings.API_BASE_URL_USER}analyze-skill-gap/",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                else:
                    error_msg = response.json().get('error', 'Failed to fetch data from API.')
            except requests.exceptions.RequestException as e:
                error_msg = f"Error connecting to API: {str(e)}"
        else:
            error_msg = "Please enter a desired role."

    return render(request, 'jobseeker/skill_gap_analyzer.html', {
        'result': result,
        'error_msg': error_msg,
    })
# ======================= INSTITUTION VIEWS =========================
def register_institute(request):
    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'name': request.POST.get('name'),
            'password': request.POST.get('password'),
            'password2': request.POST.get('password2'),
            'tc': True
        }
        response = requests.post(settings.API_BASE_URL_INSTITUTE + 'Institution_register/', data=data)
        if response.status_code == 201:
            messages.success(request, 'Registration Successful. Please login.')
            return redirect('login_institute')
        else:
            try:
                errors = response.json()
                if errors:
                    first_value = list(errors.values())[0]
                    error_msg = first_value[0] if isinstance(first_value, list) else first_value
                else:
                    error_msg = 'Registration Failed'
            except Exception:
                error_msg = 'Unexpected error occurred during registration.'
            messages.error(request, error_msg)
    return render(request, 'user/institute_register.html')


def login_institute(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            # Send login request to the API
            response = requests.post(settings.API_BASE_URL_INSTITUTE + 'Institution_login/', data={'email': email, 'password': password})

            # Print the entire response content to debug
           # print("Response Content:", response.text)

            if response.status_code == 200:
                # Attempt to extract token from the nested response
                response_data = response.json()
               # print("Response JSON:", response_data)  # Debug print
                token = response_data.get('token', {}).get('access')  # Access token from the nested 'token' dictionary

                if token:
                    # Store the token in session
                    request.session['institute_token'] = token
                    #print("Token stored in session:", token)  # Debug print
                    
                    # Use token to fetch user profile
                    profile_response = requests.get(settings.API_BASE_URL_INSTITUTE + 'Institution_profile/',
                                                    headers={'Authorization': f'Bearer {token}'})
                    
                    if profile_response.status_code == 200:
                        # Redirect to institution dashboard if profile exists
                        return redirect('dashboard_institution')
                    else:
                        # Redirect to profile creation if profile doesn't exist
                        return redirect('create_institution_profile')
                else:
                    messages.error(request, "Token not found in the response.")
            else:
                messages.error(request, "Invalid login credentials or API error.")
        except requests.exceptions.RequestException as e:
            # Handle potential request errors
            messages.error(request, f"Error connecting to the server: {str(e)}")
        
    return render(request, 'user/institute_login.html')


def Institutionabout(request):
    return render(request, 'institution/about.html')

def contact_institution(request):
    if request.method == 'POST':
        name = request.POST['institution_name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        full_message = f"From: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                settings.EMAIL_HOST_USER,     # From
                ['adityatanvoji@gmail.com'],    # To
                fail_silently=False,
            )
            messages.success(request, "Message sent successfully!")
        except Exception as e:
            messages.error(request, f"Failed to send message: {e}")

    return render(request, 'institution/contact.html')

def create_institution_profile(request):
    token = request.session.get('institute_token')
    if not token:
        return redirect('login_institute')

    if request.method == 'POST':
        data = {
            'location': request.POST.get('location'),
            'contact_number': request.POST.get('contact_number'),
            'description': request.POST.get('description'),
            'website': request.POST.get('website'),
        }
        files = {'logo': request.FILES['logo']} if 'logo' in request.FILES else {}

        response = requests.post(settings.API_BASE_URL_INSTITUTE + 'Institution_profile/',
                                 data=data,
                                 files=files,
                                 headers={'Authorization': f'Bearer {token}'})
        if response.status_code == 201:
            return redirect('dashboard_institution')
        else:
            messages.error(request, f"Failed to create profile: {response.text}")
    return render(request, 'institution/create_institution_profile.html')

def view_institution_profile(request):
    token = request.session.get('institute_token')
    if not token:
        return redirect('login_institute')

    response = requests.get(settings.API_BASE_URL_INSTITUTE + 'Institution_profile/',
                            headers={'Authorization': f'Bearer {token}'})
    
    if response.status_code == 200:
        profile = response.json()

        # Check and update logo URL if necessary
        logo_path = profile.get('logo')
        if logo_path:
            if logo_path.startswith('/'):
                logo_path = logo_path[1:]  # Remove leading slash if present
            profile['logo'] = f'{settings.API_BASE_URL1}/{logo_path}'

        return render(request, 'institution/profile.html', {'profile': profile})
    else:
        return redirect('create_institution_profile')


    

def edit_institution_profile(request):
    token = request.session.get('institute_token')
    if not token:
        return redirect('login_institute')

    if request.method == 'POST':
        data = {
            'location': request.POST.get('location'),
            'contact_number': request.POST.get('contact_number'),
            'description': request.POST.get('description'),
            'website': request.POST.get('website'),
        }
        files = {'logo': request.FILES['logo']} if 'logo' in request.FILES else {}

        response = requests.put(settings.API_BASE_URL_INSTITUTE + 'Institution_profile/',
                                data=data,
                                files=files,
                                headers={'Authorization': f'Bearer {token}'})
        if response.status_code == 200:
            messages.success(request, "Profile updated successfully.")
            return redirect('view_institution_profile')
        else:
            messages.error(request, f"Update failed: {response.text}")

    # GET request: fetch profile to pre-fill form
    response = requests.get(settings.API_BASE_URL_INSTITUTE + 'Institution_profile/',
                            headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 200:
        profile = response.json()
        return render(request, 'institution/edit_profile.html', {'profile': profile})
    else:
        return redirect('create_institution_profile')


def dashboard_institution(request):
    token = request.session.get('institute_token')
    
    if not token:
        return redirect('login_institute')  # Redirect to login if token doesn't exist

    # Fetch institution profile data using the stored token
    response = requests.get(settings.API_BASE_URL_INSTITUTE + 'Institution_profile/',
                            headers={'Authorization': f'Bearer {token}'})
    
    if response.status_code == 200:
        # Profile data fetched successfully, passing it to the template
        profile = response.json()

        # Check and update logo URL if necessary
        logo_path = profile.get('logo')
        if logo_path:
            if logo_path.startswith('/'):
                logo_path = logo_path[1:]  # Remove leading slash if present
            profile['logo'] = f'{settings.API_BASE_URL1}/{logo_path}'  # Prepend the base URL
        
        # Return the profile to the template
        return render(request, 'institution/dashboard.html', {'profile': profile})
    else:
        # If the profile data fetching fails, show an error and redirect
        messages.error(request, "Unable to fetch profile data. Please try again.")
        return redirect('create_institution_profile')


def Institution_tools(request):
    return render(request, 'institution/tools.html')

def job_performance(request):
    return render(request, 'institutionlogedin/job_performance.html')

def export_applicants(request):
    return render(request, 'institutionlogedin/export_applicants.html')

def create_job_post(request):
    error = None
    token = request.session.get('institute_token')

    if request.method == 'POST':
        data = {
            "title": request.POST.get('title'),
            "description": request.POST.get('description'),
            "requirements": request.POST.get('requirements'),
            "location": request.POST.get('location'),
            "salary_range": request.POST.get('salary_range'),
            "no_opening": request.POST.get('no_opening'),
            "application_deadline": request.POST.get('application_deadline'),
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            res = requests.post(
                f"{settings.API_BASE_URL_INSTITUTE}create/",
                data=data,
                headers=headers
            )
            if res.status_code == 201:
                # ✅ Redirect to dashboard after success
                return redirect('dashboard_institution')  # Replace with your dashboard view name
            else:
                error = res.json().get('detail', 'Something went wrong.')
        except requests.exceptions.RequestException:
            error = "Failed to connect to API."

    return render(request, 'institution/create_job.html', {'error': error})


def institution_applications(request):
    token = request.session.get('institute_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    applications = []
    saved_apps = []
    error = None

    try:
        # Get all applications
        response = requests.get(f"{settings.API_BASE_URL_INSTITUTE}applications/", headers=headers)
        if response.status_code == 200:
            applications = response.json()
        else:
            error = response.json().get("error", "Failed to fetch applications.")
        
        # Get saved applications
        saved_response = requests.get(f"{settings.API_BASE_URL_INSTITUTE}saved-applications/", headers=headers)
        if saved_response.status_code == 200:
            saved_apps = saved_response.json()
        else:
            saved_apps = []

    except Exception as e:
        error = "An error occurred while fetching applications."
        print("Fetch error:", e)

    saved_ids = {app['id'] for app in saved_apps}

    for app in applications:
        # Convert datetime string to datetime object
        if isinstance(app.get('applied_at'), str):
            app['applied_at'] = datetime.fromisoformat(app['applied_at'].replace('Z', '+00:00'))

        # Mark if the application is saved
        app['is_saved'] = app['id'] in saved_ids

        # Construct full resume URL if resume_link exists
        resume_link = app.get('resume_link')
        if resume_link:
            if resume_link.startswith('/'):
                resume_link = resume_link[1:]  # remove leading slash
            app['resume_url'] = f"{settings.API_BASE_URL1}/{resume_link}"
        else:
            app['resume_url'] = None

        # Parse profile_data (if it's a string, decode it)
        profile_data = app.get('profile_data')
        if isinstance(profile_data, str):
            try:
                import json
                app['profile_data'] = json.loads(profile_data)
            except json.JSONDecodeError:
                app['profile_data'] = {}
        elif profile_data is None:
            app['profile_data'] = {}

    return render(request, 'institution/applications.html', {
        'applications': applications,
        'error': error
    })


def update_application_status(request, app_id):
    if request.method == "POST":
        token = request.session.get('institute_token')
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        status_choice = request.POST.get("status")

        try:
            response = requests.patch(
                f"{settings.API_BASE_URL_INSTITUTE}applications/{app_id}/update/",
                headers=headers,
                data={"status": status_choice}
            )
            if response.status_code == 200:
                messages.success(request, "Application status updated.")
            else:
                messages.error(request, "Failed to update status.")
        except Exception as e:
            print("Update status error:", e)
            messages.error(request, "Error updating status.")

        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)

@require_POST
def save_application(request, app_id):
    token = request.session.get('institute_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    try:
        response = requests.post(f"{settings.API_BASE_URL_INSTITUTE}save-application/{app_id}/", headers=headers)
        if response.status_code == 200:
            messages.success(request, "Application saved.")
        else:
            messages.error(request, "Failed to save application.")
    except Exception as e:
        messages.error(request, "Error saving application.")
        print("Save error:", e)

    return redirect('institution-applications')

@require_POST
def unsave_application(request, app_id):
    token = request.session.get('institute_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    try:
        response = requests.delete(f"{settings.API_BASE_URL_INSTITUTE}unsave-application/{app_id}/", headers=headers)
        if response.status_code == 200:
            messages.success(request, "Application unsaved.")
        else:
            messages.error(request, "Failed to unsave application.")
    except Exception as e:
        messages.error(request, "Error unsaving application.")
        print("Unsave error:", e)

    return redirect('institution-applications')


def saved_applications(request):
    token = request.session.get('institute_token')
    if not token:
        return redirect('institution-login')  # Redirect if not logged in

    headers = {'Authorization': f'Bearer {token}'}
    saved_apps = []
    error = None

    try:
        response = requests.get(f"{settings.API_BASE_URL_INSTITUTE}saved-applications/", headers=headers)
        if response.status_code == 200:
            saved_apps = response.json()

            for app in saved_apps:
                # Parse and format datetime for easy template use
                applied_at_str = app.get('applied_at')
                if isinstance(applied_at_str, str):
                    try:
                        app['applied_at'] = datetime.fromisoformat(applied_at_str.replace('Z', '+00:00'))
                    except ValueError:
                        app['applied_at'] = None

                # Parse profile_data JSON string if necessary
                profile_data = app.get('profile_data')
                if isinstance(profile_data, str):
                    try:
                        app['profile_data'] = json.loads(profile_data)
                    except json.JSONDecodeError:
                        app['profile_data'] = {}
                elif profile_data is None:
                    app['profile_data'] = {}

                # Construct full resume_url if only relative path given
                resume_link = app.get('resume_link') or app.get('resume_file')
                if resume_link:
                    if resume_link.startswith('/'):
                        resume_link = resume_link[1:]
                    app['resume_url'] = f"{settings.API_BASE_URL1}/{resume_link}"
                else:
                    app['resume_url'] = None
        else:
            error = response.json().get('error', 'Failed to fetch saved applications.')

    except Exception as e:
        print("Saved applications fetch error:", e)
        error = "An error occurred while fetching saved applications."

    return render(request, 'institution/saved_applications.html', {
        'saved_apps': saved_apps,
        'error': error
    })


def export_applicants(request):
    token = request.session.get('institute_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    # Get filters from GET params
    status_filter = request.GET.get('status', '')
    export_format = request.GET.get('format', '').lower()

    params = {}
    if status_filter:
        params['status'] = status_filter

    applicants = []
    error = None

    # Step 1: Fetch applicant data for preview
    try:
        preview_response = requests.get(
            f"{settings.API_BASE_URL_INSTITUTE}applications/",
            headers=headers,
            params=params
        )
        if preview_response.status_code == 200:
            applicants = preview_response.json()
        else:
            error = preview_response.json().get('detail', 'Could not fetch applicants.')
    except requests.exceptions.RequestException as e:
        print("Fetch error:", e)
        error = "API connection error."

    # Step 2: If format is present, trigger download
    if export_format in ['csv', 'xlsx']:
        try:
            params['format'] = export_format
            export_response = requests.get(
                f"{settings.API_BASE_URL_INSTITUTE}export-applicants/",
                headers=headers,
                params=params
            )
            if export_response.status_code == 200:
                content_type = export_response.headers.get('Content-Type', 'application/octet-stream')
                filename = f"applicants.{export_format}"
                response = HttpResponse(export_response.content, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                error = export_response.json().get('detail', 'Export failed.')

        except requests.exceptions.RequestException as e:
            print("Export error:", e)
            error = "Export API connection error."

    return render(request, 'institution/export_applicants.html', {
        'applicants': applicants,
        'error': error,
        'status_filter': status_filter,
    })

def performance_dashboard(request):
    token = request.session.get('institute_token')  # use the same token key
    if not token:
        return redirect('institution-login')  # or your appropriate login route

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(f"{settings.API_BASE_URL_INSTITUTE}performance-dashboard/", headers=headers)
        if response.status_code == 200:
            data = response.json()
        else:
            data = []
    except Exception as e:
        print("Dashboard error:", e)
        data = []

    return render(request, "institution/performance_dashboard.html", {"jobs": data})
