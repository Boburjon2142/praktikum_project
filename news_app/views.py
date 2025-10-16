from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import News, Category
from django.db.models import Q
from .forms import CommentForm, ContactForm
from django.contrib.auth.decorators import login_required, user_passes_test
from newsproject.custom_permissions import OnlyLoggedSuperUser
from django.contrib.auth.models import User
from hitcount.models import HitCount  # type: ignore
from hitcount.views import HitCountMixin  # type: ignore



# Create your views here.
def news_list(request):
    news_list = News.published.all()
    context ={
        "news_list": news_list
    }
    return render(request, "news/news_list.html", context)
def news_detail(request, news):
    news = get_object_or_404(News, slug=news, status=News.Status.Published)
    context = {}
    #hitcount_logic
    hit_count = HitCount.objects.get_for_object(news)
    hits = hit_count.hits
    hitcontext = context['hitcount'] = {'pk': hit_count.pk}
    hitcount_response = HitCountMixin.hit_count(request, hit_count)
    if hitcount_response.hit_counted:
        hits += 1
        hitcontext['hit_counted'] = hitcount_response.hit_counted
        hitcontext['hit_message'] = hitcount_response.hit_message
        hitcontext['total_hits'] = hits
    comments = news.comments.filter(active=True)
    comment_count = comments.count()
    new_comment = None
    if request.method == "POST":
        # Process comment submission only for authenticated users
        if not request.user.is_authenticated:
            return HttpResponseRedirect(news.get_absolute_url())
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.news = news
            new_comment.user = request.user
            new_comment.save()
            # Redirect to avoid duplicate submissions (PRG pattern)
            return HttpResponseRedirect(news.get_absolute_url())
        else:
            # keep the form with errors
            pass
        comment_form = comment_form
    else:
        comment_form = CommentForm()

    context = {
        "news": news,
        "comments": comments,
        "comment_count": comment_count,
        "new_comment": new_comment,
        "comment_form": comment_form,
    }

    return render(request, 'news/news_detail.html', context)

def homePageView(request):
    categories = Category.objects.all()
    news_list = News.published.all().order_by('-publish_time')[:5]
    local_one = News.published.filter(category__name='Mahalliy').order_by("-publish_time")[:1]
    local_news = News.published.all().filter(category__name='Mahalliy').order_by("-publish_time")[1:6]
    context = {
        'news_list':news_list,
        'categories':categories,
        'local_one':local_one,
        'local_news':local_news
    }

    return render(request, 'news/home.html', context)

class HomePageView(ListView):
    model = News
    template_name = 'news/home.html'
    context_object_name = 'news'

    def get_context_data(
        self, *, object_list = ..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        # categories and latest_news come from context processor
        context['news_list'] = News.published.all().order_by('-publish_time')[:5]
        context['mahalliy_xabarlar'] = News.published.filter(category__name='Mahalliy').order_by("-publish_time")[:5]
        context['xorij_xabarlari'] = News.published.filter(category__name='Xorij').order_by("-publish_time")[:5]
        context['sport_xabarlari'] = News.published.filter(category__name='Sport').order_by("-publish_time")[:5]
        context['texnologiya_xabarlari'] = News.published.filter(category__name='Texnologiya').order_by("-publish_time")[:5]
        return context


# def contactPageView(request):
#     print(request.POST)
#     form = ContactForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         form.save()
#         return HttpResponse("<h2>Biz bilan bog'langaningiz uchun tashakkur!</h2>")
#     context = {
#         "form":form
#     }
#     return render(request, 'news/contact.html', context)

class ContactPageView(TemplateView):
    template_name = 'news/contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        context = {
            'form':form
        }
        return render(request, 'news/contact.html', context)

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return HttpResponse("<h2>Biz bilan bog'langaningiz uchun tashakkur!</h2>")
        context = {
                "form":form
            }

        return render(request, 'news/contact.html', context)


def aboutPageView(request):
    return render(request,'news/single_page.html')

def custom_404(request):
    return render(request, 'news/404.html')

class LocalNewsView(ListView):
    model = News
    template_name = 'news/mahalliy.html'
    context_object_name = 'mahalliy_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Mahalliy")
        return news

class ForeignNewsView(ListView):
    model = News
    template_name = 'news/xorij.html'
    context_object_name = 'xorij_yangiliklari'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Xorij")
        return news

class TechnologyNewsView(ListView):
    model = News
    template_name = 'news/texnologiya.html'
    context_object_name = 'texnologiya_yangiliklari'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Texnologiya")
        return news

class SportNewsView(ListView):
    model = News
    template_name = 'news/sport.html'
    context_object_name = 'sport_yangiliklari'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Sport")
        return news
    
class NewsUpdateView(OnlyLoggedSuperUser, UpdateView):
    model = News
    fields = ('title', 'body', 'image', 'category', 'status', )
    template_name = 'crud/news_edit.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    
# class NewsCreateView(CreateView):
#     model = News
#     fields = ('title', 'slug', 'author', 'content', 'photo', 'category', 'status', )
#     template_name = 'crud/news_create.html'
    
class NewsDeleteView(OnlyLoggedSuperUser, DeleteView):
    model = News
    template_name = 'crud/news_delete.html'
    success_url = reverse_lazy('home_page')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
class NewsCreateView(OnlyLoggedSuperUser, CreateView):
    model = News
    template_name = 'crud/news_create.html'
    fields = ('title', 'slug', 'body', 'image', 'category', 'status' )
    
@login_required
@user_passes_test(lambda u:u.is_superuser)
def admin_page_view(request):
    admin_users = User.objects.filter(is_superuser=True)
    
    context = {
        'admin_users': admin_users
    }
    
    return render(request, 'pages/admin_page.html', context)

class SearchResultList(ListView):
    model = News
    template_name = 'news/search_results.html'
    context_object_name = 'barcha_yangiliklar'

    def get_queryset(self):
        query = (self.request.GET.get('q') or '').strip()
        if not query:
            return News.published.none()
        return News.published.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )
