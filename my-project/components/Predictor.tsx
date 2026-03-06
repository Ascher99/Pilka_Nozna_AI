"use client";
import { useMemo, useState } from "react";
import { LEAGUES } from "@/data/teams";
import { predictFastAPI } from "@/lib/api";
import { USE_MOCK } from "@/lib/config";
import type { PredictOut, FormMatch } from "@/types/predict";

function FormBar({ form }: { form?: FormMatch[] }) {
  if (!form || form.length === 0) return <span className="text-xs text-gray-500">Brak danych</span>;

  return (
    <div className="flex gap-1.5">
      {form.map((match, i) => {
        let color = "bg-gray-600";
        if (match.result === "W") color = "bg-green-500";
        if (match.result === "L") color = "bg-red-500";
        
        return (
          <div
            key={i}
            className={`group relative w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow-sm cursor-help ${color}`}
          >
            {match.result}
            <div className="absolute bottom-full mb-2 hidden group-hover:block w-max bg-gray-900/90 backdrop-blur-sm text-white text-xs px-3 py-1.5 rounded-lg shadow-xl border border-gray-700 z-50">
              {match.score}
              <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 border-r border-b border-gray-700 rotate-45"></div>
            </div>
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
  
  return new Promise(resolve => setTimeout(() => resolve({ 
    label: home > away ? "home" : "away", 
    probs: { home, draw, away },
    home_form: [
      { result: "W", score: `${home_team} 2 - 0 Rywal` },
      { result: "D", score: `${home_team} 1 - 1 Rywal` },
      { result: "W", score: `Rywal 0 - 3 ${home_team}` },
      { result: "L", score: `${home_team} 0 - 1 Rywal` },
      { result: "W", score: `Rywal 1 - 2 ${home_team}` },
    ],
    away_form: [
      { result: "L", score: `${away_team} 0 - 2 Rywal` },
      { result: "L", score: `Rywal 3 - 0 ${away_team}` },
      { result: "D", score: `${away_team} 1 - 1 Rywal` },
      { result: "W", score: `Rywal 1 - 2 ${away_team}` },
      { result: "L", score: `${away_team} 0 - 1 Rywal` },
    ],
    home_stats: { avg_goals: 2.4, avg_points: 2.1 },
    away_stats: { avg_goals: 1.2, avg_points: 1.0 },
    home_table: { rank: 3, points: 55, gd: 24, mp: 28 },
    away_table: { rank: 11, points: 34, gd: -5, mp: 28 }
  }), 800));
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
    <div className="space-y-6 max-w-4xl mx-auto">
      <form onSubmit={onSubmit} className="bg-gray-800 text-gray-100 rounded-2xl shadow-xl p-6 md:p-8 space-y-6 border border-gray-700">
        <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-gray-700 pb-4 gap-4">
          <div>
            <h2 className="text-2xl font-extrabold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
              Panel Analityczny
            </h2>
            <p className="text-sm text-gray-400 mt-1">Skonfiguruj parametry spotkania do predykcji</p>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer hover:text-gray-200 transition bg-gray-900 px-3 py-2 rounded-lg border border-gray-700">
            <input
              type="checkbox"
              checked={useMock}
              onChange={(e) => setUseMock(e.target.checked)}
              className="accent-blue-500 w-4 h-4"
            />
            Użyj lokalnego środowiska (Mock)
          </label>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <div className="space-y-2">
            <label className="text-xs uppercase tracking-wider text-gray-400 font-semibold">Rozgrywki</label>
            <select
              className="w-full rounded-lg border border-gray-600 bg-gray-900 p-3 focus:ring-2 focus:ring-blue-500 outline-none transition shadow-inner"
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
              className="w-full rounded-lg border border-gray-600 bg-gray-900 p-3 focus:ring-2 focus:ring-blue-500 outline-none transition shadow-inner"
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
              className="w-full rounded-lg border border-gray-600 bg-gray-900 p-3 focus:ring-2 focus:ring-blue-500 outline-none transition shadow-inner"
              value={away}
              onChange={(e) => setAway(e.target.value)}
              disabled={loading}
            >
              {filteredAway.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
        </div>

        <button
          className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-lg hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-900/30 flex justify-center items-center gap-2"
          disabled={loading || home === away}
        >
          {loading ? (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : "Generuj Predykcję AI"}
        </button>

        {error && (
          <div className="rounded-lg bg-red-900/20 border border-red-500/50 p-4 text-sm text-red-200 text-center animate-pulse">
            {error}
          </div>
        )}
      </form>

      {loading && !result && (
        <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700 space-y-6 animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/4"></div>
          <div className="h-24 bg-gray-700 rounded w-full"></div>
          <div className="h-6 bg-gray-700 rounded w-1/3"></div>
          <div className="space-y-3">
             <div className="h-4 bg-gray-700 rounded w-full"></div>
             <div className="h-4 bg-gray-700 rounded w-full"></div>
             <div className="h-4 bg-gray-700 rounded w-full"></div>
          </div>
        </div>
      )}

      {result && !loading && (
        <div className="bg-gray-800 text-gray-100 rounded-2xl shadow-xl border border-gray-700 overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          <div className="bg-gray-900/50 p-6 border-b border-gray-700 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h3 className="text-xl font-bold flex items-center gap-2">
                 Raport Meczu
              </h3>
              <p className="text-sm text-gray-400 mt-1">{home} vs {away}</p>
            </div>
          </div>

          <div className="p-6 space-y-8">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-700 shadow-inner">
                <h4 className="text-center font-bold text-gray-300 border-b border-gray-700 pb-2 mb-3">Gospodarze</h4>
                <div className="flex justify-center mb-4"><FormBar form={result.home_form} /></div>
                {result.home_stats && (
                  <div className="grid grid-cols-2 gap-2 text-center">
                    <div className="bg-gray-800 p-2 rounded">
                      <p className="text-xs text-gray-400">Śr. bramek (ostatnie 5)</p>
                      <p className="font-bold text-blue-400">{result.home_stats.avg_goals}</p>
                    </div>
                    <div className="bg-gray-800 p-2 rounded">
                      <p className="text-xs text-gray-400">Śr. punktów (ostatnie 5)</p>
                      <p className="font-bold text-green-400">{result.home_stats.avg_points}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-gray-900 rounded-xl p-4 border border-gray-700 shadow-inner">
                <h4 className="text-center font-bold text-gray-300 border-b border-gray-700 pb-2 mb-3">Goście</h4>
                <div className="flex justify-center mb-4"><FormBar form={result.away_form} /></div>
                {result.away_stats && (
                  <div className="grid grid-cols-2 gap-2 text-center">
                    <div className="bg-gray-800 p-2 rounded">
                      <p className="text-xs text-gray-400">Śr. bramek (ostatnie 5)</p>
                      <p className="font-bold text-blue-400">{result.away_stats.avg_goals}</p>
                    </div>
                    <div className="bg-gray-800 p-2 rounded">
                      <p className="text-xs text-gray-400">Śr. punktów (ostatnie 5)</p>
                      <p className="font-bold text-green-400">{result.away_stats.avg_points}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {(result.home_table || result.away_table) && (
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-700 shadow-inner">
                <h4 className="font-bold text-gray-300 mb-4 flex items-center justify-between">
                  <span>Pozycje w tabeli ligowej</span>
                  <span className="text-xs font-normal text-gray-400 bg-gray-800 px-2 py-1 rounded">Aktualizacja na żywo</span>
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left text-gray-400">
                    <thead className="text-xs text-gray-500 uppercase bg-gray-800 rounded-t-lg">
                      <tr>
                        <th className="px-4 py-3 rounded-tl-lg">Poz</th>
                        <th className="px-4 py-3">Drużyna</th>
                        <th className="px-4 py-3 text-center">M</th>
                        <th className="px-4 py-3 text-center">Bilans</th>
                        <th className="px-4 py-3 text-center rounded-tr-lg">Pkt</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.home_table && (
                        <tr className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                          <td className="px-4 py-3 font-bold text-gray-300">{result.home_table.rank}</td>
                          <td className="px-4 py-3 font-bold text-blue-400">{home}</td>
                          <td className="px-4 py-3 text-center">{result.home_table.mp}</td>
                          <td className="px-4 py-3 text-center">{result.home_table.gd > 0 ? `+${result.home_table.gd}` : result.home_table.gd}</td>
                          <td className="px-4 py-3 text-center font-bold text-white">{result.home_table.points}</td>
                        </tr>
                      )}
                      {result.away_table && (
                        <tr className="hover:bg-gray-800/50 transition-colors">
                          <td className="px-4 py-3 font-bold text-gray-300">{result.away_table.rank}</td>
                          <td className="px-4 py-3 font-bold text-indigo-400">{away}</td>
                          <td className="px-4 py-3 text-center">{result.away_table.mp}</td>
                          <td className="px-4 py-3 text-center">{result.away_table.gd > 0 ? `+${result.away_table.gd}` : result.away_table.gd}</td>
                          <td className="px-4 py-3 text-center font-bold text-white">{result.away_table.points}</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div>
              <h4 className="font-semibold text-lg mb-4 flex items-center justify-between">
                <span>Wektory Prawdopodobieństw</span>

              </h4>
              <div className="space-y-5">
                {(["home", "draw", "away"] as const).map((k) => {
                  const probability = Math.round(result.probs[k] * 100);
                  const isWinner = result.label === k;
                  
                  return (
                    <div key={k} className={`group ${isWinner ? "opacity-100" : "opacity-75 hover:opacity-100 transition"}`}>
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className={isWinner ? "text-blue-400 font-bold uppercase tracking-wider" : "text-gray-300 uppercase tracking-wider"}>
                          {k === "home" ? `1 - ${home}` : k === "draw" ? "X - Remis" : `2 - ${away}`}
                        </span>
                        <span className="tabular-nums font-mono font-bold">{probability}%</span>
                      </div>
                      <div className="h-4 w-full rounded-full bg-gray-900 border border-gray-700 overflow-hidden">
                        <div
                          className={`h-full transition-all duration-1000 ease-out ${
                            isWinner ? "bg-gradient-to-r from-blue-500 to-indigo-500" : "bg-gray-600"
                          }`}
                          style={{ width: `${probability}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}