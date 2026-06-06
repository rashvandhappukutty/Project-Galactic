// frontend/src/pages/ResearchLab.tsx
import React, { useState } from "react";
import { FlaskConical, Cpu, ShieldAlert, CpuIcon, Eye, Radio } from "lucide-react";

export const ResearchLab: React.FC = () => {
  const [physics, setPhysics] = useState(33);
  const [society, setSociety] = useState(33);
  const [engineering, setEngineering] = useState(34);
  const [researchState, setResearchState] = useState<"ACTIVE" | "PAUSED">("ACTIVE");

  const totalBudget = physics + society + engineering;

  const handleSliderChange = (category: "physics" | "society" | "engineering", value: number) => {
    if (category === "physics") {
      setPhysics(value);
      // Balance the remaining budget between the other two
      const diff = 100 - value;
      setSociety(Math.round(diff / 2));
      setEngineering(Math.round(diff / 2));
    } else if (category === "society") {
      setSociety(value);
      const diff = 100 - value;
      setPhysics(Math.round(diff / 2));
      setEngineering(Math.round(diff / 2));
    } else {
      setEngineering(value);
      const diff = 100 - value;
      setPhysics(Math.round(diff / 2));
      setSociety(Math.round(diff / 2));
    }
  };

  const techTree = [
    { name: "Sub-space Quantum Comms", category: "Physics", progress: 85, status: "Researching", icon: <Radio className="w-4 h-4 text-cyan-400" /> },
    { name: "Dark Matter Deflectors", category: "Engineering", progress: 45, status: "Researching", icon: <CpuIcon className="w-4 h-4 text-purple-400" /> },
    { name: "Synthetic AI Core Sovereignty", category: "Society", progress: 98, status: "Near Completion", icon: <Eye className="w-4 h-4 text-pink-400" /> },
    { name: "Dyson Swarm Accumulators", category: "Engineering", progress: 20, status: "Conceptual", icon: <Cpu className="w-4 h-4 text-yellow-400" /> }
  ];

  return (
    <div className="space-y-6 text-xs font-mono text-[#e0e6ed]">
      {/* Overview Block */}
      <div className="flex justify-between items-center bg-[#06b6d4]/10 border border-[#06b6d4]/30 p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <FlaskConical className="w-5 h-5 text-teal-400 animate-pulse" />
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Physics & Engineering Research Lab</h2>
            <p className="text-[10px] text-gray-400 mt-0.5">Stellar containment arrays, cybernetic bio-implants, and Dyson structure blueprint compilers.</p>
          </div>
        </div>
        <button 
          onClick={() => setResearchState(researchState === "ACTIVE" ? "PAUSED" : "ACTIVE")}
          className={`px-3 py-1 rounded text-[10px] font-bold tracking-widest uppercase border ${
            researchState === "ACTIVE" 
              ? "bg-[#06b6d4]/10 text-[#06b6d4] border-[#06b6d4]/30 animate-pulse" 
              : "bg-red-500/10 text-red-500 border-red-500/30"
          }`}
        >
          CORE STATUS: {researchState}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel: Scientific Budget Slider Allocators */}
        <div className="glass-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <h3 className="text-[10px] font-bold text-[#06b6d4] uppercase tracking-wider mb-4 border-b border-white/5 pb-2">
              Scientific Budget Allocation ({totalBudget}%)
            </h3>

            <div className="space-y-6">
              {/* Physics */}
              <div className="space-y-2">
                <div className="flex justify-between text-[10px]">
                  <span className="text-cyan-400 font-bold">PHYSICS SCIENCES</span>
                  <span className="text-white font-extrabold">{physics}%</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={physics} 
                  onChange={(e) => handleSliderChange("physics", parseInt(e.target.value))}
                  className="w-full h-1 bg-black/40 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                />
              </div>

              {/* Society */}
              <div className="space-y-2">
                <div className="flex justify-between text-[10px]">
                  <span className="text-pink-400 font-bold">SOCIOLOGY & COMPATIBILITY</span>
                  <span className="text-white font-extrabold">{society}%</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={society} 
                  onChange={(e) => handleSliderChange("society", parseInt(e.target.value))}
                  className="w-full h-1 bg-black/40 rounded-lg appearance-none cursor-pointer accent-pink-400"
                />
              </div>

              {/* Engineering */}
              <div className="space-y-2">
                <div className="flex justify-between text-[10px]">
                  <span className="text-purple-400 font-bold">ENGINEERING & DEFENSE</span>
                  <span className="text-white font-extrabold">{engineering}%</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={engineering} 
                  onChange={(e) => handleSliderChange("engineering", parseInt(e.target.value))}
                  className="w-full h-1 bg-black/40 rounded-lg appearance-none cursor-pointer accent-purple-400"
                />
              </div>
            </div>
          </div>

          <div className="bg-[#0b1026] border border-yellow-500/10 p-3 rounded text-[9px] text-gray-400 leading-relaxed font-sans mt-6 flex items-start gap-2">
            <ShieldAlert className="w-3.5 h-3.5 text-yellow-500 shrink-0" />
            <p>Budget balancing occurs automatically to maintain a strict 100% total scientific spending cap across sectors.</p>
          </div>
        </div>

        {/* Right Panel: Tech Tree Nodes Progress */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl">
          <h3 className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider mb-4 border-b border-white/5 pb-2">
            Active Research Projects Tree
          </h3>

          <div className="space-y-4">
            {techTree.map((tech, idx) => (
              <div key={idx} className="bg-black/20 p-4 rounded border border-white/5 space-y-2">
                <div className="flex justify-between items-center text-[10px]">
                  <div className="flex items-center gap-2 text-white font-extrabold">
                    {tech.icon}
                    <span>{tech.name}</span>
                  </div>
                  <span className="text-[#06b6d4] font-bold">{tech.status} ({tech.progress}%)</span>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden border border-white/5 p-0.5">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-cyan-400 h-full rounded-full transition-all duration-1000"
                    style={{ width: `${tech.progress}%` }}
                  />
                </div>
                <div className="flex justify-between text-[8px] text-gray-500 font-mono">
                  <span>CATEGORY: {tech.category.toUpperCase()}</span>
                  <span>EST. RADIAL CYCLES: {Math.round((100 - tech.progress) * 12)} CYCLES</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
export default ResearchLab;
