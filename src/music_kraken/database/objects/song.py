import os
from typing import List
import pycountry
import copy

from .metadata import (
    Mapping as id3Mapping,
    ID3Timestamp,
    MetadataAttribute
)
from ...utils.shared import (
    MUSIC_DIR,
    DATABASE_LOGGER as logger
)
from .parents import (
    DatabaseObject,
    Reference,
    SongAttribute
)
from .source import (
    Source,
    SourceTypes,
    SourcePages,
    SourceAttribute
)
from .formatted_text import FormattedText
from .collection import Collection

"""
All Objects dependent 
"""


class Target(DatabaseObject, SongAttribute):
    """
    create somehow like that
    ```python
    # I know path is pointless, and I will change that (don't worry about backwards compatibility there)
    Target(file="~/Music/genre/artist/album/song.mp3", path="~/Music/genre/artist/album")
    ```
    """

    def __init__(self, id_: str = None, file: str = None, path: str = None) -> None:
        DatabaseObject.__init__(self, id_=id_)
        SongAttribute.__init__(self)
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


class Lyrics(DatabaseObject, SongAttribute, SourceAttribute, MetadataAttribute):
    def __init__(
            self,
            text: str,
            language: str,
            id_: str = None,
            source_list: List[Source] = None
    ) -> None:
        DatabaseObject.__init__(self, id_=id_)
        SongAttribute.__init__(self)
        self.text = text
        self.language = language

        if source_list is not None:
            self.source_list = source_list

    def get_metadata(self) -> MetadataAttribute.Metadata:
        return super().get_metadata()


class Song(DatabaseObject, SourceAttribute, MetadataAttribute):
    def __init__(
            self,
            id_: str = None,
            mb_id: str = None,
            title: str = None,
            album_name: str = None,
            isrc: str = None,
            length: int = None,
            tracksort: int = None,
            genre: str = None,
            source_list: List[Source] = None,
            target: Target = None,
            lyrics: List[Lyrics] = None,
            album=None,
            main_artist_list: list = None,
            feature_artist_list: list = None
    ) -> None:
        """
        id: is not NECESARRILY the musicbrainz id, but is DISTINCT for every song
        mb_id: is the musicbrainz_id
        target: Each Song can have exactly one target which can be either full or empty
        lyrics: There can be multiple lyrics. Each Lyrics object can me added to multiple lyrics
        """
        super().__init__(id_=id_)
        # attributes
        # *private* attributes
        self.title: str = title
        self.isrc: str = isrc
        self.length: int = length
        self.mb_id: str | None = mb_id
        self.album_name: str | None = album_name
        self.tracksort: int | None = tracksort
        self.genre: str = genre

        if source_list:
            self.source_list = source_list

        self.target = Target()
        if target is not None:
            self.target = target
        self.target.add_song(self)

        self.lyrics = []
        if lyrics is not None:
            self.lyrics = lyrics

        self._album = None
        self.album = album

        self.main_artist_list = []
        if main_artist_list is not None:
            self.main_artist_list = main_artist_list

        self.feature_artist_list = []
        if feature_artist_list is not None:
            self.feature_artist_list = feature_artist_list

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.id == other.id

    def get_artist_credits(self) -> str:
        feature_str = ""
        if len(self.feature_artist_list) > 0:
            feature_str = " feat. " + ", ".join([artist.name for artist in self.feature_artist_list])
        return ", ".join([artist.name for artist in self.main_artist_list]) + feature_str

    def __str__(self) -> str:
        artist_credit_str = ""
        artist_credits = self.get_artist_credits()
        if artist_credits != "":
            artist_credit_str = f" by {artist_credits}"

        return f"\"{self.title}\"{artist_credit_str}"

    def __repr__(self) -> str:
        return self.__str__()

    def has_isrc(self) -> bool:
        return self.isrc is not None

    def get_album_id(self):
        if self.album is None:
            return None
        return self.album.id

    def get_tracksort_str(self):
        if self.tracksort is None:
            return None

        if self.album is None:
            return str(self.tracksort)

        return f"{self.tracksort}/{len(self.album.tracklist)}"

    def get_metadata(self) -> MetadataAttribute.Metadata:
        metadata = MetadataAttribute.Metadata({
            id3Mapping.TITLE: [self.title],
            id3Mapping.ISRC: [self.isrc],
            id3Mapping.LENGTH: [self.length],
            id3Mapping.GENRE: [self.genre],
            id3Mapping.TRACKNUMBER: [self.tracksort_str]
        })

        metadata.merge_many([s.get_song_metadata() for s in self.source_list])
        if self.album is not None:
            metadata.merge(self.album.metadata)
        metadata.merge_many([a.metadata for a in self.main_artist_list])
        metadata.merge_many([a.metadata for a in self.feature_artist_list])
        metadata.merge_many([l.metadata for l in self.lyrics])
        return metadata

    def set_album(self, album):
        if album is None:
            return

        self._album = album
        if self not in self._album.tracklist:
            flat_copy = copy.copy(self)
            flat_copy.dynamic = True
            self._album.tracklist.append(flat_copy)

    def get_options(self) -> list:
        options = self.main_artist_list.copy()
        options.extend(self.feature_artist_list.copy())
        if self.album is not None:
            options.append(self.album)
        options.append(self)
        return options

    def get_option_string(self) -> str:
        return f"Song: {self.title}; Album: {self.album.title}; Artists: {self.get_artist_credits()}"

    tracksort_str = property(fget=get_tracksort_str)
    album = property(fget=lambda self: self._album, fset=set_album)


"""
All objects dependent on Album
"""


class Album(DatabaseObject, SourceAttribute, MetadataAttribute):
    """
    -------DB-FIELDS-------
    title           TEXT, 
    copyright       TEXT,
    album_status    TEXT,
    language        TEXT,
    year            TEXT,
    date            TEXT,
    country         TEXT,
    barcode         TEXT,
    song_id         BIGINT,
    is_split        BOOLEAN NOT NULL DEFAULT 0
    """

    def __init__(
            self,
            id_: str = None,
            title: str = None,
            label: str = None,
            album_status: str = None,
            language: pycountry.Languages = None,
            date: ID3Timestamp = None,
            country: str = None,
            barcode: str = None,
            is_split: bool = False,
            albumsort: int = None,
            dynamic: bool = False,
            source_list: List[Source] = None,
            artists: list = None,
            tracklist: List[Song] = None,
            album_type: str = None
    ) -> None:
        DatabaseObject.__init__(self, id_=id_, dynamic=dynamic)

        """
        TODO
        add to db
        """
        self.album_type = album_type

        self.title: str = title
        self.album_status: str = album_status
        self.label = label
        self.language: pycountry.Languages = language
        self.date: ID3Timestamp = date
        if date is None:
            self.date = ID3Timestamp()
        self.country: str = country
        """
        TODO
        find out the id3 tag for barcode and implement it
        maybee look at how mutagen does it with easy_id3
        """
        self.barcode: str = barcode
        self.is_split: bool = is_split
        self.albumsort: int | None = albumsort


        self._tracklist = Collection(
            data=tracklist or [],
            map_attributes=["title"],
            element_type=Song
        )
        self.source_list = source_list or []
        self.artists = artists or []


    def __str__(self) -> str:
        return f"-----{self.title}-----\n{self.tracklist}"

    def __repr__(self):
        return f"Album(\"{self.title}\")"

    def __len__(self) -> int:
        return len(self.tracklist)

    def set_tracklist(self, tracklist):
        tracklist_list = []
        if type(tracklist) == Collection:
            tracklist_list = tracklist_list
        elif type(tracklist) == list:
            tracklist_list = tracklist

        self._tracklist = Collection(
            data=tracklist_list,
            map_attributes=["title"],
            element_type=Song
        )

    def get_metadata(self) -> MetadataAttribute.Metadata:
        return MetadataAttribute.Metadata({
            id3Mapping.ALBUM: [self.title],
            id3Mapping.COPYRIGHT: [self.copyright],
            id3Mapping.LANGUAGE: [self.iso_639_2_language],
            id3Mapping.ALBUM_ARTIST: [a.name for a in self.artists],
            id3Mapping.DATE: [self.date.timestamp]
        })

    def get_copyright(self) -> str:
        if self.date is None:
            return None
        if self.date.year == 1 or self.label is None:
            return None

        return f"{self.date.year} {self.label}"

    def get_iso_639_2_lang(self) -> str:
        if self.language is None:
            return None

        return self.language.alpha_3

    def get_options(self) -> list:
        options = self.artists.copy()
        options.append(self)
        for track in self.tracklist:
            new_track: Song = copy.copy(track)
            new_track.album = self
            options.append(new_track)

        return options
    
    def get_option_string(self) -> str:
        return f"Album: {self.title}; Artists {', '.join([i.name for i in self.artists])}"


    copyright = property(fget=get_copyright)
    iso_639_2_language = property(fget=get_iso_639_2_lang)
    tracklist: Collection = property(fget=lambda self: self._tracklist, fset=set_tracklist)


"""
All objects dependent on Artist
"""


class Artist(DatabaseObject, SourceAttribute, MetadataAttribute):
    """
    main_songs
    feature_song

    albums
    """

    def __init__(
            self,
            id_: str = None,
            name: str = None,
            source_list: List[Source] = None,
            main_songs: List[Song] = None,
            feature_songs: List[Song] = None,
            main_albums: List[Album] = None,
            album_type: str = None,
            notes: FormattedText = None,
            lyrical_themes: List[str] = None,
            general_genre: str = "",
            country=None,
            formed_in: ID3Timestamp = None
    ):
        DatabaseObject.__init__(self, id_=id_)

        """
        TODO implement album type and notes
        """
        self.album_type = album_type
        self.country: pycountry.Country = country
        self.formed_in: ID3Timestamp = formed_in
        """
        notes, generall genre, lyrics themes are attributes
        which are meant to only use in outputs to describe the object
        i mean do as you want but there aint no strict rule about em so good luck
        """
        self.notes: FormattedText = notes
        if self.notes is None:
            self.notes = FormattedText()
        self.lyrical_themes: List[str] = lyrical_themes
        if self.lyrical_themes is None:
            self.lyrical_themes = []
        self.general_genre = general_genre

        if main_albums is None:
            main_albums = []
        if feature_songs is None:
            feature_songs = []
        if main_songs is None:
            main_songs = []

        self.name: str | None = name

        self.main_songs = main_songs

        self.feature_songs = Collection(
            data=feature_songs,
            map_attributes=["title"],
            element_type=Song
        )

        self.main_albums = Collection(
            data=main_albums,
            map_attributes=["title"],
            element_type=Album
        )

        if source_list is not None:
            self.source_list = source_list

    def __str__(self):
        string = self.name or ""
        plaintext_notes = self.notes.get_plaintext()
        if plaintext_notes is not None:
            string += "\n" + plaintext_notes
        return string

    def __repr__(self):
        return self.__str__()

    def __eq__(self, __o: object) -> bool:
        return self.id_ == __o.id_

    def get_features(self) -> Album:
        feature_release = Album(
            title="features",
            album_status="dynamic",
            is_split=True,
            albumsort=666,
            dynamic=True
        )
        for feature in self.feature_songs:
            feature_release.add_song(feature)

        return feature_release

    def get_songs(self) -> Album:
        song_release = Album(
            title="song collection",
            album_status="dynamic",
            is_split=False,
            albumsort=666,
            dynamic=True
        )
        for song in self.main_songs:
            song_release.add_song(song)
        for song in self.feature_songs:
            song_release.add_song(song)
        return song_release

    def get_discography(self) -> List[Album]:
        flat_copy_discography = self.main_albums.copy()
        flat_copy_discography.append(self.get_features())

        return flat_copy_discography

    def get_metadata(self) -> MetadataAttribute.Metadata:
        metadata = MetadataAttribute.Metadata({
            id3Mapping.ARTIST: [self.name]
        })
        metadata.merge_many([s.get_artist_metadata() for s in self.source_list])

        return metadata

    def get_options(self) -> list:
        options = [self]
        for album in self.main_albums:
            new_album: Album = copy.copy(album)
            new_album.artists.append(self)
            options.append(new_album)
        return options

    def get_option_string(self) -> str:
        return f"Artist: {self.name}"

    discography: List[Album] = property(fget=get_discography)
    features: Album = property(fget=get_features)
    songs: Album = property(fget=get_songs)
