from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile

# Create your views here.

@login_required
def adminUserProfile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    is_edit_mode = request.GET.get('edit', False)  # Check if the user wants to edit

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, editable=True)
        if form.is_valid():
            form.save()
            return redirect('educator-admin-products')
    else:
        form = UserProfileForm(instance=profile, editable=is_edit_mode)

    return render(request, 'educator/profile.html', {
        'form': form,
        'selected': 'profile',
        'is_edit_mode': is_edit_mode  # Pass this to template
    })
