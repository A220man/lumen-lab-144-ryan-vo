"""Ziwei Doushu engine service - main entry point for chart generation."""

from typing import Optional
from datetime import datetime

from app.services.ziwei.calculations import generate_chart
from app.services.ziwei.true_solar_time import calculate_true_solar_time
from app.models.chart import BirthInfo, ChartResponse, PalaceInfo


class ZiweiEngine:
    """Main service for Ziwei Doushu chart generation."""
    
    def generate_chart(
        self,
        birth_info: BirthInfo,
        use_true_solar_time: bool = True,
    ) -> ChartResponse:
        """Generate a complete Ziwei chart from birth information."""
        result = generate_chart(
            year=birth_info.year,
            month=birth_info.month,
            day=birth_info.day,
            hour=birth_info.hour,
            gender=birth_info.gender.value,
            longitude=birth_info.longitude,
            latitude=birth_info.latitude,
            timezone_offset=birth_info.timezone_offset or 8,
            use_true_solar_time=use_true_solar_time,
        )
        
        # Convert to response model
        palaces = [
            PalaceInfo(
                name=p["name"],
                major_stars=p["major_stars"],
                minor_stars=p["minor_stars"],
                brightness=p["brightness"],
            )
            for p in result["palaces"]
        ]
        
        return ChartResponse(
            birth_info=birth_info,
            solar_date=result["solar_date"],
            lunar_date=result["lunar_date"],
            ganzhi_year=result["ganzhi_year"],
            ganzhi_month=result["ganzhi_month"],
            ganzhi_day=result["ganzhi_day"],
            ganzhi_hour=result["ganzhi_hour"],
            shichen=result["shichen"],
            yin_yang_gender=result["yin_yang_gender"],
            ming_gong=result["ming_gong"],
            shen_gong=result["shen_gong"],
            palaces=palaces,
            true_solar_time_used=result["true_solar_time_used"],
            calculated_at=datetime.utcnow(),
        )
    
    def calculate_true_solar_time_preview(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        longitude: float,
        timezone_offset: int = 8,
    ) -> dict:
        """Preview true solar time calculation without full chart."""
        base_dt = datetime(year, month, day, hour, 0, 0)
        true_solar_dt = calculate_true_solar_time(base_dt, longitude, timezone_offset)
        
        return {
            "local_time": base_dt.strftime("%Y-%m-%d %H:%M"),
            "true_solar_time": true_solar_dt.strftime("%Y-%m-%d %H:%M"),
            "correction_minutes": round(
                (true_solar_dt - base_dt).total_seconds() / 60, 2
            ),
            "shichen_local": self._get_shichen(base_dt.hour),
            "shichen_true_solar": self._get_shichen(true_solar_dt.hour),
        }
    
    def _get_shichen(self, hour: int) -> str:
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


# Singleton instance
ziwei_engine = ZiweiEngine()