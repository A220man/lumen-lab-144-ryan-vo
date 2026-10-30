import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChartForm } from '../ChartForm';

// Mock the API client
vi.mock('../../api/client', () => ({
  apiClient: {
    generateChart: vi.fn(),
    getTrueSolarTimePreview: vi.fn(),
    healthCheck: vi.fn(),
  },
}));

import { apiClient } from '../../api/client';

const mockGenerateChart = vi.mocked(apiClient.generateChart);

describe('ChartForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form with all required fields', () => {
    render(<ChartForm />);
    
    expect(screen.getByLabelText('出生日期')).toBeInTheDocument();
    expect(screen.getByLabelText('出生時間')).toBeInTheDocument();
    expect(screen.getByLabelText('性別')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '開始排盤' })).toBeInTheDocument();
  });

  it('shows advanced options when toggled', () => {
    render(<ChartForm />);
    
    const toggleButton = screen.getByRole('button', { name: /展開進階選項/ });
    fireEvent.click(toggleButton);
    
    expect(screen.getByLabelText('經度')).toBeInTheDocument();
    expect(screen.getByLabelText('緯度 (預留)')).toBeInTheDocument();
    expect(screen.getByLabelText('時區')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /收起進階選項/ })).toBeInTheDocument();
  });

  it('submits form and displays result on success', async () => {
    const mockChart = {
      birth_info: { year: 1990, month: 1, day: 1, hour: 12, gender: 'male' as const },
      solar_date: '1990-01-01 12:00',
      lunar_date: '1990-01-15 (approx)',
      ganzhi_year: '庚午',
      ganzhi_month: '丙寅',
      ganzhi_day: '甲子',
      ganzhi_hour: '戊午',
      shichen: '午',
      yin_yang_gender: '陽男',
      ming_gong: '命宫',
      shen_gong: '福德',
      palaces: [
        { name: '命宫', major_stars: ['紫微'], minor_stars: [] },
        { name: '兄弟', major_stars: [], minor_stars: [] },
        { name: '夫妻', major_stars: [], minor_stars: [] },
        { name: '子女', major_stars: [], minor_stars: [] },
        { name: '财帛', major_stars: [], minor_stars: [] },
        { name: '疾厄', major_stars: [], minor_stars: [] },
        { name: '迁移', major_stars: [], minor_stars: [] },
        { name: '奴仆', major_stars: [], minor_stars: [] },
        { name: '官禄', major_stars: [], minor_stars: [] },
        { name: '田宅', major_stars: [], minor_stars: [] },
        { name: '福德', major_stars: [], minor_stars: [] },
        { name: '父母', major_stars: [], minor_stars: [] },
      ],
      true_solar_time_used: true,
      calculated_at: new Date().toISOString(),
    };
    
    mockGenerateChart.mockResolvedValue(mockChart);
    
    render(<ChartForm />);
    
    fireEvent.click(screen.getByRole('button', { name: '開始排盤' }));
    
    await waitFor(() => {
      expect(screen.getByText('排盤結果')).toBeInTheDocument();
    });
    expect(screen.getByText('庚午')).toBeInTheDocument();
    expect(screen.getAllByText('命宫')).toHaveLength(2);
  });

  it('displays error on API failure', async () => {
    mockGenerateChart.mockRejectedValue(new Error('API Error'));
    
    render(<ChartForm />);
    
    fireEvent.click(screen.getByRole('button', { name: '開始排盤' }));
    
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    
    expect(screen.getByText('API Error')).toBeInTheDocument();
  });

  it('disables submit button during loading', async () => {
    const { promise, resolve } = Promise.withResolvers<any>();
    mockGenerateChart.mockReturnValue(promise);
    
    render(<ChartForm />);
    
    fireEvent.click(screen.getByRole('button', { name: '開始排盤' }));
    
    expect(screen.getByRole('button', { name: '排盤中...' })).toBeDisabled();
    
    resolve({} as any);
    await promise;
  });
});