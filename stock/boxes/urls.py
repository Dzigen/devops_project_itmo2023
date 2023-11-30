from django.urls import path, include
from .views import *

urlpatterns = [
    path('', MainView.as_view(), name='home'),
    path('room/', RoomView.as_view(), name='room'),
    path('boxes/', BoxesView.as_view(), name='boxes'),
    path('boxes/<slug:box_name>', BoxItemsView.as_view(), name='box_items'),
    path('signup/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout')
]