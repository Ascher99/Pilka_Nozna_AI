// app/api/predict/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { home_team = "", away_team = "" } = await request.json();
  const seed = (home_team.length * 13 + away_team.length * 7) % 100;
  const home = 0.42 + (seed % 10) / 100;
  const away = 0.25 + ((seed + 3) % 10) / 100;
  const draw = Math.max(0, 1 - home - away);
  const probs = { home, draw, away };
  const label = home >= draw && home >= away ? "home" : draw >= away ? "draw" : "away";
  return NextResponse.json({ label, probs });
}
