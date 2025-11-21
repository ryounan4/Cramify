/**
 * MAIN PAGE (Home Page)
 */

'use client';

import { useState } from 'react';

export default function Home() {

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedPdfUrl, setGeneratedPdfUrl] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
  };

  const handleGenerate = async () => {

    setIsGenerating(true);
    setError(null);
    setGeneratedPdfUrl(null);

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

    try {
        const response = await fetch('http://localhost:5001/api/generate', {
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

  return (
    <div className="container-custom">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          📚 Cramify
        </h1>
        <p className="text-gray-600">
          Upload your lecture PDFs and get a dense 2-page cheat sheet
        </p>
      </div>

      {/* File Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Upload Lecture Slides</h2>

        {/* File Input with Drag & Drop Styling */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
          <p className="text-gray-500 mb-4">
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
            className="cursor-pointer bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600 inline-block transition-colors"
          >
            Choose Files
          </label>
        </div>

        {/* Display selected files */}
        {selectedFiles.length > 0 && (
          <div className="mt-4">
            <h3 className="font-medium mb-2">Selected Files ({selectedFiles.length}):</h3>
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              {selectedFiles.map((file, index) => (
                <li key={index}>
                  {file.name} <span className="text-gray-400">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
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
            className="mt-4 w-full bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
          >
            {isGenerating ? 'Generating... (this may take 1-2 minutes)' : '🚀 Generate Cheat Sheet'}
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Generated Cheat Sheet</h2>

        {generatedPdfUrl ? (
          <div className="space-y-4">
            {/* PDF Viewer */}
            <iframe
              src={generatedPdfUrl}
              className="w-full h-[800px] border rounded-lg"
              title="Generated Cheat Sheet"
            />

            {/* Download Button */}
            <a
              href={generatedPdfUrl}
              download="cramify-cheatsheet.pdf"
              className="block w-full text-center bg-blue-500 text-white px-6 py-3 rounded-md hover:bg-blue-600 transition-colors"
            >
              ⬇Download PDF
            </a>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            {isGenerating ? 'Processing your PDFs...' : 'Your cheat sheet will appear here'}
          </p>
        )}
      </div>
    </div>
  );
}
