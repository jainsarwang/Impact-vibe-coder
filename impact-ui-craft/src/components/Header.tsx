
import React from 'react';
import { Code2, Sparkles } from 'lucide-react';

const Header = () => {
  return (
    <header className="w-full px-6 py-4 bg-white/10 backdrop-blur-md border-b border-white/20 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <Code2 className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Impact Vibe Coder
            </h1>
            <p className="text-sm text-blue-200 font-medium">
              AI-Powered Project Generator
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-blue-200 bg-white/10 px-3 py-2 rounded-full backdrop-blur-sm">
            <Sparkles className="w-4 h-4 animate-pulse" />
            <span className="font-medium">Powered by AI</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
