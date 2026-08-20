import { Plus } from 'lucide-react';
import ChatInterface from '../components/ChatInterface';
import { useState } from 'react';

const ChatPage = () => {
  const [sessionKey, setSessionKey] = useState(Date.now()); // Used to force reset ChatInterface

  const handleNewChat = () => {
    setSessionKey(Date.now());
  };

  return (
    <div className="flex h-full w-full bg-gray-50">
      {/* Sidebar */}
      <div className="w-72 bg-white border-r border-gray-200 p-4 flex flex-col shrink-0">
        <button 
          onClick={handleNewChat}
          className="flex items-center justify-center space-x-2 w-full py-2.5 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium shadow-sm"
        >
          <Plus size={18} />
          <span>New Chat</span>
        </button>
        
        <div className="mt-6 flex-1 overflow-y-auto">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Recent Chats</h3>
          <div className="text-sm text-gray-500 italic px-2">
            Chat history will appear here.
          </div>
          {/* Future: Render list of chat sessions here */}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 h-full relative">
        <ChatInterface key={sessionKey} />
      </div>
    </div>
  );
};

export default ChatPage;
