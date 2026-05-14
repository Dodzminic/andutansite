import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Case, When, Value, IntegerField
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.contrib import messages
from .models import UserProfile, Gender, ActionLog

import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Case, When, Value, IntegerField
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.contrib import messages
from .models import UserProfile, Gender, ActionLog
from django.http import JsonResponse

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
            password, confirm = request.POST.get('password'), request.POST.get('confirm_password')
            if password != confirm:
                messages.error(request, "Security breach: Password mismatch detected.")
                return redirect('user_list')
            
            new_user = UserProfile.objects.create(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                gender_id=request.POST.get('gender'),
                password=make_password(password),
                profile_picture=request.FILES.get('profile_picture')
            )
            ActionLog.objects.create(action=f"New Entity: {new_user.username}")
            messages.success(request, f"Identity {new_user.username} successfully registered.")
            return redirect('user_list')
        
        # --- ADD GENDER ---
        elif 'add_gender' in request.POST:
            g_name = request.POST.get('gender_name')
            if g_name:
                Gender.objects.create(gender=g_name)
                ActionLog.objects.create(action=f"New Category: {g_name}")
                # We use simple quotes here to avoid encoding issues
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

# Rest of functions (edit_user, delete_user, archive_list, vault_action, export_students) remain the same

def edit_user(request, pk):
    # 1. Fetch the user we are currently editing
    user = get_object_or_404(UserProfile, pk=pk)
    
    if request.method == "POST":
        # 2. Get the new email they typed in the form
        new_email = request.POST.get('email')
        
        # 3. THE FIX: Check if this email is already taken by someone else
        # We look for the email, but EXCLUDE the current user's ID (pk)
        if UserProfile.objects.filter(email=new_email).exclude(pk=pk).exists():
            # If it exists, send an error message and stay on the edit page
            messages.error(request, f"ACCESS DENIED: Email '{new_email}' is already in use by another account.")
            return redirect('edit_user', pk=pk)
        
        # 4. If the check passes, update the fields
        user.username = request.POST.get('username')
        user.email = new_email
        user.gender_id = request.POST.get('gender')
        
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES.get('profile_picture')
            
        # 5. Now it is safe to save! MySQL won't complain anymore.
        user.save()
        messages.success(request, "IDENTITY UPDATED: Credentials synchronized.")
        return redirect('user_list')
        
    return render(request, 'form.html', {'u': user, 'genders': Gender.objects.all()})
        
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

def check_email_exists(request):
    email = request.GET.get('email', None)
    current_user_id = request.GET.get('user_id', None)
    
    # We look for the email but ignore the user we are currently editing
    is_taken = UserProfile.objects.filter(email__iexact=email).exclude(id=current_user_id).exists()
    
    return JsonResponse({'is_taken': is_taken})