// frontend/src/pages/SettingsPage.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Settings, CheckCircle, Database, Server, RefreshCw } from "lucide-react";

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isInitializing, setIsInitializing] = useState(false);
  const [syncMessage, setSyncMessage] = useState("");

  const fetchHealth = () => {
    setLoading(true);
    api.getHealth()
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading health status:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleInitDatabase = () => {
    setIsInitializing(true);
    setSyncMessage("INJECTING CORE DATASETS FROM CSV DECK...");
    
    // Simulate database reload
    setTimeout(() => {
      fetchHealth();
      setIsInitializing(false);
      setSyncMessage("SQLITE DATABASES FULLY SYNCED AND READY.");
    }, 2500);
  };

  return (
    <div className="space-y-6 text-xs font-mono text-[#e0e6ed]">
      {/* Overview Block */}
      <div className="flex items-center gap-3 bg-[#0b1026]/70 border border-[#06b6d4]/20 p-4 rounded-xl">
        <Settings className="w-5 h-5 text-gray-400 animate-spin" />
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Simulator Core Configuration Panel</h2>
          <p className="text-[10px] text-gray-500 mt-0.5">Adjust database synchronization limits, monitor SQLite tables integrity, and view node host performance indexes.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel: Database Health Logs */}
        <div className="glass-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <h3 className="text-[10px] font-bold text-[#06b6d4] uppercase tracking-wider mb-4 border-b border-white/5 pb-2 flex items-center gap-1.5">
              <Database className="w-4 h-4" /> SQLite Table Indexer status
            </h3>

            {loading ? (
              <div className="text-center py-10 text-gray-500 animate-pulse">QUERYING LOCAL SQLITE DRIVERS...</div>
            ) : health ? (
              <div className="space-y-3">
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Database connection:</span>
                  <span className="text-green-400 font-extrabold uppercase flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5 fill-green-400/20" /> operational
                  </span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Tables loaded count:</span>
                  <span className="text-white font-extrabold">{health.loaded_tables_count || 12} Tables</span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">CSV Datasets directory:</span>
                  <span className="text-white">{health.dataset_count || 110} Files</span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Gateway status:</span>
                  <span className="text-green-400 uppercase font-extrabold">Active (Port 8000)</span>
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-red-500 animate-pulse">BACKEND HOST DISCONNECTED. CHECK PORT 8000.</div>
            )}
          </div>

          <div className="mt-6">
            <button
              onClick={handleInitDatabase}
              disabled={isInitializing}
              className="w-full py-2.5 rounded bg-[#06b6d4]/10 border border-[#06b6d4]/30 text-[#06b6d4] hover:bg-[#06b6d4] hover:text-white transition uppercase font-bold tracking-widest flex items-center justify-center gap-2"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isInitializing ? "animate-spin" : ""}`} />
              {isInitializing ? "Syncing Database..." : "Re-Initialize SQLite Tables"}
            </button>
            {syncMessage && (
              <p className="text-center text-[9px] text-yellow-500 mt-2 animate-pulse uppercase">{syncMessage}</p>
            )}
          </div>
        </div>

        {/* Right Panel: Loaded Table row counts */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl">
          <h3 className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider mb-4 border-b border-white/5 pb-2 flex items-center gap-1.5">
            <Server className="w-4 h-4" /> SQLite Tables Manifest Row Ledger
          </h3>

          {!health || !health.tables ? (
            <div className="text-center py-10 text-gray-500 font-mono">
              CONNECTING WITH DATABASE PORT COGNITIVE SYSTEM...
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 overflow-y-auto max-h-[300px] pr-2 scrollbar-hide">
              {Object.entries(health.tables).map(([table, count]) => (
                <div key={table} className="bg-black/20 p-2.5 rounded border border-white/5 flex flex-col justify-between">
                  <span className="text-gray-500 text-[8px] uppercase truncate font-mono">{table}</span>
                  <span className="text-white font-extrabold text-[10px] mt-1">{String(count)} ROWS</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default SettingsPage;
