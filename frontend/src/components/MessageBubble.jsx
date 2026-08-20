import { useState } from 'react';
import { User, Bot, AlertTriangle, ChevronDown, ChevronUp, CheckCircle, HelpCircle, XCircle, Clock } from 'lucide-react';
import SourceCard from './SourceCard';

const MessageBubble = ({ message }) => {
  const [showConflicts, setShowConflicts] = useState(false);

  const getConfidenceDetails = (confidence) => {
    switch (confidence) {
      case 'Verified':
        return { color: 'text-green-700 bg-green-50 border-green-200', icon: <CheckCircle size={14} className="mr-1" /> };
      case 'Conflicting':
        return { color: 'text-yellow-700 bg-yellow-50 border-yellow-200', icon: <AlertTriangle size={14} className="mr-1" /> };
      case 'Outdated':
        return { color: 'text-orange-700 bg-orange-50 border-orange-200', icon: <Clock size={14} className="mr-1" /> };
      case 'Insufficient':
        return { color: 'text-red-700 bg-red-50 border-red-200', icon: <XCircle size={14} className="mr-1" /> };
      case 'Not Available':
      default:
        return { color: 'text-gray-600 bg-gray-100 border-gray-200', icon: <HelpCircle size={14} className="mr-1" /> };
    }
  };

  if (message.isUser) {
    return (
      <div className="flex w-full justify-end message-appear">
        <div className="max-w-[85%] md:max-w-[75%] rounded-2xl p-4 bg-indigo-600 text-white rounded-br-none shadow-sm flex flex-col">
          <div className="flex items-center space-x-2 mb-1 justify-end opacity-80">
            <span className="text-xs font-medium">You</span>
            <User size={14} />
          </div>
          <div className="whitespace-pre-wrap">{message.text}</div>
        </div>
      </div>
    );
  }

  const confDetails = message.confidence ? getConfidenceDetails(message.confidence) : null;

  return (
    <div className="flex w-full justify-start message-appear">
      <div className={`max-w-[90%] md:max-w-[85%] rounded-2xl p-4 bg-white border ${message.isError ? 'border-red-300' : 'border-gray-200'} text-gray-800 rounded-bl-none shadow-sm flex flex-col`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2 text-indigo-600">
            <Bot size={16} />
            <span className="text-xs font-semibold uppercase tracking-wider">Helpdesk AI</span>
          </div>
          {message.classification && (
            <span className="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full font-medium">
              {message.classification}
            </span>
          )}
        </div>
        
        <div className={`whitespace-pre-wrap ${message.isError ? 'text-red-600' : 'text-gray-800'}`}>
          {message.text}
        </div>

        {confDetails && (
          <div className="mt-4 pt-3 border-t border-gray-100">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${confDetails.color}`}>
                {confDetails.icon}
                Confidence: {message.confidence}
              </span>
            </div>

            {message.conflicts && message.conflicts.length > 0 && (
              <div className="mb-3">
                <button 
                  onClick={() => setShowConflicts(!showConflicts)}
                  className="flex items-center text-xs font-medium text-yellow-700 hover:text-yellow-800 bg-yellow-50 px-3 py-1.5 rounded-md w-full border border-yellow-200 transition-colors"
                >
                  <AlertTriangle size={14} className="mr-1.5" />
                  <span>View conflicting information found</span>
                  {showConflicts ? <ChevronUp size={14} className="ml-auto" /> : <ChevronDown size={14} className="ml-auto" />}
                </button>
                
                {showConflicts && (
                  <div className="mt-2 p-3 bg-yellow-50/50 border border-yellow-100 rounded-md text-sm text-gray-700 space-y-2">
                    {message.conflicts.map((conflict, idx) => (
                      <div key={idx} className="flex gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-yellow-500 mt-1.5 shrink-0"></div>
                        <p>{conflict}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {message.sources && message.sources.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Sources</h4>
                <div className="flex flex-wrap gap-2">
                  {message.sources.map((source, idx) => (
                    <SourceCard key={idx} source={source} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
