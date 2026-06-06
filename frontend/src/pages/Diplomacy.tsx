// frontend/src/pages/Diplomacy.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Handshake, MessageSquare, ShieldCheck, Heart, AlertTriangle } from "lucide-react";

interface Empire {
  empire_id: string;
  empire_name: string;
  capital_world: string;
  population: number;
  gdp: number;
  power_index: number;
  colonies_count: number;
}

interface PeaceTreaty {
  treaty_id: string;
  war_id: string;
  signer_a: string;
  signer_b: string;
  terms: string;
  reparations_credits: number;
  year: number;
}

export const Diplomacy: React.FC = () => {
  const [empires, setEmpires] = useState<Empire[]>([]);
  const [treaties, setTreaties] = useState<PeaceTreaty[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getEmpires(20),
      api.getPeaceTreaties()
    ])
      .then(([empData, treatyData]) => {
        setEmpires(empData);
        setTreaties(treatyData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading diplomatic data:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-xl text-center font-mono text-[#06b6d4] animate-pulse">
        ESTABLISHING SECURE MULTI-LATERAL TRANSCEIVER FREQUENCIES...
      </div>
    );
  }

  // Define some mock alliances or relationship details based on actual empires in SQLite
  const allianceList = empires.slice(0, 3).map((emp, idx) => {
    const targets = ["Vesperan Covenant", "Solari Coalition", "Thranian Coalition", "Cygnian Union"];
    const target = targets[(idx + 1) % targets.length];
    return {
      alliance_name: `Grand Axis of ${emp.empire_name.split(" ")[0]}`,
      member_a: emp.empire_name,
      member_b: target,
      defense_pact: true,
      stability: 95.2 - idx * 4
    };
  });

  return (
    <div className="space-y-6 text-xs font-mono text-[#e0e6ed]">
      {/* HUD Overview Banner */}
      <div className="flex items-center gap-3 bg-[#8b5cf6]/10 border border-[#8b5cf6]/30 p-4 rounded-xl">
        <Handshake className="w-5 h-5 text-purple-400 animate-bounce" />
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Galactic Assembly Command Deck</h2>
          <p className="text-[10px] text-gray-400 mt-0.5">Sovereignty accords, non-aggression treaties, and coalition security logs.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Coalitions & Alliances */}
        <div className="glass-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <h3 className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider mb-4 flex items-center gap-1.5 border-b border-white/5 pb-2">
              <ShieldCheck className="w-4 h-4" /> Active Defense Alliances
            </h3>

            <div className="space-y-4">
              {allianceList.map((all, idx) => (
                <div key={idx} className="bg-black/20 p-4 rounded border border-white/5 space-y-2">
                  <div className="flex justify-between items-center text-[10px] text-white font-extrabold uppercase">
                    <span>{all.alliance_name}</span>
                    <span className="text-emerald-400 font-normal">Active</span>
                  </div>
                  <div className="text-[9px] text-gray-400 leading-normal">
                    Alliance bound between <strong className="text-white">{all.member_a}</strong> and <strong className="text-white">{all.member_b}</strong>.
                  </div>
                  <div className="flex justify-between items-center text-[8px] text-gray-500 pt-1 border-t border-white/5">
                    <span>DEFENSE PACT: YES</span>
                    <span className="text-[#06b6d4]">COHESION STABILITY: {all.stability.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Accords & Treaties Ledger */}
        <div className="glass-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <h3 className="text-[10px] font-bold text-[#ec4899] uppercase tracking-wider mb-4 flex items-center gap-1.5 border-b border-white/5 pb-2">
              <MessageSquare className="w-4 h-4" /> Peace Treaties & Accords Ledger
            </h3>

            {treaties.length === 0 ? (
              <div className="space-y-3">
                {/* Fallback mock records if peace_treaties is empty in database */}
                <div className="border-l-2 border-emerald-400 bg-emerald-500/5 p-3.5 rounded">
                  <div className="flex justify-between font-bold text-white text-[10px]">
                    <span>Treaty of Centauri Sector</span>
                    <span>Year 154,203</span>
                  </div>
                  <p className="text-gray-400 text-[9px] mt-1 font-sans">
                    Agreed White Peace and demilitarized shipping corridor buffer zone between Zelis Worlds and Valan Union.
                  </p>
                  <p className="text-[8px] text-emerald-400 font-bold mt-1 uppercase">Reparations: 50,000,000 Credits</p>
                </div>

                <div className="border-l-2 border-emerald-400 bg-emerald-500/5 p-3.5 rounded">
                  <div className="flex justify-between font-bold text-white text-[10px]">
                    <span>Accord of Orion-bulgis Gate</span>
                    <span>Year 292,928</span>
                  </div>
                  <p className="text-gray-400 text-[9px] mt-1 font-sans">
                    Established open-border jump gate network agreements, removing FTL tolls for merchant convoys.
                  </p>
                  <p className="text-[8px] text-emerald-400 font-bold mt-1 uppercase">Reparations: None</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {treaties.map((t, idx) => (
                  <div key={idx} className="border-l-2 border-emerald-400 bg-emerald-500/5 p-3.5 rounded">
                    <div className="flex justify-between font-bold text-white text-[10px]">
                      <span>Treaty #{t.treaty_id}</span>
                      <span>Year {t.year}</span>
                    </div>
                    <p className="text-gray-300 text-[9px] mt-1 font-sans">
                      {t.terms}
                    </p>
                    <p className="text-[8px] text-emerald-400 font-bold mt-1 uppercase">
                      Reparations: {t.reparations_credits.toLocaleString()} Credits
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Diplomatic Relationship Scoring Matrix */}
      <div className="glass-panel p-5 rounded-xl">
        <h3 className="text-[10px] font-bold text-yellow-500 uppercase tracking-wider mb-4 flex items-center gap-1.5 border-b border-white/5 pb-2">
          <Heart className="w-4 h-4 text-red-500" /> Empire Tension Matrix (Score 0-100)
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {empires.slice(0, 6).map((emp, idx) => {
            const relationshipScore = Math.round(85 - idx * 11);
            const status = relationshipScore >= 70 ? "FRIENDLY / PACT" : 
                           relationshipScore >= 45 ? "NEUTRAL / COLD" : "WAR ALERT / HOSTILE";
            const colorClass = relationshipScore >= 70 ? "text-green-400" :
                               relationshipScore >= 45 ? "text-yellow-400" : "text-red-500 animate-pulse";

            return (
              <div key={idx} className="bg-black/20 p-4 rounded border border-white/5 space-y-2">
                <span className="text-white font-extrabold block truncate">{emp.empire_name}</span>
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-gray-500">Tension Index:</span>
                  <span className={`${colorClass} font-bold`}>{relationshipScore}/100</span>
                </div>
                <div className="text-[8px] text-gray-500 uppercase font-mono tracking-wider pt-1 border-t border-white/5 flex items-center justify-between">
                  <span>STATUS: {status}</span>
                  {relationshipScore < 45 && <AlertTriangle className="w-3.5 h-3.5 text-red-500 animate-pulse" />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
export default Diplomacy;
