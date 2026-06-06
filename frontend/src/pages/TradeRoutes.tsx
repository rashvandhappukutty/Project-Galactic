// frontend/src/pages/TradeRoutes.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Search, Route, Clock, ArrowRightLeft } from "lucide-react";

interface FtlRoute {
  route_id: string;
  empire_id: string;
  empire_name: string;
  source_star_id: string;
  source_star_name: string;
  target_star_id: string;
  target_star_name: string;
  travel_time_years: number;
  stops_count: number;
  route_type: string;
}

export const TradeRoutes: React.FC = () => {
  const [routes, setRoutes] = useState<FtlRoute[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRoute, setSelectedRoute] = useState<FtlRoute | null>(null);

  useEffect(() => {
    // Load a slightly larger limit to ensure we have various FTL routes
    api.getFtlRoutes(200)
      .then((data) => {
        // Filter or display routes
        setRoutes(data);
        if (data.length > 0) setSelectedRoute(data[0]);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading FTL routes:", err);
        setLoading(false);
      });
  }, []);

  const filteredRoutes = routes.filter((r) =>
    r.source_star_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.target_star_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.empire_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="glass-panel p-6 rounded-xl grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-[500px] text-xs font-mono text-[#e0e6ed]">
      {/* Sidebar - Shipping Lanes list */}
      <div className="lg:border-r border-white/10 pr-4 flex flex-col h-full max-h-[500px]">
        <div className="flex items-center gap-2 mb-3">
          <Route className="w-4 h-4 text-emerald-400 animate-pulse" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Transit Lanes Matrix</h3>
        </div>
        <div className="relative mb-4">
          <input
            type="text"
            placeholder="FILTER BY STAR OR EMPIRE..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/40 border border-[#06b6d4]/20 rounded p-2 pl-8 text-[10px] text-white focus:outline-none focus:border-[#06b6d4] uppercase"
          />
          <Search className="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" />
        </div>

        {loading ? (
          <div className="text-center py-10 text-gray-500 animate-pulse">QUERYING SHUTTLE POSITION CODES...</div>
        ) : filteredRoutes.length === 0 ? (
          <div className="text-center py-10 text-gray-600">NO FTL ROUTES RECORDED.</div>
        ) : (
          <div className="overflow-y-auto flex-1 space-y-1 pr-1 scrollbar-hide">
            {filteredRoutes.map((r, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedRoute(r)}
                className={`w-full text-left p-2.5 rounded transition relative group flex justify-between items-center ${
                  selectedRoute?.route_id === r.route_id
                    ? "bg-[#10b981]/10 text-white border-l-2 border-[#10b981]"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <div className="flex flex-col gap-0.5 truncate">
                  <span className="font-bold text-white truncate text-[10px]">
                    {r.source_star_name} → {r.target_star_name}
                  </span>
                  <span className="text-[8px] text-gray-500 truncate uppercase">{r.empire_name}</span>
                </div>
                <span className="text-[8px] bg-white/5 px-1 py-0.5 rounded text-emerald-400 font-bold shrink-0">
                  {r.route_type.split(" ")[0]}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Details Panel */}
      {selectedRoute ? (
        <div className="lg:col-span-2 space-y-6 overflow-y-auto max-h-[500px] pr-2 scrollbar-hide">
          {/* Header */}
          <div className="flex justify-between items-start border-b border-[#06b6d4]/10 pb-4">
            <div>
              <h2 className="text-lg font-bold text-white uppercase tracking-widest">
                FTL LANES CORRIDOR #{selectedRoute.route_id.slice(-6)}
              </h2>
              <p className="text-[10px] text-gray-500 uppercase mt-0.5">
                Jurisdiction Authority: <span className="text-blue-400 font-bold">{selectedRoute.empire_name}</span>
              </p>
            </div>
            <div className="px-2.5 py-1 rounded bg-[#10b981]/10 border border-[#10b981]/30 text-[9px] text-[#10b981] font-bold tracking-widest uppercase">
              STATUS: ESTABLISHED
            </div>
          </div>

          {/* Route Visual Details */}
          <div className="bg-black/30 p-6 rounded-lg border border-[#06b6d4]/10 flex flex-col items-center justify-center gap-4">
            <div className="flex items-center gap-6 w-full max-w-md justify-between">
              <div className="text-center bg-black/40 border border-white/5 p-3 rounded-lg w-2/5">
                <span className="text-[7px] text-gray-500 uppercase">DEP. HARBOR</span>
                <p className="text-xs font-extrabold text-[#06b6d4] mt-0.5">{selectedRoute.source_star_name}</p>
                <p className="text-[7px] text-gray-600 font-mono mt-0.5">ID: #{selectedRoute.source_star_id.slice(0,6)}</p>
              </div>

              <div className="flex-1 flex flex-col items-center gap-1">
                <ArrowRightLeft className="w-4 h-4 text-emerald-400 animate-pulse" />
                <div className="w-full h-0.5 bg-gradient-to-r from-blue-500 via-emerald-400 to-purple-500 relative">
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-white animate-ping" />
                </div>
                <span className="text-[7px] text-gray-500 uppercase">Warp Transit Link</span>
              </div>

              <div className="text-center bg-black/40 border border-white/5 p-3 rounded-lg w-2/5">
                <span className="text-[7px] text-gray-500 uppercase">DEST. ANCHOR</span>
                <p className="text-xs font-extrabold text-purple-400 mt-0.5">{selectedRoute.target_star_name}</p>
                <p className="text-[7px] text-gray-600 font-mono mt-0.5">ID: #{selectedRoute.target_star_id.slice(0,6)}</p>
              </div>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Clock className="w-5 h-5 text-yellow-400 shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Transit Duration</p>
                <p className="text-xs font-extrabold text-white mt-0.5">
                  {selectedRoute.travel_time_years === 0 ? "INSTANT JUMP" : `${selectedRoute.travel_time_years.toFixed(3)} Years`}
                </p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Route className="w-5 h-5 text-teal-400 shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">Sub-system Stops</p>
                <p className="text-xs font-extrabold text-white mt-0.5">{selectedRoute.stops_count} Junctions</p>
              </div>
            </div>

            <div className="bg-black/20 p-4 rounded border border-white/5 flex items-center gap-3">
              <Route className="w-5 h-5 text-[#06b6d4] shrink-0" />
              <div>
                <p className="text-[8px] text-gray-500 uppercase font-mono">FTL Classification</p>
                <p className="text-xs font-extrabold text-white mt-0.5 uppercase truncate">{selectedRoute.route_type}</p>
              </div>
            </div>
          </div>

          <div className="bg-[#0b1026] border border-emerald-500/10 p-3.5 rounded text-[10px] text-gray-400 leading-normal font-sans">
            <strong className="text-emerald-400 font-mono uppercase">Logistics Matrix:</strong> FTL lane runs through secure sovereign hyperlane networks. Cargo ships are covered under military patrol shields. Safe for civilian freighters and fuel transports.
          </div>
        </div>
      ) : (
        <div className="lg:col-span-2 flex items-center justify-center text-gray-500">
          SELECT AN ACTIVE FTL SHIPPING NODE TO AUDIT CARGO ROUTE SPECIFICATIONS
        </div>
      )}
    </div>
  );
};
export default TradeRoutes;
