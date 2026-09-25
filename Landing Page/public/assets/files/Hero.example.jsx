'use client';

import React from 'react';
import StarfieldBackground from '@/components/effects/StarfieldBackground';
import RotatingEarth from '@/components/effects/RotatingEarth';

export default function Hero() {
  return (
    <section 
      id="home" 
      className="relative w-full h-screen overflow-hidden"
    >
      {/* Starfield Background - Fixed behind everything */}
      <StarfieldBackground />

      {/* Content Container */}
      <div className="relative z-10 w-full h-full flex items-center justify-center">
        <div className="max-w-7xl w-full mx-auto px-6">
          
          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center h-full">
            
            {/* Left Column - Text Content */}
            <div className="flex flex-col justify-center space-y-8">
              
              {/* Main Heading */}
              <div className="space-y-4">
                <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-tight">
                  Welcome to AeroGuard
                </h1>
                <p className="text-xl md:text-2xl text-blue-300">
                  AI-Powered Airport Safety
                </p>
              </div>

              {/* Description */}
              <p className="text-lg text-gray-300 max-w-lg leading-relaxed">
                Next-generation runway safety monitoring using advanced AI and real-time analytics. 
                Protect your operations with intelligent, always-vigilant security.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                
                {/* Primary Button */}
                <a
                  href="#features"
                  className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 text-center"
                >
                  Explore Features
                </a>

                {/* Secondary Button */}
                <a
                  href="#contact"
                  className="px-8 py-3 border-2 border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white font-semibold rounded-lg transition-all duration-300 text-center"
                >
                  Get Started
                </a>
              </div>

              {/* Stats Section */}
              <div className="grid grid-cols-3 gap-4 pt-8 border-t border-gray-700">
                <div>
                  <p className="text-3xl font-bold text-blue-400">99.9%</p>
                  <p className="text-sm text-gray-400">Uptime</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-blue-400">24/7</p>
                  <p className="text-sm text-gray-400">Monitoring</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-blue-400">Real-time</p>
                  <p className="text-sm text-gray-400">Alerts</p>
                </div>
              </div>
            </div>

            {/* Right Column - Rotating Earth */}
            <div className="hidden lg:flex items-center justify-center h-full">
              <div className="w-96 h-96 flex items-center justify-center">
                {/* Rotating Earth - Interactive Globe */}
                <RotatingEarth />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-20 animate-bounce">
        <svg
          className="w-6 h-6 text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 14l-7 7m0 0l-7-7m7 7V3"
          />
        </svg>
      </div>

      {/* Gradient Overlay (Optional) */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/30 pointer-events-none" />
    </section>
  );
}
