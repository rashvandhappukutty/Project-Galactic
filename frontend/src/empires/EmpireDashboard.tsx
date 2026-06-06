// frontend/src/components/EmpireDashboard.tsx
import React, { useEffect, useState } from "react";
import { Briefcase, Landmark, Shield, Users } from "lucide-react";

interface Empire {
  empire_id: string;
  empire_name: string;
  capital_world: string;
  population: number;
  gdp: number;
  power_index: number;
  colonies_count: number;
}

interface Chronicle {
  empire_name: string;
  origin_story: string;
  expansion_era: string;
  golden_age: string;
  major_wars: string;
  peak_influence: string;
  decline: string;
  legacy: string;
}

interface Lifecycle {
  status: string;
  year: number;
  description: string;
}

export const EmpireDashboard: React.FC = () => {
  const [empires, setEmpires] = useState<Empire[]>([]);
  const [selectedEmpire, setSelectedEmpire] = useState<Empire | null>(null);
  const [chronicle, setChronicle] = useState<Chronicle | null>(null);
  const [lifecycles, setLifecycles] = useState<Lifecycle[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/empires")
      .then((res) => res.json())
      .then((data) => {
        setEmpires(data);
        if (data.length > 0) setSelectedEmpire(data[0]);
      })
      .catch((err) => console.error("Error loading empires:", err));
  }, []);

  useEffect(() => {
    if (!selectedEmpire) return;

    // Load Chronicle
    fetch(`http://localhost:8000/api/chronicles?empire_name=${encodeURIComponent(selectedEmpire.empire_name)}`)
      .then((res) => res.json())
      .then((data) => setChronicle(data[0] || null))
      .catch((err) => console.error("Error loading chronicles:", err));

    // Load Lifecycles
    fetch(`http://localhost:8000/api/lifecycles?empire_name=${encodeURIComponent(selectedEmpire.empire_name)}`)
      .then((res) => res.json())
      .then((data) => setLifecycles(data))
      .catch((err) => console.error("Error loading lifecycles:", err));
  }, [selectedEmpire]);

  const filteredEmpires = empires.filter((e) =>
    e.empire_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="glass-panel p-6 rounded-xl grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-[500px]">
      
      {/* Sidebar - List of Empires */}
      <div className="lg:border-r border-white/10 pr-4 flex flex-col h-full max-h-[500px]">
        <h3 className="text-lg font-bold text-white mb-3 tracking-wide">Galactic Empires</h3>
        <input
          type="text"
          placeholder="Search empires..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-space-dark border border-white/10 text-white rounded p-1.5 text-xs font-mono mb-4 w-full focus:outline-none focus:border-blue-500"
        />
        <div className="overflow-y-auto flex-1 space-y-1">
          {filteredEmpires.map((e) => (
            <button
              key={e.empire_id}
              onClick={() => setSelectedEmpire(e)}
              className={`w-full text-left p-2 rounded text-xs font-mono transition ${
                selectedEmpire?.empire_id === e.empire_id
                  ? "bg-blue-500/20 text-blue-400 border-l-2 border-blue-500"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              {e.empire_name}
            </button>
          ))}
        </div>
      </div>

      {/* Main Details Panel */}
      {selectedEmpire && (
        <div className="lg:col-span-2 space-y-6 overflow-y-auto max-h-[500px] pr-2">
          
          {/* Empire Header */}
          <div className="flex justify-between items-start border-b border-white/10 pb-3">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-wide">{selectedEmpire.empire_name}</h2>
              <p className="text-xs text-gray-400 font-mono mt-0.5">Capital: {selectedEmpire.capital_world}</p>
            </div>
            <span className="text-xs font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded">
              Index: {selectedEmpire.power_index.toFixed(2)}
            </span>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-space-dark/60 p-3 rounded-lg border border-white/5 flex items-center gap-3">
              <Users className="w-5 h-5 text-blue-400" />
              <div>
                <p className="text-[10px] text-gray-400 font-mono">Population</p>
                <p className="text-sm font-bold text-white font-mono">{(selectedEmpire.population / 1e9).toFixed(1)}B</p>
              </div>
            </div>
            <div className="bg-space-dark/60 p-3 rounded-lg border border-white/5 flex items-center gap-3">
              <Briefcase className="w-5 h-5 text-yellow-400" />
              <div>
                <p className="text-[10px] text-gray-400 font-mono">GDP</p>
                <p className="text-sm font-bold text-white font-mono">{(selectedEmpire.gdp / 1e9).toFixed(1)}B</p>
              </div>
            </div>
            <div className="bg-space-dark/60 p-3 rounded-lg border border-white/5 flex items-center gap-3">
              <Landmark className="w-5 h-5 text-purple-400" />
              <div>
                <p className="text-[10px] text-gray-400 font-mono">Colonies</p>
                <p className="text-sm font-bold text-white font-mono">{selectedEmpire.colonies_count}</p>
              </div>
            </div>
            <div className="bg-space-dark/60 p-3 rounded-lg border border-white/5 flex items-center gap-3">
              <Shield className="w-5 h-5 text-red-400" />
              <div>
                <p className="text-[10px] text-gray-400 font-mono">Power index</p>
                <p className="text-sm font-bold text-white font-mono">{selectedEmpire.power_index.toFixed(1)}</p>
              </div>
            </div>
          </div>

          {/* Lifecycle Transitions Timeline */}
          {lifecycles.length > 0 && (
            <div className="bg-space-dark/30 p-4 rounded-lg border border-white/5">
              <h3 className="text-xs font-bold text-yellow-400 uppercase tracking-wider mb-3 font-mono">Historical Lifecycle Transitions</h3>
              <div className="space-y-3 pl-2 border-l border-white/10">
                {lifecycles.map((l, idx) => (
                  <div key={idx} className="relative pl-4">
                    <div className="absolute -left-[18px] top-1 w-2.5 h-2.5 rounded-full bg-blue-500 border-2 border-space-dark" />
                    <span className="text-[10px] text-gray-500 font-mono">Year {l.year}</span>
                    <span className="ml-2 px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[9px] font-mono uppercase border border-blue-500/20">
                      {l.status}
                    </span>
                    <p className="text-xs text-gray-300 mt-1 font-sans">{l.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chronicles Narrative */}
          {chronicle && (
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider font-mono">Empire Chronicles</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-sans">
                <div className="bg-space-dark/20 p-3 rounded border border-white/5">
                  <p className="text-blue-300 font-bold mb-1">Origin Story</p>
                  <p className="text-gray-400">{chronicle.origin_story}</p>
                </div>
                <div className="bg-space-dark/20 p-3 rounded border border-white/5">
                  <p className="text-blue-300 font-bold mb-1">Expansion Era</p>
                  <p className="text-gray-400">{chronicle.expansion_era}</p>
                </div>
                <div className="bg-space-dark/20 p-3 rounded border border-white/5">
                  <p className="text-blue-300 font-bold mb-1">Golden Age</p>
                  <p className="text-gray-400">{chronicle.golden_age}</p>
                </div>
                <div className="bg-space-dark/20 p-3 rounded border border-white/5">
                  <p className="text-blue-300 font-bold mb-1">Major Conflicts</p>
                  <p className="text-gray-400">{chronicle.major_wars}</p>
                </div>
                <div className="bg-space-dark/20 p-3 rounded border border-white/5 md:col-span-2">
                  <p className="text-blue-300 font-bold mb-1">Peak Hegemony & Decline</p>
                  <p className="text-gray-400">{chronicle.peak_influence} {chronicle.decline}</p>
                </div>
                <div className="bg-space-dark/20 p-3 rounded border border-white/5 md:col-span-2">
                  <p className="text-blue-300 font-bold mb-1">Legacy</p>
                  <p className="text-gray-400">{chronicle.legacy}</p>
                </div>
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
};
