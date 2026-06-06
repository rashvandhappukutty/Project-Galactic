// frontend/src/pages/GalaxyExplorer.tsx
import React from "react";
import { GalaxyExplorer as MapComponent } from "../maps/GalaxyExplorer";

interface Star {
  id?: string;
  star_id?: string;
  name: string;
  x: number;
  y: number;
  z: number;
  star_type: string;
}

interface GalaxyExplorerProps {
  stars: Star[];
  selectedStar: Star | null;
  setSelectedStar: (star: Star) => void;
}

export const GalaxyExplorer: React.FC<GalaxyExplorerProps> = ({
  stars,
  selectedStar,
  setSelectedStar,
}) => {
  return (
    <div className="h-full flex flex-col gap-4">
      <div className="glass-panel p-4 rounded-xl flex justify-between items-center text-xs font-mono uppercase text-blue-400">
        <span>Milky Way Galaxy Explorer</span>
        <span>Particles: {stars.length} Stars Loaded</span>
      </div>
      <div className="flex-1 min-h-[450px]">
        <MapComponent
          stars={stars}
          selectedStar={selectedStar}
          onSelectStar={setSelectedStar}
        />
      </div>
    </div>
  );
};
