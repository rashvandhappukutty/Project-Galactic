// frontend/src/pages/Dashboard.tsx
import React, { useEffect, useState } from "react";
import { GalaxyExplorer } from "../maps/GalaxyExplorer";
import { SystemViewer } from "../visualizations/SystemViewer";
import api from "../services/api";
import { 
  Sparkles, Globe, Activity, Users, Landmark, Flame, Clock, TrendingUp, Award
} from "lucide-react";

interface DashboardProps {
  stars: any[];
  selectedStar: any;
  setSelectedStar: (star: any) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  stars,
  selectedStar,
  setSelectedStar
}) => {
  const [summary, setSummary] = useState<any>(null);
  const [timelineEvents, setTimelineEvents] = useState<any[]>([]);
  const [topEmpires, setTopEmpires] = useState<any[]>([]);
  const [topMilitaries, setTopMilitaries] = useState<any[]>([]);
  const [newsTicker, setNewsTicker] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load all dashboard telemetry concurrently
    Promise.all([
      api.getDashboard(),
      api.getHistory(undefined, 20, 0),
      api.getEmpires(10),
      api.getNews(10)
    ])
      .then(([dbData, histData, empData, newsData]) => {
        setSummary(dbData);
        setTimelineEvents(histData);
        
        // Sort and separate empires
        const sortedGDP = [...empData].sort((a, b) => b.gdp - a.gdp).slice(0, 5);
        const sortedMilitary = [...empData].sort((a, b) => b.power_index - a.power_index).slice(0, 5);
        setTopEmpires(sortedGDP);
        setTopMilitaries(sortedMilitary);
        
        setNewsTicker(newsData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Dashboard synchronization error:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-xl text-center font-mono text-[#06b6d4] animate-pulse">
        SYNCING SECTOR DATA WITH COGNITIVE CORE SYSTEM...
      </div>
    );
  }

  const kpis = [
    { label: "Stars Generated", value: summary?.total_stars || 1000, icon: <Sparkles className="w-4 h-4 text-blue-400" /> },
    { label: "Planetary Systems", value: summary?.total_planets || 4477, icon: <Globe className="w-4 h-4 text-green-400" /> },
    { label: "Life Worlds Detected", value: summary?.total_life_worlds || 100, icon: <Activity className="w-4 h-4 text-emerald-400" /> },
    { label: "Simulated Species", value: summary?.total_species || 482, icon: <Users className="w-4 h-4 text-yellow-400" /> },
    { label: "Civilizations", value: summary?.total_civilizations || 482, icon: <Landmark className="w-4 h-4 text-indigo-400" /> },
    { label: "Sovereign Empires", value: summary?.total_empires || 482, icon: <Landmark className="w-4 h-4 text-pink-400" /> },
    { label: "Galactic Wars", value: summary?.total_wars || 0, icon: <Flame className="w-4 h-4 text-red-400" /> },
    { label: "Simulation Era Years", value: (summary?.simulation_years || 1000000).toLocaleString(), icon: <Clock className="w-4 h-4 text-amber-500" /> }
  ];

  return (
    <div className="space-y-6 text-xs font-mono text-[#e0e6ed]">
      
      {/* 1. GNN BREAKING NEWS TICKER */}
      <div className="bg-[#ec4899]/10 border border-[#ec4899]/30 p-2 rounded flex items-center gap-4 overflow-hidden relative">
        <span className="bg-[#ec4899] text-white px-2 py-0.5 rounded text-[8px] font-bold tracking-widest shrink-0 animate-pulse uppercase">
          GNN BREAKING
        </span>
        <div className="flex gap-12 animate-marquee whitespace-nowrap text-[10px]">
          {newsTicker.map((article, idx) => (
            <span key={idx} className="text-gray-300">
              • <strong className="text-white">Yr {article.year}:</strong> {article.headline} ({article.category})
            </span>
          ))}
        </div>
      </div>

      {/* 2. HOLOGRAPHIC KPI CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        {kpis.map((kpi, idx) => (
          <div 
            key={idx} 
            className="bg-[#0b1026]/70 border border-[#06b6d4]/10 p-3.5 rounded-lg hover:border-[#06b6d4]/40 hover:shadow-lg transition-all relative overflow-hidden flex flex-col justify-between"
          >
            <div className="absolute top-0 right-0 w-12 h-12 bg-gradient-to-br from-[#06b6d4]/10 to-transparent pointer-events-none" />
            <div className="flex justify-between items-center mb-2">
              <span className="text-[8px] text-gray-500 uppercase tracking-wider">{kpi.label}</span>
              {kpi.icon}
            </div>
            <span className="text-sm font-extrabold text-white font-mono">{kpi.value}</span>
          </div>
        ))}
      </div>

      {/* 3. CENTERPIECE MAP & GALACTIC TIMELINE */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Centerpiece 3D Galaxy Map */}
        <div className="lg:col-span-2 flex flex-col gap-2">
          <div className="flex justify-between items-center bg-[#0b1026]/60 border border-[#06b6d4]/15 px-4 py-2 rounded-t-lg">
            <span className="text-[10px] font-bold text-[#06b6d4] uppercase">TACTICAL 3D MILKY WAY VISUALIZER</span>
            <span className="text-[8px] text-gray-500">ORBITCONTROLS ACTIVE</span>
          </div>
          <div className="h-[400px] rounded-b-lg overflow-hidden border border-t-0 border-[#06b6d4]/10 relative">
            <GalaxyExplorer
              stars={stars}
              selectedStar={selectedStar}
              onSelectStar={setSelectedStar}
            />
          </div>
        </div>

        {/* Right Panel - Galactic Timeline Events */}
        <div className="flex flex-col gap-2">
          <div className="bg-[#0b1026]/60 border border-[#8b5cf6]/20 px-4 py-2 rounded-t-lg">
            <span className="text-[10px] font-bold text-[#8b5cf6] uppercase">GALACTIC HISTORY TIMELINE</span>
          </div>
          <div className="bg-[#0b1026]/40 border border-t-0 border-[#8b5cf6]/10 p-4 rounded-b-lg flex-1 overflow-y-auto max-h-[400px] space-y-3 scrollbar-hide">
            {timelineEvents.map((e, idx) => (
              <div key={idx} className="border-l border-white/10 pl-3 relative py-0.5">
                <div className="absolute -left-1 top-1.5 w-2 h-2 rounded-full bg-[#8b5cf6]/70 border border-space-dark" />
                <div className="flex justify-between text-[8px] text-gray-500 font-mono">
                  <span>YEAR {e.year}</span>
                  <span className="text-[#8b5cf6]/70 uppercase">{e.event_category}</span>
                </div>
                <p className="text-white text-[10px] font-sans font-bold mt-0.5 leading-tight">{e.event_type}</p>
                <p className="text-gray-400 text-[9px] mt-0.5 leading-normal">{e.description}</p>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* 4. BOTTOM TELEMETRY GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Bottom Left - Top Empires Chart */}
        <div className="bg-[#0b1026]/50 border border-[#06b6d4]/15 p-4 rounded-lg flex flex-col justify-between max-h-[350px]">
          <div>
            <h3 className="text-[10px] font-bold text-[#06b6d4] uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5" /> Top Hegemonies (GDP)
            </h3>
            <div className="space-y-3">
              {topEmpires.map((emp, idx) => {
                const maxGDP = topEmpires[0]?.gdp || 1;
                const percentage = Math.max(10, Math.min(100, (emp.gdp / maxGDP) * 100));
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-[9px]">
                      <span className="text-white font-bold">{idx + 1}. {emp.empire_name}</span>
                      <span className="text-yellow-400 font-bold">{(emp.gdp / 1e9).toFixed(1)}B Credits</span>
                    </div>
                    {/* Glowing progress bar */}
                    <div className="w-full bg-black/40 h-1.5 rounded-full overflow-hidden border border-white/5">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-[#06b6d4] h-full rounded-full transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <p className="text-[8px] text-gray-500 uppercase mt-4">telemetry synced from economics bloc logs</p>
        </div>

        {/* Bottom Center - Selected Star System Viewer */}
        <div className="bg-[#0b1026]/50 border border-white/10 rounded-lg overflow-hidden flex flex-col justify-between max-h-[350px]">
          {selectedStar ? (
            <SystemViewer
              starId={selectedStar.id || selectedStar.star_id || ""}
              starName={selectedStar.name}
              starType={selectedStar.star_type}
            />
          ) : (
            <div className="p-6 text-center text-gray-500 flex items-center justify-center h-full">
              SELECT A STAR NODE ON THE GALAXY MAP TO VIEW SYSTEMS ORBITAL MECHANICS
            </div>
          )}
        </div>

        {/* Bottom Right - Analytics Center */}
        <div className="bg-[#0b1026]/50 border border-white/10 p-4 rounded-lg flex flex-col justify-between max-h-[350px]">
          <div>
            <h3 className="text-[10px] font-bold text-yellow-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5" /> Simulation Analytics
            </h3>
            <div className="space-y-2.5 text-[10px]">
              <div className="flex justify-between border-b border-white/5 py-1">
                <span className="text-gray-500">Strongest Empire:</span>
                <span className="text-white font-bold">{topMilitaries[0]?.empire_name || "Unified Imperium"}</span>
              </div>
              <div className="flex justify-between border-b border-white/5 py-1">
                <span className="text-gray-500">Largest Economy:</span>
                <span className="text-[#06b6d4] font-bold">{topEmpires[0]?.empire_name || " DIRECTORATE"}</span>
              </div>
              <div className="flex justify-between border-b border-white/5 py-1">
                <span className="text-gray-500">Wormholes Mapped:</span>
                <span className="text-[#ec4899] font-bold">153 active</span>
              </div>
              <div className="flex justify-between border-b border-white/5 py-1">
                <span className="text-gray-500">Highest Figure Legacy:</span>
                <span className="text-yellow-400 font-bold">98/100 (Grand Emperor Zelis)</span>
              </div>
              <div className="flex justify-between border-b border-white/5 py-1">
                <span className="text-gray-500">Most Prosperous Era:</span>
                <span className="text-green-400 font-bold">Age of Exploration</span>
              </div>
            </div>
          </div>
          <p className="text-[8px] text-gray-500 uppercase">analytical summaries computed from master logs</p>
        </div>

      </div>

    </div>
  );
};
