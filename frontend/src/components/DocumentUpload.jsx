import { useState } from 'react';
import { Upload, X, Check } from 'lucide-react';
import { uploadDocument } from '../services/api';

const DocumentUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [formData, setFormData] = useState({
    category: 'general',
    authority_level: 5,
    version: '1.0',
    effective_date: new Date().toISOString().split('T')[0],
    expiry_date: '',
    status: 'active',
    supersedes_id: '',
    revision_reason: ''
  });
  
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage({ type: 'error', text: 'Please select a file to upload.' });
      return;
    }

    setUploading(true);
    setMessage(null);

    const data = new FormData();
    data.append('file', file);
    Object.keys(formData).forEach(key => {
      if (formData[key]) {
        data.append(key, formData[key]);
      }
    });

    try {
      await uploadDocument(data);
      setMessage({ type: 'success', text: 'Document uploaded successfully!' });
      setFile(null);
      // Reset form but keep defaults
      setFormData(prev => ({
        ...prev,
        version: '1.0',
        supersedes_id: '',
        revision_reason: ''
      }));
      // Reset file input
      document.getElementById('file-upload').value = '';
      if (onUploadSuccess) onUploadSuccess();
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error uploading document. Please try again.' 
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-800">Upload Document</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="p-5 space-y-4">
        {message && (
          <div className={`p-3 rounded-md text-sm flex items-start space-x-2 ${
            message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            {message.type === 'success' ? <Check size={18} className="mt-0.5 shrink-0" /> : <X size={18} className="mt-0.5 shrink-0" />}
            <span>{message.text}</span>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">File</label>
          <input
            id="file-upload"
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleInputChange}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            >
              <option value="academic">Academic</option>
              <option value="examination">Examination</option>
              <option value="scholarship">Scholarship</option>
              <option value="hostel">Hostel</option>
              <option value="certificate">Certificate</option>
              <option value="general">General</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Authority Level</label>
            <select
              name="authority_level"
              value={formData.authority_level}
              onChange={handleInputChange}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            >
              <option value="1">1 - UGC/Govt</option>
              <option value="2">2 - University</option>
              <option value="3">3 - College Core</option>
              <option value="4">4 - Department</option>
              <option value="5">5 - General</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Version</label>
            <input
              type="text"
              name="version"
              value={formData.version}
              onChange={handleInputChange}
              placeholder="e.g. v1.0"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            >
              <option value="active">Active</option>
              <option value="superseded">Superseded</option>
              <option value="withdrawn">Withdrawn</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Effective Date</label>
            <input
              type="date"
              name="effective_date"
              value={formData.effective_date}
              onChange={handleInputChange}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date <span className="text-gray-400 font-normal">(Optional)</span></label>
            <input
              type="date"
              name="expiry_date"
              value={formData.expiry_date}
              onChange={handleInputChange}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Supersedes Doc ID <span className="text-gray-400 font-normal">(Optional)</span></label>
          <input
            type="number"
            name="supersedes_id"
            value={formData.supersedes_id}
            onChange={handleInputChange}
            placeholder="Document ID this replaces"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Revision Reason <span className="text-gray-400 font-normal">(Optional)</span></label>
          <textarea
            name="revision_reason"
            value={formData.revision_reason}
            onChange={handleInputChange}
            rows={2}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          />
        </div>

        <button
          type="submit"
          disabled={uploading || !file}
          className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
        >
          {uploading ? (
            'Processing and Uploading...'
          ) : (
            <>
              <Upload size={16} className="mr-2" />
              Upload Document
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default DocumentUpload;
