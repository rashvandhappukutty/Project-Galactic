// frontend/src/components/HistoryCenter.tsx
import React, { useEffect, useState } from "react";
import { Calendar, Search, Sparkles, Filter } from "lucide-react";

interface Event {
  event_id: string;
  year: number;
  timestamp: string;
  event_type: string;
  event_category: string;
  empire: string;
  participants: string;
  location: string;
  impact_score: number;
  historical_significance: string;
  description: string;
}

interface Era {
  era_name: string;
  start_year: number;
  end_year: number;
  dominant_empire: string;
  major_events: string;
}

export const HistoryCenter: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [eras, setEras] = useState<Era[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 50;

  const categories = ["Civilization", "Colonization", "Economy", "Logistics", "Military", "Diplomacy", "Espionage", "Science", "Crisis"];

  useEffect(() => {
    fetch("http://localhost:8000/api/eras")
      .then((res) => res.json())
      .then((data) => setEras(data))
      .catch((err) => console.error("Error loading eras:", err));
  }, []);

  useEffect(() => {
    const catQuery = selectedCategory ? `&category=${selectedCategory}` : "";
    fetch(`http://localhost:8000/api/history?limit=${limit}&offset=${offset}${catQuery}`)
      .then((res) => res.json())
      .then((data) => setEvents(data))
      .catch((err) => console.error("Error loading history:", err));
  }, [offset, selectedCategory]);

  const filteredEvents = events.filter((e) =>
    e.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.event_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="glass-panel p-6 rounded-xl grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-[500px]">
      
      {/* Sidebar - Era Classifications & Category Filters */}
      <div className="lg:border-r border-white/10 pr-4 space-y-6 max-h-[500px] overflow-y-auto">
        
        {/* Category Filter */}
        <div>
          <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-3 font-mono flex items-center gap-2">
            <Filter className="w-4 h-4" /> Filter by Category
          </h3>
          <div className="flex flex-wrap gap-1">
            <button
              onClick={() => { setSelectedCategory(""); setOffset(0); }}
              className={`px-2 py-1 rounded text-[10px] font-mono border transition ${
                selectedCategory === ""
                  ? "bg-blue-500/20 text-blue-400 border-blue-500/30"
                  : "bg-space-dark text-gray-400 border-white/5 hover:text-white"
              }`}
            >
              All Events
            </button>
            {categories.map((c) => (
              <button
                key={c}
                onClick={() => { setSelectedCategory(c); setOffset(0); }}
                className={`px-2 py-1 rounded text-[10px] font-mono border transition ${
                  selectedCategory === c
                    ? "bg-blue-500/20 text-blue-400 border-blue-500/30"
                    : "bg-space-dark text-gray-400 border-white/5 hover:text-white"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Era Logs */}
        <div>
          <h3 className="text-sm font-bold text-yellow-400 uppercase tracking-wider mb-3 font-mono flex items-center gap-2">
            <Sparkles className="w-4 h-4" /> Historical Epochs
          </h3>
          <div className="space-y-3">
            {eras.map((era, idx) => (
              <div key={idx} className="bg-space-dark/40 p-3 rounded border border-white/5 text-xs">
                <p className="text-yellow-400 font-bold font-mono">{era.era_name}</p>
                <p className="text-[10px] text-gray-500 font-mono mt-0.5">Year {era.start_year} - {era.end_year}</p>
                <p className="text-gray-400 mt-1 text-[11px] font-sans">Dominant Power: <span className="text-white">{era.dominant_empire}</span></p>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Main Timeline Stream */}
      <div className="lg:col-span-2 flex flex-col h-full max-h-[500px]">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-2 border-b border-white/10 pb-3 mb-4">
          <h2 className="text-xl font-bold text-white tracking-wide">Galactic History Log</h2>
          <div className="relative w-full sm:w-64">
            <input
              type="text"
              placeholder="Search historical events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-space-dark border border-white/10 text-white rounded p-1.5 text-xs font-mono w-full pl-8 focus:outline-none focus:border-blue-500"
            />
            <Search className="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" />
          </div>
        </div>

        {/* Vertical Timeline List */}
        <div className="overflow-y-auto flex-1 space-y-4 pr-2 pl-2">
          {filteredEvents.map((e) => (
            <div key={e.event_id} className="relative pl-6 border-l border-white/5 p-2 bg-space-dark/10 rounded-lg hover:bg-space-dark/30 border border-white/5 transition">
              <div className="absolute -left-[6px] top-4 w-2.5 h-2.5 rounded-full bg-blue-500/80 border-2 border-space-dark" />
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-yellow-400 font-mono flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> Year {e.year}
                </span>
                <span className="text-[9px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20 px-1.5 py-0.25 rounded uppercase">
                  {e.event_category}
                </span>
              </div>
              <p className="text-xs text-white font-bold mt-1">{e.event_type}</p>
              <p className="text-xs text-gray-400 mt-1 font-sans">{e.description}</p>
              {e.impact_score > 0 && (
                <div className="mt-2 flex items-center gap-2 text-[9px] font-mono">
                  <span className="text-blue-400">Impact Score: {e.impact_score}</span>
                  <span className="text-gray-500">|</span>
                  <span className="text-yellow-400">Significance: {e.historical_significance}</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Pagination Controls */}
        <div className="flex justify-between items-center mt-4 border-t border-white/10 pt-3">
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="px-3 py-1.5 bg-space-dark border border-white/10 rounded text-xs font-mono hover:bg-white/5 disabled:opacity-30 disabled:pointer-events-none"
          >
            &lt; Previous Page
          </button>
          <span className="text-xs text-gray-500 font-mono">Events {offset} - {offset + limit}</span>
          <button
            onClick={() => setOffset(offset + limit)}
            disabled={events.length < limit}
            className="px-3 py-1.5 bg-space-dark border border-white/10 rounded text-xs font-mono hover:bg-white/5 disabled:opacity-30 disabled:pointer-events-none"
          >
            Next Page &gt;
          </button>
        </div>

      </div>

    </div>
  );
};
