"""True Solar Time calculation for Ziwei Doushu.

Implements NOAA equation of time and longitude correction.
Based on the orphaned true-solar-time.ts from upstream, unified as canonical implementation.
"""
from datetime import datetime, timedelta
from math import sin, cos, radians, degrees, atan2

# Earth's orbital parameters for equation of time (NOAA algorithm)
def equation_of_time(dt: datetime) -> float:
    """Calculate equation of time in minutes (NOAA Solar Calculator algorithm).
    
    Returns the difference between apparent solar time and mean solar time.
    Positive means sundial is ahead of clock.
    """
    # Days since J2000.0 (2000-01-01 12:00 UTC)
    jd = _julian_day(dt)
    n = jd - 2451545.0
    
    # Mean longitude of the sun (degrees)
    L = (280.460 + 0.9856474 * n) % 360
    # Mean anomaly of the sun (degrees)
    g = (357.528 + 0.9856003 * n) % 360
    # Ecliptic longitude (degrees)
    lambda_sun = L + 1.915 * sin(radians(g)) + 0.020 * sin(radians(2 * g))
    lambda_sun %= 360
    
    # Obliquity of the ecliptic (degrees)
    epsilon = 23.439 - 0.0000004 * n
    
    # Right ascension (degrees)
    alpha = degrees(
        atan2(
            cos(radians(epsilon)) * sin(radians(lambda_sun)),
            cos(radians(lambda_sun))
        )
    )
    alpha %= 360
    
    # Equation of time in minutes
    # EoT = 4 * (L - alpha) - but need to handle wrap-around
    diff = L - alpha
    if diff < -180:
        diff += 360
    elif diff > 180:
        diff -= 360
    
    eot = 4 * diff  # minutes
    
    return eot


def _julian_day(dt: datetime) -> float:
    """Calculate Julian Day Number for a datetime (UTC)."""
    year = dt.year
    month = dt.month
    day = dt.day + dt.hour / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    
    if month <= 2:
        year -= 1
        month += 12
    
    a = year // 100
    b = 2 - a + a // 4
    
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    return jd


def calculate_true_solar_time(
    dt: datetime,
    longitude: float,
    timezone_offset: int = 8,
) -> datetime:
    """Calculate true solar time from local clock time.
    
    Args:
        dt: Local clock time (naive datetime, assumed to be in timezone_offset)
        longitude: Longitude in degrees (East positive, e.g., 114.17 for Hong Kong)
        timezone_offset: Hours from UTC (e.g., 8 for HKT)
    
    Returns:
        True solar time as naive datetime (same date component adjusted)
    
    Formula:
        True Solar Time = Local Clock Time 
                        + (longitude - timezone_meridian) * 4 minutes
                        + Equation of Time
        where timezone_meridian = timezone_offset * 15
    """
    # Standard meridian for the timezone
    standard_meridian = timezone_offset * 15.0
    
    # Longitude correction: 4 minutes per degree
    longitude_correction = (longitude - standard_meridian) * 4.0  # minutes
    
    # Equation of time correction
    eot = equation_of_time(dt)  # minutes
    
    # Total correction in minutes
    total_correction = longitude_correction + eot
    
    # Apply correction
    true_solar_dt = dt + timedelta(minutes=total_correction)
    
    return true_solar_dt


def resolve_ziwei_day_offset(true_solar_dt: datetime) -> tuple[datetime, bool]:
    """Resolve Ziwei day boundary using Late Zishi rule.
    
    In Ziwei Doushu, the day changes at 23:00 (start of 子时) true solar time.
    If true solar time is >= 23:00, the ganzhi day advances to next day.
    
    Returns:
        (adjusted_date, day_advanced)
    """
    if true_solar_dt.hour >= 23:
        # Late Zishi: day advances
        adjusted = true_solar_dt + timedelta(days=1)
        return adjusted.replace(hour=0, minute=0, second=0, microsecond=0), True
    return true_solar_dt, False


def get_shichen(hour: int) -> str:
    """Get Chinese shichen (时辰) name from hour (0-23)."""
    shichen_map = {
        23: "子", 0: "子",
        1: "丑", 2: "丑",
        3: "寅", 4: "寅",
        5: "卯", 6: "卯",
        7: "辰", 8: "辰",
        9: "巳", 10: "巳",
        11: "午", 12: "午",
        13: "未", 14: "未",
        15: "申", 16: "申",
        17: "酉", 18: "酉",
        19: "戌", 20: "戌",
        21: "亥", 22: "亥",
    }
    return shichen_map.get(hour, "子")


# Gan-Zhi (Stem-Branch) calculation
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def ganzhi_year(year: int) -> str:
    """Calculate year pillar (ganzhi) for given solar year.
    Reference: 1984 = 甲子 (start of 60-year cycle)"""
    offset = (year - 1984) % 60
    stem = HEAVENLY_STEMS[offset % 10]
    branch = EARTHLY_BRANCHES[offset % 12]
    return stem + branch


def ganzhi_month(year: int, month: int) -> str:
    """Calculate month pillar. Month branches start with 寅 (month 1 = 寅月).
    Year stem determines month stem via 五虎遁."""
    # Month branch: 1=寅, 2=卯, ..., 12=丑
    month_branch_idx = (month + 1) % 12
    month_branch = EARTHLY_BRANCHES[month_branch_idx]
    
    # 五虎遁: year stem determines first month stem
    year_stem_idx = (year - 1984) % 10
    # Mapping: 甲/己 years -> 丙寅月, 乙/庚 -> 戊寅, 丙/辛 -> 庚寅, 丁/壬 -> 壬寅, 戊/癸 -> 甲寅
    first_month_stem_map = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]  # 丙戊庚壬甲...
    first_month_stem_idx = first_month_stem_map[year_stem_idx]
    month_stem_idx = (first_month_stem_idx + month - 1) % 10
    month_stem = HEAVENLY_STEMS[month_stem_idx]
    
    return month_stem + month_branch


def ganzhi_day(dt: datetime) -> str:
    """Calculate day pillar using known reference: 2000-01-01 = 戊辰 (JD 2451545)."""
    jd = int(_julian_day(dt.replace(hour=12, minute=0, second=0, microsecond=0)) + 0.5)
    # 2000-01-01 JD 2451545 = 戊辰 (index 4 in 60-cycle: 甲子=0, 乙丑=1, 丙寅=2, 丁卯=3, 戊辰=4)
    offset = (jd - 2451545) % 60
    stem = HEAVENLY_STEMS[(4 + offset) % 10]
    branch = EARTHLY_BRANCHES[(4 + offset) % 12]
    return stem + branch


def ganzhi_hour(day_stem: str, hour: int) -> str:
    """Calculate hour pillar from day stem and hour (0-23).
    子时 (23:00-00:59) uses branch 子."""
    # Convert hour to branch index (0=子, 1=丑, ..., 11=亥)
    if hour == 23:
        branch_idx = 0
    else:
        branch_idx = (hour + 1) // 2
    branch = EARTHLY_BRANCHES[branch_idx]
    
    # Day stem determines hour stem via 五鼠遁
    stem_idx = HEAVENLY_STEMS.index(day_stem)
    # 甲/己日 -> 甲子时, 乙/庚 -> 丙子, 丙/辛 -> 戊子, 丁/壬 -> 庚子, 戊/癸 -> 壬子
    first_hour_stem_map = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]
    first_hour_stem_idx = first_hour_stem_map[stem_idx]
    hour_stem_idx = (first_hour_stem_idx + branch_idx) % 10
    hour_stem = HEAVENLY_STEMS[hour_stem_idx]
    
    return hour_stem + branch