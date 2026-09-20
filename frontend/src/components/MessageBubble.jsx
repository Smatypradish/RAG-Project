import { useState } from 'react';
import { AlertTriangle, Bot, CheckCircle, ChevronDown, ChevronUp, Clock, HelpCircle, User, XCircle } from 'lucide-react';
import SourceCard from './SourceCard';

const MessageBubble = ({ message }) => {
  const [showConflicts, setShowConflicts] = useState(false);

  // Render the answer as clean structured text: headings for "**...:**" lines,
  // bullet lists for "- "/"• " lines, plain paragraphs otherwise.
  const renderAnswer = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    const blocks = [];
    let list = [];
    let key = 0;

    const flushList = () => {
      if (list.length === 0) return;
      blocks.push(
        <ul key={`ul-${key++}`} className="my-2 space-y-1.5 pl-1">
          {list.map((item, i) => (
            <li key={i} className="flex gap-2 text-sm leading-6 text-[#27443d]">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-[#3a7463]" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      );
      list = [];
    };

    for (const raw of lines) {
      const line = raw.trim();
      if (!line) { flushList(); continue; }

      const headingMatch = line.match(/^\*\*(.+?)\*\*:?$/);
      if (headingMatch) {
        flushList();
        blocks.push(
          <p key={`h-${key++}`} className="mt-3 text-[13px] font-bold text-[#14322f] first:mt-0">
            {headingMatch[1]}
          </p>
        );
        continue;
      }

      if (line.endsWith(':') && line.length < 60 && !line.startsWith('-') && !line.startsWith('•')) {
        flushList();
        blocks.push(
          <p key={`h2-${key++}`} className="mt-3 text-[13px] font-bold text-[#14322f] first:mt-0">{line}</p>
        );
        continue;
      }

      const bulletMatch = line.match(/^[-•*]\s+(.+)/);
      if (bulletMatch) {
        list.push(bulletMatch[1].replace(/\*\*(.+?)\*\*/g, '$1'));
        continue;
      }

      flushList();
      blocks.push(
        <p key={`p-${key++}`} className="my-1.5 text-sm leading-6 text-[#27443d]">
          {line.replace(/\*\*(.+?)\*\*/g, '$1')}
        </p>
      );
    }
    flushList();
    return blocks;
  };

  const getConfidenceDetails = (type) => {
    const key = (type || '').toLowerCase();
    switch (key) {
      case 'verified':
        return { label: 'Verified', color: 'border-[#b9dd92] bg-[#effadc] text-[#446b19]', icon: <CheckCircle size={14} /> };
      case 'conflicting':
        return { label: 'Conflicting', color: 'border-[#f2d68b] bg-[#fff9df] text-[#8a6515]', icon: <AlertTriangle size={14} /> };
      case 'outdated':
        return { label: 'Outdated', color: 'border-[#f2c49a] bg-[#fff1e7] text-[#a4531e]', icon: <Clock size={14} /> };
      case 'insufficient':
        return { label: 'Insufficient Evidence', color: 'border-[#efb9b0] bg-[#fff0ed] text-[#a33e35]', icon: <XCircle size={14} /> };
      case 'not_available':
        return { label: 'Not Found in Docs', color: 'border-[#d5e0da] bg-[#f0f5f2] text-[#547067]', icon: <HelpCircle size={14} /> };
      default:
        return { label: type || 'Grounded', color: 'border-[#d5e0da] bg-[#f0f5f2] text-[#547067]', icon: <HelpCircle size={14} /> };
    }
  };

  if (message.isUser) {
    return (
      <article className="ml-auto flex max-w-[88%] justify-end gap-3 message-appear sm:max-w-[72%]">
        <div className="rounded-2xl rounded-tr-sm bg-[#12302d] px-5 py-4 text-white shadow-sm">
          <p className="whitespace-pre-wrap text-sm leading-6">{message.text}</p>
        </div>
        <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-[#d9ff75] text-[#12302d]"><User size={16} /></div>
      </article>
    );
  }

  const confidenceType = message.classification || (message.confidence_score > 0.65 ? 'verified' : message.confidence_score > 0.4 ? 'insufficient' : 'not_available');
  const confidence = getConfidenceDetails(confidenceType);

  return (
    <article className="flex max-w-[94%] gap-3 message-appear sm:max-w-[84%]">
      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-[#dfece5] text-[#265449]"><Bot size={17} /></div>
      <div className={`min-w-0 flex-1 rounded-2xl rounded-tl-sm border bg-white p-5 shadow-sm ${message.isError ? 'border-[#efb9b0]' : 'border-[#dce5df]'}`}>
        <div className="mb-3 flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-[0.13em] text-[#3a6659]">Academic helpdesk</span>
          {confidence && (
            <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${confidence.color}`}>
              {confidence.icon} {confidence.label}
              {message.confidence_score !== undefined && ` · relevance ${Math.round(message.confidence_score * 100)}%`}
            </span>
          )}
        </div>
        <div className={message.isError ? 'text-sm text-[#a33e35]' : ''}>
          {message.isError
            ? <p className="whitespace-pre-wrap leading-6">{message.text}</p>
            : renderAnswer(message.text)}
        </div>

        {((message.conflicts && message.conflicts.length > 0) || (message.sources && message.sources.length > 0)) && (
          <div className="mt-5 border-t border-[#e6ede9] pt-4">
            {message.conflicts && message.conflicts.length > 0 && (
              <div className="mt-3">
                <button onClick={() => setShowConflicts(!showConflicts)} className="flex w-full items-center gap-2 rounded-xl border border-[#f2d68b] bg-[#fff9df] px-3 py-2 text-left text-xs font-semibold text-[#8a6515] transition hover:bg-[#fff4c5]">
                  <AlertTriangle size={14} />
                  <span>Review Policy Conflict Resolution ({message.conflicts.length})</span>
                  {showConflicts ? <ChevronUp size={14} className="ml-auto" /> : <ChevronDown size={14} className="ml-auto" />}
                </button>
                {showConflicts && (
                  <div className="mt-2 space-y-2 rounded-xl border border-[#f7e6ad] bg-[#fffdf1] p-3 text-xs leading-5 text-[#6c5a27]">
                    {message.conflicts.map((conflict, index) => (
                      <div key={index} className="border-b border-[#ebd79b] pb-2 last:border-b-0 last:pb-0">
                        <p className="font-bold text-[#8a6515]">Topic: {conflict.topic || 'Policy Overlap'}</p>
                        <p className="mt-0.5"><strong>Resolution:</strong> {conflict.resolution}</p>
                        {conflict.explanation && <p className="text-[11px] text-[#7a5b14] italic">Reason: {conflict.explanation}</p>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {message.sources && message.sources.length > 0 && (
              <div className="mt-4">
                <h3 className="mb-2 text-[11px] font-bold uppercase tracking-[0.13em] text-[#70877e]">Supporting Official Documents</h3>
                <div className="grid gap-2 sm:grid-cols-2">
                  {Array.from(new Map(message.sources.map((s) => [`${s.document_id}-${s.page_number}`, s])).values()).map((source, index) => <SourceCard key={index} source={source} />)}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </article>
  );
};

export default MessageBubble;
