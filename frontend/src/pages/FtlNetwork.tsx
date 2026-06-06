// frontend/src/pages/FtlNetwork.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Search, GitMerge, AlertCircle, Star, Anchor } from "lucide-react";

interface JumpGate {
  gate_id: string;
  star_id: string;
  star_name: string;
  stability: number;
  capacity: number;
  status: string;
}

interface Wormhole {
  wormhole_id: string;
  wormhole_type: string;
  stability_type: string;
  entry_system: string;
  exit_system: string;
  distance_reduction: number;
  stability: number;
  capacity: number;
  owner_empire: string;
}

export const FtlNetwork: React.FC = () => {
  const [gates, setGates] = useState<JumpGate[]>([]);
  const [wormholes, setWormholes] = useState<Wormhole[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState<"gates" | "wormholes">("gates");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    Promise.all([
      api.getJumpGates(100),
      api.getWormholes()
    ])
      .then(([gateData, wormholeData]) => {
        setGates(gateData);
        setWormholes(wormholeData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading FTL networks:", err);
        setLoading(false);
      });
  }, []);

  const filteredGates = gates.filter((g) =>
    g.star_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    g.gate_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredWormholes = wormholes.filter((w) =>
    w.wormhole_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    w.entry_system.toLowerCase().includes(searchQuery.toLowerCase()) ||
    w.exit_system.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 text-xs font-mono text-[#e0e6ed]">
      {/* HUD Header */}
      <div className="flex justify-between items-center bg-[#0b1026]/70 border border-[#06b6d4]/20 p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <GitMerge className="w-5 h-5 text-cyan-400 animate-pulse" />
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">FTL GATEWAY & WORMHOLE DIAGNOSTICS</h2>
            <p className="text-[10px] text-gray-500 mt-0.5">Tactical sub-space corridors status, coordinate bindings, and gateway stability indexes.</p>
          </div>
        </div>

        {/* Sub-tab selection */}
        <div className="flex bg-black/40 border border-white/10 rounded p-1 text-[10px] gap-2">
          <button
            onClick={() => { setActiveSubTab("gates"); setSearchQuery(""); }}
            className={`px-3 py-1 rounded transition uppercase ${
              activeSubTab === "gates" 
                ? "bg-[#06b6d4]/20 text-[#06b6d4] font-bold" 
                : "text-gray-400 hover:text-white"
            }`}
          >
            Jump Gates ({gates.length})
          </button>
          <button
            onClick={() => { setActiveSubTab("wormholes"); setSearchQuery(""); }}
            className={`px-3 py-1 rounded transition uppercase ${
              activeSubTab === "wormholes" 
                ? "bg-[#ec4899]/20 text-[#ec4899] font-bold" 
                : "text-gray-400 hover:text-white"
            }`}
          >
            Wormholes ({wormholes.length})
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <input
          type="text"
          placeholder={activeSubTab === "gates" ? "SEARCH JUMP GATES..." : "SEARCH WORMHOLES..."}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-black/40 border border-[#06b6d4]/20 rounded p-2 pl-8 text-[10px] text-white focus:outline-none focus:border-[#06b6d4] uppercase"
        />
        <Search className="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" />
      </div>

      {loading ? (
        <div className="glass-panel p-10 rounded-xl text-center text-gray-500 animate-pulse">
          INTERCEPING SUB-SPACE FREQUENCY CHANNELS...
        </div>
      ) : activeSubTab === "gates" ? (
        /* Jump Gates Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {filteredGates.map((gate, idx) => (
            <div key={idx} className="bg-[#0b1026]/80 border border-[#06b6d4]/15 p-4 rounded-lg flex flex-col justify-between hover:border-[#06b6d4]/40 hover:shadow-lg transition">
              <div className="space-y-2">
                <div className="flex justify-between items-center border-b border-white/5 pb-1">
                  <span className="text-cyan-400 font-bold uppercase tracking-wider text-[10px]">
                    {gate.star_name} GATE
                  </span>
                  <span className={`text-[8px] px-1.5 py-0.5 rounded font-bold uppercase ${
                    gate.status === "Operational" ? "bg-green-500/10 text-green-400" : "bg-yellow-500/10 text-yellow-500"
                  }`}>
                    {gate.status}
                  </span>
                </div>

                <div className="space-y-1 text-[10px] text-gray-300">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Stability:</span>
                    <span className="text-white font-extrabold">{gate.stability.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Toll Capacity:</span>
                    <span className="text-white">{(gate.capacity / 1e3).toFixed(1)}K Ships</span>
                  </div>
                </div>
              </div>

              {/* Stability progress bar */}
              <div className="mt-3 w-full bg-black/40 h-1 rounded-full overflow-hidden border border-white/5">
                <div 
                  className="bg-cyan-400 h-full rounded-full"
                  style={{ width: `${gate.stability}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Wormholes Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {filteredWormholes.map((worm, idx) => {
            const stabPercentage = Math.round(worm.stability * 100);
            return (
              <div key={idx} className="bg-[#0b1026]/80 border border-[#ec4899]/15 p-4 rounded-lg flex flex-col justify-between hover:border-[#ec4899]/40 hover:shadow-lg transition">
                <div className="space-y-2">
                  <div className="flex justify-between items-center border-b border-white/5 pb-1">
                    <span className="text-[#ec4899] font-bold uppercase tracking-wider text-[10px]">
                      {worm.wormhole_id}
                    </span>
                    <span className={`text-[8px] px-1.5 py-0.5 rounded font-bold uppercase ${
                      worm.stability_type === "Stable" ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400 animate-pulse"
                    }`}>
                      {worm.stability_type}
                    </span>
                  </div>

                  <div className="space-y-1.5 text-[9px] text-gray-300 font-mono">
                    <div className="flex items-center gap-1">
                      <Star className="w-3 h-3 text-cyan-400 shrink-0" />
                      <span className="text-gray-500">Entry:</span>
                      <span className="text-white truncate">Civ #{worm.entry_system.slice(0, 8)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Anchor className="w-3 h-3 text-purple-400 shrink-0" />
                      <span className="text-gray-500">Exit:</span>
                      <span className="text-white truncate">Civ #{worm.exit_system.slice(0, 8)}</span>
                    </div>
                    <div className="flex justify-between mt-1 border-t border-white/5 pt-1">
                      <span className="text-gray-500">Stability Index:</span>
                      <span className="text-white font-bold">{stabPercentage}%</span>
                    </div>
                  </div>
                </div>

                {/* Stability bar */}
                <div className="mt-3 w-full bg-black/40 h-1 rounded-full overflow-hidden border border-white/5">
                  <div 
                    className="bg-[#ec4899] h-full rounded-full"
                    style={{ width: `${stabPercentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tech warning bulletin */}
      <div className="bg-[#0b1026] border border-red-500/15 p-4 rounded-lg flex gap-3 items-start">
        <AlertCircle className="w-4 h-4 text-red-400 shrink-0 animate-ping mt-0.5" />
        <div className="space-y-1 text-[10px] text-gray-400 font-sans leading-relaxed">
          <strong className="text-red-400 font-mono uppercase">Unstable Sub-space Warning:</strong> Wormholes marked as <span className="text-red-400 font-bold font-mono">Unstable</span> exhibit critical energy fluctuations. Freighters must verify stabilization fields before warping to prevent immediate cargo dissolution.
        </div>
      </div>
    </div>
  );
};
export default FtlNetwork;
