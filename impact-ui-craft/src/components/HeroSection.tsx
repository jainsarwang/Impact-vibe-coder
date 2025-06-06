
import React from 'react';
import { Zap, Rocket, Star, ArrowRight } from 'lucide-react';

const HeroSection = () => {
  return (
    <section className="w-full px-6 py-20 text-center relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-cyan-500/10 rounded-full blur-2xl animate-pulse delay-500"></div>
      </div>
      
      <div className="max-w-5xl mx-auto relative z-10">
        <div className="flex justify-center mb-8">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-pulse"></div>
            <div className="relative p-6 bg-gradient-to-r from-blue-500/30 to-indigo-500/30 rounded-full border border-blue-400/50 backdrop-blur-sm">
              <Zap className="w-16 h-16 text-blue-300" />
            </div>
          </div>
        </div>
        
        <h1 className="text-6xl md:text-8xl font-extrabold text-white mb-8 leading-tight">
          Transform Ideas into
          <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent animate-pulse">
            {" "}Code
          </span>
        </h1>
        
        <p className="text-xl md:text-2xl text-slate-200 mb-12 max-w-3xl mx-auto leading-relaxed font-light">
          Simply describe your project and watch as Impact Vibe Coder generates 
          a complete, production-ready application in real-time with the power of AI.
        </p>
        
        <div className="flex flex-wrap justify-center gap-8 mb-16">
          <div className="flex items-center space-x-3 text-blue-300 bg-white/10 px-6 py-3 rounded-full backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all duration-300 group">
            <Rocket className="w-6 h-6 group-hover:scale-110 transition-transform duration-300" />
            <span className="font-medium">Lightning Fast</span>
          </div>
          <div className="flex items-center space-x-3 text-blue-300 bg-white/10 px-6 py-3 rounded-full backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all duration-300 group">
            <Star className="w-6 h-6 group-hover:scale-110 transition-transform duration-300" />
            <span className="font-medium">Production Ready</span>
          </div>
          <div className="flex items-center space-x-3 text-blue-300 bg-white/10 px-6 py-3 rounded-full backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all duration-300 group">
            <Zap className="w-6 h-6 group-hover:scale-110 transition-transform duration-300" />
            <span className="font-medium">AI Powered</span>
          </div>
        </div>

        <div className="flex justify-center">
          <div className="flex items-center space-x-2 text-blue-200 animate-bounce">
            <span className="text-lg font-medium">Start building below</span>
            <ArrowRight className="w-5 h-5" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
