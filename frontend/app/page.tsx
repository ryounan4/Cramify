/**
 * MAIN PAGE (Home Page)
 */

'use client';

import { useState } from 'react';
import { Upload, File, FileText, Zap, Loader2 } from 'lucide-react';
import { useAuth } from './auth/AuthContext';
import LoginModal from './components/LoginModal';
import UserMenu from './components/UserMenu';

export default function Home() {
  // Get user state from auth context
  const { user, getAuthToken } = useAuth();

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedPdfUrl, setGeneratedPdfUrl] = useState<string | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);  // Controls login modal visibility

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
  };

  // Actual API call logic (assumes user is already logged in)
  const performGeneration = async () => {
    setIsGenerating(true);
    setError(null);
    setGeneratedPdfUrl(null);

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

    try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';
        const response = await fetch(`${API_URL}/api/generate`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        const blob = await response.blob();
        const pdfUrl = URL.createObjectURL(blob);
        setGeneratedPdfUrl(pdfUrl);
    } catch (err) {
        console.error('Error during API request:', err);
        setError('Failed to generate cheat sheet');
    } finally {
        setIsGenerating(false);
    }
  };

  // Called when user clicks "Generate" button
  const handleGenerate = async () => {
    // Route 1: User NOT logged in → show login modal
    if (!user) {
      setShowLoginModal(true);
      return;
    }

    // Route 2: User IS logged in → make API call
    await performGeneration();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Login Modal - appears when showLoginModal is true */}
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onSuccess={() => {
          setShowLoginModal(false);   // Close modal - user can now click Generate again
        }}
      />

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20 px-4 relative">
        {/* User Menu in top-right corner */}
        <div className="absolute top-6 right-6">
          <UserMenu onSignInClick={() => setShowLoginModal(true)} />
        </div>

        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block bg-white/20 backdrop-blur-sm rounded-full px-4 py-1 text-sm font-medium mb-6">
            AI-Powered Study Tool
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Cramify
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 mb-8">
           <b>Save time. Study smarter. Ace more exams.</b>
           <br></br><br></br>
           Transfrom all your lectures and notes into a cheat sheet within minutes
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">

      {/* File Upload Section */}
      <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <Upload className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Upload Lecture Slides</h2>
        </div>

        {/* File Input with Drag & Drop Styling */}
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-400 hover:bg-blue-50/50 transition-all">
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4 text-lg">
            Click to select PDF files or drag and drop
          </p>
          <input
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg hover:from-blue-600 hover:to-purple-700 inline-flex items-center gap-2 font-medium transition-all shadow-md hover:shadow-lg"
          >
            <File className="w-5 h-5" />
            Choose Files
          </label>
        </div>

        {/* Display selected files */}
        {selectedFiles.length > 0 && (
          <div className="mt-6 bg-gray-50 rounded-xl p-6">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Selected Files ({selectedFiles.length}):
            </h3>
            <ul className="space-y-2">
              {selectedFiles.map((file, index) => (
                <li key={index} className="flex items-center gap-2 text-gray-700 bg-white rounded-lg px-4 py-2">
                  <File className="w-4 h-4 text-blue-500" />
                  <span className="flex-1">{file.name}</span>
                  <span className="text-sm text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Generate Button */}
        {selectedFiles.length > 0 && (
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="mt-6 w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white px-8 py-4 rounded-xl hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed font-semibold text-lg transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-3"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating... (this may take 1-2 minutes)
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Generate Cheat Sheet
              </>
            )}
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-6 py-4 rounded-lg mb-8 shadow-md">
          <div className="flex items-center gap-2">
            <strong className="font-semibold">Error:</strong>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Results Section */}
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-green-600" />
            <h2 className="text-2xl font-bold text-gray-900">Generated Cheat Sheet</h2>
          </div>
          {generatedPdfUrl && (
            <button
              onClick={() => {
                setSelectedFiles([]);
                setGeneratedPdfUrl(null);
                setError(null);
              }}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors font-medium"
            >
              Create Another
            </button>
          )}
        </div>

        {generatedPdfUrl ? (
          <div className="space-y-4">
            {/* PDF Viewer */}
            <iframe
              src={generatedPdfUrl}
              className="w-full h-[800px] border rounded-xl"
              title="Generated Cheat Sheet"
            />

            {/* Download Button */}
            <a
              href={generatedPdfUrl}
              download="cramify-cheatsheet.pdf"
              className="block w-full text-center bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all font-semibold text-lg shadow-md hover:shadow-lg"
            >
              Download PDF
            </a>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            {isGenerating ? 'Processing your PDFs...' : 'Your cheat sheet will appear here'}
          </p>
        )}
      </div>
      </div>
    </div>
  );
}
