from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView, DetailView

from songs.forms import SongForm
from songs.models import Song
from songs.utils import get_song_lyrics, summarize_lyrics


class AddSongView(View):
    def get(self, request):
        form = SongForm()
        return render(request, 'add_song.html', {'form': form})

    def post(self, request):
        form = SongForm(request.POST)
        if form.is_valid():
            artist = form.cleaned_data['artist']
            title = form.cleaned_data['title']
            cache_key = f'song_{artist}_{title}'
            cached_song = cache.get(cache_key)
            if cached_song:
                return render(request, 'result.html', {'song': cached_song})

            lyrics = get_song_lyrics(artist, title)
            if lyrics is None:
                messages.info(request, 'Lyrics not available. Please add another song.')
                return redirect('add_song')

            lyrics = lyrics.split("*******")[0]
            data = summarize_lyrics(lyrics)
            if data is None:
                messages.info(request, 'Oops, something went wrong! We are looking into this. Please try again.')
                return redirect('add_song')

            summary = data["summary"]
            countries = data["countries"]
            if not countries:
                countries_str = ""
            else:
                countries_str = countries
            song = Song(
                artist=artist,
                title=title,
                lyrics=lyrics,
                summary=summary,
                countries=countries_str
            )
            song.save()
            cache.set(cache_key, song, 60 * 60)
            return render(request, 'result.html', {'song': song})
        else:
            return render(request, 'add_song.html', {'form': form})
        

class SongListView(TemplateView):
    template_name = 'song_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cache_key = 'songs_list'
        songs_list = cache.get(cache_key)
        if not songs_list:
            songs_list = Song.objects.order_by('-id').all()
            cache.set(cache_key, songs_list, 60 * 60)  # Cache for 1 hour

        paginator = Paginator(songs_list, 10)  # Show 10 songs per page

        page = self.request.GET.get('page')
        try:
            songs = paginator.page(page)
        except PageNotAnInteger:
            songs = paginator.page(1)
        except EmptyPage:
            songs = paginator.page(paginator.num_pages)

        context['songs'] = songs
        return context


def song_detail(request, pk):
    song = get_object_or_404(Song, pk=pk)
    return render(request, 'song_detail.html', {'song': song})