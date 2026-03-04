export type PredictIn = { 
  league_id: string; 
  home_team: string; 
  away_team: string 
};

export type TeamStats = {
  avg_goals: number;
  avg_points: number;
};

export type FormMatch = {
  result: string;
  score: string;
};

export type TablePos = {
  rank: number;
  points: number;
  gd: number; 
  mp: number; 
};

export type PredictOut = {
  label: "home" | "draw" | "away";
  probs: { home: number; draw: number; away: number };
  home_form?: FormMatch[]; 
  away_form?: FormMatch[]; 
  home_stats?: TeamStats;
  away_stats?: TeamStats;
  home_table?: TablePos; 
  away_table?: TablePos; 
};