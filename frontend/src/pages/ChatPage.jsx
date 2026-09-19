import { useEffect, useState } from 'react';
import { Archive, BookOpen, ChevronRight, Clock3, Plus, Sparkles } from 'lucide-react';
import ChatInterface from '../components/ChatInterface';

const STORAGE_KEY = 'rag_chat_sessions';
const MAX_SESSIONS = 20;

const createSession = () => ({
  id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
  title: 'New enquiry',
  updatedAt: Date.now(),
  preview: 'Start a document-based conversation',
  messages: [],
});

const loadSessions = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return Array.isArray(stored) ? stored : [];
  } catch {
    return [];
  }
};

const ChatPage = () => {
  const [activeSession, setActiveSession] = useState(createSession);
  const [sessions, setSessions] = useState(loadSessions);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions.slice(0, MAX_SESSIONS)));
    } catch {
      // Storage full or unavailable — history simply won't persist.
    }
  }, [sessions]);

  const handleNewChat = () => {
    setActiveSession(createSession());
  };

  const updateConversation = (details) => {
    setActiveSession(details);
    setSessions((currentSessions) =>
      [details, ...currentSessions.filter((session) => session.id !== details.id)].slice(0, MAX_SESSIONS)
    );
  };

  return (
    <main className="flex h-full w-full overflow-hidden bg-[#eef2f0] p-3 sm:p-5">
      <aside className="hidden w-80 shrink-0 flex-col overflow-hidden rounded-[28px] bg-[#12302d] p-4 text-white shadow-[0_24px_70px_rgba(15,38,35,0.2)] lg:flex">
        <div className="mb-8 flex items-center gap-3 px-2 pt-2">
          <div className="grid h-10 w-10 place-items-center rounded-2xl bg-[#d9ff75] text-[#12302d]">
            <BookOpen size={20} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-wide text-white">Student desk</p>
            <p className="text-xs text-[#a8c4bc]">Official document support</p>
          </div>
        </div>

        <button
          onClick={handleNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#d9ff75] px-4 py-3 text-sm font-bold text-[#12302d] transition hover:bg-[#e5ff9c] focus:outline-none focus:ring-2 focus:ring-[#d9ff75] focus:ring-offset-2 focus:ring-offset-[#12302d]"
        >
          <Plus size={18} />
          New enquiry
        </button>

        <div className="mt-8 flex min-h-0 flex-1 flex-col">
          <div className="mb-3 flex items-center justify-between px-2">
            <span className="text-[11px] font-bold uppercase tracking-[0.16em] text-[#8daca3]">Recent enquiries</span>
            <Clock3 size={14} className="text-[#8daca3]" />
          </div>
          <div className="space-y-1 overflow-y-auto pr-1">
            {sessions.length ? sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => setActiveSession(session)}
                className={`group flex w-full items-center gap-3 rounded-xl p-3 text-left transition ${activeSession.id === session.id ? 'bg-white/14' : 'hover:bg-white/8'}`}
              >
                <Archive size={16} className="shrink-0 text-[#b7d2ca]" />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-medium text-white">{session.title}</span>
                  <span className="mt-0.5 block truncate text-xs text-[#a8c4bc]">{session.preview}</span>
                </span>
                <ChevronRight size={15} className="shrink-0 opacity-0 transition group-hover:opacity-100" />
              </button>
            )) : (
              <div className="rounded-2xl border border-dashed border-white/20 px-4 py-5 text-center">
                <Sparkles size={18} className="mx-auto mb-2 text-[#d9ff75]" />
                <p className="text-sm font-medium text-white">Your enquiries stay here</p>
                <p className="mt-1 text-xs leading-5 text-[#a8c4bc]">Start a conversation to keep it handy during this visit.</p>
              </div>
            )}
          </div>
        </div>

        <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs font-semibold text-[#d9ff75]">Grounded responses</p>
          <p className="mt-1 text-xs leading-5 text-[#b7d2ca]">Answers are built from your institution’s uploaded documents and include source references.</p>
        </div>
      </aside>

      <section className="min-w-0 flex-1 overflow-hidden lg:ml-5">
        <ChatInterface key={activeSession.id} session={activeSession} onConversationChange={updateConversation} onNewChat={handleNewChat} />
      </section>
    </main>
  );
};

export default ChatPage;
