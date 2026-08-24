import { useState } from 'react';
import { AlertTriangle, Bot, CheckCircle, ChevronDown, ChevronUp, Clock, HelpCircle, User, XCircle } from 'lucide-react';
import SourceCard from './SourceCard';

const formatInlineText = (text) => text.split(/(\*\*[^*]+\*\*)/).map((part, index) => {
  if (part.startsWith('**') && part.endsWith('**')) {
    return <strong key={index} className="font-semibold text-[#14322f]">{part.slice(2, -2)}</strong>;
  }
  return part;
});

const getResponseBlocks = (text = '') => {
  const blocks = [];
  let paragraph = [];
  let list = null;

  const flushParagraph = () => {
    if (paragraph.length > 0) {
      blocks.push({ type: 'paragraph', lines: paragraph });
      paragraph = [];
    }
  };

  const flushList = () => {
    if (list) {
      blocks.push(list);
      list = null;
    }
  };

  text.split('\n').forEach((line) => {
    const trimmedLine = line.trim();
    const headingMatch = trimmedLine.match(/^#{1,3}\s+(.+)$/);
    const boldHeadingMatch = trimmedLine.match(/^\*\*(.+?)\*\*:?$/);
    const orderedMatch = trimmedLine.match(/^\d+[.)]\s+(.+)$/);
    const unorderedMatch = trimmedLine.match(/^(?:[-*•])\s+(.+)$/);

    if (!trimmedLine) {
      flushParagraph();
      flushList();
    } else if (headingMatch || boldHeadingMatch) {
      flushParagraph();
      flushList();
      blocks.push({ type: 'heading', text: headingMatch?.[1] || boldHeadingMatch[1].replace(/:$/, '') });
    } else if (orderedMatch || unorderedMatch) {
      flushParagraph();
      const type = orderedMatch ? 'ordered-list' : 'unordered-list';
      if (!list || list.type !== type) {
        flushList();
        list = { type, items: [] };
      }
      list.items.push(orderedMatch ? orderedMatch[1] : unorderedMatch[1]);
    } else {
      flushList();
      paragraph.push(trimmedLine);
    }
  });

  flushParagraph();
  flushList();
  return blocks;
};

const StructuredResponse = ({ text }) => (
  <div className="space-y-3 text-sm leading-6 text-[#27443d]">
    {getResponseBlocks(text).map((block, index) => {
      if (block.type === 'heading') {
        return <h3 key={index} className="pt-1 text-base font-bold leading-6 text-[#14322f]">{formatInlineText(block.text)}</h3>;
      }

      if (block.type === 'ordered-list') {
        return <ol key={index} className="list-decimal space-y-2 pl-5 marker:font-semibold marker:text-[#51756a]">{block.items.map((item, itemIndex) => <li key={itemIndex} className="pl-1">{formatInlineText(item)}</li>)}</ol>;
      }

      if (block.type === 'unordered-list') {
        return <ul key={index} className="list-disc space-y-2 pl-5 marker:text-[#7fa89a]">{block.items.map((item, itemIndex) => <li key={itemIndex} className="pl-1">{formatInlineText(item)}</li>)}</ul>;
      }

      return <p key={index}>{formatInlineText(block.lines.join(' '))}</p>;
    })}
  </div>
);

const MessageBubble = ({ message }) => {
  const [showConflicts, setShowConflicts] = useState(false);

  const getConfidenceDetails = (confidence) => {
    switch (confidence) {
      case 'Verified':
        return { color: 'border-[#b9dd92] bg-[#effadc] text-[#446b19]', icon: <CheckCircle size={14} /> };
      case 'Conflicting':
        return { color: 'border-[#f2d68b] bg-[#fff9df] text-[#8a6515]', icon: <AlertTriangle size={14} /> };
      case 'Outdated':
        return { color: 'border-[#f2c49a] bg-[#fff1e7] text-[#a4531e]', icon: <Clock size={14} /> };
      case 'Insufficient':
        return { color: 'border-[#efb9b0] bg-[#fff0ed] text-[#a33e35]', icon: <XCircle size={14} /> };
      default:
        return { color: 'border-[#d5e0da] bg-[#f0f5f2] text-[#547067]', icon: <HelpCircle size={14} /> };
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

  const confidence = message.confidence ? getConfidenceDetails(message.confidence) : null;

  return (
    <article className="flex max-w-[94%] gap-3 message-appear sm:max-w-[84%]">
      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-[#dfece5] text-[#265449]"><Bot size={17} /></div>
      <div className={`min-w-0 flex-1 rounded-2xl rounded-tl-sm border bg-white p-5 shadow-sm ${message.isError ? 'border-[#efb9b0]' : 'border-[#dce5df]'}`}>
        <div className="mb-3 flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-[0.13em] text-[#3a6659]">Academic helpdesk</span>
          {message.classification && <span className="rounded-full bg-[#edf4ef] px-2 py-0.5 text-[10px] font-semibold text-[#688078]">{message.classification}</span>}
        </div>
        {message.isError ? <p className="text-sm leading-6 text-[#a33e35]">{message.text}</p> : <StructuredResponse text={message.text} />}

        {(confidence || message.sources?.length > 0) && <div className="mt-5 border-t border-[#e6ede9] pt-4">
          {confidence && <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${confidence.color}`}>{confidence.icon} {message.confidence}</span>}

          {message.conflicts?.length > 0 && (
            <div className="mt-3">
              <button onClick={() => setShowConflicts(!showConflicts)} className="flex w-full items-center gap-2 rounded-xl border border-[#f2d68b] bg-[#fff9df] px-3 py-2 text-left text-xs font-semibold text-[#8a6515] transition hover:bg-[#fff4c5]">
                <AlertTriangle size={14} />
                Review conflicting information
                {showConflicts ? <ChevronUp size={14} className="ml-auto" /> : <ChevronDown size={14} className="ml-auto" />}
              </button>
              {showConflicts && <div className="mt-2 space-y-2 rounded-xl border border-[#f7e6ad] bg-[#fffdf1] p-3 text-xs leading-5 text-[#6c5a27]">{message.conflicts.map((conflict, index) => <p key={index}>{conflict}</p>)}</div>}
            </div>
          )}

          {message.sources?.length > 0 && <div className="mt-4">
            <h3 className="mb-2 text-[11px] font-bold uppercase tracking-[0.13em] text-[#70877e]">Supporting documents</h3>
            <div className="flex flex-wrap gap-2">{message.sources.map((source, index) => <SourceCard key={index} source={source} />)}</div>
          </div>}
        </div>}
      </div>
    </article>
  );
};

export default MessageBubble;
