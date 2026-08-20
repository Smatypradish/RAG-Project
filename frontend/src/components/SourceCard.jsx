import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';

const SourceCard = ({ source }) => {
  const [expanded, setExpanded] = useState(false);

  // Status badge colors
  const statusColors = {
    active: 'bg-green-100 text-green-800 border-green-200',
    superseded: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    withdrawn: 'bg-red-100 text-red-800 border-red-200'
  };

  const authorityLabels = {
    1: 'UGC/Government',
    2: 'University',
    3: 'College Core',
    4: 'Department',
    5: 'General'
  };

  const statusStyle = statusColors[source.status?.toLowerCase()] || 'bg-gray-100 text-gray-800 border-gray-200';
  const authorityLabel = source.authority_level 
    ? `${authorityLabels[source.authority_level] || 'Unknown'} (L${source.authority_level})` 
    : 'Unknown Authority';

  return (
    <div className="flex flex-col bg-gray-50 border border-gray-200 rounded-lg overflow-hidden w-full max-w-sm text-sm hover:border-gray-300 transition-colors">
      <div 
        className="p-3 cursor-pointer flex items-start justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start space-x-2 overflow-hidden">
          <FileText size={16} className="text-indigo-500 mt-0.5 shrink-0" />
          <div className="flex flex-col">
            <span className="font-semibold text-gray-800 truncate" title={source.document_name}>
              {source.document_name}
            </span>
            <div className="flex flex-wrap gap-1 mt-1 text-xs text-gray-500">
              {source.page && <span>Pg {source.page}</span>}
              {source.page && source.section && <span>•</span>}
              {source.section && <span>Sec: {source.section}</span>}
            </div>
          </div>
        </div>
        <div className="ml-2 shrink-0">
          {expanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
        </div>
      </div>
      
      {expanded && (
        <div className="px-3 pb-3 pt-1 border-t border-gray-200/60 bg-white">
          <div className="flex flex-wrap gap-2 mb-3 mt-2">
            <span className={`text-[10px] px-1.5 py-0.5 rounded border ${statusStyle} uppercase font-semibold`}>
              {source.status || 'Unknown'}
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded border bg-blue-50 text-blue-800 border-blue-200">
              {authorityLabel}
            </span>
            {source.effective_date && (
              <span className="text-[10px] px-1.5 py-0.5 rounded border bg-gray-100 text-gray-700 border-gray-200">
                Effective: {source.effective_date}
              </span>
            )}
          </div>
          <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded border border-gray-100 italic break-words line-clamp-6">
            "{source.text || 'Text snippet not available.'}"
          </div>
        </div>
      )}
    </div>
  );
};

export default SourceCard;
