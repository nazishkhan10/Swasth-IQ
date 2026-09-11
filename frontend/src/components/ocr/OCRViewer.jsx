import React, { useState, useMemo } from 'react';
import { Eye, FileText, Layout, Table as TableIcon, Code, Search, AlertCircle } from 'lucide-react';
import OCRStatusCard from './OCRStatusCard';
import OCRToolbar from './OCRToolbar';
import PageNavigator from './PageNavigator';
import TableViewer from './TableViewer';

export const OCRViewer = ({ report, ocrData, onRetry, isProcessing = false }) => {
  const [activeTab, setActiveTab] = useState('text'); // text | blocks | tables | json
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBlockId, setSelectedBlockId] = useState(null);
  const [matchIndex, setMatchIndex] = useState(0);

  const pages = ocrData?.pages || [];
  const totalPages = pages.length || 1;
  const pageData = pages.find((p) => p.page === currentPage) || pages[0] || {};
  const pageText = pageData.text || '';
  const blocks = pageData.blocks || [];
  const tables = pageData.tables || [];

  // Calculate search matches across blocks, text, and tables
  const searchMatches = useMemo(() => {
    if (!searchTerm.trim()) return [];
    const term = searchTerm.toLowerCase();
    const matches = [];

    blocks.forEach((b, idx) => {
      if (b.text && b.text.toLowerCase().includes(term)) {
        matches.push({ type: 'block', id: b.id, text: b.text, blockIndex: idx });
      }
    });

    tables.forEach((t, tIdx) => {
      const headersStr = (t.headers || []).join(' ').toLowerCase();
      if (headersStr.includes(term)) {
        matches.push({ type: 'table_header', id: `t_${tIdx}`, text: headersStr });
      }
      (t.rows || []).forEach((row, rIdx) => {
        const rowStr = row.join(' ').toLowerCase();
        if (rowStr.includes(term)) {
          matches.push({ type: 'table_row', id: `t_${tIdx}_r_${rIdx}`, text: rowStr });
        }
      });
    });

    return matches;
  }, [searchTerm, blocks, tables]);

  const handleNextMatch = () => {
    if (searchMatches.length === 0) return;
    const nextIdx = (matchIndex + 1) % searchMatches.length;
    setMatchIndex(nextIdx);
    const match = searchMatches[nextIdx];
    if (match && match.id) {
      setSelectedBlockId(match.id);
    }
  };

  const handlePrevMatch = () => {
    if (searchMatches.length === 0) return;
    const prevIdx = (matchIndex - 1 + searchMatches.length) % searchMatches.length;
    setMatchIndex(prevIdx);
    const match = searchMatches[prevIdx];
    if (match && match.id) {
      setSelectedBlockId(match.id);
    }
  };

  // Copy raw text to clipboard
  const handleCopyText = () => {
    const fullText = pages.map((p) => `--- PAGE ${p.page} ---\n${p.text}`).join('\n\n');
    navigator.clipboard.writeText(fullText);
  };

  // Export handlers
  const handleExport = (format) => {
    const filename = `${report?.original_filename || 'report'}_ocr.${format}`;
    let content = '';

    if (format === 'txt') {
      content = pages.map((p) => `=== PAGE ${p.page} ===\n${p.text}`).join('\n\n');
    } else if (format === 'json') {
      content = JSON.stringify(ocrData, null, 2);
    } else if (format === 'md') {
      content = `# OCR Document intelligence Report\n**Filename:** ${report?.original_filename || 'Report'}\n**Engine:** ${ocrData?.engine || 'PyMuPDF'}\n**Confidence:** ${Math.round((ocrData?.confidence || 1) * 100)}%\n\n`;
      pages.forEach((p) => {
        content += `## Page ${p.page}\n\n`;
        (p.blocks || []).forEach((b) => {
          if (b.type === 'header') {
            content += `### ${b.text}\n\n`;
          } else if (b.type === 'list') {
            content += `- ${b.text}\n`;
          } else {
            content += `${b.text}\n\n`;
          }
        });
        if (p.tables && p.tables.length > 0) {
          p.tables.forEach((t, tIdx) => {
            content += `\n#### Table ${tIdx + 1}\n`;
            if (t.headers) content += `| ${t.headers.join(' | ')} |\n| ${t.headers.map(() => '---').join(' | ')} |\n`;
            (t.rows || []).forEach((row) => {
              content += `| ${row.join(' | ')} |\n`;
            });
            content += '\n';
          });
        }
      });
    }

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Render text with search term highlighting
  const renderHighlightedText = (text) => {
    if (!searchTerm.trim()) return text;
    const parts = text.split(new RegExp(`(${searchTerm})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === searchTerm.toLowerCase() ? (
        <mark key={i} className="bg-amber-400/30 text-amber-200 font-semibold px-0.5 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  const isLowConfidence = (ocrData?.confidence || 1.0) < 0.70;

  return (
    <div className="space-y-4">
      {/* OCR Status Header */}
      <OCRStatusCard ocrData={ocrData} onRetry={() => onRetry()} />

      {/* Low Confidence Warning Callout */}
      {isLowConfidence && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-center justify-between gap-4 text-rose-300">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <div>
              <h5 className="text-xs font-bold">Low OCR Confidence Warning</h5>
              <p className="text-[11px] text-rose-300/80">Average OCR confidence is below threshold (&lt;70%). Extraction may contain inaccuracies.</p>
            </div>
          </div>
          <button
            onClick={() => onRetry()}
            className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg shrink-0"
          >
            Retry Extraction
          </button>
        </div>
      )}

      {/* OCR Toolbar: Search, Copy, Export, Retry */}
      <OCRToolbar
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        matchCount={searchMatches.length}
        currentMatchIndex={matchIndex}
        onNextMatch={handleNextMatch}
        onPrevMatch={handlePrevMatch}
        onCopyText={handleCopyText}
        onExport={handleExport}
        onRetry={onRetry}
        isProcessing={isProcessing}
      />

      {/* Page Navigator */}
      <PageNavigator
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
        currentVersion={ocrData?.version || 1}
      />

      {/* Master Side-by-Side Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-[580px]">
        {/* LEFT PANE: Original Document Preview */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-4 flex flex-col shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3 text-xs font-bold text-slate-700">
            <span className="flex items-center gap-2">
              <Eye className="w-4 h-4 text-sky-500" />
              Original Document Scan
            </span>
            <span className="text-[11px] font-mono text-slate-400">{report?.original_filename}</span>
          </div>

          <div className="flex-1 relative bg-slate-50 border border-slate-200/80 rounded-xl overflow-hidden flex items-center justify-center p-2 min-h-[480px]">
            {report?.mime_type === 'application/pdf' || report?.filename?.endsWith('.pdf') ? (
              <iframe
                src={`${import.meta.env.VITE_API_BASE_URL || ''}${report?.file_url}`}
                className="w-full h-full min-h-[500px] rounded-lg border-0"
                title="Original PDF Document"
              />
            ) : report?.mime_type?.startsWith('image/') || /\.(jpg|jpeg|png)$/i.test(report?.filename || '') ? (
              <div className="relative w-full h-full flex items-center justify-center">
                <img
                   src={`${import.meta.env.VITE_API_BASE_URL || ''}${report?.file_url}`}
                  alt="Original Report Scan"
                  className="max-h-[520px] object-contain rounded-lg shadow-sm"
                />
                {/* Bounding box overlay indicator */}
                {selectedBlockId && (
                  <div className="absolute inset-x-4 top-4 p-2 bg-sky-500/10 border border-sky-400 text-sky-700 text-[11px] font-mono rounded-xl backdrop-blur">
                    Highlighting Block: #{selectedBlockId}
                  </div>
                )}
              </div>
            ) : (
              <div className="w-full h-full p-4 overflow-auto font-mono text-xs text-slate-800 bg-white rounded-lg max-w-full">
                <pre className="whitespace-pre-wrap break-words max-w-full">{pageText || 'Preview unrenderable'}</pre>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANE: Extracted Structure & Text */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-4 flex flex-col shadow-sm min-w-0">
          {/* Right Pane Navigation Tabs */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
            <div className="flex items-center gap-1 bg-slate-100/80 p-1 rounded-xl border border-slate-200 text-xs overflow-x-auto">
              <button
                onClick={() => setActiveTab('text')}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 shrink-0 ${
                  activeTab === 'text' ? 'bg-sky-600 text-white shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                Raw Text
              </button>
              <button
                onClick={() => setActiveTab('blocks')}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 shrink-0 ${
                  activeTab === 'blocks' ? 'bg-sky-600 text-white shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Layout className="w-3.5 h-3.5" />
                Blocks ({blocks.length})
              </button>
              <button
                onClick={() => setActiveTab('tables')}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 shrink-0 ${
                  activeTab === 'tables' ? 'bg-sky-600 text-white shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <TableIcon className="w-3.5 h-3.5" />
                Tables ({tables.length})
              </button>
              <button
                onClick={() => setActiveTab('json')}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 shrink-0 ${
                  activeTab === 'json' ? 'bg-sky-600 text-white shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Code className="w-3.5 h-3.5" />
                JSON
              </button>
            </div>
          </div>

          {/* Right Pane Tab Content */}
          <div className="flex-1 bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 overflow-y-auto max-h-[540px] min-w-0">
            {activeTab === 'text' && (
              <div className="font-mono text-xs leading-relaxed text-slate-800 whitespace-pre-wrap break-words">
                {renderHighlightedText(pageText || 'No text extracted for this page.')}
              </div>
            )}

            {activeTab === 'blocks' && (
              <div className="space-y-3">
                {blocks.map((block) => {
                  const isSelected = selectedBlockId === block.id;

                  return (
                    <div
                      key={block.id}
                      onClick={() => setSelectedBlockId(block.id)}
                      className={`p-3 rounded-xl border transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-sky-50 border-sky-300 text-sky-900 shadow-2xs'
                          : 'bg-white border-slate-200/80 text-slate-800 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 mb-1.5">
                        <span className="uppercase px-1.5 py-0.5 rounded bg-slate-100 text-sky-700 font-bold">
                          {block.type}
                        </span>
                        {block.bbox && <span>BBox: [{block.bbox.join(', ')}]</span>}
                      </div>
                      <p className="text-xs font-mono text-slate-800">
                        {renderHighlightedText(block.text)}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}

            {activeTab === 'tables' && <TableViewer tables={tables} />}

            {activeTab === 'json' && (
              <pre className="font-mono text-[11px] text-slate-800 leading-normal overflow-x-auto">
                {JSON.stringify(pageData, null, 2)}
              </pre>
            )}
          </div>
        </div>
      </div>

    </div>
  );
};

export default OCRViewer;
