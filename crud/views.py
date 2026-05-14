import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import UserProfile, Gender, ActionLog

def user_list(request):
    if request.method == "POST":
        # --- BULK ARCHIVE ---
        if 'bulk_archive' in request.POST:
            user_ids = request.POST.getlist('selected_users')
            if user_ids:
                UserProfile.objects.filter(id__in=user_ids).update(is_archived=True)
                ActionLog.objects.create(action=f"Bulk archived {len(user_ids)} identities")
                messages.success(request, f"Security Protocol: {len(user_ids)} records moved to Vault.")
            return redirect('user_list')

        # --- ADD IDENTITY ---
        if 'add_student' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            
            # SECURITY CHECK: Prevent duplicate username or email on creation
            if UserProfile.objects.filter(username__iexact=username).exists():
                messages.error(request, f"BREACH: Username '{username}' already exists.")
                return redirect('user_list')
            
            if UserProfile.objects.filter(email__iexact=email).exists():
                messages.error(request, f"BREACH: Email '{email}' is already in use.")
                return redirect('user_list')

            password, confirm = request.POST.get('password'), request.POST.get('confirm_password')
            if password != confirm:
                messages.error(request, "Security breach: Password mismatch detected.")
                return redirect('user_list')
            
            try:
                new_user = UserProfile.objects.create(
                    username=username,
                    email=email,
                    gender_id=request.POST.get('gender'),
                    password=make_password(password),
                    profile_picture=request.FILES.get('profile_picture')
                )
                ActionLog.objects.create(action=f"New Entity: {new_user.username}")
                messages.success(request, f"Identity {new_user.username} successfully registered.")
            except IntegrityError:
                messages.error(request, "CRITICAL: Database Integrity Error. Entry could not be saved.")
            
            return redirect('user_list')
        
        # --- ADD GENDER ---
        elif 'add_gender' in request.POST:
            g_name = request.POST.get('gender_name')
            if g_name:
                Gender.objects.create(gender=g_name)
                ActionLog.objects.create(action=f"New Category: {g_name}")
                messages.success(request, f"Category '{g_name}' has been activated.")
            return redirect('user_list')

    # Data Retrieval
    users_all = UserProfile.objects.filter(is_archived=False).order_by('-id')
    logs = ActionLog.objects.all().order_by('-timestamp')[:5]

    return render(request, 'user_list.html', {
        'users': users_all, 
        'genders': Gender.objects.all(), 
        'logs': logs,
        'count': users_all.count(), 
        'm_count': users_all.filter(gender__gender__iexact='Male').count(), 
        'f_count': users_all.filter(gender__gender__iexact='Female').count(),
    })

def edit_user(request, pk):
    user = get_object_or_404(UserProfile, pk=pk)
    if request.method == "POST":
        new_email = request.POST.get('email')
        new_username = request.POST.get('username')
        
        if UserProfile.objects.filter(email=new_email).exclude(pk=pk).exists():
            messages.error(request, f"ACCESS DENIED: Email '{new_email}' is already in use.")
            return redirect('edit_user', pk=pk)

        if UserProfile.objects.filter(username__iexact=new_username).exclude(pk=pk).exists():
            messages.error(request, f"ACCESS DENIED: Username '{new_username}' already exists.")
            return redirect('edit_user', pk=pk)
        
        user.username = new_username
        user.email = new_email
        user.gender_id = request.POST.get('gender')
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES.get('profile_picture')
            
        user.save()
        messages.success(request, "IDENTITY UPDATED: Credentials synchronized.")
        return redirect('user_list')
    return render(request, 'form.html', {'u': user, 'genders': Gender.objects.all()})

def edit_gender(request, pk):
    gender = get_object_or_404(Gender, pk=pk)
    if request.method == "POST":
        gender.gender = request.POST.get('gender_name')
        gender.save()
        messages.success(request, "Category Updated.")
        return redirect('user_list')
    return render(request, 'gender_form.html', {'g': gender})

def delete_user(request, pk):
    user = get_object_or_404(UserProfile, pk=pk)
    user.is_archived = True
    user.save()
    messages.success(request, "Archived to Vault.")
    return redirect('user_list')

def delete_gender(request, pk):
    Gender.objects.filter(pk=pk).delete()
    return redirect('user_list')

def archive_list(request):
    return render(request, 'archive_list.html', {'students': UserProfile.objects.filter(is_archived=True).order_by('-id')})

def vault_action(request):
    if request.method == "POST":
        user_ids, action = request.POST.getlist('selected_users'), request.POST.get('action')
        if not user_ids: return redirect('archive_list')
        if action == "recover": UserProfile.objects.filter(id__in=user_ids).update(is_archived=False)
        elif action == "permanently_delete": UserProfile.objects.filter(id__in=user_ids).delete()
    return redirect('archive_list')

def export_students(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registry.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Gender'])
    for u in UserProfile.objects.filter(is_archived=False):
        writer.writerow([u.username, u.email, u.gender.gender])
    return response

# --- LIVE AJAX ENDPOINTS ---
def check_email_exists(request):
    email = request.GET.get('email', None)
    current_user_id = request.GET.get('user_id', None)
    is_taken = UserProfile.objects.filter(email__iexact=email).exclude(id=current_user_id).exists()
    return JsonResponse({'is_taken': is_taken})

def check_username_exists(request):
    username = request.GET.get('username', None)
    current_user_id = request.GET.get('user_id', None)
    is_taken = UserProfile.objects.filter(username__iexact=username).exclude(id=current_user_id).exists()
    return JsonResponse({'is_taken': is_taken})