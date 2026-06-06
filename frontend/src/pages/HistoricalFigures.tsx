// frontend/src/pages/HistoricalFigures.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Search, Award, Star, BookOpen, Compass, Landmark } from "lucide-react";

interface Figure {
  name: string;
  civilization: string;
  role: string;
  achievements: string;
  legacy_score: number;
}

export const HistoricalFigures: React.FC = () => {
  const [figures, setFigures] = useState<Figure[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedFigure, setSelectedFigure] = useState<Figure | null>(null);

  useEffect(() => {
    api.getFigures(150)
      .then((data) => {
        setFigures(data);
        if (data.length > 0) setSelectedFigure(data[0]);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading historical figures:", err);
        setLoading(false);
      });
  }, []);

  const filteredFigures = figures.filter((f) =>
    f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.civilization.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="glass-panel p-6 rounded-xl grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-[500px] text-xs font-mono text-[#e0e6ed]">
      {/* Sidebar - List of Figures */}
      <div className="lg:border-r border-white/10 pr-4 flex flex-col h-full max-h-[500px]">
        <div className="flex items-center gap-2 mb-3">
          <Award className="w-4 h-4 text-yellow-500 animate-pulse" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Pantheon of Legends</h3>
        </div>
        <div className="relative mb-4">
          <input
            type="text"
            placeholder="FILTER BY HERO OR CIVILIZATION..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/40 border border-[#06b6d4]/20 rounded p-2 pl-8 text-[10px] text-white focus:outline-none focus:border-[#06b6d4] uppercase"
          />
          <Search className="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" />
        </div>

        {loading ? (
          <div className="text-center py-10 text-gray-500 animate-pulse">QUERYING ANCESTRAL LEGACY GRIDS...</div>
        ) : filteredFigures.length === 0 ? (
          <div className="text-center py-10 text-gray-600">NO HEROES MATCH COGNITIVE PARAMETERS.</div>
        ) : (
          <div className="overflow-y-auto flex-1 space-y-1 pr-1 scrollbar-hide">
            {filteredFigures.map((f, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedFigure(f)}
                className={`w-full text-left p-2.5 rounded transition relative group flex justify-between items-center ${
                  selectedFigure?.name === f.name
                    ? "bg-yellow-500/10 text-white border-l-2 border-yellow-500"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <div className="flex flex-col gap-0.5 truncate">
                  <span className="font-bold text-white truncate text-[10px]">{f.name}</span>
                  <span className="text-[8px] text-gray-500 truncate uppercase">{f.role}</span>
                </div>
                <span className="text-[8px] bg-white/5 px-1 py-0.5 rounded text-yellow-500 font-bold shrink-0">
                  {f.legacy_score} / 100
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Details Panel */}
      {selectedFigure ? (
        <div className="lg:col-span-2 space-y-6 overflow-y-auto max-h-[500px] pr-2 scrollbar-hide">
          {/* Header */}
          <div className="flex justify-between items-start border-b border-[#06b6d4]/10 pb-4">
            <div>
              <h2 className="text-xl font-bold text-white uppercase tracking-widest">{selectedFigure.name}</h2>
              <p className="text-[10px] text-gray-500 uppercase mt-0.5">
                Affiliation: <span className="text-blue-400 font-bold">{selectedFigure.civilization}</span>
              </p>
            </div>
            <div className="px-2.5 py-1 rounded bg-yellow-500/10 border border-yellow-500/30 text-[9px] text-yellow-500 font-bold tracking-widest uppercase flex items-center gap-1">
              <Star className="w-3.5 h-3.5 text-yellow-500 shrink-0 fill-yellow-500" /> LEGACY SCORE: {selectedFigure.legacy_score}
            </div>
          </div>

          {/* Quick Metrics Info */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Compass className="w-5 h-5 text-cyan-400 shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Assembly Role Assignment</p>
                <p className="text-xs font-extrabold text-white mt-0.5 uppercase">{selectedFigure.role}</p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Landmark className="w-5 h-5 text-indigo-400 shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Sovereignty Domain</p>
                <p className="text-xs font-extrabold text-white mt-0.5 uppercase truncate max-w-[150px]">{selectedFigure.civilization}</p>
              </div>
            </div>
          </div>

          {/* Chronicle Dossier Achievements */}
          <div className="bg-black/30 p-5 rounded-lg border border-yellow-500/15 space-y-3">
            <h3 className="text-[9px] font-bold text-yellow-500 uppercase tracking-widest flex items-center gap-1.5">
              <BookOpen className="w-4 h-4" /> LEGENDARY CONVENING & ACHIEVEMENTS
            </h3>
            <p className="text-xs text-gray-300 font-sans leading-relaxed">
              {selectedFigure.achievements}
            </p>
          </div>

          <div className="bg-[#0b1026] border border-yellow-500/10 p-3.5 rounded text-[10px] text-gray-400 leading-normal font-sans">
            <strong className="text-yellow-400 font-mono uppercase">Assembly Chronicler Note:</strong> Legacy scores are evaluated automatically based on military defense ratios, technological breakthrough vectors, and diplomatic treaty stability indices.
          </div>
        </div>
      ) : (
        <div className="lg:col-span-2 flex items-center justify-center text-gray-500">
          SELECT A HISTORICAL LEGEND TO HARVEST INDIVIDUAL ACHIEVEMENTS
        </div>
      )}
    </div>
  );
};
export default HistoricalFigures;
