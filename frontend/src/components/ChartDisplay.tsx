import React from 'react';
import { ChartResponse, PalaceInfo } from '../api/client';

interface ChartDisplayProps {
  chart: ChartResponse;
}

const PALACE_EMOJI: Record<string, string> = {
  命宫: '🏠',
  兄弟: '👥',
  夫妻: '💑',
  子女: '👶',
  财帛: '💰',
  疾厄: '🏥',
  迁移: '✈️',
  奴仆: '🤝',
  官禄: '💼',
  田宅: '🏘️',
  福德: '🍀',
  父母: '👨‍👩‍👧‍👦',
};

const BRIGHTNESS_COLORS: Record<string, string> = {
  庙: '#27ae60',
  旺: '#2ecc71',
  得: '#3498db',
  平: '#95a5a6',
  陷: '#e74c3c',
};

export function ChartDisplay({ chart }: ChartDisplayProps) {
  const { palaces = [], ...info } = chart;
  return (
    <div style={styles.container}>
      <div style={styles.infoGrid}>
        <div style={styles.infoCard}>
          <h3 style={styles.infoTitle}>基本資料</h3>
          <dl style={styles.infoList}>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>陽曆生日</dt>
              <dd style={styles.infoValue}>{info.solar_date}</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>農曆生日</dt>
              <dd style={styles.infoValue}>{info.lunar_date}</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>年柱</dt>
              <dd style={styles.infoValue}>{info.ganzhi_year}</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>月柱</dt>
              <dd style={styles.infoValue}>{info.ganzhi_month}</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>日柱</dt>
              <dd style={styles.infoValue}>{info.ganzhi_day}</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>時柱</dt>
              <dd style={styles.infoValue}>{info.ganzhi_hour}</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>時辰</dt>
              <dd style={styles.infoValue}>{info.shichen}時</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>陰陽性別</dt>
              <dd style={styles.infoValue}>{info.yin_yang_gender}</dd>
            </div>
          </dl>
        </div>

        <div style={styles.infoCard}>
          <h3 style={styles.infoTitle}>宮位總覽</h3>
          <dl style={styles.infoList}>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>命宮</dt>
              <dd style={styles.infoValue}>{info.ming_gong}</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>身宮</dt>
              <dd style={styles.infoValue}>{info.shen_gong}</dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>真太陽時修正</dt>
              <dd style={styles.infoValue}>
                {info.true_solar_time_used ? '已啟用 ✓' : '未啟用'}
              </dd>
            </div>
            <div style={styles.infoRow}>
              <dt style={styles.infoLabel}>計算時間</dt>
              <dd style={styles.infoValue}>
                {new Date(info.calculated_at).toLocaleString('zh-TW')}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <div style={styles.palacesSection}>
        <h3 style={styles.sectionTitle}>十二宮位星盤</h3>
        <div style={styles.palacesGrid}>
          {palaces.map((palace, index) => (
            <PalaceCard key={palace.name} palace={palace} index={index} />
          ))}
        </div>
      </div>

      <div style={styles.legend}>
        <h4 style={styles.legendTitle}>亮度說明</h4>
        <div style={styles.legendItems}>
          {Object.entries(BRIGHTNESS_COLORS).map(([level, color]) => (
            <span key={level} style={{ ...styles.legendItem, borderLeftColor: color }}>
              {level}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function PalaceCard({ palace, index }: { palace: PalaceInfo; index: number }) {
  const isMingGong = index === 0; // Simplified - actual would check name
  const emoji = PALACE_EMOJI[palace.name] || '⭐';

  return (
    <div
      style={{
        ...styles.palaceCard,
        ...(isMingGong ? styles.palaceCardMingGong : {}),
      }}
    >
      <div style={styles.palaceHeader}>
        <span style={styles.palaceEmoji}>{emoji}</span>
        <h4 style={styles.palaceName}>{palace.name}</h4>
        {isMingGong && <span style={styles.mingGongBadge}>命宮</span>}
      </div>

      {palace.major_stars.length > 0 && (
        <div style={styles.starGroup}>
          <span style={styles.starLabel}>主星</span>
          <div style={styles.starList}>
            {palace.major_stars.map((star) => (
              <span key={star} style={styles.starMajor}>{star}</span>
            ))}
          </div>
        </div>
      )}

      {palace.minor_stars.length > 0 && (
        <div style={styles.starGroup}>
          <span style={styles.starLabel}>輔星</span>
          <div style={styles.starList}>
            {palace.minor_stars.map((star) => (
              <span key={star} style={styles.starMinor}>{star}</span>
            ))}
          </div>
        </div>
      )}

      {palace.major_stars.length === 0 && palace.minor_stars.length === 0 && (
        <div style={styles.emptyPalace}>無主星</div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: 'var(--color-bg-card)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-md)',
    padding: 'var(--spacing-lg)',
    animation: 'fadeIn 0.3s ease-out',
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: 'var(--spacing-lg)',
    marginBottom: 'var(--spacing-xl)',
  },
  infoCard: {
    background: 'var(--color-bg)',
    borderRadius: 'var(--radius-md)',
    padding: 'var(--spacing-md)',
  },
  infoTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    marginBottom: 'var(--spacing-md)',
    color: 'var(--color-primary)',
    borderBottom: '2px solid var(--color-accent)',
    paddingBottom: 'var(--spacing-xs)',
  },
  infoList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-sm)',
  },
  infoRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 'var(--spacing-xs) 0',
    borderBottom: '1px solid var(--color-border)',
  },
  infoLabel: {
    fontSize: '0.875rem',
    color: 'var(--color-text-muted)',
    fontWeight: 500,
  },
  infoValue: {
    fontSize: '0.875rem',
    fontWeight: 600,
    color: 'var(--color-text)',
    fontFamily: 'var(--font-mono)',
  },
  palacesSection: {
    marginTop: 'var(--spacing-lg)',
  },
  sectionTitle: {
    fontSize: '1.1rem',
    fontWeight: 600,
    marginBottom: 'var(--spacing-md)',
    color: 'var(--color-primary)',
  },
  palacesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
    gap: 'var(--spacing-md)',
  },
  palaceCard: {
    background: 'var(--color-bg)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    padding: 'var(--spacing-md)',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  palaceCardMingGong: {
    borderColor: 'var(--color-accent)',
    boxShadow: '0 0 0 2px var(--color-accent)',
  },
  palaceHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--spacing-sm)',
    marginBottom: 'var(--spacing-sm)',
    paddingBottom: 'var(--spacing-sm)',
    borderBottom: '1px solid var(--color-border)',
  },
  palaceEmoji: {
    fontSize: '1.25rem',
  },
  palaceName: {
    fontSize: '0.9rem',
    fontWeight: 600,
    color: 'var(--color-primary)',
    flex: 1,
  },
  mingGongBadge: {
    fontSize: '0.65rem',
    fontWeight: 700,
    background: 'var(--color-accent)',
    color: '#fff',
    padding: '2px 6px',
    borderRadius: 'var(--radius-sm)',
  },
  starGroup: {
    marginBottom: 'var(--spacing-sm)',
  },
  starLabel: {
    fontSize: '0.7rem',
    fontWeight: 600,
    color: 'var(--color-text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    marginBottom: 'var(--spacing-xs)',
    display: 'block',
  },
  starList: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 'var(--spacing-xs)',
  },
  starMajor: {
    fontSize: '0.8rem',
    fontWeight: 600,
    background: 'var(--color-primary)',
    color: '#fff',
    padding: '2px 8px',
    borderRadius: 'var(--radius-sm)',
  },
  starMinor: {
    fontSize: '0.75rem',
    background: 'var(--color-bg-card)',
    color: 'var(--color-text)',
    padding: '2px 6px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--color-border)',
  },
  emptyPalace: {
    fontSize: '0.8rem',
    color: 'var(--color-text-muted)',
    fontStyle: 'italic',
    textAlign: 'center',
    padding: 'var(--spacing-sm)',
  },
  legend: {
    marginTop: 'var(--spacing-xl)',
    paddingTop: 'var(--spacing-md)',
    borderTop: '1px solid var(--color-border)',
  },
  legendTitle: {
    fontSize: '0.875rem',
    fontWeight: 600,
    marginBottom: 'var(--spacing-sm)',
    color: 'var(--color-text-muted)',
  },
  legendItems: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 'var(--spacing-md)',
  },
  legendItem: {
    fontSize: '0.75rem',
    paddingLeft: 'var(--spacing-sm)',
    borderLeft: '3px solid',
    color: 'var(--color-text-muted)',
  },
};