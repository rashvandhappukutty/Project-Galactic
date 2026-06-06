// frontend/src/components/AnalyticsCenter.tsx
import React, { useEffect, useState } from "react";
import { TrendingUp, Award, DollarSign, Star } from "lucide-react";

interface Figure {
  name: string;
  civilization: string;
  role: string;
  achievements: string;
  legacy_score: number;
}

interface EmpireRanking {
  empire_name: string;
  gdp: number;
  population: number;
}

export const AnalyticsCenter: React.FC = () => {
  const [figures, setFigures] = useState<Figure[]>([]);
  const [rankings, setRankings] = useState<EmpireRanking[]>([]);

  useEffect(() => {
    // Load top figures
    fetch("http://localhost:8000/api/figures?limit=50")
      .then((res) => res.json())
      .then((data) => setFigures(data))
      .catch((err) => console.error("Error loading figures:", err));

    // Load top GDP rankings
    fetch("http://localhost:8000/api/empires")
      .then((res) => res.json())
      .then((data: any[]) => {
        // Sort by GDP descending
        const sorted = [...data].sort((a, b) => b.gdp - a.gdp);
        setRankings(sorted.slice(0, 15));
      })
      .catch((err) => console.error("Error loading rankings:", err));
  }, []);

  return (
    <div className="glass-panel p-6 rounded-xl grid grid-cols-1 lg:grid-cols-2 gap-6 h-full min-h-[500px]">
      
      {/* Left Column - GDP Rankings */}
      <div className="lg:border-r border-white/10 pr-4 space-y-4 max-h-[500px] overflow-y-auto">
        <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-2 font-mono flex items-center gap-2">
          <TrendingUp className="w-4 h-4" /> Top Galactic GDP Rankings
        </h3>
        <div className="space-y-2">
          {rankings.map((r, idx) => (
            <div key={idx} className="flex items-center justify-between bg-space-dark/40 p-2.5 rounded border border-white/5 font-mono text-xs">
              <div className="flex items-center gap-3">
                <span className="text-gray-500 w-4 font-bold">{idx + 1}.</span>
                <span className="text-white font-bold">{r.empire_name}</span>
              </div>
              <div className="flex items-center gap-1 text-yellow-400 font-bold">
                <DollarSign className="w-3.5 h-3.5" />
                <span>{(r.gdp / 1e9).toFixed(1)}B</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Column - Historical Figures Catalog */}
      <div className="space-y-4 max-h-[500px] overflow-y-auto">
        <h3 className="text-sm font-bold text-yellow-400 uppercase tracking-wider mb-2 font-mono flex items-center gap-2">
          <Award className="w-4 h-4" /> Notable Historical Figures
        </h3>
        <div className="space-y-3">
          {figures.slice(0, 15).map((f, idx) => (
            <div key={idx} className="bg-space-dark/40 p-3 rounded-lg border border-white/5 font-sans text-xs">
              <div className="flex items-center justify-between border-b border-white/5 pb-1 mb-2">
                <div>
                  <span className="text-white font-bold text-sm">{f.name}</span>
                  <span className="ml-2 text-[10px] text-gray-500 font-mono">({f.role})</span>
                </div>
                <div className="flex items-center gap-1 text-yellow-500">
                  <Star className="w-3 h-3 fill-yellow-500" />
                  <span className="font-mono font-bold">{f.legacy_score}</span>
                </div>
              </div>
              <p className="text-gray-400 leading-relaxed"><strong className="text-blue-400 font-mono">Civilization:</strong> {f.civilization}</p>
              <p className="text-gray-400 leading-relaxed mt-1"><strong className="text-blue-400 font-mono">Achievement:</strong> {f.achievements}</p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
