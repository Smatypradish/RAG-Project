import { useEffect, useRef, useState } from 'react';
import { ArrowUp, Bot, FileCheck2, Menu, Send, Sparkles } from 'lucide-react';
import { sendMessage } from '../services/api';
import MessageBubble from './MessageBubble';

const promptSuggestions = [
  'What is the procedure for applying for a bonafide certificate?',
  'How is CGPA calculated under the academic regulations?',
  'What are the rules for supplementary examinations?',
];

const ChatInterface = ({ session, onConversationChange, onNewChat }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (event, suggestedQuestion) => {
    event?.preventDefault();
    const userText = (suggestedQuestion || input).trim();
    if (!userText || isLoading) return;

    setInput('');
    setMessages((currentMessages) => [...currentMessages, { id: Date.now(), text: userText, isUser: true }]);
    onConversationChange(userText);
    setIsLoading(true);

    try {
      const response = await sendMessage(userText, session.id);
      setMessages((currentMessages) => [...currentMessages, {
        id: Date.now() + 1,
        text: response.answer,
        isUser: false,
        confidence_score: response.confidence_score,
        classification: response.classification,
        sources: response.sources || [],
        conflicts: response.conflicts || [],
      }]);
    } catch (error) {
      setMessages((currentMessages) => [...currentMessages, {
        id: Date.now() + 1,
        text: 'I could not reach the document service just now. Please try your question again in a moment.',
        isUser: false,
        isError: true,
      }]);
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-[28px] bg-[#fbfcf8] shadow-[0_24px_70px_rgba(15,38,35,0.11)]">
      <header className="flex items-center justify-between border-b border-[#dce5df] px-5 py-4 sm:px-7">
        <div className="flex items-center gap-3">
          <button onClick={onNewChat} className="grid h-10 w-10 place-items-center rounded-xl bg-[#e5ece7] text-[#31534d] transition hover:bg-[#d8e4dc] lg:hidden" aria-label="Start new enquiry">
            <Menu size={19} />
          </button>
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-[#12302d] text-[#d9ff75]">
            <Bot size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-[#14322f] sm:text-base">Academic helpdesk</h1>
              <span className="hidden rounded-full bg-[#e3f7bd] px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-[#42610d] sm:inline">Document-aware</span>
            </div>
            <p className="mt-0.5 text-xs text-[#6e827b]">Ask about regulations, exams, certificates, and more.</p>
          </div>
        </div>
        <button onClick={onNewChat} className="hidden items-center gap-2 rounded-xl border border-[#d6e2dc] bg-white px-3 py-2 text-xs font-semibold text-[#31534d] transition hover:border-[#a9c3b8] hover:bg-[#f3f7f4] sm:flex">
          <Sparkles size={15} />
          New enquiry
        </button>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-8 sm:py-8">
        <div className="mx-auto max-w-4xl">
          {!hasMessages && !isLoading && (
            <div className="flex min-h-[min(56vh,520px)] flex-col justify-center pb-8">
              <div className="max-w-2xl">
                <span className="mb-5 inline-flex items-center gap-2 rounded-full bg-[#e6f4ed] px-3 py-1.5 text-xs font-bold text-[#376255]">
                  <FileCheck2 size={15} />
                  Source-first support
                </span>
                <h2 className="max-w-xl text-3xl font-bold tracking-[-0.04em] text-[#14322f] sm:text-5xl">Find the rule, not just an answer.</h2>
                <p className="mt-4 max-w-xl text-base leading-7 text-[#637871]">Ask a campus question and receive an answer grounded in the official documents available to your college helpdesk.</p>
              </div>
              <div className="mt-9 grid gap-3 sm:grid-cols-3">
                {promptSuggestions.map((suggestion) => (
                  <button key={suggestion} onClick={() => handleSend(null, suggestion)} className="group rounded-2xl border border-[#dce5df] bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-[#98bcb0] hover:shadow-md">
                    <span className="mb-4 grid h-8 w-8 place-items-center rounded-lg bg-[#e6f4ed] text-[#315e50]"><ArrowUp size={16} className="-rotate-45" /></span>
                    <span className="block text-sm font-semibold leading-5 text-[#294740]">{suggestion}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {hasMessages && <div className="space-y-6 pb-5">{messages.map((message) => <MessageBubble key={message.id} message={message} />)}</div>}
          {isLoading && (
            <div className="flex items-center gap-3 message-appear">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-[#12302d] text-[#d9ff75]"><Bot size={17} /></div>
              <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-[#e8efeb] px-4 py-3">
                <span className="h-1.5 w-1.5 rounded-full bg-[#51756a] typing-dot" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#51756a] typing-dot" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#51756a] typing-dot" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t border-[#dce5df] bg-[#f7faf6] px-4 py-4 sm:px-8 sm:py-5">
        <form onSubmit={handleSend} className="mx-auto flex max-w-4xl items-center gap-2 rounded-2xl border border-[#cbdad2] bg-white p-2 shadow-sm focus-within:border-[#7fa89a] focus-within:ring-4 focus-within:ring-[#dcece4]">
          <input type="text" value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask about an official college process..." className="min-w-0 flex-1 bg-transparent px-3 py-2 text-sm text-[#193e37] outline-none placeholder:text-[#91a49d]" disabled={isLoading} />
          <button type="submit" disabled={!input.trim() || isLoading} className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#12302d] text-[#d9ff75] transition hover:bg-[#1b4942] disabled:cursor-not-allowed disabled:opacity-40" aria-label="Send message">
            <Send size={17} />
          </button>
        </form>
        <p className="mx-auto mt-3 max-w-4xl text-center text-[11px] text-[#7c9088]">Responses may be incomplete. Confirm important decisions with the relevant college office.</p>
      </div>
    </div>
  );
};

export default ChatInterface;
