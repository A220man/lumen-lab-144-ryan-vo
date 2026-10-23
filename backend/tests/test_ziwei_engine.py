"""Tests for Ziwei Doushu engine - core calculations and boundary cases."""

import pytest
from datetime import datetime

from app.services.ziwei.true_solar_time import (
    calculate_true_solar_time,
    equation_of_time,
    resolve_ziwei_day_offset,
    get_shichen,
    ganzhi_year,
    ganzhi_month,
    ganzhi_day,
    ganzhi_hour,
)
from app.services.ziwei.calculations import generate_chart
from app.services.ziwei.engine import ziwei_engine
from app.models.chart import BirthInfo, Gender


class TestEquationOfTime:
    """Test NOAA equation of time calculation."""
    
    def test_eot_known_values(self):
        """Test equation of time against known approximate values."""
        # Around winter solstice: EoT ~ -3 to -4 min (sundial behind)
        dt = datetime(2025, 12, 21, 12, 0, 0)
        eot = equation_of_time(dt)
        assert -5 < eot < 5  # Reasonable range
    
    def test_eot_summer(self):
        """Test EoT around summer solstice."""
        dt = datetime(2025, 6, 21, 12, 0, 0)
        eot = equation_of_time(dt)
        assert -5 < eot < 5
    
    def test_eot_april(self):
        """Test EoT around April (near zero crossing)."""
        dt = datetime(2025, 4, 15, 12, 0, 0)
        eot = equation_of_time(dt)
        assert -3 < eot < 3


class TestTrueSolarTime:
    """Test true solar time calculation with longitude + EoT."""
    
    def test_hong_kong_boundary_case(self):
        """Test HK 2025-12-31 23:00 -> should be 亥 shichen (22:34 true solar).
        
        This is the critical boundary case from issue #45:
        - Clock: 2025-12-31 23:00 HKT (longitude 114.17, UTC+8)
        - Longitude correction: (114.17 - 120) * 4 = -23.32 min
        - EoT around Dec 31: ~+3 min
        - Total: ~-20 min -> 22:40 true solar -> 亥 shichen (21:00-22:59)
        """
        dt = datetime(2025, 12, 31, 23, 0, 0)
        true_solar = calculate_true_solar_time(dt, longitude=114.17, timezone_offset=8)
        
        # Should be in 亥 hour (21:00-22:59)
        assert true_solar.hour == 22 or true_solar.hour == 21
        shichen = get_shichen(true_solar.hour)
        assert shichen == "亥", f"Expected 亥 shichen, got {shichen}"
    
    def test_longitude_only_correction(self):
        """Test that longitude correction works without EoT (if disabled)."""
        # At standard meridian (120°E for UTC+8), no longitude correction
        dt = datetime(2025, 1, 1, 12, 0, 0)
        true_solar = calculate_true_solar_time(dt, longitude=120.0, timezone_offset=8)
        # Only EoT applies
        assert abs((true_solar - dt).total_seconds() / 60) < 20
    
    def test_west_longitude(self):
        """Test locations west of standard meridian."""
        # San Francisco: longitude -122.4, UTC-8 (but test with UTC+8 offset for math)
        dt = datetime(2025, 6, 15, 12, 0, 0)
        true_solar = calculate_true_solar_time(dt, longitude=-122.4, timezone_offset=-8)
        # Should be corrected
        assert true_solar != dt


class TestZiweiDayOffset:
    """Test Late Zishi rule (day changes at 23:00 true solar)."""
    
    def test_before_23_no_advance(self):
        """Before 23:00 true solar, day stays same."""
        dt = datetime(2025, 12, 31, 22, 30, 0)
        adjusted, advanced = resolve_ziwei_day_offset(dt)
        assert not advanced
        assert adjusted.day == 31
    
    def test_at_23_advances(self):
        """At 23:00 true solar, day advances."""
        dt = datetime(2025, 12, 31, 23, 0, 0)
        adjusted, advanced = resolve_ziwei_day_offset(dt)
        assert advanced
        assert adjusted.day == 1
        assert adjusted.month == 1
    
    def test_after_23_advances(self):
        """After 23:00 true solar (e.g., 23:30), day advances."""
        dt = datetime(2025, 12, 31, 23, 30, 0)
        adjusted, advanced = resolve_ziwei_day_offset(dt)
        assert advanced
        assert adjusted.day == 1


class TestShichen:
    """Test shichen (时辰) determination."""
    
    def test_shichen_boundaries(self):
        """Test all shichen boundaries."""
        cases = [
            (23, "子"), (0, "子"),
            (1, "丑"), (2, "丑"),
            (3, "寅"), (4, "寅"),
            (5, "卯"), (6, "卯"),
            (7, "辰"), (8, "辰"),
            (9, "巳"), (10, "巳"),
            (11, "午"), (12, "午"),
            (13, "未"), (14, "未"),
            (15, "申"), (16, "申"),
            (17, "酉"), (18, "酉"),
            (19, "戌"), (20, "戌"),
            (21, "亥"), (22, "亥"),
        ]
        for hour, expected in cases:
            assert get_shichen(hour) == expected, f"Hour {hour}: expected {expected}"


class TestGanzhi:
    """Test ganzhi (stem-branch) calculations."""
    
    def test_year_pillar(self):
        """Test year pillar known values."""
        # 1984 = 甲子
        assert ganzhi_year(1984) == "甲子"
        # 2024 = 甲辰
        assert ganzhi_year(2024) == "甲辰"
        # 2025 = 乙巳
        assert ganzhi_year(2025) == "乙巳"
    
    def test_month_pillar(self):
        """Test month pillar."""
        # 2024年1月 (甲辰年) -> 丙寅月
        assert ganzhi_month(2024, 1) == "丙寅"
    
    def test_day_pillar(self):
        """Test day pillar against known reference."""
        # 2000-01-01 = 戊辰
        dt = datetime(2000, 1, 1)
        assert ganzhi_day(dt) == "戊辰"
    
    def test_hour_pillar(self):
        """Test hour pillar from day stem using standard 五鼠遁."""
        # 戊日子时 -> 壬子 (standard 五鼠遁: 戊/癸日 -> 壬子时)
        assert ganzhi_hour("戊", 23) == "壬子"
        assert ganzhi_hour("戊", 0) == "壬子"
        # 戊日丑时 -> 癸丑
        assert ganzhi_hour("戊", 1) == "癸丑"
        # 甲日子时 -> 甲子
        assert ganzhi_hour("甲", 23) == "甲子"
        # 戊日丑时 -> 癸丑
        assert ganzhi_hour("戊", 1) == "癸丑"
        # 己日子时 -> 甲子


class TestGenerateChart:
    """Test full chart generation."""
    
    def test_basic_chart_generation(self):
        """Test basic chart generation works."""
        result = generate_chart(
            year=1990,
            month=1,
            day=1,
            hour=12,
            gender="male",
            longitude=None,
            use_true_solar_time=False,
        )
        
        assert result["solar_date"] == "1990-01-01 12:00"
        assert result["yin_yang_gender"] == "阳男"
        assert result["shichen"] == "午"
        assert len(result["palaces"]) == 12
        assert result["ming_gong"] in [p["name"] for p in result["palaces"]]
        assert result["shen_gong"] in [p["name"] for p in result["palaces"]]
    
    def test_chart_with_true_solar_time(self):
        """Test chart with true solar time enabled."""
        result = generate_chart(
            year=1990,
            month=1,
            day=1,
            hour=12,
            gender="female",
            longitude=116.4,  # Beijing
            timezone_offset=8,
            use_true_solar_time=True,
        )
        
        assert result["true_solar_time_used"] is True
        assert result["yin_yang_gender"] == "阴女"
    
    def test_gender_validation_rejects_invalid(self):
        """Test that invalid gender values raise ValueError (issue #38)."""
        invalid_values = ["typo", "", "Male", "FEMALE", "other", None, 123, "male ", " male"]
        
        for invalid in invalid_values:
            with pytest.raises(ValueError, match="gender must be 'male' or 'female'"):
                generate_chart(
                    year=1990, month=1, day=1, hour=12,
                    gender=invalid,  # type: ignore
                    use_true_solar_time=False,
                )
    
    def test_gender_validation_accepts_valid(self):
        """Test that valid gender values work."""
        for valid in ["male", "female"]:
            result = generate_chart(
                year=1990, month=1, day=1, hour=12,
                gender=valid, use_true_solar_time=False,
            )
            assert result["yin_yang_gender"] in ("阳男", "阴女")
    
    def test_hk_boundary_chart(self):
        """Test the critical HK boundary case from issue #45.
        
        Birth: 2025-12-31 23:00 HKT, Hong Kong (longitude ≈ 114.17)
        Expected: 亥 shichen (true solar ~22:34), day stays 2025-12-31.
        Our calculated day pillar for 2025-12-31 is 甲申.
        Without fix: 子 shichen, day advances to 2026-01-01 (乙酉).
        """
        result = generate_chart(
            year=2025,
            month=12,
            day=31,
            hour=23,
            gender="male",
            longitude=114.17,
            timezone_offset=8,
            use_true_solar_time=True,
        )
        
        # With true solar time, should be 亥 shichen
        assert result["shichen"] == "亥", f"Expected 亥, got {result['shichen']}"
        # Day should NOT advance (stays 2025-12-31) -> day pillar 甲申
        assert result["ganzhi_day"] == "甲申", f"Expected 甲申 day, got {result['ganzhi_day']}"
    def test_without_true_solar_time_uses_clock(self):
        """Test that without true solar time, clock hour determines shichen."""
        result = generate_chart(
            year=2025,
            month=12,
            day=31,
            hour=23,
            gender="male",
            longitude=114.17,
            use_true_solar_time=False,
        )
        
        # Clock hour 23 -> 子 shichen
        assert result["shichen"] == "子"
        # Day advances (Late Zishi rule: hour 23 -> day advances)
        # Original date 2025-12-31 (甲申) -> next day 2026-01-01 (乙酉)
        assert result["ganzhi_day"] == "乙酉"


class TestEngineService:
    """Test the engine service facade."""
    
    def test_engine_generate_chart(self):
        """Test engine service produces ChartResponse."""
        birth_info = BirthInfo(
            year=1990, month=1, day=1, hour=12,
            gender=Gender.MALE, longitude=116.4, timezone_offset=8
        )
        response = ziwei_engine.generate_chart(birth_info, use_true_solar_time=True)
        
        assert response.yin_yang_gender == "阳男"
        assert len(response.palaces) == 12
        assert response.true_solar_time_used is True
    
    def test_engine_preview_true_solar_time(self):
        """Test true solar time preview."""
        preview = ziwei_engine.calculate_true_solar_time_preview(
            year=2025, month=12, day=31, hour=23,
            longitude=114.17, timezone_offset=8
        )
        
        assert "local_time" in preview
        assert "true_solar_time" in preview
        assert "correction_minutes" in preview
        assert "shichen_local" in preview
        assert "shichen_true_solar" in preview
        # Local 23:00 -> 子, true solar ~22:40 -> 亥
        assert preview["shichen_local"] == "子"
        assert preview["shichen_true_solar"] == "亥"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_leap_year_feb_29(self):
        """Test Feb 29 on leap year."""
        result = generate_chart(
            year=2024, month=2, day=29, hour=12,
            gender="male", use_true_solar_time=False,
        )
        assert result["solar_date"] == "2024-02-29 12:00"
    
    def test_year_boundary_dec_31_jan_1(self):
        """Test year boundary with true solar time."""
        # 2025-12-31 23:00 with longitude correction pushing to next day
        result = generate_chart(
            year=2025, month=12, day=31, hour=23,
            gender="male", longitude=130.0, timezone_offset=8,
            use_true_solar_time=True,
        )
        # Should handle year rollover correctly
        assert result["ganzhi_year"] in ("乙巳", "丙午")
    
    def test_polar_longitude(self):
        """Test extreme longitudes."""
        for lon in [-179, 179]:
            result = generate_chart(
                year=1990, month=6, day=15, hour=12,
                gender="male", longitude=lon, timezone_offset=0,
                use_true_solar_time=True,
            )
            assert result["true_solar_time_used"] is True