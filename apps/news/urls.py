from django.urls import path
from . import views
# url的命名空间
app_name = 'news'
# <a href="{% url 'news:index' %}"></a>
urlpatterns = [
    path('', views.index, name='index'),    # 将这条路由命名为index
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/banners/', views.NewsBannerView.as_view(), name='news_banner'),
    path('news/<int:news_id>/', views.NewDetailView.as_view(), name='news_detail'),
    path('news/<int:news_id>/comment/', views.NewsCommentView.as_view(), name='news_comment'),
    path('search/', views.NewsSearchView.as_view(), name='news_search'),
    # path('search/', views.NewsSearchView.as_view(), name='search'),
]
