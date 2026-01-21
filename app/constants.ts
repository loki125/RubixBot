import { Color, CubeState } from './types';

export const COLORS: Record<Color, string> = {
  'W': '#f8fafc', // White (Slate-50)
  'Y': '#facc15', // Yellow (Yellow-400)
  'G': '#22c55e', // Green (Green-500)
  'B': '#3b82f6', // Blue (Blue-500)
  'O': '#f97316', // Orange (Orange-500)
  'R': '#ef4444', // Red (Red-500)
  'X': '#1e293b', // Unknown (Slate-800)
};

export const SOLVED_STATE: CubeState = {
  U: Array(9).fill('W'),
  D: Array(9).fill('Y'),
  F: Array(9).fill('G'),
  B: Array(9).fill('B'),
  L: Array(9).fill('O'),
  R: Array(9).fill('R'),
};

// A scrambled state for demo
export const SCRAMBLED_STATE: CubeState = {
  U: ['W','W','Y', 'W','W','B', 'R','R','R'] as Color[],
  R: ['R','R','O', 'R','R','W', 'G','G','G'] as Color[],
  F: ['G','G','W', 'G','G','R', 'Y','Y','Y'] as Color[],
  D: ['Y','Y','W', 'Y','Y','G', 'O','O','O'] as Color[],
  L: ['O','O','Y', 'O','O','B', 'B','B','B'] as Color[],
  B: ['B','B','R', 'B','B','O', 'W','W','W'] as Color[],
};