import { CubeState, SolveResult } from '../types';
import { SOLVED_STATE, SCRAMBLED_STATE } from '../constants';

const API_BASE = 'http://localhost:8000'; // Default python server

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const detectCube = async (mock: boolean = false): Promise<CubeState> => {
  if (mock) {
    await delay(1500); // Simulate scanning
    return SCRAMBLED_STATE;
  }
  const res = await fetch(`${API_BASE}/detect`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to detect cube');
  return res.json();
};

export const solveCube = async (mock: boolean = false): Promise<SolveResult> => {
  if (mock) {
    await delay(3000); // Simulate processing
    return {
      success: true,
      moves: 21,
      finalState: SOLVED_STATE
    };
  }
  const res = await fetch(`${API_BASE}/solve`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to solve cube');
  return res.json();
};

export const scrambleCube = async (mock: boolean = false): Promise<CubeState> => {
  if (mock) {
    await delay(2000); // Simulate mechanics
    return SCRAMBLED_STATE;
  }
  const res = await fetch(`${API_BASE}/scramble`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to scramble cube');
  return res.json();
};

export const performMove = async (move: string, mock: boolean = false): Promise<void> => {
  if (mock) {
    await delay(300); 
    return;
  }
  const res = await fetch(`${API_BASE}/move`, { 
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ move }) 
  });
  if (!res.ok) throw new Error(`Failed to perform move ${move}`);
};

export const getInstructions = async (mock: boolean = false): Promise<string[]> => {
  if (mock) {
    return ["R", "U", "R'", "U'", "L'", "U", "L", "F", "U", "F'", "R2", "D", "R'", "U2", "R", "D'", "R'"];
  }
  const res = await fetch(`${API_BASE}/instructions`);
  if (!res.ok) throw new Error('Failed to get instructions');
  return res.json();
};