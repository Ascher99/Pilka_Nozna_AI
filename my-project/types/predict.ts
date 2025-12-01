export type PredictIn = { league_id: string; home_team: string; away_team: string };

export type PredictOut = {
  label: "home" | "draw" | "away";
  probs: { home: number; draw: number; away: number };
  home_form?: string[];
  away_form?: string[];
};