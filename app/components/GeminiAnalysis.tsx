import React, { useState } from 'react';
import { GoogleGenAI } from "@google/genai";
import { CubeState } from '../types';
import { Sparkles, BrainCircuit, Loader2 } from 'lucide-react';

interface GeminiAnalysisProps {
  cubeState: CubeState | null;
}

export const GeminiAnalysis: React.FC<GeminiAnalysisProps> = ({ cubeState }) => {
  const [analysis, setAnalysis] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!cubeState) return;
    if (!process.env.API_KEY) {
      setAnalysis("Error: No API Key configured for Gemini.");
      return;
    }

    setLoading(true);
    setAnalysis("");

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      // Convert state to string representation for the prompt
      const stateStr = JSON.stringify(cubeState);
      
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: `You are a Rubik's Cube expert robot. Here is the current state of a cube in JSON format representing the colors of the faces (U, D, F, B, L, R): ${stateStr}.
        
        Provide a very short, futuristic, robotic status report (max 2 sentences) estimating the entropy/difficulty of the scramble. Do not give the solution. End with a percentage of "Entropy Detected".`,
      });

      setAnalysis(response.text || "Analysis complete. No data returned.");
    } catch (error) {
      console.error(error);
      setAnalysis("System Malfunction: AI Neural Link failed.");
    } finally {
      setLoading(false);
    }
  };

  if (!cubeState) return null;

  return (
    <div className="flex flex-col gap-2">
       <button 
        onClick={handleAnalyze} 
        disabled={loading}
        className="text-xs flex items-center justify-between text-purple-400 hover:text-purple-300 transition-colors uppercase font-bold tracking-widest mb-1"
      >
        <span className="flex items-center gap-2">
           <BrainCircuit className="w-4 h-4" /> AI Neural Analysis
        </span>
        {loading && <Loader2 className="w-3 h-3 animate-spin" />}
      </button>
      
      <div className={`p-3 rounded border border-purple-500/20 bg-purple-500/5 min-h-[60px] text-xs font-mono text-purple-200 transition-all ${loading ? 'opacity-50' : 'opacity-100'}`}>
        {analysis ? (
           <p className="animate-in fade-in leading-relaxed">
             <span className="text-purple-500 mr-2">➜</span>
             {analysis}
           </p>
        ) : (
          <p className="text-purple-500/40 italic text-center py-2">
            Awaiting analysis request...
          </p>
        )}
      </div>
    </div>
  );
};