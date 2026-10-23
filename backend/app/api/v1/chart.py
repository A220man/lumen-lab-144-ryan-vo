from fastapi import APIRouter, HTTPException, status
from app.models.chart import ChartRequest, ChartResponse, ErrorResponse
from app.services.ziwei.engine import ziwei_engine

router = APIRouter(tags=["chart"])


@router.post(
    "/chart",
    response_model=ChartResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid birth data"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Generate Ziwei Doushu chart",
    description="Generate a complete Ziwei Doushu natal chart from birth information. "
                "Uses true solar time correction (longitude + equation of time) by default.",
)
async def generate_chart(request: ChartRequest) -> ChartResponse:
    """Generate Ziwei Doushu chart.
    
    - **birth_info**: Birth date, time, gender, and optional location for true solar time
    - **use_true_solar_time**: Apply longitude correction and NOAA equation of time (default: true)
    
    Returns complete chart with 12 palaces, major/minor stars, ganzhi pillars, and palace positions.
    """
    try:
        result = ziwei_engine.generate_chart(
            birth_info=request.birth_info,
            use_true_solar_time=request.use_true_solar_time,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chart generation failed: {str(e)}",
        )


@router.get(
    "/chart/true-solar-time-preview",
    summary="Preview true solar time correction",
    description="Calculate true solar time correction for a given birth time and location "
                "without generating a full chart. Useful for verifying shichen boundary.",
)
async def true_solar_time_preview(
    year: int,
    month: int,
    day: int,
    hour: int,
    longitude: float,
    timezone_offset: int = 8,
) -> dict:
    """Preview true solar time adjustment."""
    return ziwei_engine.calculate_true_solar_time_preview(
        year=year,
        month=month,
        day=day,
        hour=hour,
        longitude=longitude,
        timezone_offset=timezone_offset,
    )


@router.get("/health", tags=["health"])
async def chart_health():
    return {"status": "ok", "service": "chart-api"}