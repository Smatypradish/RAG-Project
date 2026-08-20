import { GraduationCap, MessageSquare, Settings } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();
  const linkClasses = (isActive) => `flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive ? 'bg-[#e6f4ed] text-[#234f43]' : 'text-[#647972] hover:bg-[#f0f5f2] hover:text-[#234f43]'}`;

  return (
    <nav className="z-10 flex h-16 shrink-0 items-center justify-between border-b border-[#dce5df] bg-[#fbfcf8] px-4 sm:px-6">
      <Link to="/" className="flex items-center gap-2 text-[#14322f]">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#12302d] text-[#d9ff75]"><GraduationCap size={20} /></span>
        <span className="hidden text-base font-bold tracking-tight sm:inline">College helpdesk</span>
      </Link>
      <div className="flex items-center gap-1">
        <Link to="/" className={linkClasses(location.pathname === '/')}><MessageSquare size={17} /><span className="hidden sm:inline">Helpdesk</span></Link>
        <Link to="/admin" className={linkClasses(location.pathname === '/admin')}><Settings size={17} /><span className="hidden sm:inline">Admin</span></Link>
      </div>
    </nav>
  );
};

export default Navbar;
