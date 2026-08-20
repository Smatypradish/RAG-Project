import { useState, useEffect } from 'react';
import { Trash2, Edit2, AlertCircle } from 'lucide-react';
import { getDocuments, updateDocument, deleteDocument } from '../services/api';

const DocumentList = ({ onDocumentChange }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // For inline editing status
  const [editingId, setEditingId] = useState(null);
  const [editStatus, setEditStatus] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"? This will remove it from the knowledge base.`)) {
      return;
    }
    
    try {
      await deleteDocument(id);
      fetchDocuments();
      if (onDocumentChange) onDocumentChange();
    } catch (err) {
      alert('Failed to delete document');
      console.error(err);
    }
  };

  const startEdit = (doc) => {
    setEditingId(doc.id);
    setEditStatus(doc.status);
  };

  const saveEdit = async (id) => {
    try {
      await updateDocument(id, { status: editStatus });
      setEditingId(null);
      fetchDocuments();
      if (onDocumentChange) onDocumentChange();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'superseded': return 'bg-yellow-100 text-yellow-800';
      case 'withdrawn': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-96 flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-8 w-8 bg-gray-200 rounded-full mb-4"></div>
          <div className="text-gray-400 font-medium">Loading knowledge base...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col h-full min-h-[500px]">
      <div className="px-5 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-800">Knowledge Base</h2>
        <span className="bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
          {documents.length} Docs
        </span>
      </div>

      {error ? (
        <div className="p-8 text-center text-red-500 flex flex-col items-center">
          <AlertCircle size={32} className="mb-2" />
          <p>{error}</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-gray-500">
          <div className="bg-gray-50 p-4 rounded-full mb-3">
            <AlertCircle size={24} className="text-gray-400" />
          </div>
          <p className="font-medium">No documents uploaded yet</p>
          <p className="text-sm mt-1">Upload a document to start building your knowledge base.</p>
        </div>
      ) : (
        <div className="overflow-x-auto flex-1">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID / Name</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version/Auth</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-xs text-gray-400 mb-1">#{doc.id}</div>
                    <div className="text-sm font-medium text-gray-900 truncate max-w-[200px]" title={doc.name}>
                      {doc.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500 capitalize">{doc.category || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{doc.version || 'v1.0'}</div>
                    <div className="text-xs text-gray-500">Lvl {doc.authority_level || '?'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{new Date(doc.effective_date).toLocaleDateString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {editingId === doc.id ? (
                      <div className="flex items-center space-x-2">
                        <select
                          value={editStatus}
                          onChange={(e) => setEditStatus(e.target.value)}
                          className="text-sm border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                        >
                          <option value="active">Active</option>
                          <option value="superseded">Superseded</option>
                          <option value="withdrawn">Withdrawn</option>
                        </select>
                        <button onClick={() => saveEdit(doc.id)} className="text-green-600 hover:text-green-900">
                          <Check size={16} />
                        </button>
                        <button onClick={() => setEditingId(null)} className="text-gray-400 hover:text-gray-600">
                          <X size={16} />
                        </button>
                      </div>
                    ) : (
                      <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full uppercase ${getStatusColor(doc.status)}`}>
                        {doc.status}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-3">
                      <button 
                        onClick={() => startEdit(doc)}
                        className="text-indigo-600 hover:text-indigo-900"
                        title="Edit Status"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button 
                        onClick={() => handleDelete(doc.id, doc.name)}
                        className="text-red-600 hover:text-red-900"
                        title="Delete Document"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Quick fix for X import missing in DocumentList
import { X } from 'lucide-react';
export default DocumentList;
