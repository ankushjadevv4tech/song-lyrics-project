from django.urls import path, include
from songs import views

urlpatterns = [
    path('add_song/', views.AddSongView.as_view(), name='add_song'),
    path('song_list/', views.SongListView.as_view(), name='song_list'),
    path('song/<int:pk>/', views.song_detail, name='song_details'),
]