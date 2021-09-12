from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ask/', views.ask, name='ask'),
    path('edit/<int:pk>/', views.edit, name='edit'),
    #path('update/<int:pk>/', views.ItemUpdateView.as_view(), name='update'),
    path('update/', views.ItemFilterEditkeyView.as_view(), name='update'),
    path('list/', views.ItemFilterView.as_view(), name='list'),
    path('about/', views.about, name='about'),
    path('linebot/', views.linebot, name='linebot'),
]