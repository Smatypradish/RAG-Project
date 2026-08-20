import { Link, useLocation } from 'react-router-dom';
import { GraduationCap, MessageSquare, Settings } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 shrink-0 z-10 shadow-sm">
      <Link to="/" className="flex items-center space-x-2 text-indigo-600 hover:text-indigo-700 transition-colors">
        <GraduationCap size={28} />
        <span className="font-bold text-xl text-gray-900">College Helpdesk</span>
      </Link>
      <div className="flex items-center space-x-6">
        <Link 
          to="/" 
          className={`flex items-center space-x-1 ${location.pathname === '/' ? 'text-indigo-600 font-medium' : 'text-gray-600 hover:text-indigo-600'}`}
        >
          <MessageSquare size={18} />
          <span>Chat</span>
        </Link>
        <Link 
          to="/admin" 
          className={`flex items-center space-x-1 ${location.pathname === '/admin' ? 'text-indigo-600 font-medium' : 'text-gray-600 hover:text-indigo-600'}`}
        >
          <Settings size={18} />
          <span>Admin</span>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
