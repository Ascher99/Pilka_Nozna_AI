"use client";
import { useMemo, useState } from "react";
import { LEAGUES } from "@/data/teams";
import { predictFastAPI } from "@/lib/api";
import { USE_MOCK, API_BASE } from "@/lib/config";
import type { PredictOut } from "@/types/predict";

async function mockPredict(home_team: string, away_team: string): Promise<PredictOut> {
  const seed = (home_team.length * 13 + away_team.length * 7) % 100;
  const home = 0.4 + (seed % 10) / 100;
  const away = 0.25 + ((seed + 3) % 10) / 100;
  const draw = Math.max(0, 1 - home - away);
  const probs = { home, draw, away };
  const label = home >= draw && home >= away ? "home" : draw >= away ? "draw" : "away";
  return { label, probs };
}

export default function Predictor() {
  const [leagueId, setLeagueId] = useState(LEAGUES[0].id);
  const league = useMemo(() => LEAGUES.find(l => l.id === leagueId)!, [leagueId]);

  const [home, setHome] = useState(league.teams[0]);
  const [away, setAway] = useState(league.teams.find(t => t !== league.teams[0]) || league.teams[0]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [useMock, setUseMock] = useState<boolean>(USE_MOCK); // start z .env

  const teams = league.teams;
  const filteredAway = useMemo(() => teams.filter(t => t !== home), [teams, home]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const body = { home_team: home, away_team: away };
      const data = useMock ? await mockPredict(home, away) : await predictFastAPI(body);
      setResult(data);
    } catch (err: any) {
      setError(err?.message || "Błąd zapytania do API");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={onSubmit} className="bg-gray-800 text-gray-100 rounded-2xl shadow p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Football Predictor MVP</h2>
          <div className="flex items-center gap-3 text-xs text-gray-300">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={useMock}
                onChange={(e) => setUseMock(e.target.checked)}
              />
              Użyj mock backend
            </label>
            {!useMock && <span className="opacity-80">API: {API_BASE}/api/predict</span>}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="block text-sm font-medium mb-1">Liga</label>
            <select
              className="w-full rounded-xl border border-gray-700 bg-gray-900 p-2"
              value={leagueId}
              onChange={(e) => {
                const id = e.target.value;
                const l = LEAGUES.find(x => x.id === id)!;
                setLeagueId(id);
                setHome(l.teams[0]);
                setAway(l.teams.find(t => t !== l.teams[0]) || l.teams[0]);
              }}
              disabled={loading}
            >
              {LEAGUES.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Gospodarz</label>
            <select
              className="w-full rounded-xl border border-gray-700 bg-gray-900 p-2"
              value={home}
              onChange={(e) => setHome(e.target.value)}
              disabled={loading}
            >
              {teams.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Goście</label>
            <select
              className="w-full rounded-xl border border-gray-700 bg-gray-900 p-2"
              value={away}
              onChange={(e) => setAway(e.target.value)}
              disabled={loading}
            >
              {filteredAway.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
        </div>

        <button
          className="px-4 py-2 rounded-xl bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50"
          disabled={loading || home === away}
        >
          {loading ? "Liczenie..." : "Przewiduj"}
        </button>

        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
            {error}
          </div>
        )}
      </form>

      <div className="bg-gray-800 text-gray-100 rounded-2xl shadow p-5">
        <h3 className="font-semibold">Wynik predykcji</h3>
        {!result && <p className="mt-2 text-sm text-gray-300">Brak danych. Uruchom predykcję.</p>}
        {result && (
          <div className="mt-3 space-y-3">
            {(["home", "draw", "away"] as const).map((k) => (
              <div key={k}>
                <div className="flex justify-between text-sm">
                  <span>{k === "home" ? "Gospodarze" : k === "draw" ? "Remis" : "Goście"}</span>
                  <span className="tabular-nums">{Math.round(result.probs[k] * 100)}%</span>
                </div>
                <div className="mt-1 h-2 w-full rounded-full bg-gray-700">
                  <div
                    className="h-2 rounded-full bg-gray-100"
                    style={{ width: `${Math.round(result.probs[k] * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
