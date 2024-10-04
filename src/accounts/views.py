from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def adminUserProfile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('educator-admin-products')
    else:
        form = UserProfileForm()

    return render(request, 'educator/profile.html', {'form': form,'selected':'profile'})