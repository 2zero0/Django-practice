from typing import Any, Dict
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment, HashTag
from .forms import PostForm, CommentForm, HashTagForm
from django.urls import reverse_lazy, reverse

### Post
# def index(request):
#     if request.method == "GET":
#         return HttpResponse("Index page GET")
#     # 나머지 요청
#     # 에러, 예외처리
#     return HttpResponse("No!")


class Index(View):
    # method-get일때
    def get(self, request):
        # return HttpResponse("Index page GET class")

        # DB 접근해서 값을 가져옴
        # 게시판에 글 보여줘야하기 때문에 데이터베이스에서 값 조회
        post_objs = Post.objects.all()
        # context = DB에서 가져온 값
        context = {"posts": post_objs}
        # print(post_objs)
        return render(request, "blog/post_list.html", context)


# write
# post-form
# 글 작성 화면
def write(request):
    if request.method == "POST":
        # form 확인
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect("blog:list")

    # get인 경우
    form = PostForm()
    return render(request, "blog/post_form.html", {"form": form})


# class (genericView 사용)
# django 자체의 클래스 뷰 기능 강력, 편리
#class List(ListView):
#    model = Post  # 모델
#    template_name = "blog/post_list.html"  # 템플릿
#    context_object_name = "posts"  # 변수 값의 이름


#class Write(CreateView):
#    model = Post  # 모델
#    form_class = PostForm  # 폼
#    success_url = reverse_lazy("blog:list")  # 성공시 보내줄 url

class Write(LoginRequiredMixin ,View):
    # Mixin: LoginRequiredMixin
    # 이 클래스를 상속받게 되면 로그인 된 사람만 접근가능
    def get(self, request): # 글 작성 화면
        form = PostForm()
        context = {
            'form': form
        }
        return render(request, 'blog/post_form.html', context)
    
    def post(self, request): # submit시 동작
        form = PostForm(request. POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.writer=request.user
            post.save()
            return redirect('blog:list')
        form.add_error(None, '폼이 유효하지 않습니다.')
        context = {
            'form': form
        }
        return render(request, 'blog/post_form.html')


class Detail(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"


class Update(UpdateView):
    model = Post
    template_name = "blog/post_edit.html"
    fields = ["title", "content"]
    # success_url = reverse_lazy("blog:list") 아래 함수로 작성해서 지움

    # initial 기능
    # form에 값을 미리 넣어주기 위해서서
    def get_initial(self):
        # UpdateView(부모)의 것을 갖고옴
        # 딕셔너리 형태
        initial = super().get_initial()
        # 이 Update 클래스 자체의 것
        # pk 기반으로 객체를 가져옴
        post = self.get_object()

        initial["title"] = post.title
        initial["content"] = post.content
        return initial

    # get_absolute_url
    def get_success_url(self):
        # pk 기반으로 현제 객체 가져오기
        post = self.get_object()
        return reverse("blog:detail", kwargs={"pk": post.pk})


class Delete(DeleteView):
    model = Post
    success_url = reverse_lazy("blog:list")


class DetailView(View):
    def get(self, request, pk):
        # 해당 글
        post = Post.objects.get(pk=pk)

        # 댓글
        comments = Comment.objects.filter(post=post)

        # 해시태그
        hashtags = HashTag.objects.filter(post=post)

        # 댓글 Form
        comment_form = CommentForm()

        # 해시태그 Form
        hashtag_form = HashTagForm()

        context = {
            "post": post,
            "comments": comments,
            "hashtags": hashtags,
            "comment_form": comment_form,
            "hashtag_form": hashtag_form,
        }

        # 넣어준 값이 있을 때 사용
        # 값들이 들어간 채로 페이지에 출력이 되도록 (템플릿 안에 값 넣어서 출력)
        return render(request, "blog/post_detail.html", context)


### Comment
class CommentWrite(View):
    # def get(self, request):
    #     pass
    def post(self, request, pk):
        form = CommentForm(request.POST)
        if form.is_valid():
            # 사용자에게 댓글 내용 받아옴
            content = form.cleaned_data["content"]
            # 해당 아이디에 해당하는 글 불러옴(댓글은 어떤 한 글의 댓글이므로)
            post = Post.objects.get(pk=pk)
            # 댓글 객체 생성
            comment = Comment.objects.create(post=post, content=content)
            return redirect("blog:detail", pk=pk)


class CommentDelete(View):
    def post(self, request, pk):
        # 지울 객체를 찾음 (댓글 객체)
        comment = Comment.objects.get(pk=pk)
        # 상세페이지로 돌아감
        post_id = comment.post.id
        # 삭제
        comment.delete()

        return redirect("blog:detail", pk=post_id)


### Hashtag
class HashTagWrite(View):
    def post(self, request, pk):
        form = HashTagForm(request.POST)
        if form.is_valid():
            # 사용자에게 태그 내용 받아옴
            name = form.cleaned_data["name"]
            # 해당 아이디에 해당하는 글 불러옴(댓글은 어떤 한 글의 댓글이므로)
            post = Post.objects.get(pk=pk)
            # 댓글 객체 생성
            hashtag = HashTag.objects.create(post=post, name=name)
            return redirect("blog:detail", pk=pk)


class HashTagDelete(View):
    def post(self, request, pk):
        # 해시태그의 pk(id)
        # 해시태그 불러오기
        hashtag = HashTag.objects.get(pk=pk)
        # 포스트의 pk(id)값 가져오기
        post_id = hashtag.post.id
        # 해시태그 삭제
        hashtag.delete()
        # 응답
        return redirect('blog:detail', pk=post_id)
