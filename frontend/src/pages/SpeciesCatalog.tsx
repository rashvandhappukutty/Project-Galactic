// frontend/src/pages/SpeciesCatalog.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Search, Dna, Heart, Brain, Compass, Users } from "lucide-react";

interface Species {
  species_id: string;
  name: string;
  planet_id: string;
  intelligence: number;
  cooperation: number;
  aggression: number;
  adaptability: number;
  lifespan: number;
  population: number;
}

export const SpeciesCatalog: React.FC = () => {
  const [speciesList, setSpeciesList] = useState<Species[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSpecies, setSelectedSpecies] = useState<Species | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSpecies(100)
      .then((data) => {
        setSpeciesList(data);
        if (data.length > 0) setSelectedSpecies(data[0]);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching species:", err);
        setLoading(false);
      });
  }, []);

  const filteredSpecies = speciesList.filter((s) =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Custom circular telemetry SVG progress bar
  const TelemetryCircle = ({ value, label, color }: { value: number; label: string; color: string }) => {
    const radius = 24;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (value / 100) * circumference;

    return (
      <div className="flex flex-col items-center gap-1">
        <div className="relative w-14 h-14 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background ring */}
            <circle
              cx="28"
              cy="28"
              r={radius}
              className="stroke-white/5 fill-none"
              strokeWidth="2.5"
            />
            {/* Active glowing ring */}
            <circle
              cx="28"
              cy="28"
              r={radius}
              className="fill-none transition-all duration-1000 ease-out"
              stroke={color}
              strokeWidth="2.5"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              style={{ filter: `drop-shadow(0 0 3px ${color}50)` }}
            />
          </svg>
          <span className="absolute text-[9px] font-bold text-white">{Math.round(value)}%</span>
        </div>
        <span className="text-[7px] text-gray-500 uppercase tracking-widest">{label}</span>
      </div>
    );
  };

  return (
    <div className="glass-panel p-6 rounded-xl grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-[500px] text-xs font-mono text-[#e0e6ed]">
      {/* Sidebar - List of Species */}
      <div className="lg:border-r border-white/10 pr-4 flex flex-col h-full max-h-[500px]">
        <div className="flex items-center gap-2 mb-3">
          <Dna className="w-4 h-4 text-[#ec4899] animate-pulse" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Bio-Genetic Registry</h3>
        </div>
        <div className="relative mb-4">
          <input
            type="text"
            placeholder="FILTER BY GENUS..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/40 border border-[#06b6d4]/20 rounded p-2 pl-8 text-[10px] text-white focus:outline-none focus:border-[#06b6d4] uppercase"
          />
          <Search className="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" />
        </div>

        {loading ? (
          <div className="text-center py-10 text-gray-500 animate-pulse">SYNAPSE CONNECTIONS LINKING...</div>
        ) : filteredSpecies.length === 0 ? (
          <div className="text-center py-10 text-gray-600">NO SPECIES ALIGN WITH PARAMETERS.</div>
        ) : (
          <div className="overflow-y-auto flex-1 space-y-1 pr-1 scrollbar-hide">
            {filteredSpecies.map((s) => (
              <button
                key={s.species_id}
                onClick={() => setSelectedSpecies(s)}
                className={`w-full text-left p-2.5 rounded transition relative group flex justify-between items-center ${
                  selectedSpecies?.species_id === s.species_id
                    ? "bg-[#ec4899]/10 text-white border-l-2 border-[#ec4899]"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <span>{s.name}</span>
                <span className="text-[9px] text-gray-600">Yr. {s.lifespan.toFixed(0)} Lifespan</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Details Panel */}
      {selectedSpecies ? (
        <div className="lg:col-span-2 space-y-6 overflow-y-auto max-h-[500px] pr-2 scrollbar-hide">
          {/* Genus Header */}
          <div className="flex justify-between items-start border-b border-[#06b6d4]/10 pb-4">
            <div>
              <h2 className="text-xl font-bold text-white uppercase tracking-widest">{selectedSpecies.name} GENUS</h2>
              <p className="text-[10px] text-gray-500 uppercase mt-0.5">Taxonomy Classification: Intelligent Organic Life</p>
            </div>
            <div className="px-2.5 py-1 rounded bg-[#ec4899]/10 border border-[#ec4899]/30 text-[9px] text-[#ec4899] font-bold tracking-widest uppercase">
              SPECIES ID: {selectedSpecies.species_id}
            </div>
          </div>

          {/* Telemetry Rings */}
          <div className="bg-black/30 p-5 rounded-lg border border-[#06b6d4]/10">
            <h3 className="text-[9px] font-bold text-[#06b6d4] uppercase tracking-widest mb-4">NEURAL & BEHAVIORAL MATRIX</h3>
            <div className="grid grid-cols-4 gap-4 justify-items-center">
              <TelemetryCircle value={selectedSpecies.intelligence} label="Intellect" color="#8b5cf6" />
              <TelemetryCircle value={selectedSpecies.cooperation} label="Cooperation" color="#06b6d4" />
              <TelemetryCircle value={selectedSpecies.aggression} label="Aggression" color="#ec4899" />
              <TelemetryCircle value={selectedSpecies.adaptability} label="Adaptability" color="#10b981" />
            </div>
          </div>

          {/* Bio Statistics dossiers */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Brain className="w-5 h-5 text-[#8b5cf6] shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Cognitive Threshold</p>
                <p className="text-sm font-extrabold text-white mt-0.5">
                  {selectedSpecies.intelligence >= 80 ? "SAPIENT HYPER-MIND" : 
                   selectedSpecies.intelligence >= 60 ? "HIGH COGNITIVE" : "SEMISAPIENT CORE"}
                </p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Compass className="w-5 h-5 text-[#06b6d4] shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Primary Habitat Anchor</p>
                <p className="text-sm font-extrabold text-white mt-0.5">Planet Node #{selectedSpecies.planet_id.slice(0,8)}</p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Heart className="w-5 h-5 text-[#ec4899] shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Average Life Expectancy</p>
                <p className="text-sm font-extrabold text-white mt-0.5">{selectedSpecies.lifespan.toFixed(1)} Cycles (Years)</p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Users className="w-5 h-5 text-[#10b981] shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Global Census Count</p>
                <p className="text-sm font-extrabold text-white mt-0.5">
                  {(selectedSpecies.population / 1e9).toFixed(2)} Billion Bodies
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#0b1026] border border-red-500/10 p-3.5 rounded text-[10px] text-gray-400 leading-normal font-sans">
            <strong className="text-red-400 font-mono uppercase">System Diagnostic:</strong> Neural scan reveals high synaptic adaptability. Species is fully compatible with neural-link telemetry implants and hyperlane transit shielding grids.
          </div>
        </div>
      ) : (
        <div className="lg:col-span-2 flex items-center justify-center text-gray-500">
          SELECT A SPECIES CLASS DOSSIER TO LOAD BIO-GENETIC TELEMETRY
        </div>
      )}
    </div>
  );
};
export default SpeciesCatalog;
