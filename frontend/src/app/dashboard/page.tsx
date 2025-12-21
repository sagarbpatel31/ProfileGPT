'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

interface TenantInfo {
  tenant_id: string;
  name: string;
  email?: string;
  profession?: string;
  bio?: string;
  api_key: string;
  embed_code: string;
  chat_url: string;
}

interface Document {
  id: string;
  title: string;
  source_type: string;
  status: string;
  chunks_created?: number;
}

interface DocumentResponse {
  id: string;
  title: string;
  source_type: string;
  url?: string | null;
  chunks_count: number;
  created_at: string;
}

interface SupportedPlatform {
  name: string;
  domain: string;
  example: string;
  note?: string;
}

export default function Dashboard() {
  const [tenantInfo, setTenantInfo] = useState<TenantInfo | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadType, setUploadType] = useState('resume');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadMode, setUploadMode] = useState<'file' | 'url'>('file');
  const [profileUrl, setProfileUrl] = useState('');
  const [supportedPlatforms, setSupportedPlatforms] = useState<SupportedPlatform[]>([]);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const router = useRouter();

  const getDocumentTypeLabel = (sourceType: string) => {
    const labels: Record<string, string> = {
      'resume': 'Resume',
      'cover_letter': 'Cover Letter',
      'portfolio': 'Portfolio',
      'linkedin': 'LinkedIn',
      'github': 'GitHub',
      'paper': 'Research Paper',
      'misc': 'Other',
      'github_profile': 'GitHub',
      'linkedin_profile': 'LinkedIn',
      'devto_profile': 'Dev.to',
      'stackoverflow_profile': 'Stack Overflow',
      'medium_profile': 'Medium',
      'twitter_profile': 'Twitter',
      'uploaded': 'Document'
    };
    return labels[sourceType] || sourceType;
  };

  useEffect(() => {
    // Load tenant info from localStorage
    const stored = localStorage.getItem('profilegpt_tenant');
    if (stored) {
      const tenant = JSON.parse(stored);
      setTenantInfo(tenant);
      loadDocuments(tenant.tenant_id);
    }

    // Load supported platforms
    fetch(`${API_BASE}/platforms`)
      .then(res => res.json())
      .then(data => setSupportedPlatforms(data.supported_platforms || []))
      .catch(err => console.error('Failed to load platforms:', err));
  }, []);
  useEffect(() => {
    if (infoMessage && documents.length > 0) {
      setInfoMessage(null);
    }
  }, [documents, infoMessage]);

  const loadDocuments = async (tenantId: string) => {
    try {
      const response = await fetch(`${API_BASE}/documents`);
      const data = await response.json();

      // For now, show recently uploaded documents from localStorage
      const recentUploads = JSON.parse(localStorage.getItem('recent_uploads') || '[]');

      const formattedDocs = recentUploads.map((doc: any) => ({
        id: doc.id,
        title: doc.title,
        source_type: doc.source_type,
        status: doc.status || 'completed',
        chunks_created: doc.chunks_created || 0,
        url: doc.url,
        created_at: doc.created_at || new Date().toISOString()
      }));

      setDocuments(formattedDocs);
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const deleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      // Remove from localStorage
      const recentUploads = JSON.parse(localStorage.getItem('recent_uploads') || '[]');
      const updatedUploads = recentUploads.filter((doc: any) => doc.id !== documentId);
      localStorage.setItem('recent_uploads', JSON.stringify(updatedUploads));

      // Reload documents after deletion
      if (tenantInfo) {
        loadDocuments(tenantInfo.tenant_id);
      }

      alert('Document deleted successfully!');
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Error deleting document');
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !tenantInfo) return;

    setIsUploading(true);
    setUploadError('');

    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('source_type', uploadType);
    formData.append('tenant_id', tenantInfo.tenant_id);
    if (uploadTitle) {
      formData.append('title', uploadTitle);
    }

    try {
      const response = await fetch(`${API_BASE}/ingest`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        // Store uploaded document locally for now
        const recentUploads = JSON.parse(localStorage.getItem('recent_uploads') || '[]');
        const newDoc = {
          id: data.document.id,
          title: data.document.title,
          source_type: data.document.source_type,
          status: data.document.status,
          chunks_created: 1,
          created_at: new Date().toISOString()
        };
        recentUploads.unshift(newDoc);
        localStorage.setItem('recent_uploads', JSON.stringify(recentUploads.slice(0, 10))); // Keep latest 10

        // Reload documents from localStorage
        loadDocuments(tenantInfo.tenant_id);

        // Show success message
        alert('Document uploaded successfully!');

        // Reset form
        setUploadFile(null);
        setUploadTitle('');
        setUploadType('resume');

        // Reset file input
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        setUploadError(data.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError('Network error. Please make sure the backend server is running.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleUrlUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profileUrl.trim() || !tenantInfo) return;

    setIsUploading(true);
    setUploadError('');

    try {
      const response = await fetch(`${API_BASE}/ingest/url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: profileUrl,
          source_type: uploadType,
          title: uploadTitle,
          tenant_id: tenantInfo.tenant_id,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Reload documents from server to ensure consistency
        loadDocuments(tenantInfo.tenant_id);

        // Reset form
        setProfileUrl('');
        setUploadTitle('');
        setUploadType('resume');
      } else {
        setUploadError(data.message || 'URL import failed');
      }
    } catch (error) {
      console.error('Error importing URL:', error);
      setUploadError('Network error. Please make sure the backend server is running.');
    } finally {
      setIsUploading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (!tenantInfo) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">No Account Found</h1>
          <p className="text-gray-600 mb-6">Please create an account first.</p>
          <Link
            href="/signup"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Create Account
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold">P</span>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">ProfileGPT Dashboard</h1>
                <p className="text-sm text-gray-500">Welcome back, {tenantInfo.name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => {
                  localStorage.removeItem('profilegpt_tenant');
                  router.push('/login');
                }}
                className="text-gray-500 hover:text-gray-700 text-sm"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-gray-900">Workspace verified</p>
              <p className="text-sm text-gray-800">Signed in as {tenantInfo.email}. Tenant ID: {tenantInfo.tenant_id}</p>
            </div>
            <div className="text-sm text-gray-700">
              Upload a resume, portfolio, GitHub, LinkedIn, or Google Scholar link to unlock your AI chat.
            </div>
          </div>
        </div>
        {infoMessage && (
          <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-900">
            {infoMessage}
          </div>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Upload Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Add Content to Your ProfileGPT</h2>
              <p className="text-gray-700 mb-6">
                Import resumes, portfolios, GitHub/LinkedIn/Google Scholar pages, or any professional site. Richer sources yield stronger answers.
              </p>

              {/* Upload Mode Selector */}
              <div className="mb-6">
                <div className="flex border-b border-gray-200">
                  <button
                    type="button"
                    onClick={() => setUploadMode('file')}
                    className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                      uploadMode === 'file'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    📄 Upload Files
                  </button>
                  <button
                    type="button"
                    onClick={() => setUploadMode('url')}
                    className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                      uploadMode === 'url'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    🔗 Import from URL
                  </button>
                </div>
              </div>

              {uploadMode === 'file' ? (
                <form onSubmit={handleFileUpload} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Type
                  </label>
                  <select
                    value={uploadType}
                    onChange={(e) => setUploadType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                  >
                    <option value="resume">Resume/CV</option>
                    <option value="cover_letter">Cover Letter</option>
                    <option value="portfolio">Portfolio</option>
                    <option value="linkedin">LinkedIn Profile</option>
                    <option value="github">GitHub Profile</option>
                    <option value="paper">Research Paper</option>
                    <option value="misc">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Title (optional)
                  </label>
                  <input
                    type="text"
                    value={uploadTitle || ''}
                    onChange={(e) => setUploadTitle(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black placeholder-gray-500"
                    placeholder="Resume"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select File
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    accept=".pdf,.doc,.docx,.txt,.md"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Supports: PDF, DOC, DOCX, TXT, MD files
                  </p>
                </div>

                {uploadError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-red-700 text-sm">{uploadError}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!uploadFile || isUploading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUploading ? 'Uploading...' : 'Upload Document'}
                </button>
              </form>
              ) : (
                <form onSubmit={handleUrlUpload} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Profile URL
                    </label>
                    <input
                      type="url"
                      value={profileUrl || ''}
                      onChange={(e) => setProfileUrl(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black placeholder-gray-500"
                      placeholder="https://github.com/username, https://linkedin.com/in/username, https://scholar.google.com/citations?user=..."
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Paste a public GitHub/LinkedIn/Google Scholar/portfolio link and we’ll capture the visible content.
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Content Type
                    </label>
                    <select
                      value={uploadType}
                      onChange={(e) => setUploadType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    >
                      <option value="github_profile">GitHub Profile</option>
                      <option value="linkedin_profile">LinkedIn Profile</option>
                      <option value="devto_profile">Dev.to Profile</option>
                      <option value="stackoverflow_profile">Stack Overflow Profile</option>
                      <option value="medium_profile">Medium Profile</option>
                      <option value="twitter_profile">Twitter Profile</option>
                      <option value="portfolio">Personal Website</option>
                      <option value="misc">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Custom Title (optional)
                    </label>
                    <input
                      type="text"
                      value={uploadTitle}
                      onChange={(e) => setUploadTitle(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black placeholder-gray-500"
                      placeholder="GitHub Profile"
                    />
                  </div>

                  {uploadError && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-red-700 text-sm">{uploadError}</p>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={!profileUrl.trim() || isUploading}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isUploading ? 'Importing...' : 'Import Profile'}
                  </button>

                  {/* Supported Platforms */}
                  {supportedPlatforms.length > 0 && (
                    <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Popular Sources</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm text-blue-900">
                        {supportedPlatforms.map((platform, index) => (
                          <div key={index}>
                            • {platform.name}
                            {platform.note && <span className="text-blue-600"> ({platform.note})</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </form>
              )}
            </div>

            {/* Documents List */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Documents</h2>

              {documents.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-gray-400 text-2xl">📄</span>
                  </div>
                  <p className="text-gray-500">No documents uploaded yet</p>
                  <p className="text-sm text-gray-400 mt-1">Upload your first document above to get started</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div key={doc.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{doc.title}</h3>
                          <p className="text-sm text-gray-500">
                            {getDocumentTypeLabel(doc.source_type)} • {doc.status}
                            {doc.chunks_created && ` • ${doc.chunks_created} chunks processed`}
                          </p>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            doc.status === 'completed' ? 'bg-green-100 text-green-800' :
                            doc.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {doc.status}
                          </span>
                          <button
                            onClick={() => deleteDocument(doc.id)}
                            className="text-red-600 hover:text-red-800 text-sm font-medium"
                            title="Delete document"
                          >
                            🗑️ Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">

            {/* Account Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Info</h2>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-700">Tenant ID</label>
                  <div className="mt-1 flex">
                    <code className="flex-1 text-xs bg-gray-100 px-2 py-1 rounded">{tenantInfo.tenant_id}</code>
                    <button
                      onClick={() => copyToClipboard(tenantInfo.tenant_id)}
                      className="ml-2 text-blue-600 hover:text-blue-500 text-xs"
                    >
                      Copy
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Widget Integration */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Widget Integration</h2>
              <p className="text-sm text-gray-600 mb-4">
                Add this code to your website to embed the chat widget:
              </p>
              <div className="bg-gray-100 p-3 rounded text-xs font-mono break-all">
                {tenantInfo.embed_code}
              </div>
              <button
                onClick={() => copyToClipboard(tenantInfo.embed_code)}
                className="mt-3 w-full bg-gray-600 text-white py-2 px-4 rounded text-sm hover:bg-gray-700"
              >
                Copy Embed Code
              </button>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button
                  onClick={() => {
                    if (documents.length === 0) {
                      setInfoMessage('Please upload at least one document or profile URL before launching the chat.');
                      return;
                    }
                    router.push(`/personalized?tenant=${tenantInfo.tenant_id}`);
                  }}
                  className={`w-full py-2 px-4 rounded text-white ${documents.length === 0 ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
                >
                  Try Your ProfileGPT
                </button>
                <Link
                  href="/widget-demo.html"
                  target="_blank"
                  className="block w-full bg-green-600 text-white py-2 px-4 rounded text-center hover:bg-green-700"
                >
                  Widget Demo
                </Link>
                <button
                  onClick={() => window.open(`${API_BASE}/docs`, '_blank')}
                  className="w-full bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700"
                >
                  API Documentation
                </button>
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}
