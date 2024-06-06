from django.db import models


class Song(models.Model):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    summary = models.TextField(blank=True, null=True)
    lyrics = models.TextField(blank=True, null=True)
    countries = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.artist} - {self.title}"
