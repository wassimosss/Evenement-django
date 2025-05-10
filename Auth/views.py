from django.shortcuts import render,redirect
from .models import Utilisateur
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib import messages
def inscription(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'Authentification.html')
        if Utilisateur.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, 'Authentification.html')
        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'Authentification.html')
        user = Utilisateur.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Inscription réussie ! Connecte-toi maintenant.")
        return redirect("login")
    return render(request, 'Authentification.html')
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not username or not password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, 'Authentification.html')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.role == 'admin':
                return redirect('/admin') 
            else:
                return redirect('/pages')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'Authentification.html')