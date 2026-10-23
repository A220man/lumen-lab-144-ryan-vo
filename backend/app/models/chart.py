from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class BirthInfo(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="Birth year (solar)")
    month: int = Field(..., ge=1, le=12, description="Birth month (solar)")
    day: int = Field(..., ge=1, le=31, description="Birth day (solar)")
    hour: int = Field(..., ge=0, le=23, description="Birth hour (0-23, local clock time)")
    gender: Gender = Field(..., description="Birth gender: 'male' or 'female'")
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
        description="Birth longitude for true solar time correction (e.g., 114.17 for Hong Kong)",
    )
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
        description="Birth latitude (optional, for future use)",
    )
    timezone_offset: Optional[int] = Field(
        default=None,
        ge=-12,
        le=14,
        description="Timezone offset in hours from UTC (e.g., 8 for HKT/UTC+8)",
    )

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: int, info):
        # Basic validation; true validation happens in engine with month/year
        if v < 1 or v > 31:
            raise ValueError("day must be 1-31")
        return v


class ChartRequest(BaseModel):
    birth_info: BirthInfo
    use_true_solar_time: bool = Field(
        default=True,
        description="Whether to apply true solar time correction (longitude + equation of time)",
    )


class PalaceInfo(BaseModel):
    name: str
    major_stars: list[str] = []
    minor_stars: list[str] = []
    brightness: Optional[str] = None


class ChartResponse(BaseModel):
    birth_info: BirthInfo
    solar_date: str
    lunar_date: str
    ganzhi_year: str
    ganzhi_month: str
    ganzhi_day: str
    ganzhi_hour: str
    shichen: str
    yin_yang_gender: str
    ming_gong: str
    shen_gong: str
    palaces: list[PalaceInfo]
    true_solar_time_used: bool
    calculated_at: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None