import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText } from 'lucide-react';

const SourceCard = ({ source }) => {
  const [expanded, setExpanded] = useState(false);
  const statusColors = {
    active: 'border-[#b9dd92] bg-[#effadc] text-[#446b19]',
    superseded: 'border-[#f2d68b] bg-[#fff9df] text-[#8a6515]',
    withdrawn: 'border-[#efb9b0] bg-[#fff0ed] text-[#a33e35]',
  };
  const authorityLabels = { 1: 'UGC/Government', 2: 'University', 3: 'College Core', 4: 'Department', 5: 'General' };
  const statusStyle = statusColors[source.status?.toLowerCase()] || 'border-[#d5e0da] bg-[#f0f5f2] text-[#547067]';
  const authorityLabel = source.authority_level ? `${authorityLabels[source.authority_level] || 'Unknown'} (L${source.authority_level})` : 'Unknown authority';

  return (
    <div className="w-full max-w-sm overflow-hidden rounded-xl border border-[#dce5df] bg-[#f7faf8] text-sm transition hover:border-[#aac6ba]">
      <button onClick={() => setExpanded(!expanded)} className="flex w-full items-start justify-between gap-3 p-3 text-left">
        <span className="flex min-w-0 items-start gap-2">
          <FileText size={16} className="mt-0.5 shrink-0 text-[#3a7463]" />
          <span className="min-w-0"><span className="block truncate font-semibold text-[#315148]">{source.document_name}</span><span className="mt-1 flex flex-wrap gap-1 text-xs text-[#71867f]">{source.page && <span>Page {source.page}</span>}{source.section && <span>{source.page && '· '} {source.section}</span>}</span></span>
        </span>
        {expanded ? <ChevronUp size={16} className="shrink-0 text-[#7c9189]" /> : <ChevronDown size={16} className="shrink-0 text-[#7c9189]" />}
      </button>
      {expanded && <div className="border-t border-[#dce5df] bg-white px-3 pb-3 pt-2"><div className="mb-3 flex flex-wrap gap-2"><span className={`rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase ${statusStyle}`}>{source.status || 'Unknown'}</span><span className="rounded-full border border-[#c9ded5] bg-[#eef7f2] px-2 py-0.5 text-[10px] font-bold text-[#42645a]">{authorityLabel}</span>{source.effective_date && <span className="rounded-full bg-[#f0f4f2] px-2 py-0.5 text-[10px] font-semibold text-[#60766e]">Effective {source.effective_date}</span>}</div><p className="rounded-lg bg-[#f7faf8] p-2 text-xs italic leading-5 text-[#61766f]">“{source.text || 'Text snippet not available.'}”</p></div>}
    </div>
  );
};

export default SourceCard;
