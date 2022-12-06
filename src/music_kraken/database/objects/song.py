import os
from typing import List
from mutagen.easyid3 import EasyID3

from ...utils.shared import (
    MUSIC_DIR,
    DATABASE_LOGGER as logger
)
from .database_object import (
    DatabaseObject,
    Reference
)


class Metadata:
    """
    Shall only be read or edited via the Song object.
    For this reason there is no reference to the song needed.
    """
    def __init__(self, data: dict = {}) -> None:
        self.data = {}

    def get_all_metadata(self):
        return list(self.data.items())

    def __setitem__(self, item, value):
        if item in EasyID3.valid_keys.keys():
            self.data[item] = value

    def __getitem__(self, item):
        if item not in self.data:
            return None
        return self.data[item]


class Source(DatabaseObject):
    """
    create somehow like that
    ```python
    # url won't be a valid one due to it being just an example
    Source(src="youtube", url="https://youtu.be/dfnsdajlhkjhsd")
    ```
    """
    def __init__(self, id_: str = None, src: str = None, url: str = None) -> None:
        super().__init__(id_=id_)

        self.src = src
        self.url = url


class Target(DatabaseObject):
    """
    create somehow like that
    ```python
    # I know path is pointles, and I will change that (don't worry about backwards compatibility there)
    Target(file="~/Music/genre/artist/album/song.mp3", path="~/Music/genre/artist/album")
    ```
    """
    def __init__(self, id_:str = None, file: str = None, path: str = None) -> None:
        super().__init__(id_=id_)
        self._file = file
        self._path = path

    def set_file(self, _file: str):
        self._file = _file

    def get_file(self) -> str | None:
        if self._file is None:
            return None
        return os.path.join(MUSIC_DIR, self._file)

    def set_path(self, _path: str):
        self._path = _path

    def get_path(self) -> str | None:
        if self._path is None:
            return None
        return os.path.join(MUSIC_DIR, self._path)

    def get_exists_on_disc(self) -> bool:
        """
        returns True when file can be found on disc
        returns False when file can't be found on disc or no filepath is set
        """
        if not self.is_set():
            return False

        return os.path.exists(self.file)
    
    def is_set(self) -> bool:
        return not (self._file is None or self._path is None)

    file = property(fget=get_file, fset=set_file)
    path = property(fget=get_path, fset=set_path)

    exists_on_disc = property(fget=get_exists_on_disc)


class Lyrics(DatabaseObject):
    def __init__(self, text: str, language: str, id_: str = None) -> None:
        super().__init__(id_=id_)
        self.text = text
        self.language = language


class Song(DatabaseObject):
    def __init__(
        self, 
        id_: str = None,
        mb_id: str = None,
        title: str = None,
        release_name: str = None,
        artist_names: List[str] = [],
        isrc: str = None,
        length: int = None,
        sources: List[Source] = None,
        target: Target = None,
        lyrics: List[Lyrics] = None,
        metadata: dict = {},
        release_ref: str = None,
        artist_refs: List[Reference] = None
        ) -> None:
        """
        id: is not NECESARRILY the musicbrainz id, but is DISTINCT for every song
        mb_id: is the musicbrainz_id
        target: Each Song can have exactly one target which can be either full or empty
        lyrics: There can be multiple lyrics. Each Lyrics object can me added to multiple lyrics
        """
        super().__init__(id_=id_)
        # attributes
        # self.id_: str | None = id_
        self.mb_id: str | None = mb_id
        self.title: str | None = title
        self.release_name: str | None = release_name
        self.isrc: str | None = isrc
        self.length: int | None = length
        self.artist_names = artist_names

        self.metadata = Metadata(data=metadata)
        

        if sources is None:
            sources = []
        self.sources: List[Source] = sources
        
        if target is None:
            target = Target()
        self.target: Target = target

        if lyrics is None:
            lyrics = []
        self.lyrics: List[Lyrics] = lyrics

        self.release_ref = release_ref
        self.artist_refs = artist_refs

    def __str__(self) -> str:
        return f"\"{self.title}\" by {', '.join([str(a) for a in self.artists])}"

    def __repr__(self) -> str:
        return self.__str__()

    def get_metadata(self):
        return self.metadata.get_all_metadata()

    def has_isrc(self) -> bool:
        return self.isrc is not None

    def get_artist_names(self) -> List[str]:
        return [a.name for a in self.artists]

if __name__ == "__main__":
    """
    Example for creating a Song object
    """

    song = Song(
        title="Vein Deep in the Solution",
        release_name="One Final Action",
        target=Target(file="~/Music/genre/artist/album/song.mp3", path="~/Music/genre/artist/album"),
        metadata={
            "album": "One Final Action"
        },
        lyrics=[
            Lyrics(text="these are some depressive lyrics", language="en")
        ],
        sources=[
            Source(src="youtube", url="https://youtu.be/dfnsdajlhkjhsd")
        ]
    )