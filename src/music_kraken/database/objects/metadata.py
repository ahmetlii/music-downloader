from enum import Enum
from typing import List, Dict, Tuple

import dateutil.tz
from mutagen import id3
import datetime

from .parents import (
    ID3Metadata
)


class Mapping(Enum):
    """
    These frames belong to the id3 standart
    https://web.archive.org/web/20220830091059/https://id3.org/id3v2.4.0-frames
    https://id3lib.sourceforge.net/id3/id3v2com-00.html
    https://mutagen-specs.readthedocs.io/en/latest/id3/id3v2.4.0-frames.html
    """
    # Textframes
    TITLE = "TIT2"
    ISRC = "TSRC"
    LENGTH = "TLEN"
    DATE = "TYER"
    TRACKNUMBER = "TRCK"
    TOTALTRACKS = "TRCK"  # Stored in the same frame with TRACKNUMBER, separated by '/': e.g. '4/9'.
    TITLESORTORDER = "TSOT"
    ENCODING_SETTINGS = "TSSE"
    SUBTITLE = "TIT3"
    SET_SUBTITLE = "TSST"
    RELEASE_DATE = "TDRL"
    RECORDING_DATES = "TXXX"
    PUBLISHER_URL = "WPUB"
    PUBLISHER = "TPUB"
    RATING = "POPM"
    DISCNUMBER = "TPOS"
    MOVEMENT_COUNT = "MVIN"
    TOTALDISCS = "TPOS"
    ORIGINAL_RELEASE_DATE = "TDOR"
    ORIGINAL_ARTIST = "TOPE"
    ORIGINAL_ALBUM = "TOAL"
    MEDIA_TYPE = "TMED"
    LYRICIST = "TEXT"
    WRITER = "TEXT"
    ARTIST = "TPE1"
    LANGUAGE = "TLAN" # https://en.wikipedia.org/wiki/ISO_639-2
    ITUNESCOMPILATION = "TCMP"
    REMIXED_BY = "TPE4"
    RADIO_STATION_OWNER = "TRSO"
    RADIO_STATION = "TRSN"
    INITIAL_KEY = "TKEY"
    OWNER = "TOWN"
    ENCODED_BY = "TENC"
    COPYRIGHT = "TCOP"
    GENRE = "TCON"
    GROUPING = "TIT1"
    CONDUCTOR = "TPE3"
    COMPOSERSORTORDER = "TSOC"
    COMPOSER = "TCOM"
    BPM = "TBPM"
    ALBUM_ARTIST = "TPE2"
    BAND = "TPE2"
    ARTISTSORTORDER = "TSOP"
    ALBUM = "TALB"
    ALBUMSORTORDER = "TSOA"
    ALBUMARTISTSORTORDER = "TSO2"
    TAGGING_TIME = "TDTG"

    SOURCE_WEBPAGE_URL = "WOAS"
    FILE_WEBPAGE_URL = "WOAF"
    INTERNET_RADIO_WEBPAGE_URL = "WORS"
    ARTIST_WEBPAGE_URL = "WOAR"
    COPYRIGHT_URL = "WCOP"
    COMMERCIAL_INFORMATION_URL = "WCOM"
    PAYMEMT_URL = "WPAY"

    MOVEMENT_INDEX = "MVIN"
    MOVEMENT_NAME = "MVNM"

    UNSYNCED_LYRICS = "USLT"
    COMMENT = "COMM"

    @classmethod
    def get_text_instance(cls, key: str, value: str):
        return id3.Frames[key](encoding=3, text=value)

    @classmethod
    def get_url_instance(cls, key: str, url: str):
        return id3.Frames[key](encoding=3, url=url)

    @classmethod
    def get_mutagen_instance(cls, attribute, value):
        key = attribute.value

        if key[0] == 'T':
            # a text fiel
            return cls.get_text_instance(key, value)
        if key[0] == "W":
            # an url field
            return cls.get_url_instance(key, value)


class ID3Timestamp:
    def __init__(
            self,
            year: int = None,
            month: int = None,
            day: int = None,
            hour: int = None,
            minute: int = None,
            second: int = None
    ):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

        self.has_year = year is not None
        self.has_month = month is not None
        self.has_day = day is not None
        self.has_hour = hour is not None
        self.has_minute = minute is not None
        self.has_second = second is not None

        if not self.has_year:
            year = 1
        if not self.has_month:
            month = 1
        if not self.has_day:
            day = 1
        if not self.has_hour:
            hour = 1
        if not self.has_minute:
            minute = 1
        if not self.has_second:
            second = 1

        self.date_obj = datetime.datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second
        )

    def get_timestamp(self) -> str:
        """
        https://mutagen-specs.readthedocs.io/en/latest/id3/id3v2.4.0-structure.html

        The timestamp fields are based on a subset of ISO 8601. When being as precise as possible the format of a
        time string is
         - yyyy-MM-ddTHH:mm:ss
         - (year[%Y], “-”, month[%m], “-”, day[%d], “T”, hour (out of 24)[%H], ”:”, minutes[%M], ”:”, seconds[%S])
         - %Y-%m-%dT%H:%M:%S
        but the precision may be reduced by removing as many time indicators as wanted. Hence valid timestamps are
         - yyyy
         - yyyy-MM
         - yyyy-MM-dd
         - yyyy-MM-ddTHH
         - yyyy-MM-ddTHH:mm
         - yyyy-MM-ddTHH:mm:ss
        All time stamps are UTC. For durations, use the slash character as described in 8601,
        and for multiple non-contiguous dates, use multiple strings, if allowed by the frame definition.

        :return timestamp: as timestamp in the format of the id3 time as above described
        """

        if self.has_year and self.has_month and self.has_day and self.has_hour and self.has_minute and self.has_second:
            return self.date_obj.strftime("%Y-%m-%dT%H:%M:%S")
        if self.has_year and self.has_month and self.has_day and self.has_hour and self.has_minute:
            return self.date_obj.strftime("%Y-%m-%dT%H:%M")
        if self.has_year and self.has_month and self.has_day and self.has_hour:
            return self.date_obj.strftime("%Y-%m-%dT%H")
        if self.has_year and self.has_month and self.has_day:
            return self.date_obj.strftime("%Y-%m-%d")
        if self.has_year and self.has_month:
            return self.date_obj.strftime("%Y-%m")
        if self.has_year:
            return self.date_obj.strftime("%Y")
        return ""

    @classmethod
    def strptime(cls, time_stamp: str, format: str):
        """
        day: "%d" 
        month: "%b", "%B", "%m"
        year: "%y", "%Y"
        hour: "%H", "%I"
        minute: "%M"
        second: "%S"
        """
        date_obj = datetime.datetime.strptime(time_stamp, format)

        day = None
        if "%d" in format:
            day = date_obj.day
        month = None
        if any([i in format for i in ("%b", "%B", "%m")]):
            month = date_obj.month
        year = None
        if any([i in format for i in ("%y", "%Y")]):
            year = date_obj.year
        hour = None
        if any([i in format for i in ("%H", "%I")]):
            hour = date_obj.hour
        minute = None
        if "%M" in format:
            minute = date_obj.minute
        second = None
        if "%S" in format:
            second = date_obj.second

        return cls(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second
        )

    @classmethod
    def now(cls):
        date_obj = datetime.datetime.now()

        return cls(
            year=date_obj.year,
            month=date_obj.month,
            day=date_obj.day,
            hour=date_obj.hour,
            minute=date_obj.minute,
            second=date_obj.second
        )

    def strftime(self, format: str) -> str:
        return self.date_obj.strftime(format)

    def __str__(self) -> str:
        return self.timestamp

    def __repr__(self) -> str:
        return self.timestamp

    timestamp: str = property(fget=get_timestamp)


class Metadata:
    """
    Shall only be read or edited via the Song object.
    call it like a dict to read/write values
    """

    def __init__(self, id3_dict: dict = None) -> None:
        # this is pretty self-explanatory
        # the key is a 4 letter key from the id3 standards like TITL

        self.id3_attributes: Dict[str, list] = {}
        if id3_dict is not None:
            self.add_metadata_dict(id3_dict)

        # its a null byte for the later concatenation of text frames
        self.null_byte = "\x00"

    def get_all_metadata(self):
        return list(self.id3_attributes.items())

    def __setitem__(self, key: str, value: list, override_existing: bool = True):
        if len(value) == 0:
            return
        if type(value) != list:
            raise ValueError(f"can only set attribute to list, not {type(value)}")

        if override_existing:
            new_val = []
            for elem in value:
                if elem is not None:
                    new_val.append(elem)
            if len(new_val) > 0:
                self.id3_attributes[key] = new_val
        else:
            if key not in self.id3_attributes:
                self.id3_attributes[key] = value
                return
            self.id3_attributes[key].extend(value)

    def __getitem__(self, key):
        if key not in self.id3_attributes:
            return None
        return self.id3_attributes[key]

    def add_metadata_dict(self, metadata_dict: dict, override_existing: bool = True):
        for field_enum, value in metadata_dict.items():
            self.__setitem__(field_enum.value, value, override_existing=override_existing)

    def add_many_metadata_dict(self, id3_metadata_list: List[dict], override_existing: bool = False):
        for metadata_dict in id3_metadata_list:
            self.add_metadata_dict(metadata_dict, override_existing=override_existing)

    def delete_item(self, key: str):
        if key in self.id3_attributes:
            return self.id3_attributes.pop(key)

    def get_id3_value(self, key: str):
        if key not in self.id3_attributes:
            return None

        list_data = self.id3_attributes[key]

        # convert for example the time objects to timestamps
        for i, element in enumerate(list_data):
            # for performance’s sake I don't do other checks if it is already the right type
            if type(element) == str:
                continue

            if type(element) == ID3Timestamp:
                list_data[i] = element.timestamp
                continue

        """
        Version 2.4 of the specification prescribes that all text fields (the fields that start with a T, except for TXXX) can contain multiple values separated by a null character. 
        Thus if above conditions are met, I concatenate the list,
        else I take the first element
        """
        if key[0].upper() == "T" and key.upper() != "TXXX":
            return self.null_byte.join(list_data)

        return list_data[0]

    def get_mutagen_object(self, key: str):
        return Mapping.get_mutagen_instance(Mapping(key), self.get_id3_value(key))

    def __iter__(self):
        # set the tagging timestamp to the current time
        self.__setitem__(Mapping.TAGGING_TIME.value, [ID3Timestamp.now()])

        for key in self.id3_attributes:
            yield key, self.get_mutagen_object(key)

    def __str__(self) -> str:
        rows = []
        for key, value in self.id3_attributes.items():
            rows.append(f"{key} - {str(value)}")
        return "\n".join(rows)
