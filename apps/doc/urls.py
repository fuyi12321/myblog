from django.urls import path
from . import views

app_name = 'doc'

urlpatterns = [
    path('', views.DocView.as_view(), name='index'),
    path('docs/', views.DocListView.as_view(), name='doclist'),
    path('docs/<int:doc_id>/', views.DocDownload.as_view(), name='doc_download'),
]
