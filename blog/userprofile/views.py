from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from article.models import ArticlePost
from userprofile.forms import UserLoginForm, UserRegisterForm
from .forms import ProfileForm
from .models import Profile


def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            data = user_login_form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("Incorrect username or password, try again! ")
        else:
            return HttpResponse("Username or password is invalid")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form': user_login_form}
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("Use GET or POST to request data")


def user_logout(request):
    logout(request)
    return redirect("article:article_list")


def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)
            return redirect("article:article_list")
        else:
            return HttpResponse("register error, try again")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse("Please use GET Or POST method")


@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        if request.user == user:
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("You don't have permission to delete article")
    else:
        return HttpResponse("Need POST request")


@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        if request.user != user:
            return HttpResponse("You don't have permission to modify this. ")

        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("register list error, please try again. ")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("Please use GET or POST to request data. ")


def article_list(request):
    article_list = ArticlePost.objects.all()
    paginator = Paginator(article_list, 1)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    context = {'articles': articles}
    return render(request, 'article/list.html', context)
