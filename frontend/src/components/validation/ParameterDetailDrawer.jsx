import React from 'react';

const DrawerOverlay = ({ onClick }) => (
  <div onClick={onClick} style={{
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
    backdropFilter: 'blur(2px)', zIndex: 100
  }} />
);

const Section = ({ title, children }) => (
  <div style={{ marginBottom: 20 }}>
    <div style={{
      fontSize: '0.65rem', fontWeight: 700, color: '#64748b',
      letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 10,
      paddingBottom: 6, borderBottom: '1px solid #1e293b'
    }}>{title}</div>
    {children}
  </div>
);

const Field = ({ label, value, color = '#e2e8f0', mono = false }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, alignItems: 'flex-start' }}>
    <span style={{ fontSize: '0.78rem', color: '#64748b', flexShrink: 0, marginRight: 12 }}>{label}</span>
    <span style={{
      fontSize: '0.8rem', color, fontWeight: 600,
      textAlign: 'right', wordBreak: 'break-word',
      fontFamily: mono ? 'monospace' : 'inherit',
      maxWidth: '60%'
    }}>
      {value ?? '—'}
    </span>
  </div>
);

const StatusBadge = ({ status, severity }) => {
  const STATUS_CONFIG = {
    NORMAL:           { label: 'Normal',        bg: '#0d2d1a', border: '#16a34a', text: '#4ade80' },
    LOW:              { label: 'Low',           bg: '#1a1a0d', border: '#ca8a04', text: '#facc15' },
    HIGH:             { label: 'High',          bg: '#2d0d0d', border: '#dc2626', text: '#f87171' },
    CRITICAL_HIGH:    { label: 'Critical High', bg: '#3d0000', border: '#ff0000', text: '#ff6b6b' },
    CRITICAL_LOW:     { label: 'Critical Low',  bg: '#3d0000', border: '#ff0000', text: '#ff6b6b' },
    INVALID_UNIT:     { label: 'Invalid Unit',  bg: '#2d1200', border: '#ea580c', text: '#fb923c' },
    INVALID_VALUE:    { label: 'Invalid Value', bg: '#2d0a0a', border: '#b91c1c', text: '#fca5a5' },
    QUALITATIVE:      { label: 'Qualitative',   bg: '#1a0a2e', border: '#9333ea', text: '#d8b4fe' },
    MISSING_REFERENCE:{ label: 'No Reference',  bg: '#1a1a2e', border: '#6366f1', text: '#a5b4fc' },
    UNKNOWN:          { label: 'Unknown',       bg: '#1a1a2e', border: '#475569', text: '#94a3b8' },
  };
  const sc = STATUS_CONFIG[status?.toUpperCase()] || STATUS_CONFIG.UNKNOWN;
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
      <span style={{
        padding: '4px 12px', borderRadius: 8,
        background: sc.bg, border: `1px solid ${sc.border}`,
        color: sc.text, fontWeight: 700, fontSize: '0.85rem'
      }}>{sc.label}</span>
      {severity && severity !== 'UNKNOWN' && severity !== 'NORMAL' && (
        <span style={{
          padding: '3px 10px', borderRadius: 8,
          background: '#1e293b', color: '#94a3b8',
          fontSize: '0.75rem', border: '1px solid #334155'
        }}>{severity}</span>
      )}
    </div>
  );
};

const ConfBar = ({ label, value, color }) => {
  const pct = Math.round((value || 0) * 100);
  const c = color || (pct >= 80 ? '#16a34a' : pct >= 60 ? '#ca8a04' : '#dc2626');
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{label}</span>
        <span style={{ fontSize: '0.75rem', color: c, fontWeight: 700 }}>{pct}%</span>
      </div>
      <div style={{ height: 5, background: '#1e293b', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: c, borderRadius: 3 }} />
      </div>
    </div>
  );
};

const ParameterDetailDrawer = ({ parameter: p, onClose }) => {
  if (!p) return null;

  const traceSteps = p.validation_trace
    ? p.validation_trace.split(' | ').filter(Boolean)
    : [];

  return (
    <>
      <DrawerOverlay onClick={onClose} />
      <div style={{
        position: 'fixed', top: 0, right: 0, height: '100vh',
        width: 'min(460px, 95vw)', background: '#0d1117',
        borderLeft: '1px solid #1e293b', zIndex: 101, overflowY: 'auto',
        padding: '24px 22px', boxSizing: 'border-box'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 22 }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#f1f5f9' }}>
              {p.parameter_name}
            </div>
            <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: 3 }}>
              {p.parameter_code} · {p.category}
            </div>
          </div>
          <button onClick={onClose} style={{
            background: '#1e293b', border: '1px solid #334155', color: '#94a3b8',
            borderRadius: 8, padding: '5px 11px', cursor: 'pointer', fontSize: '0.85rem'
          }}>✕ Close</button>
        </div>

        {/* Clinical Status */}
        <Section title="Clinical Status">
          <div style={{ marginBottom: 12 }}>
            <StatusBadge status={p.status} severity={p.severity} />
          </div>
          {p.critical && (
            <div style={{
              background: '#3d000020', border: '1px solid #ff000055',
              borderRadius: 8, padding: '8px 12px', marginTop: 8,
              color: '#ff6b6b', fontSize: '0.78rem', fontWeight: 600
            }}>
              ⚠ Critical Value — Immediate clinical attention required
            </div>
          )}
          {p.validation_notes && (
            <div style={{
              marginTop: 10, padding: '8px 12px', background: '#1e293b',
              borderRadius: 8, fontSize: '0.77rem', color: '#94a3b8', lineHeight: 1.5
            }}>{p.validation_notes}</div>
          )}
        </Section>

        {/* Raw vs Converted Values */}
        <Section title="Value Analysis">
          <Field label="Raw OCR Value" value={`${p.raw_value} ${p.raw_unit || ''}`} />
          {p.is_converted ? (
            <>
              <Field label="Converted Value" value={`${Number(p.converted_value).toFixed(3)} ${p.canonical_unit}`} color="#2dd4bf" />
              <Field label="Conversion Factor" value={`× ${p.conversion_factor}`} color="#94a3b8" />
              <div style={{
                padding: '8px 12px', background: '#0d2d2d', border: '1px solid #0f766e',
                borderRadius: 8, fontSize: '0.77rem', color: '#2dd4bf', marginTop: 4
              }}>
                {p.raw_value} {p.raw_unit} × {p.conversion_factor} = {Number(p.converted_value).toFixed(3)} {p.canonical_unit}
              </div>
            </>
          ) : (
            <Field label="Validated Value" value={`${p.validated_value ?? p.raw_value} ${p.normalized_unit || ''}`} />
          )}
        </Section>

        {/* Unit Analysis */}
        <Section title="Unit Analysis">
          <Field label="Original Unit" value={p.raw_unit || '—'} />
          <Field label="Normalized Unit" value={p.normalized_unit || '—'} />
          {p.is_converted && <Field label="Canonical Unit" value={p.canonical_unit} color="#2dd4bf" />}
          <Field
            label="Unit Status"
            value={p.status === 'INVALID_UNIT' ? 'INCOMPATIBLE' : p.is_converted ? 'CONVERTED' : 'COMPATIBLE'}
            color={p.status === 'INVALID_UNIT' ? '#ea580c' : p.is_converted ? '#2dd4bf' : '#4ade80'}
          />
        </Section>

        {/* Reference Range */}
        <Section title="Reference Range">
          <Field label="Source" value={p.reference_source} color={
            p.reference_source === 'REPORT' ? '#3b82f6' :
            p.reference_source === 'STANDARD_DATABASE' ? '#10b981' : '#6b7280'
          } />
          <Field label="Range" value={p.reference_text || '—'} />
          {p.reference_low != null && <Field label="Lower Bound" value={p.reference_low} />}
          {p.reference_high != null && <Field label="Upper Bound" value={p.reference_high} />}
        </Section>

        {/* Confidence */}
        <Section title="Confidence Metrics">
          <ConfBar
            label="OCR Confidence"
            value={p.ocr_confidence}
            color={p.ocr_confidence < 0.7 ? '#dc2626' : '#3b82f6'}
          />
          <ConfBar label="Validation Confidence" value={p.validation_confidence} />
          {p.ocr_confidence != null && p.ocr_confidence < 0.7 && (
            <div style={{
              padding: '6px 10px', background: '#2d0a0a', border: '1px solid #dc262655',
              borderRadius: 6, fontSize: '0.72rem', color: '#f87171', marginTop: 4
            }}>
              Low OCR confidence — validation confidence is capped
            </div>
          )}
        </Section>

        {/* Validation Trace */}
        {traceSteps.length > 0 && (
          <Section title="Validation Trace">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {traceSteps.map((step, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'flex-start', gap: 8,
                  padding: '5px 8px', background: '#0f172a', borderRadius: 6,
                  borderLeft: '2px solid #334155'
                }}>
                  <span style={{ fontSize: '0.6rem', color: '#475569', marginTop: 2, flexShrink: 0 }}>
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: '#94a3b8', lineHeight: 1.4, fontFamily: 'monospace' }}>
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </Section>
        )}
      </div>
    </>
  );
};

export default ParameterDetailDrawer;
