"""UTILITIES TO HANDLE DATE VALUES"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import re
from typing import Tuple, Generator, Union
from dateutil.relativedelta import relativedelta


class HelpersException(Exception):
    """A base class for date_helpers' exceptions."""


class TimeIntervalError(HelpersException):
    """Exception Raised When you provide a wrong time interval value"""


class DateValueError(HelpersException):
    """Exception Raised When you provide a wrong time interval value"""


class IntervalError(HelpersException):
    """Exception Raised When you provide a wrong time interval value"""


class TimeBucketError(HelpersException):
    """Exception Raised When you provide a wrong time bucket value"""


class IntervalTimeBucketError(HelpersException):
    """Exception Raised When you provide a wrong interval or time bucket value"""


class DatePhraseHandler(ABC):
    """Handles Phrases In the Input Date"""

    date_value: Union[str, None] = None
    time_bucket: Union[str, None] = None
    interval: Union[int, None] = None

    def __init__(self, date_value: str):
        self.date_value = date_value

    @abstractmethod
    def phrase_to_date(self) -> str:
        """Processes the date_value and translates it to a datetime value
        Raises:
            NotImplementedError: _description_
        Returns:
            str: _description_
        """
        raise NotImplementedError


class BaseDateInterval(ABC):
    """Get Start of the Date Range"""

    def __init__(self, time_bucket: str, interval: int):
        self.time_bucket = time_bucket
        self.interval = interval

    @abstractmethod
    def get_start_date(self, start_date: datetime) -> datetime:
        """Gets the start date of the range provided the input startdate
        Args:
            start_date (datetime): should be a datetime value
        Raises:
            NotImplementedError: _description_
        Returns:
            datetime: the processed start date
        """
        raise NotImplementedError

    @abstractmethod
    def add_interval(self, date_value: datetime, interval: int) -> datetime:
        """Add the time interval to the current start date to get the end date
        Args:
            date_value (datetime): datetime value that is the start of the period
            interval (int): time interval to add to the start date tp the end date
        Raises:
            NotImplementedError: raise error of NotImplementedError
        Returns:
            datetime: the end date value not inclusive
        """
        raise NotImplementedError

    @abstractmethod
    def subtract_interval(self, date_value: datetime, interval: int) -> datetime:
        """Subtract the time interval to the current start date to get the end date
        Args:
            date_value (datetime): datetime value that is the start of the period
            interval (int): time interval to add to the start date tp the end date
        Raises:
            NotImplementedError: raise error of NotImplementedError
        Returns:
            datetime: the end date value not inclusive
        """
        raise NotImplementedError


class YearInterval(BaseDateInterval):
    """Class ti Get Yearly interval Start Date"""

    def __init__(self, time_bucket: str, interval: int):
        super().__init__(time_bucket=time_bucket, interval=interval)

    def get_start_date(self, start_date: datetime) -> datetime:
        """Handles Yearly Buckets"""
        if self.time_bucket in ["yearly", "last_year", "this_year", "next_year"]:
            start_date = start_date.replace(month=1, day=1)
        return start_date

    def add_interval(self, date_value: datetime, interval: int):
        """Return a date that's `years` years after the date (or datetime)
        object `date_value`. Return the same calendar date (month and day) in the
        destination year, if it exists, otherwise use the following day
        (thus changing February 29 to March 1).
        """
        next_date = date_value + relativedelta(years=interval)
        return next_date

    def subtract_interval(self, date_value: datetime, interval: int):
        next_date = date_value - relativedelta(years=interval)
        return next_date


class MonthInterval(BaseDateInterval):
    """Gets the Monthly interval Start Date"""

    def __init__(self, time_bucket: str, interval: int):
        super().__init__(time_bucket=time_bucket, interval=interval)

    def get_start_date(self, start_date: datetime) -> datetime:
        """Handles Monthly Buckets"""
        if self.time_bucket in [
            "monthly",
            "month",
            "last_month",
            "this_month",
            "next_month",
        ]:
            start_date = start_date.replace(day=1)
        return start_date

    def add_interval(self, date_value: datetime, interval: int):
        next_date = date_value + relativedelta(months=interval)
        return next_date

    def subtract_interval(self, date_value: datetime, interval: int):
        next_date = date_value - relativedelta(months=interval)
        return next_date


class WeekInterval(BaseDateInterval):
    """Get the Weekly interval Start Date"""

    def __init__(self, time_bucket: str, interval: int):
        super().__init__(time_bucket=time_bucket, interval=interval)

    def get_start_date(self, start_date: datetime) -> datetime:
        """Handles Weekly Buckets"""
        if self.time_bucket in ["weekly", "last_week", "this_week", "next_week"]:
            if datetime.strftime(start_date, "%A") == "Sunday":
                return start_date
            start_date = start_date - timedelta(days=start_date.weekday() + 1)
        return start_date

    def add_interval(self, date_value: datetime, interval: int):
        next_date = date_value + relativedelta(weeks=interval)
        return next_date

    def subtract_interval(self, date_value: datetime, interval: int):
        next_date = date_value - relativedelta(weeks=interval)
        return next_date


class DayInterval(BaseDateInterval):
    """Get the Daily interval Start Date"""

    def __init__(self, time_bucket: str, interval: int):
        super().__init__(time_bucket=time_bucket, interval=interval)

    def get_start_date(self, start_date: datetime) -> datetime:
        """Handles Daily Buckets"""
        return start_date

    def add_interval(self, date_value: datetime, interval: int):
        next_date = date_value + relativedelta(days=interval)
        return next_date

    def subtract_interval(self, date_value: datetime, interval: int):
        next_date = date_value - relativedelta(days=interval)
        return next_date


class HourInterval(BaseDateInterval):
    """Get the Daily interval Start Date"""

    def __init__(self, time_bucket: str, interval: int):
        super().__init__(time_bucket=time_bucket, interval=interval)

    def get_start_date(self, start_date: datetime) -> datetime:
        """Handles Monthly Buckets"""
        if self.time_bucket in ["hourly", "this_hour"]:
            start_date = start_date.replace(minute=1)
        return start_date

    def add_interval(self, date_value: datetime, interval: int):
        next_date = date_value + timedelta(hours=interval)
        return next_date

    def subtract_interval(self, date_value: datetime, interval: int):
        next_date = date_value - timedelta(hours=interval)
        return next_date


class PastDatePhraseHandler(DatePhraseHandler):
    """Handles Past Date Phrases"""

    def phrase_to_date(self) -> Tuple[int, str]:
        """Processes the date value to return self.interval and bucket
        Args:
            date_value (str): string representing date
        Raises:
            ValueError: if passed a wrong and unexpected date value
        Returns:
            Tuple[int, str]: self.interval and bucket(day, week, month, year)
        """
        direction = None
        pattern = re.compile(r"[a-z]+")
        if not isinstance(self.date_value, str) or not pattern.search(
            self.date_value.strip().lower()
        ):
            raise TypeError(
                f"wrong date_string provided, expecting a string but got: {self.date_value}"
            )
        date_value = self.date_value.lower().strip()
        if date_value in [
            "yesterday",
            "last_week",
            "last_month",
            "last_year",
            "last_hour",
        ]:
            self.interval, self.time_bucket, direction = 1, date_value, "ago"
        if date_value in [
            "tomorrow",
            "next_week",
            "next_month",
            "next_year",
            "next_hour",
        ]:
            self.interval, self.time_bucket, direction = 1, date_value, "next"
        if date_value in ["today", "this_week", "this_year", "this_month", "this_hour"]:
            self.interval, self.time_bucket, direction = 0, date_value, None
        if re.search(r"\_", date_value) and self.time_bucket is None:
            if len(date_value.split("_")) != 3 or date_value.split("_")[2] not in (
                "ago",
                "next",
            ):
                raise DateValueError(f"wrong date string provided: {date_value}")
            if len(date_value.split("_")) == 3:
                self.interval, self.time_bucket, direction = date_value.split("_")[:3]
                if self.time_bucket.endswith("s"):
                    self.time_bucket = self.time_bucket.replace("s", "")
        if self.interval is None or self.time_bucket is None:
            raise IntervalTimeBucketError(
                f"interval or time_bucket is None, wrong date_string provided: '{date_value}'"
            )
        # print(self.interval, self.time_bucket)

        self.interval, self.time_bucket = int(self.interval), self.time_bucket.strip()
        if direction == "next":
            self.interval = self.interval * -1
        return self.interval, self.time_bucket


class IntervalDatePhraseHandler(DatePhraseHandler):
    """Class for handling interval date string"""

    def phrase_to_date(self) -> Tuple[int, str]:
        """Processes the interval variable to get the interval and the time_bucket
        Raises:
            TypeError: is the interval value p[rovided is not a string]
            ValueError: if the interval can be split more than 2 times
            ValueError: if time_bucket and interval end up to be None
        Returns:
            Tuple[int, str]: interval that is an int and time_bucket
        """
        if not isinstance(self.date_value, str) or not re.search(
            r"[a-z]+", str(self.date_value).lower()
        ):
            raise TypeError(
                f"wrong interval provided, expecting a string but got: {self.date_value}"
            )
        date_value = self.date_value.lower().strip()
        if date_value in ["day", "yearly", "weekly", "monthly", "hourly"]:
            self.interval, self.time_bucket = 1, date_value
        if len(date_value.split("_")) > 2 and self.time_bucket is None:
            raise TimeIntervalError(
                f"invalid value for interval provided: {date_value}"
            )
        if len(self.date_value.replace(" ", "_").split("_")) == 2:
            self.interval, self.time_bucket = date_value.split("_")
        if self.interval is None or self.time_bucket is None:
            raise IntervalTimeBucketError(
                f"interval or time_bucket is None, wrong interval provided: '{date_value}'"
            )
        # print(self.interval, self.time_bucket)
        self.interval, self.time_bucket = int(self.interval), self.time_bucket.strip()
        return self.interval, self.time_bucket


class DateHandlerFactory:
    """A class that handles provided date to translate it to valie datetime object"""

    def get_date_handler(self, time_bucket: str, interval: int) -> BaseDateInterval:
        """Factory method to determine what time bucket we are going to process
        Args:
            time_bucket (str): either day, week, month, year
            interval (int): interval to be used to subtract or add date
        Raises:
            TimeBucketError: If the time bucket provided is not catered for
        Returns:
            BaseDateInterval: Returns and instance of BaseDateInterval
        """
        root_bucket = None
        time_bucket_mapping = {
            "hour": ["hour", "last_hour", "this_hour", "next_hour"],
            "day": ["day", "yesterday", "today", "tomorrow"],
            "week": ["week", "weekly", "last_week", "this_week", "next_week"],
            "month": ["month", "monthly", "last_month", "this_month", "next_month"],
            "year": ["year", "yearly", "last_year", "this_year", "next_year"],
        }
        for key, val in time_bucket_mapping.items():
            if time_bucket in val:
                root_bucket = key
        if root_bucket is None:
            raise TimeBucketError(f"wrong time bucket in the provided: '{time_bucket}'")
        date_handlers = {
            "hour": HourInterval,
            "day": DayInterval,
            "week": WeekInterval,
            "month": MonthInterval,
            "year": YearInterval,
        }
        return date_handlers[root_bucket](time_bucket=time_bucket, interval=interval)


def string_to_date(date_string: str, time_format="%Y-%m-%d") -> datetime:
    """Processes the Date and Returns the date value to work with
    Args:
        date_string (str): used to determine the date '2022-11-14', 2_days_ago, yeaterday, today
    Returns:
        datetime: datetime value
    """
    date_string = str(date_string).strip()
    if re.search(r"(\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2})", date_string):
        date_part = re.search(
            r"(\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2})", date_string
        ).group()
        return datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S")
    if re.search(r"(\d{4}\-\d{2}\-\d{2})", date_string):
        date_part = re.search(r"(\d{4}\-\d{2}\-\d{2})", date_string).group()
        return datetime.strptime(date_part, "%Y-%m-%d")
    phrase_handler = PastDatePhraseHandler(date_value=date_string)
    interval, time_bucket = phrase_handler.phrase_to_date()
    handler = DateHandlerFactory().get_date_handler(
        time_bucket=time_bucket, interval=interval
    )
    start_date = datetime.now()
    start_date = handler.get_start_date(start_date=start_date)
    date_value = handler.subtract_interval(date_value=start_date, interval=interval)
    return datetime.strptime(date_value.strftime(time_format), time_format)


def date_iterator(
    start_date: str,
    end_date: str,
    interval: str,
    end_inclusive: bool = False,
    time_format: str = "%Y-%m-%d",
) -> Generator[Tuple[str, str], None, None]:
    """Processes the Date and Returns the date value to work with
    Args:
        start_date (str): date string (2022-11-14 or the allowed date string values)
        end_date (str): date string (2022-11-14 or the allowed date string values)
        interval (str): string 1_month, 1_day, yearly, monthly, weekly
        end_inclusive (bool): whether the yielded end for period/interval is inclusive or not.
        time_format (str, optional): The format of the returned date value. Defaults to "%Y-%m-%d".
    Yields:
        Generator[Tuple[str, str], None, None]: start and end (exclusive) for each time interval.
    """
    phrase_handler = IntervalDatePhraseHandler(date_value=interval)
    interval, time_bucket = phrase_handler.phrase_to_date()
    handler = DateHandlerFactory().get_date_handler(
        time_bucket=time_bucket, interval=interval
    )
    startdate = string_to_date(start_date, time_format=time_format)
    enddate = string_to_date(end_date, time_format=time_format)
    startdate = handler.get_start_date(start_date=startdate)
    next_end = handler.add_interval(date_value=startdate, interval=interval)
    while startdate <= enddate:
        end = next_end
        if end_inclusive:
            end = next_end - timedelta(days=1)
            if time_bucket == "hour":
                end = next_end - timedelta(hours=1)
        yield datetime.strftime(startdate, time_format), datetime.strftime(
            end, time_format
        )
        startdate = next_end
        next_end = handler.add_interval(date_value=startdate, interval=interval)
