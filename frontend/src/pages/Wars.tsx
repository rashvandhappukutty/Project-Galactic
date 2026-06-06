// frontend/src/pages/Wars.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Flame, ShieldAlert, Swords } from "lucide-react";

interface WarReport {
  participants: string;
  cause: string;
  timeline: string;
  casualties: string;
  outcome: string;
  historical_impact: string;
}

interface Battle {
  battle_id: string;
  war_id: string;
  battle_type: string;
  location_star_id: string;
  attacker_id: string;
  defender_id: string;
  attacker_fleet_power: number;
  defender_fleet_power: number;
  casualties: number;
  fleet_losses_attacker: number;
  fleet_losses_defender: number;
  winner_id: string;
  year: number;
}

export const Wars: React.FC = () => {
  const [reports, setReports] = useState<WarReport[]>([]);
  const [battles, setBattles] = useState<Battle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getWarReports(50),
      api.getBattles(50)
    ])
      .then(([reportData, battleData]) => {
        setReports(reportData);
        setBattles(battleData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading conflict telemetry:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-xl text-center font-mono text-red-500 animate-pulse">
        COLLECTING WEAPONS TELEMETRY AND CASUALTY LOGS...
      </div>
    );
  }

  return (
    <div className="space-y-6 text-xs font-mono text-[#e0e6ed]">
      {/* Overview Block */}
      <div className="flex justify-between items-center bg-red-500/10 border border-red-500/30 p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center gap-3">
          <Flame className="w-5 h-5 text-red-500 animate-pulse" />
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Strategic War Room Command</h2>
            <p className="text-[10px] text-gray-400 mt-0.5">Fleet movements, planetary invasions, skirmish casualties, and military peace covenants.</p>
          </div>
        </div>
        <div className="text-[10px] text-red-500 bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded animate-pulse font-bold tracking-widest uppercase">
          DEFCON LEVEL: ACTIVE THREAT
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Sidebar / Column: War Reports */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <h3 className="text-[10px] font-bold text-red-400 uppercase tracking-wider mb-4 flex items-center gap-1.5 border-b border-white/5 pb-2">
              <Swords className="w-4 h-4" /> Historical Conflict Chronicles
            </h3>

            {reports.length === 0 ? (
              <div className="space-y-3">
                {/* Fallback war records if reports table is empty in SQLite */}
                <div className="bg-black/20 p-4 rounded border border-white/5 space-y-2">
                  <div className="flex justify-between font-bold text-white text-[10px]">
                    <span>Orion Hegemony vs Alpha Coalition</span>
                    <span className="text-red-400 animate-pulse">Armistice</span>
                  </div>
                  <div className="space-y-1 text-[9px] text-gray-300">
                    <p><strong>Cause:</strong> Jump Gate Toll Disputes</p>
                    <p><strong>Casualties:</strong> 1.5 Billion organic lives</p>
                    <p><strong>Outcome:</strong> White Peace signed in Centauri Sector</p>
                  </div>
                </div>

                <div className="bg-black/20 p-4 rounded border border-white/5 space-y-2">
                  <div className="flex justify-between font-bold text-white text-[10px]">
                    <span>Cygnian Crusade</span>
                    <span className="text-red-400">Empire Victory</span>
                  </div>
                  <div className="space-y-1 text-[9px] text-gray-300">
                    <p><strong>Cause:</strong> Border Sector Annexation</p>
                    <p><strong>Casualties:</strong> 8.2 Billion organic lives</p>
                    <p><strong>Outcome:</strong> Demilitarized buffer zones established</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {reports.map((rep, idx) => (
                  <div key={idx} className="bg-black/20 p-4 rounded border border-white/5 space-y-2">
                    <div className="flex justify-between font-bold text-white text-[10px]">
                      <span>{rep.participants}</span>
                      <span className="text-red-400 font-bold uppercase">{rep.outcome}</span>
                    </div>
                    <div className="space-y-1 text-[9px] text-gray-300">
                      <p><strong>Cause:</strong> {rep.cause}</p>
                      <p><strong>Casualties:</strong> {rep.casualties} Lives</p>
                      <p><strong>Historical Impact:</strong> {rep.historical_impact}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Battles & Skirmish Telemetry */}
        <div className="glass-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <h3 className="text-[10px] font-bold text-yellow-500 uppercase tracking-wider mb-4 flex items-center gap-1.5 border-b border-white/5 pb-2">
              <ShieldAlert className="w-4 h-4" /> Battles & Ship Loss Reports
            </h3>

            {battles.length === 0 ? (
              <div className="space-y-3">
                {/* Fallback mock battle records */}
                <div className="bg-black/20 p-3.5 rounded border border-white/5 space-y-2">
                  <div className="flex justify-between text-[10px] text-white font-extrabold uppercase">
                    <span>Siege of Solari Prime</span>
                    <span className="text-red-500">Year 15,202</span>
                  </div>
                  <div className="space-y-1 text-[9px] text-gray-400 font-sans">
                    <p><strong>Type:</strong> Planet Invasion</p>
                    <p><strong>Casualties:</strong> 42M lives lost</p>
                    <p><strong>Fleet Power Attacker:</strong> 12,000 index</p>
                    <p><strong>Fleet Power Defender:</strong> 8,200 index</p>
                  </div>
                  <span className="text-[8px] bg-red-500/10 text-red-500 px-1 py-0.5 rounded uppercase font-mono font-bold block text-center mt-2">
                    WINNER: ATTACKING COALITION
                  </span>
                </div>

                <div className="bg-black/20 p-3.5 rounded border border-white/5 space-y-2">
                  <div className="flex justify-between text-[10px] text-white font-extrabold uppercase">
                    <span>Skirmish at Vega Junction</span>
                    <span className="text-red-500">Year 244,375</span>
                  </div>
                  <div className="space-y-1 text-[9px] text-gray-400 font-sans">
                    <p><strong>Type:</strong> Gate Interception</p>
                    <p><strong>Casualties:</strong> 1.5M lives lost</p>
                    <p><strong>Fleet Power Attacker:</strong> 4,500 index</p>
                    <p><strong>Fleet Power Defender:</strong> 5,100 index</p>
                  </div>
                  <span className="text-[8px] bg-purple-500/10 text-purple-400 px-1 py-0.5 rounded uppercase font-mono font-bold block text-center mt-2">
                    WINNER: DEFENDING REGIMENT
                  </span>
                </div>
              </div>
            ) : (
              <div className="space-y-3 overflow-y-auto max-h-[400px]">
                {battles.map((b, idx) => (
                  <div key={idx} className="bg-black/20 p-3.5 rounded border border-white/5 space-y-2">
                    <div className="flex justify-between text-[10px] text-white font-extrabold uppercase">
                      <span>Battle #{b.battle_id}</span>
                      <span className="text-red-500">Yr {b.year}</span>
                    </div>
                    <div className="space-y-1 text-[9px] text-gray-400 font-sans">
                      <p><strong>Type:</strong> {b.battle_type}</p>
                      <p><strong>Casualties:</strong> {b.casualties.toLocaleString()} Lives</p>
                      <p><strong>Attacker Power:</strong> {b.attacker_fleet_power.toLocaleString()}</p>
                      <p><strong>Defender Power:</strong> {b.defender_fleet_power.toLocaleString()}</p>
                      <p><strong>Attacker Loss:</strong> {b.fleet_losses_attacker} ships</p>
                      <p><strong>Defender Loss:</strong> {b.fleet_losses_defender} ships</p>
                    </div>
                    <span className="text-[8px] bg-red-500/10 text-red-500 px-1 py-0.5 rounded uppercase font-mono font-bold block text-center mt-2">
                      WINNER: {b.winner_id}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default Wars;
