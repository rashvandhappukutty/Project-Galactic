// frontend/src/pages/Civilizations.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Search, Landmark, Zap, Cpu, Calendar, Compass } from "lucide-react";

interface Civilization {
  civilization_id: string;
  name: string;
  species: string | Record<string, any>;
  planet_id: string;
  tech_level: number;
  energy_source: string;
  government_type: string;
  civilization_age: number;
}

export const Civilizations: React.FC = () => {
  const [civs, setCivs] = useState<Civilization[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCiv, setSelectedCiv] = useState<Civilization | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCivilizations(100)
      .then((data) => {
        setCivs(data);
        if (data.length > 0) setSelectedCiv(data[0]);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching civilizations:", err);
        setLoading(false);
      });
  }, []);

  const filteredCivs = civs.filter((c) =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Helper to resolve species name from serialized string/object
  const getSpeciesName = (speciesData: any) => {
    if (!speciesData) return "Unknown Organic";
    if (typeof speciesData === "string") {
      try {
        const parsed = JSON.parse(speciesData.replace(/'/g, '"'));
        return parsed.name || parsed.species_name || "Organic Genus";
      } catch {
        // Strip string regex format if not clean JSON
        const match = speciesData.match(/'name':\s*'([^']+)'/);
        return match ? match[1] : "Organic Genus";
      }
    }
    return speciesData.name || "Organic Genus";
  };

  const getKardashevScale = (tech: number) => {
    const scale = (tech / 100) * 2.2;
    return `Type ${scale.toFixed(2)}`;
  };

  return (
    <div className="glass-panel p-6 rounded-xl grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-[500px] text-xs font-mono text-[#e0e6ed]">
      {/* Sidebar - List of Civilizations */}
      <div className="lg:border-r border-white/10 pr-4 flex flex-col h-full max-h-[500px]">
        <div className="flex items-center gap-2 mb-3">
          <Landmark className="w-4 h-4 text-indigo-400 animate-pulse" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Civilization Register</h3>
        </div>
        <div className="relative mb-4">
          <input
            type="text"
            placeholder="FILTER SOCIO-COGNITIVE NODES..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/40 border border-[#06b6d4]/20 rounded p-2 pl-8 text-[10px] text-white focus:outline-none focus:border-[#06b6d4] uppercase"
          />
          <Search className="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" />
        </div>

        {loading ? (
          <div className="text-center py-10 text-gray-500 animate-pulse">EXTRACTING COLONY PATTERNS...</div>
        ) : filteredCivs.length === 0 ? (
          <div className="text-center py-10 text-gray-600">NO CIVILIZATIONS DETECTED IN INDEX.</div>
        ) : (
          <div className="overflow-y-auto flex-1 space-y-1 pr-1 scrollbar-hide">
            {filteredCivs.map((c) => (
              <button
                key={c.civilization_id}
                onClick={() => setSelectedCiv(c)}
                className={`w-full text-left p-2.5 rounded transition relative group flex justify-between items-center ${
                  selectedCiv?.civilization_id === c.civilization_id
                    ? "bg-[#8b5cf6]/10 text-white border-l-2 border-[#8b5cf6]"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <span className="truncate max-w-[150px]">{c.name}</span>
                <span className="text-[8px] bg-white/5 px-1 py-0.5 rounded text-gray-400 font-bold">
                  {getKardashevScale(c.tech_level)}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Details Panel */}
      {selectedCiv ? (
        <div className="lg:col-span-2 space-y-6 overflow-y-auto max-h-[500px] pr-2 scrollbar-hide">
          {/* Civ Header */}
          <div className="flex justify-between items-start border-b border-[#06b6d4]/10 pb-4">
            <div>
              <h2 className="text-xl font-bold text-white uppercase tracking-widest">{selectedCiv.name}</h2>
              <p className="text-[10px] text-gray-500 uppercase mt-0.5">
                Primary Species Genus: <span className="text-[#ec4899] font-bold">{getSpeciesName(selectedCiv.species)}</span>
              </p>
            </div>
            <div className="px-2.5 py-1 rounded bg-[#8b5cf6]/10 border border-[#8b5cf6]/30 text-[9px] text-[#8b5cf6] font-bold tracking-widest uppercase">
              SECTOR ID: #{selectedCiv.civilization_id.slice(0, 8)}
            </div>
          </div>

          {/* Kardashev Scale Bar */}
          <div className="bg-black/30 p-5 rounded-lg border border-[#06b6d4]/10 space-y-3">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-gray-400 font-bold uppercase tracking-wider">Kardashev Progression Matrix</span>
              <span className="text-indigo-400 font-bold">{getKardashevScale(selectedCiv.tech_level)} (Level {selectedCiv.tech_level.toFixed(1)}/100)</span>
            </div>
            <div className="w-full bg-black/40 h-3 rounded-full overflow-hidden border border-white/5 p-0.5 relative">
              <div 
                className="bg-gradient-to-r from-blue-500 via-purple-500 to-[#ec4899] h-full rounded-full transition-all duration-1000 ease-out"
                style={{ width: `${selectedCiv.tech_level}%`, filter: "drop-shadow(0 0 4px rgba(139, 92, 246, 0.6))" }}
              />
            </div>
            <div className="flex justify-between text-[8px] text-gray-600 font-mono">
              <span>TYPE 0: PLANETARY ENERGY</span>
              <span>TYPE I: STELLAR HARVEST</span>
              <span>TYPE II: DYSON SPHERE COMPLETE</span>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Zap className="w-5 h-5 text-yellow-400 shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Energy Grid Catalyst</p>
                <p className="text-sm font-extrabold text-white mt-0.5 uppercase">{selectedCiv.energy_source}</p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Cpu className="w-5 h-5 text-teal-400 shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Societal Structure Regime</p>
                <p className="text-sm font-extrabold text-white mt-0.5 uppercase">{selectedCiv.government_type}</p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Calendar className="w-5 h-5 text-indigo-400 shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Chronological Era Age</p>
                <p className="text-sm font-extrabold text-white mt-0.5">{selectedCiv.civilization_age.toLocaleString()} Solar Cycles</p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Compass className="w-5 h-5 text-[#06b6d4] shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Central System Core</p>
                <p className="text-sm font-extrabold text-white mt-0.5">Planet Node #{selectedCiv.planet_id.slice(0, 8)}</p>
              </div>
            </div>
          </div>

          <div className="bg-[#0b1026] border border-blue-500/10 p-3.5 rounded text-[10px] text-gray-400 leading-normal font-sans">
            <strong className="text-blue-400 font-mono uppercase">Simulation Vector:</strong> This civilization has successfully harnessed <span className="text-white font-bold">{selectedCiv.energy_source}</span>. Societal stability index stands at 97.4%, making them a key player in hyperlane trade route alliances and planetary colony expansions.
          </div>
        </div>
      ) : (
        <div className="lg:col-span-2 flex items-center justify-center text-gray-500">
          SELECT A SOCIO-COGNITIVE SYSTEM NODE TO COMMENCE TELEMETRY HARVEST
        </div>
      )}
    </div>
  );
};
export default Civilizations;
