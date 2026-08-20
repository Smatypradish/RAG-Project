import { useState, useEffect, useRef } from 'react';
import { Send, Bot } from 'lucide-react';
import { sendMessage } from '../services/api';
import MessageBubble from './MessageBubble';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm the College Helpdesk assistant. How can I help you today?",
      isUser: false,
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => Math.random().toString(36).substring(2, 15));
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput('');
    
    // Add user message immediately
    const newUserMsg = { id: Date.now(), text: userText, isUser: true };
    setMessages(prev => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      const response = await sendMessage(userText, sessionId);
      
      const botMsg = {
        id: Date.now() + 1,
        text: response.answer,
        isUser: false,
        confidence: response.confidence,
        classification: response.classification,
        sources: response.sources || [],
        conflicts: response.conflicts || []
      };
      
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      const errorMsg = {
        id: Date.now() + 1,
        text: "I'm sorry, I encountered an error while trying to answer your question. Please try again later.",
        isUser: false,
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        
        {isLoading && (
          <div className="flex w-full justify-start message-appear">
            <div className="max-w-[85%] md:max-w-[75%] rounded-2xl p-4 bg-gray-100 text-gray-800 rounded-bl-none flex items-center space-x-2">
              <Bot size={20} className="text-gray-500" />
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="w-full bg-gray-50 border border-gray-300 rounded-full pl-6 pr-14 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-shadow shadow-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors"
          >
            <Send size={18} className={input.trim() && !isLoading ? 'ml-0.5' : ''} />
          </button>
        </form>
        <div className="text-center mt-2 text-xs text-gray-400">
          College Helpdesk AI can make mistakes. Verify important information.
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
