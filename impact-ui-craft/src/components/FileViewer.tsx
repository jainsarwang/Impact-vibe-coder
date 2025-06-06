
import React from 'react';
import { X, Copy, Download, Code } from 'lucide-react';
import { FileStatus } from './ProjectBuilder';

interface FileViewerProps {
  file: FileStatus;
  onClose: () => void;
}

const FileViewer = ({ file, onClose }: FileViewerProps) => {
  const copyToClipboard = () => {
    if (file.content) {
      navigator.clipboard.writeText(file.content);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="relative group w-full max-w-6xl max-h-[85vh]">
        {/* Glow effect */}
        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl blur opacity-50 group-hover:opacity-75 transition duration-1000"></div>
        
        <div className="relative bg-slate-900/95 backdrop-blur-lg rounded-3xl border border-white/20 flex flex-col shadow-2xl">
          {/* Enhanced Header */}
          <div className="flex items-center justify-between p-6 border-b border-white/20">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                <Code className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">{file.name}</h3>
                <p className="text-sm text-blue-200">Generated file content</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={copyToClipboard}
                className="p-3 hover:bg-white/20 rounded-xl transition-all duration-300 text-slate-300 hover:text-white group"
                title="Copy to clipboard"
              >
                <Copy className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
              </button>
              <button
                className="p-3 hover:bg-white/20 rounded-xl transition-all duration-300 text-slate-300 hover:text-white group"
                title="Download file"
              >
                <Download className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
              </button>
              <button
                onClick={onClose}
                className="p-3 hover:bg-red-500/20 rounded-xl transition-all duration-300 text-slate-300 hover:text-red-300 group"
              >
                <X className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
              </button>
            </div>
          </div>

          {/* Enhanced Content */}
          <div className="flex-1 overflow-auto p-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-2xl"></div>
              <pre className="relative bg-black/50 rounded-2xl p-6 text-sm text-slate-200 font-mono overflow-x-auto border border-white/10 backdrop-blur-sm">
                <code>{file.content || '// File content will appear here...'}</code>
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileViewer;
