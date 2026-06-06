// frontend/src/pages/StarSystem.tsx
import React from "react";
import { SystemViewer } from "../visualizations/SystemViewer";



interface StarSystemProps {
  selectedStar: any;
  stars: any[];
  setSelectedStar: (star: any) => void;
}

export const StarSystem: React.FC<StarSystemProps> = ({
  selectedStar,
  stars,
  setSelectedStar,
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
      {/* Sidebar selection list */}
      <div className="glass-panel p-4 rounded-xl flex flex-col h-full max-h-[520px]">
        <h3 className="text-xs font-bold font-mono uppercase text-blue-400 tracking-wider mb-3">
          Select Star System
        </h3>
        <div className="overflow-y-auto flex-1 space-y-1">
          {stars.map((star) => (
            <button
              key={star.name}
              onClick={() => setSelectedStar(star)}
              className={`w-full text-left p-2 rounded text-xs font-mono transition ${
                selectedStar?.name === star.name
                  ? "bg-blue-500/20 text-blue-400 border-l-2 border-blue-500"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              ✦ {star.name} ({star.star_type})
            </button>
          ))}
        </div>
      </div>

      {/* Main system orbit visualizer */}
      <div className="lg:col-span-2">
        {selectedStar ? (
          <SystemViewer
            starId={selectedStar.id || selectedStar.star_id || ""}
            starName={selectedStar.name}
            starType={selectedStar.star_type}
          />
        ) : (
          <div className="glass-panel p-6 rounded-xl text-center text-gray-400 font-mono flex items-center justify-center h-full min-h-[400px]">
            Please select a star system from the list to display planetary orbit configurations.
          </div>
        )}
      </div>
    </div>
  );
};
