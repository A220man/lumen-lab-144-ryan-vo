import React, { useState } from 'react';
import { apiClient, BirthInfo, ChartResponse } from '../api/client';
import { ChartDisplay } from './ChartDisplay';

const GENDER_OPTIONS = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
] as const;

const TIMEZONE_OPTIONS = [
  { value: -12, label: 'UTC-12' },
  { value: -11, label: 'UTC-11' },
  { value: -10, label: 'UTC-10 (HST)' },
  { value: -9, label: 'UTC-9 (AKST)' },
  { value: -8, label: 'UTC-8 (PST)' },
  { value: -7, label: 'UTC-7 (MST)' },
  { value: -6, label: 'UTC-6 (CST)' },
  { value: -5, label: 'UTC-5 (EST)' },
  { value: -4, label: 'UTC-4 (AST)' },
  { value: -3, label: 'UTC-3' },
  { value: -2, label: 'UTC-2' },
  { value: -1, label: 'UTC-1' },
  { value: 0, label: 'UTC+0 (GMT)' },
  { value: 1, label: 'UTC+1 (CET)' },
  { value: 2, label: 'UTC+2 (EET)' },
  { value: 3, label: 'UTC+3 (MSK)' },
  { value: 4, label: 'UTC+4 (GST)' },
  { value: 5, label: 'UTC+5 (PKT)' },
  { value: 6, label: 'UTC+6 (BST)' },
  { value: 7, label: 'UTC+7 (ICT)' },
  { value: 8, label: 'UTC+8 (HKT/CST)' },
  { value: 9, label: 'UTC+9 (JST/KST)' },
  { value: 10, label: 'UTC+10 (AEST)' },
  { value: 11, label: 'UTC+11 (SBT)' },
  { value: 12, label: 'UTC+12 (NZST)' },
  { value: 13, label: 'UTC+13' },
  { value: 14, label: 'UTC+14' },
] as const;

export function ChartForm() {
  const [formData, setFormData] = useState<BirthInfo>({
    year: 1990,
    month: 1,
    day: 1,
    hour: 12,
    gender: 'male',
    longitude: 116.4,
    latitude: 39.9,
    timezone_offset: 8,
  });
  const [result, setResult] = useState<ChartResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleChange = <K extends keyof BirthInfo>(field: K, value: BirthInfo[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.generateChart({
        birth_info: formData,
        use_true_solar_time: true,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : '生成排盤失敗，請重試');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentYear = () => new Date().getFullYear();

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>紫微斗數排盤</h1>
        <p style={styles.subtitle}>基於瞿海藩《天紀》系統 · 真太陽時修正</p>
      </header>

      <main style={styles.main}>
        <section style={styles.formSection} aria-labelledby="form-title">
          <h2 id="form-title" style={styles.sectionTitle}>出生資料</h2>
          
          <form onSubmit={handleSubmit} style={styles.form} noValidate>
            <div style={styles.grid}>
              <div style={styles.field}>
                <label htmlFor="year" style={styles.label}>年份</label>
                <input
                  id="year"
                  type="number"
                  min="1900"
                  max={getCurrentYear()}
                  value={formData.year}
                  onChange={(e) => handleChange('year', Number(e.target.value))}
                  style={styles.input}
                  required
                  aria-required="true"
                />
              </div>

              <div style={styles.field}>
                <label htmlFor="month" style={styles.label}>月份</label>
                <input
                  id="month"
                  type="number"
                  min="1"
                  max="12"
                  value={formData.month}
                  onChange={(e) => handleChange('month', Number(e.target.value))}
                  style={styles.input}
                  required
                  aria-required="true"
                />
              </div>

              <div style={styles.field}>
                <label htmlFor="day" style={styles.label}>日期</label>
                <input
                  id="day"
                  type="number"
                  min="1"
                  max="31"
                  value={formData.day}
                  onChange={(e) => handleChange('day', Number(e.target.value))}
                  style={styles.input}
                  required
                  aria-required="true"
                />
              </div>

              <div style={styles.field}>
                <label htmlFor="hour" style={styles.label}>時辰 (小時)</label>
                <input
                  id="hour"
                  type="number"
                  min="0"
                  max="23"
                  value={formData.hour}
                  onChange={(e) => handleChange('hour', Number(e.target.value))}
                  style={styles.input}
                  required
                  aria-required="true"
                />
              </div>

              <div style={styles.field}>
                <label htmlFor="gender" style={styles.label}>性別</label>
                <select
                  id="gender"
                  value={formData.gender}
                  onChange={(e) => handleChange('gender', e.target.value as 'male' | 'female')}
                  style={styles.select}
                  required
                  aria-required="true"
                >
                  {GENDER_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              style={styles.advancedToggle}
              aria-expanded={showAdvanced}
            >
              {showAdvanced ? '收起進階選項' : '展開進階選項 (真太陽時修正)'}
            </button>

            {showAdvanced && (
              <fieldset style={styles.advancedFieldset}>
                <legend style={styles.legend}>真太陽時修正參數</legend>
                <p style={styles.helperText}>
                  經度用於計算真太陽時（當地平太陽時），修正時辰邊界誤差。
                  香港約 114.17°E，北京約 116.4°E，台北約 121.5°E。
                </p>
                <div style={styles.grid}>
                  <div style={styles.field}>
                    <label htmlFor="longitude" style={styles.label}>經度</label>
                    <input
                      id="longitude"
                      type="number"
                      step="0.01"
                      min="-180"
                      max="180"
                      value={formData.longitude ?? ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        const num = val ? Number(val) : undefined;
                        handleChange('longitude', num as number | undefined);
                      }}
                      style={styles.input}
                      placeholder="如 114.17"
                    />
                  </div>

                  <div style={styles.field}>
                    <label htmlFor="latitude" style={styles.label}>緯度 (預留)</label>
                    <input
                      id="latitude"
                      type="number"
                      step="0.01"
                      min="-90"
                      max="90"
                      value={formData.latitude ?? ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        const num = val ? Number(val) : undefined;
                        handleChange('latitude', num as number | undefined);
                      }}
                      style={styles.input}
                      placeholder="如 39.9"
                    />
                  </div>

                  <div style={styles.field}>
                    <label htmlFor="timezone_offset" style={styles.label}>時區</label>
                    <select
                      id="timezone_offset"
                      value={formData.timezone_offset ?? 8}
                      onChange={(e) => handleChange('timezone_offset', Number(e.target.value))}
                      style={styles.select}
                    >
                      {TIMEZONE_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </fieldset>
            )}

            {error && (
              <div style={styles.error} role="alert">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                ...styles.submitButton,
                ...(loading ? styles.submitButtonDisabled : {}),
              }}
            >
              {loading ? '排盤中...' : '開始排盤'}
            </button>
          </form>
        </section>

        {result && (
          <section style={styles.resultSection} aria-labelledby="result-title">
            <h2 id="result-title" style={styles.sectionTitle}>排盤結果</h2>
            <ChartDisplay chart={result} />
          </section>
        )}

        {!result && !loading && !error && (
          <section style={styles.emptySection}>
            <p style={styles.emptyText}>請填寫出生資料並點擊「開始排盤」</p>
          </section>
        )}
      </main>

      <footer style={styles.footer}>
        <p>Lumen Lab - 紫微斗數排盤 | Ryan Vo &copy; 2024</p>
        <p style={styles.footerNote}>僅供學習研究參考，不構成任何決策建議</p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    padding: 'var(--spacing-xl) var(--spacing-lg)',
    textAlign: 'center',
    background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%)',
    color: '#fff',
  },
  title: {
    fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
    fontWeight: 700,
    marginBottom: 'var(--spacing-xs)',
  },
  subtitle: {
    fontSize: 'clamp(0.875rem, 2vw, 1rem)',
    opacity: 0.9,
    fontWeight: 300,
  },
  main: {
    flex: 1,
    padding: 'var(--spacing-lg)',
    maxWidth: '800px',
    width: '100%',
    margin: '0 auto',
  },
  formSection: {
    background: 'var(--color-bg-card)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-md)',
    padding: 'var(--spacing-lg)',
    marginBottom: 'var(--spacing-lg)',
  },
  sectionTitle: {
    fontSize: '1.25rem',
    fontWeight: 600,
    marginBottom: 'var(--spacing-md)',
    color: 'var(--color-primary)',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-md)',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: 'var(--spacing-md)',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-xs)',
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: 500,
    color: 'var(--color-text)',
  },
  input: {
    padding: 'var(--spacing-sm) var(--spacing-md)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    background: 'var(--color-bg-card)',
    color: 'var(--color-text)',
    transition: 'border-color 0.2s, box-shadow 0.2s',
  },
  select: {
    padding: 'var(--spacing-sm) var(--spacing-md)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    background: 'var(--color-bg-card)',
    color: 'var(--color-text)',
  },
  advancedToggle: {
    background: 'none',
    border: 'none',
    color: 'var(--color-primary)',
    fontSize: '0.875rem',
    fontWeight: 500,
    padding: 'var(--spacing-sm) 0',
    textAlign: 'left',
    cursor: 'pointer',
  },
  advancedFieldset: {
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    padding: 'var(--spacing-md)',
    marginTop: 'var(--spacing-sm)',
  },
  legend: {
    fontWeight: 600,
    fontSize: '0.875rem',
    color: 'var(--color-primary)',
    padding: '0 var(--spacing-sm)',
  },
  helperText: {
    fontSize: '0.8rem',
    color: 'var(--color-text-muted)',
    marginBottom: 'var(--spacing-md)',
    lineHeight: 1.5,
  },
  error: {
    padding: 'var(--spacing-md)',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 'var(--radius-md)',
    color: 'var(--color-error)',
    fontSize: '0.875rem',
  },
  submitButton: {
    marginTop: 'var(--spacing-sm)',
    padding: 'var(--spacing-md) var(--spacing-xl)',
    background: 'var(--color-accent)',
    color: '#fff',
    border: 'none',
    borderRadius: 'var(--radius-md)',
    fontSize: '1rem',
    fontWeight: 600,
    transition: 'background-color 0.2s, transform 0.1s',
  },
  submitButtonDisabled: {
    background: 'var(--color-text-muted)',
    cursor: 'not-allowed',
  },
  resultSection: {
    animation: 'fadeIn 0.3s ease-out',
  },
  emptySection: {
    textAlign: 'center',
    padding: 'var(--spacing-xl)',
    color: 'var(--color-text-muted)',
  },
  emptyText: {
    fontSize: '1rem',
  },
  footer: {
    padding: 'var(--spacing-lg)',
    textAlign: 'center',
    color: 'var(--color-text-muted)',
    fontSize: '0.875rem',
    borderTop: '1px solid var(--color-border)',
    marginTop: 'auto',
  },
  footerNote: {
    fontSize: '0.75rem',
    marginTop: 'var(--spacing-xs)',
  },
};