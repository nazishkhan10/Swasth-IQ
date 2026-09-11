import React, { useState } from 'react';
import ParameterDetailDrawer from './ParameterDetailDrawer';

// ── Status config ──────────────────────────────────────────────────────────
const STATUS_CONFIG = {
  NORMAL:           { label: 'Normal',          bg: '#ecfdf5', border: '#a7f3d0', text: '#047857', dot: '#10b981' },
  LOW:              { label: 'Low',             bg: '#f0f9ff', border: '#bae6fd', text: '#0369a1', dot: '#0284c7' },
  HIGH:             { label: 'High',            bg: '#fffbeb', border: '#fde68a', text: '#b45309', dot: '#f59e0b' },
  CRITICAL_HIGH:    { label: 'Critical High',   bg: '#fff1f2', border: '#fecdd3', text: '#be123c', dot: '#f43f5e' },
  CRITICAL_LOW:     { label: 'Critical Low',    bg: '#fff1f2', border: '#fecdd3', text: '#be123c', dot: '#f43f5e' },
  MISSING_REFERENCE:{ label: 'No Reference',    bg: '#f8fafc', border: '#e2e8f0', text: '#475569', dot: '#64748b' },
  UNKNOWN:          { label: 'Unknown',         bg: '#f8fafc', border: '#e2e8f0', text: '#475569', dot: '#64748b' },
  INVALID:          { label: 'Invalid',         bg: '#fff7ed', border: '#ffedd5', text: '#c2410c', dot: '#f97316' },
  INVALID_UNIT:     { label: 'Invalid Unit',    bg: '#fff7ed', border: '#ffedd5', text: '#c2410c', dot: '#f97316' },
  INVALID_VALUE:    { label: 'Invalid Value',   bg: '#fff1f2', border: '#fecdd3', text: '#be123c', dot: '#f43f5e' },
  QUALITATIVE:      { label: 'Qualitative',     bg: '#faf5ff', border: '#e9d5ff', text: '#6b21a8', dot: '#a855f7' },
};

const getStatus = (status) => STATUS_CONFIG[status?.toUpperCase()] || STATUS_CONFIG.UNKNOWN;


// ── Reference source badges ────────────────────────────────────────────────
const RefBadge = ({ source }) => {
  const cfg = {
    REPORT:               { label: 'Report Ref',   color: '#3b82f6' },
    STANDARD_DATABASE:    { label: 'Standard DB',  color: '#10b981' },
    FALLBACK_FROM_REPORT: { label: 'DB Fallback',  color: '#f59e0b' },
    UNKNOWN:              { label: 'No Reference', color: '#6b7280' },
  };
  const c = cfg[source] || cfg.UNKNOWN;
  return (
    <span style={{
      fontSize: '0.65rem', padding: '1px 6px', borderRadius: '4px',
      backgroundColor: c.color + '22', color: c.color,
      border: `1px solid ${c.color}55`, fontWeight: 600, letterSpacing: '0.03em'
    }}>
      {c.label}
    </span>
  );
};

// ── Conversion badge ────────────────────────────────────────────────────────
const ConvBadge = ({ row }) => {
  if (!row.is_converted) return null;
  return (
    <span style={{
      fontSize: '0.65rem', padding: '1px 6px', borderRadius: '4px',
      backgroundColor: '#0d4a4a', color: '#2dd4bf',
      border: '1px solid #0f766e55', fontWeight: 600,
      display: 'inline-flex', alignItems: 'center', gap: '3px'
    }}>
      ⇄ {row.raw_unit} → {row.canonical_unit}
    </span>
  );
};

// ── Confidence bar ─────────────────────────────────────────────────────────
const ConfBar = ({ value }) => {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 80 ? '#16a34a' : pct >= 60 ? '#ca8a04' : '#dc2626';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
      <div style={{ width: 60, height: 4, background: '#1e293b', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 2 }} />
      </div>
      <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{pct}%</span>
    </div>
  );
};

// ── OCR confidence chip ────────────────────────────────────────────────────
const OcrChip = ({ value }) => {
  if (value == null) return null;
  const pct = Math.round(value * 100);
  const color = pct >= 70 ? '#4ade80' : '#f87171';
  return (
    <span style={{
      fontSize: '0.6rem', padding: '1px 5px', borderRadius: '4px',
      backgroundColor: color + '22', color, border: `1px solid ${color}44`,
      fontWeight: 600
    }}>
      OCR {pct}%
    </span>
  );
};

// ── Main component ─────────────────────────────────────────────────────────
const ValidationStatusTable = ({ validatedValues = [], searchTerm = '', selectedCategory = 'All' }) => {
  const [selected, setSelected] = useState(null);

  const filtered = validatedValues.filter(v => {
    const matchSearch = !searchTerm ||
      v.parameter_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.parameter_code?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchCat = selectedCategory === 'All' || v.category === selectedCategory;
    return matchSearch && matchCat;
  });

  if (filtered.length === 0) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#475569' }}>
        <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔬</div>
        <div>No validated parameters found</div>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-x-auto border border-slate-200/80 rounded-2xl bg-white shadow-2xs">
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #e2e8f0', background: '#f8fafc' }}>
              {['Parameter', 'Value', 'Unit', 'Reference', 'Status', 'Confidence', 'Source'].map(h => (
                <th key={h} style={{
                  padding: '12px 14px', textAlign: 'left', color: '#475569',
                  fontWeight: 700, fontSize: '0.7rem', letterSpacing: '0.06em',
                  textTransform: 'uppercase', whiteSpace: 'nowrap'
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map((row, idx) => {
              const sc = getStatus(row.status);
              const isInvalid = ['INVALID_UNIT', 'INVALID_VALUE', 'INVALID'].includes(row.status?.toUpperCase());
              return (
                <tr
                  key={row.id ?? idx}
                  onClick={() => setSelected(row)}
                  className="hover:bg-slate-50/80 transition-all cursor-pointer"
                >
                  {/* Parameter */}
                  <td style={{ padding: '12px 14px' }}>
                    <div style={{ fontWeight: 700, color: '#0f172a' }}>{row.parameter_name}</div>
                    <div style={{ fontSize: '0.68rem', color: '#64748b', marginTop: 2, fontWeight: 500 }}>
                      {row.parameter_code} · {row.category}
                    </div>
                  </td>


                  {/* Value */}
                  <td style={{ padding: '10px 14px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      {row.is_converted ? (
                        <>
                          <span style={{ color: '#94a3b8', textDecoration: 'line-through', fontSize: '0.72rem' }}>
                            {row.raw_value} {row.raw_unit}
                          </span>
                          <span style={{ color: '#2dd4bf', fontWeight: 700 }}>
                            {row.converted_value != null ? Number(row.converted_value).toFixed(2) : '—'} {row.canonical_unit}
                          </span>
                        </>
                      ) : (
                        <span style={{ fontWeight: 600, color: '#e2e8f0' }}>
                          {row.raw_value}
                        </span>
                      )}
                      {row.is_converted && <ConvBadge row={row} />}
                    </div>
                  </td>

                  {/* Unit */}
                  <td style={{ padding: '10px 14px', color: '#94a3b8' }}>
                    {row.is_converted ? row.canonical_unit : (row.normalized_unit || row.raw_unit || '—')}
                  </td>

                  {/* Reference */}
                  <td style={{ padding: '10px 14px' }}>
                    <div style={{ color: '#94a3b8', fontSize: '0.78rem' }}>
                      {row.reference_text || (
                        row.reference_low != null && row.reference_high != null
                          ? `${row.reference_low} – ${row.reference_high}`
                          : row.reference_low != null
                          ? `≥ ${row.reference_low}`
                          : row.reference_high != null
                          ? `≤ ${row.reference_high}`
                          : '—'
                      )}
                    </div>
                  </td>

                  {/* Status */}
                  <td style={{ padding: '10px 14px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', gap: '5px',
                        padding: '3px 8px', borderRadius: '6px',
                        background: sc.bg, border: `1px solid ${sc.border}`,
                        color: sc.text, fontSize: '0.72rem', fontWeight: 700,
                        width: 'fit-content'
                      }}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: sc.dot, flexShrink: 0 }} />
                        {sc.label}
                      </span>
                      {row.severity && row.severity !== 'UNKNOWN' && row.severity !== 'NORMAL' && (
                        <span style={{ fontSize: '0.65rem', color: '#94a3b8', paddingLeft: 2 }}>
                          {row.severity}
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Confidence */}
                  <td style={{ padding: '10px 14px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                      <ConfBar value={row.validation_confidence} />
                      <OcrChip value={row.ocr_confidence} />
                    </div>
                  </td>

                  {/* Reference Source */}
                  <td style={{ padding: '10px 14px' }}>
                    <RefBadge source={row.reference_source} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {selected && (
        <ParameterDetailDrawer
          parameter={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
};

export default ValidationStatusTable;
