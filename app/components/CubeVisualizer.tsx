import React from 'react';
import { CubeState, Color, RobotStatus } from '../types';
import { COLORS, SOLVED_STATE } from '../constants';

interface CubeVisualizerProps {
  state: CubeState | null;
  status: RobotStatus;
}

const FaceGrid: React.FC<{ colors: Color[] }> = ({ colors }) => (
  <div className="grid grid-cols-3 gap-1 p-1 bg-black h-full w-full border border-black rounded-sm">
    {colors.map((c, i) => (
      <div 
        key={i} 
        className="w-full h-full rounded-[2px] transition-colors duration-500 shadow-inner"
        style={{ 
          backgroundColor: COLORS[c],
          boxShadow: `inset 0 0 10px rgba(0,0,0,0.2)`
        }} 
      />
    ))}
  </div>
);

export const CubeVisualizer: React.FC<CubeVisualizerProps> = ({ state, status }) => {
  const displayState = state || SOLVED_STATE;

  // CSS for the 3D cube assembly
  const size = 180; // Size of one face in px
  const translate = size / 2;

  // We are creating a "net" view for simplicity as a pure CSS 3D rotatable cube 
  // without Three.js requires complex state management for rotation.
  // Instead, let's make an isometric-like 3D CSS object that rotates slowly.

  return (
    <div className="perspective-[1000px] w-full h-96 flex items-center justify-center overflow-visible">
      <div className={`relative w-[180px] h-[180px] transform-style-3d animate-slow-spin ${status === 'solving' ? 'animate-fast-spin' : ''}`}>
        
        {/* Front Face */}
        <div className="absolute inset-0 backface-hidden" style={{ transform: `translateZ(${translate}px)` }}>
          <FaceGrid colors={displayState.F} />
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
             <span className="text-black/50 font-bold text-4xl select-none opacity-20">F</span>
          </div>
        </div>

        {/* Back Face */}
        <div className="absolute inset-0 backface-hidden" style={{ transform: `rotateY(180deg) translateZ(${translate}px)` }}>
          <FaceGrid colors={displayState.B} />
           <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
             <span className="text-black/50 font-bold text-4xl select-none opacity-20">B</span>
          </div>
        </div>

        {/* Right Face */}
        <div className="absolute inset-0 backface-hidden" style={{ transform: `rotateY(90deg) translateZ(${translate}px)` }}>
          <FaceGrid colors={displayState.R} />
           <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
             <span className="text-black/50 font-bold text-4xl select-none opacity-20">R</span>
          </div>
        </div>

        {/* Left Face */}
        <div className="absolute inset-0 backface-hidden" style={{ transform: `rotateY(-90deg) translateZ(${translate}px)` }}>
          <FaceGrid colors={displayState.L} />
           <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
             <span className="text-black/50 font-bold text-4xl select-none opacity-20">L</span>
          </div>
        </div>

        {/* Top Face (Up) */}
        <div className="absolute inset-0 backface-hidden" style={{ transform: `rotateX(90deg) translateZ(${translate}px)` }}>
          <FaceGrid colors={displayState.U} />
           <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
             <span className="text-black/50 font-bold text-4xl select-none opacity-20">U</span>
          </div>
        </div>

        {/* Bottom Face (Down) */}
        <div className="absolute inset-0 backface-hidden" style={{ transform: `rotateX(-90deg) translateZ(${translate}px)` }}>
          <FaceGrid colors={displayState.D} />
           <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
             <span className="text-black/50 font-bold text-4xl select-none opacity-20">D</span>
          </div>
        </div>

      </div>

      <style jsx>{`
        .transform-style-3d {
          transform-style: preserve-3d;
        }
        .backface-hidden {
          backface-visibility: hidden; /* Or visible if we want to see inside */
          /* Actually for a solid cube, hidden is okay if the walls are solid, but transparency helps debug */
          backface-visibility: visible; 
          background: black;
        }
        @keyframes spin {
          0% { transform: rotateX(-20deg) rotateY(0deg); }
          100% { transform: rotateX(-20deg) rotateY(360deg); }
        }
        @keyframes fastSpin {
          0% { transform: rotateX(-20deg) rotateY(0deg); }
          100% { transform: rotateX(-20deg) rotateY(360deg); }
        }
        .animate-slow-spin {
          animation: spin 20s linear infinite;
        }
        .animate-fast-spin {
          animation: fastSpin 2s linear infinite;
        }
      `}</style>
    </div>
  );
};