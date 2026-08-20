import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, FileText, CheckCircle, Database, MessageSquare } from 'lucide-react';
import { getAdminStats } from '../services/api';
import DocumentUpload from '../components/DocumentUpload';
import DocumentList from '../components/DocumentList';

const AdminPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_documents: 0,
    active_documents: 0,
    total_chunks: 0,
    total_queries: 0
  });
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchStats();
  }, [navigate, refreshTrigger]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await getAdminStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch stats", error);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const triggerRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const StatCard = ({ title, value, icon, color }) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex items-center space-x-4">
      <div className={`p-3 rounded-lg ${color}`}>
        {icon}
      </div>
      <div>
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className="text-2xl font-bold text-gray-900">{loading ? '-' : value}</p>
      </div>
    </div>
  );

  return (
    <div className="h-full overflow-y-auto bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Knowledge Base Admin</h1>
            <p className="text-gray-500 text-sm mt-1">Manage documents, versions, and chatbot knowledge</p>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center space-x-2 text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 px-4 py-2 rounded-lg transition-colors text-sm font-medium"
          >
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard 
            title="Total Documents" 
            value={stats.total_documents} 
            icon={<FileText size={24} />} 
            color="bg-blue-100 text-blue-600" 
          />
          <StatCard 
            title="Active Documents" 
            value={stats.active_documents} 
            icon={<CheckCircle size={24} />} 
            color="bg-green-100 text-green-600" 
          />
          <StatCard 
            title="Vector Chunks" 
            value={stats.total_chunks} 
            icon={<Database size={24} />} 
            color="bg-purple-100 text-purple-600" 
          />
          <StatCard 
            title="Total Queries" 
            value={stats.total_queries || 0} 
            icon={<MessageSquare size={24} />} 
            color="bg-indigo-100 text-indigo-600" 
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <DocumentUpload onUploadSuccess={triggerRefresh} />
          </div>
          <div className="lg:col-span-2">
            <DocumentList key={refreshTrigger} onDocumentChange={triggerRefresh} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
