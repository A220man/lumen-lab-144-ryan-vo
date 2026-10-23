const API_BASE = '/api/v1';

export interface BirthInfo {
  year: number;
  month: number;
  day: number;
  hour: number;
  gender: 'male' | 'female';
  longitude?: number;
  latitude?: number;
  timezone_offset?: number;
}

export interface ChartRequest {
  birth_info: BirthInfo;
  use_true_solar_time?: boolean;
}

export interface PalaceInfo {
  name: string;
  major_stars: string[];
  minor_stars: string[];
  brightness?: string | null;
}

export interface ChartResponse {
  birth_info: BirthInfo;
  solar_date: string;
  lunar_date: string;
  ganzhi_year: string;
  ganzhi_month: string;
  ganzhi_day: string;
  ganzhi_hour: string;
  shichen: string;
  yin_yang_gender: string;
  ming_gong: string;
  shen_gong: string;
  palaces: PalaceInfo[];
  true_solar_time_used: boolean;
  calculated_at: string;
}

export interface TrueSolarTimePreview {
  local_time: string;
  true_solar_time: string;
  correction_minutes: number;
  shichen_local: string;
  shichen_true_solar: string;
}

export interface ApiError {
  error: string;
  detail?: string;
}

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'Request failed',
        detail: `HTTP ${response.status}`,
      }));
      throw new Error(error.detail || error.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async generateChart(request: ChartRequest): Promise<ChartResponse> {
    return this.request<ChartResponse>('/chart', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getTrueSolarTimePreview(
    year: number,
    month: number,
    day: number,
    hour: number,
    longitude: number,
    timezone_offset: number = 8
  ): Promise<TrueSolarTimePreview> {
    const params = new URLSearchParams({
      year: String(year),
      month: String(month),
      day: String(day),
      hour: String(hour),
      longitude: String(longitude),
      timezone_offset: String(timezone_offset),
    });
    return this.request<TrueSolarTimePreview>(`/chart/true-solar-time-preview?${params}`);
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }
}

export const apiClient = new ApiClient();