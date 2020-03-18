from django.urls import path

from . import views

app_name = 'myadmin'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path('index/', views.index_fn, name='index_fn')
    path('tags/', views.TagManageView.as_view(), name='tags_manage'),
    path('tags/<int:tag_id>/', views.TagEditView.as_view(), name='tag_delete'),
    path('news/', views.NewsManageView.as_view(), name="news_manage"),
    path('news/<int:news_id>/', views.NewsEditView.as_view(), name="news_delete"),
    path('news/pub/', views.NewsPubView.as_view(), name="news_pub"),
    path('news/addpermission/', views.addpermission)
]
