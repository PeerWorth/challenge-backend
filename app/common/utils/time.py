from datetime import datetime, timezone

from app.common.enums import Timezone


class TimeConverter:
    DB_TIMEZONE = Timezone.UTC  # DB는 항상 UTC
    DISPLAY_TIMEZONE = Timezone.KST  # 기본 표시는 KST

    @classmethod
    def now(cls, tz: Timezone | None = None) -> datetime:
        target_tz = tz or cls.DB_TIMEZONE
        if target_tz == Timezone.UTC:
            return datetime.now(timezone.utc)
        return datetime.now(target_tz.get_zone_info())

    @classmethod
    def convert(cls, dt: datetime, to_tz: Timezone, from_tz: Timezone | None = None) -> datetime:
        if dt.tzinfo is None:
            if from_tz is None:
                dt = dt.replace(tzinfo=timezone.utc)
            elif from_tz == Timezone.UTC:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.replace(tzinfo=from_tz.get_zone_info())

        if to_tz == Timezone.UTC:
            return dt.astimezone(timezone.utc)
        return dt.astimezone(to_tz.get_zone_info())

    @classmethod
    def to_db(cls, dt: datetime, from_tz: Timezone | None = None) -> datetime:
        from_tz = from_tz or cls.DISPLAY_TIMEZONE
        return cls.convert(dt, cls.DB_TIMEZONE, from_tz)

    @classmethod
    def from_db(cls, dt: datetime, to_tz: Timezone | None = None) -> datetime:
        to_tz = to_tz or cls.DISPLAY_TIMEZONE
        return cls.convert(dt, to_tz, cls.DB_TIMEZONE)


def utc_now() -> datetime:
    return TimeConverter.now(Timezone.UTC)


def to_utc(dt: datetime) -> datetime:
    return TimeConverter.to_db(dt, Timezone.KST)


def kst_now() -> datetime:
    return TimeConverter.now(Timezone.KST)


def to_kst(dt: datetime) -> datetime:
    return TimeConverter.from_db(dt, Timezone.KST)
