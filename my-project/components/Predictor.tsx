"use client";
import { useMemo, useState } from "react";
import { LEAGUES } from "@/data/teams";
import { predictFastAPI } from "@/lib/api";
import { USE_MOCK, API_BASE } from "@/lib/config";
import type { PredictOut } from "@/types/predict";

function FormBar({ form }: { form?: string[] }) {
  if (!form || form.length === 0) return <span className="text-xs text-gray-500">Brak danych</span>;

  return (
    <div className="flex gap-1">
      {form.map((res, i) => {
        let color = "bg-gray-600";
        if (res === "W") color = "bg-green-500";
        if (res === "L") color = "bg-red-500";
        
        return (
          <div
            key={i}
            className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white ${color}`}
            title={res === "W" ? "Wygrana" : res === "L" ? "Przegrana" : "Remis"}
          >
            {res}
          </div>
        );
      })}
    </div>
  );
}

async function mockPredict(home_team: string, away_team: string): Promise<PredictOut> {
  const seed = (home_team.length * 13 + away_team.length * 7) % 100;
  const home = 0.4 + (seed % 10) / 100;
  const away = 0.25 + ((seed + 3) % 10) / 100;
  const draw = Math.max(0, 1 - home - away);
  return { 
    label: home > away ? "home" : "away", 
    probs: { home, draw, away },
    home_form: ["W", "D", "W", "L", "W"],
    away_form: ["L", "L", "D", "W", "L"]
  };
}

export default function Predictor() {
  const [leagueId, setLeagueId] = useState(LEAGUES[0].id);
  const league = useMemo(() => LEAGUES.find(l => l.id === leagueId)!, [leagueId]);

  const [home, setHome] = useState(league.teams[0]);
  const [away, setAway] = useState(league.teams.find(t => t !== league.teams[0]) || league.teams[0]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [useMock, setUseMock] = useState<boolean>(USE_MOCK);

  const teams = league.teams;
  const filteredAway = useMemo(() => teams.filter(t => t !== home), [teams, home]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    try {

      const body = { league_id: leagueId, home_team: home, away_team: away };
      
      const data = useMock ? await mockPredict(home, away) : await predictFastAPI(body);
      setResult(data);
    } catch (err: any) {
      setError(err?.message || "Błąd zapytania do API");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Formularz */}
      <form onSubmit={onSubmit} className="bg-gray-800 text-gray-100 rounded-2xl shadow-lg p-6 space-y-5 border border-gray-700">
        <div className="flex items-center justify-between border-b border-gray-700 pb-3">
          <h2 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            Football AI
          </h2>
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer hover:text-gray-200 transition">
            <input
              type="checkbox"
              checked={useMock}
              onChange={(e) => setUseMock(e.target.checked)}
              className="accent-blue-500"
            />
            Tryb Mock
          </label>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <div className="space-y-2">
            <label className="text-xs uppercase tracking-wider text-gray-400 font-semibold">Liga</label>
            <select
              className="w-full rounded-lg border border-gray-600 bg-gray-900 p-3 focus:ring-2 focus:ring-blue-500 outline-none transition"
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

          <div className="space-y-2">
            <label className="text-xs uppercase tracking-wider text-gray-400 font-semibold">Gospodarz</label>
            <select
              className="w-full rounded-lg border border-gray-600 bg-gray-900 p-3 focus:ring-2 focus:ring-blue-500 outline-none transition"
              value={home}
              onChange={(e) => setHome(e.target.value)}
              disabled={loading}
            >
              {teams.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-xs uppercase tracking-wider text-gray-400 font-semibold">Gość</label>
            <select
              className="w-full rounded-lg border border-gray-600 bg-gray-900 p-3 focus:ring-2 focus:ring-blue-500 outline-none transition"
              value={away}
              onChange={(e) => setAway(e.target.value)}
              disabled={loading}
            >
              {filteredAway.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
        </div>

        <button
          className="w-full py-3 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-lg shadow-blue-900/20"
          disabled={loading || home === away}
        >
          {loading ? "Analizuję dane..." : "Oblicz prawdopodobieństwo"}
        </button>

        {error && (
          <div className="rounded-lg bg-red-900/20 border border-red-500/50 p-3 text-sm text-red-200 text-center">
            {error}
          </div>
        )}
      </form>

      {/* Wyniki */}
      {result && (
        <div className="bg-gray-800 text-gray-100 rounded-2xl shadow-lg p-6 border border-gray-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* Sekcja Formy */}
          <div className="grid grid-cols-2 gap-4 mb-6 pb-6 border-b border-gray-700">
            <div className="flex flex-col items-center space-y-2">
              <span className="text-sm text-gray-400 font-medium">Forma Gospodarzy</span>
              <FormBar form={result.home_form} />
            </div>
            <div className="flex flex-col items-center space-y-2">
              <span className="text-sm text-gray-400 font-medium">Forma Gości</span>
              <FormBar form={result.away_form} />
            </div>
          </div>

          <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
            📊 Prognoza AI
            <span className="text-xs font-normal text-gray-400 ml-auto">Ostatnie 5 meczów ma kluczowy wpływ</span>
          </h3>
          
          <div className="space-y-4">
            {(["home", "draw", "away"] as const).map((k) => {
              const probability = Math.round(result.probs[k] * 100);
              const isWinner = result.label === k;
              
              return (
                <div key={k} className={`group ${isWinner ? "opacity-100" : "opacity-70 hover:opacity-100 transition"}`}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={isWinner ? "text-blue-400 font-bold" : "text-gray-300"}>
                      {k === "home" ? "Gospodarze" : k === "draw" ? "Remis" : "Goście"}
                    </span>
                    <span className="tabular-nums font-mono">{probability}%</span>
                  </div>
                  <div className="h-3 w-full rounded-full bg-gray-700 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-1000 ease-out ${
                        isWinner ? "bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]" : "bg-gray-500"
                      }`}
                      style={{ width: `${probability}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}