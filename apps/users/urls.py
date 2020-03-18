from django.urls import path
from . import views
# url的命名空间
app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),    # 将这条路由命名为login
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout')
]
