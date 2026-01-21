export type RobotStatus = 'idle' | 'detecting' | 'solving' | 'scrambling' | 'error';

export type Color = 'W' | 'Y' | 'G' | 'B' | 'O' | 'R' | 'X'; // X for unknown/scanning

export interface CubeState {
  // Representation of the 6 faces.
  // Standard order often used: U, R, F, D, L, B
  // Each face is a 9-char string or array of colors
  U: Color[];
  R: Color[];
  F: Color[];
  D: Color[];
  L: Color[];
  B: Color[];
}

export interface SolveResult {
  success: boolean;
  moves: number;
  finalState: CubeState;
}

export interface LogEntry {
  id: string;
  timestamp: Date;
  message: string;
  type: 'info' | 'success' | 'error' | 'warning';
}

export interface ApiError {
  message: string;
  code: number;
}