from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import User
from .forms import RegisterForm, LoginForm

# 회원가입
# 로그인
# 로그아웃


### Registration
# 일반 뷰로 작성
class Registration(View):
    # 회원가입 정보 입력받음
    def get(self, request):
        # 회원가입 페이지
        # => 정보를 입력할 폼을 보여줘야함
        form = RegisterForm()
        context = {"form": form}
        return render(request, "user/user_register.html", context)

    # 제출 눌렀을 때 동작
    def post(self, request):
        # 요청 넣은 채로 폼 만듦
        form = RegisterForm(request.POST)
        if form.is_valid():
            # user모델 사용, form의 내용 저장
            user = form.save()
            # 로그인한 다음 이동동
            return redirect("blog:list")


### Login
class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("blog:list")

        form = LoginForm()
        context = {"form": form}
        return render(request, "user/user_login.html", context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("blog:list")

        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            # boolean값으로 True/False로 반환
            user = authenticate(username=email, password=password)

            if user:
                login(request, user)
                return redirect("blog:list")

            form.add_error(None, "아이디가 없습니다.")

        # 에러가 들어있는 폼
        context = {"form": form}
        return render(request, "user/user_login.html", context)


### Logout
class Logout(View):
    # 이미 로그인이 된 상태이므로 원래 유저가 정해져 있음
    def get(self, request):
        logout(request)
        return redirect("blog:list")
