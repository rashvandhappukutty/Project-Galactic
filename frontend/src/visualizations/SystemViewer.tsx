// frontend/src/components/SystemViewer.tsx
import React, { useEffect, useRef, useState } from "react";
import { Globe } from "lucide-react";

interface Planet {
  planet_id: string;
  planet_name: string;
  star_id: string;
  orbital_distance_au: number;
  habitability_score: number;
  resource_score: number;
  planet_type: string;
  population?: number;
  temperature?: number;
}

interface SystemViewerProps {
  starId: string;
  starName: string;
  starType: string;
}

export const SystemViewer: React.FC<SystemViewerProps> = ({
  starId,
  starName,
  starType,
}) => {
  const [planets, setPlanets] = useState<Planet[]>([]);
  const [selectedPlanet, setSelectedPlanet] = useState<Planet | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:8000/api/planets?star_id=${starId}`)
      .then((res) => res.json())
      .then((data) => {
        setPlanets(data);
        setSelectedPlanet(data[0] || null);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading planets:", err);
        setLoading(false);
      });
  }, [starId]);

  // Orbit animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || planets.length === 0) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let angle = 0;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;

      // Draw central star
      const gradient = ctx.createRadialGradient(cx, cy, 2, cx, cy, 15);
      gradient.addColorStop(0, "#f59e0b");
      gradient.addColorStop(0.8, "#d97706");
      gradient.addColorStop(1, "rgba(217, 119, 6, 0)");
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(cx, cy, 15, 0, Math.PI * 2);
      ctx.fill();

      // Draw planet orbits and planets
      planets.forEach((planet, idx) => {
        const dist = 30 + (idx + 1) * 22; // Orbit radius
        const speed = 0.05 / (idx + 1); // Orbit speed

        // Draw orbit line
        ctx.strokeStyle = "rgba(255, 255, 255, 0.06)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(cx, cy, dist, 0, Math.PI * 2);
        ctx.stroke();

        // Draw planet
        const px = cx + Math.cos(angle * speed) * dist;
        const py = cy + Math.sin(angle * speed) * dist;

        ctx.fillStyle = selectedPlanet?.planet_id === planet.planet_id ? "#3b82f6" : "#64748b";
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.fill();

        // Label planet
        ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
        ctx.font = "8px monospace";
        ctx.fillText(planet.planet_name.split(" ")[1] || planet.planet_name, px + 6, py + 3);
      });

      angle += 0.5;
      animId = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(animId);
  }, [planets, selectedPlanet]);

  return (
    <div className="glass-panel p-6 rounded-xl h-full flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
          <h2 className="text-xl font-bold text-white tracking-wide">{starName} System</h2>
          <span className="text-xs bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 px-2 py-0.5 rounded font-mono">
            Spectral: {starType}
          </span>
        </div>

        {loading ? (
          <div className="text-center py-10 font-mono text-gray-400">Loading system entities...</div>
        ) : planets.length === 0 ? (
          <div className="text-center py-10 font-mono text-gray-400">No orbiting planetary bodies detected.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 2D Canvas Orbit View */}
            <div className="flex items-center justify-center bg-black/30 rounded-lg border border-white/5 p-4 min-h-[220px]">
              <canvas ref={canvasRef} width={220} height={220} className="max-w-full" />
            </div>

            {/* Planet Stats */}
            <div className="flex flex-col justify-between">
              <div>
                <select
                  value={selectedPlanet?.planet_id || ""}
                  onChange={(e) => {
                    const match = planets.find((p) => p.planet_id === e.target.value);
                    if (match) setSelectedPlanet(match);
                  }}
                  className="bg-space-dark border border-white/10 text-white rounded p-1.5 w-full text-sm font-mono focus:outline-none focus:border-blue-500 mb-4"
                >
                  {planets.map((p) => (
                    <option key={p.planet_id} value={p.planet_id}>
                      {p.planet_name}
                    </option>
                  ))}
                </select>

                {selectedPlanet && (
                  <div className="space-y-2 font-mono text-xs text-gray-300">
                    <div className="flex justify-between border-b border-white/5 py-1">
                      <span>Type:</span>
                      <span className="text-white font-bold">{selectedPlanet.planet_type}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 py-1">
                      <span>Habitability:</span>
                      <span className={`font-bold ${selectedPlanet.habitability_score >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                        {selectedPlanet.habitability_score.toFixed(1)}/100
                      </span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 py-1">
                      <span>Resources:</span>
                      <span className="text-yellow-400 font-bold">{selectedPlanet.resource_score.toFixed(1)}/100</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 py-1">
                      <span>Distance:</span>
                      <span className="text-white">{selectedPlanet.orbital_distance_au.toFixed(2)} AU</span>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 bg-blue-500/5 border border-blue-500/10 p-3 rounded text-xs text-gray-400 flex items-start gap-2">
                <Globe className="w-4 h-4 text-blue-400 shrink-0" />
                <p>System shows stable gravitational orbits. Safe for jump gate network anchors.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
