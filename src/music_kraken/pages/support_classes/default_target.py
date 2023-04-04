from dataclasses import dataclass

from ...utils.shared import DOWNLOAD_PATH, DOWNLOAD_FILE, DEFAULT_VALUES
from ...utils.string_processing import fit_to_file_system
from ...objects import (
    Song,
    Album,
    Artist,
    Target,
    Label
)


@dataclass
class DefaultTarget:
    genre: str = DEFAULT_VALUES["genre"]
    label: str = DEFAULT_VALUES["label"]
    artist: str = DEFAULT_VALUES["artist"]
    album: str = DEFAULT_VALUES["album"]
    album_type: str = DEFAULT_VALUES["album_type"]
    song: str = DEFAULT_VALUES["song"]

    def __setattr__(self, __name: str, __value: str) -> None:
        if __name in DEFAULT_VALUES:
            if self.__getattribute__(__name) == DEFAULT_VALUES[__name]:
                super().__setattr__(__name, fit_to_file_system(__value))
            return

        super().__setattr__(__name, __value)

    @property
    def target(self) -> Target:
        return Target(
            relative_to_music_dir=True,
            path=DOWNLOAD_PATH.format(genre=self.genre, label=self.label, artist=self.artist, album=self.album,
                                      song=self.song, album_type=self.album_type),
            file=DOWNLOAD_FILE.format(genre=self.genre, label=self.label, artist=self.artist, album=self.album,
                                      song=self.song, album_type=self.album_type)
        )

    def song_object(self, song: Song):
        self.song = song.title

        if not song.album_collection.empty:
            self.album_object(song.album_collection[0])
        if not song.main_artist_collection.empty:
            self.artist_object(song.main_artist_collection[0])

    def album_object(self, album: Album):
        self.album = album.title
        self.album_type = album.album_type.value

        if not album.artist_collection.empty:
            self.artist_object(album.artist_collection[0])
        if not album.label_collection.empty:
            self.label_object(album.label_collection[0])

    def artist_object(self, artist: Artist):
        self.artist = artist.name

        if not artist.label_collection.empty:
            self.label_object(artist.label_collection[0])

    def label_object(self, label: Label):
        self.label = label.name