export type PredictIn = { home_team: string; away_team: string };
export type PredictOut = {
  label: "home" | "draw" | "away";
  probs: { home: number; draw: number; away: number };
};
