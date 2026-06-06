// frontend/src/pages/EconomyTrade.tsx
import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Coins, BarChart3, TrendingUp, ShieldAlert, Award, ArrowUpRight } from "lucide-react";

interface EconomyRecord {
  tick: number;
  year: number;
  civilization_id: string;
  gdp: number;
  gdp_growth: number;
  treasury: number;
  capital_reserves: number;
  money_supply: number;
  inflation_rate: number;
  exchange_rate: number;
  purchasing_power_index: number;
  trade_volume: number;
  trade_balance: number;
}

export const EconomyTrade: React.FC = () => {
  const [economyList, setEconomyList] = useState<EconomyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState<EconomyRecord | null>(null);

  useEffect(() => {
    api.getEconomy(50)
      .then((data) => {
        setEconomyList(data);
        if (data.length > 0) setSelectedRecord(data[0]);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading economy data:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-xl text-center font-mono text-[#06b6d4] animate-pulse">
        SYNCHRONIZING COMMERCIAL BLOCK EXCHANGE RATES...
      </div>
    );
  }

  // Get top GDP nodes for custom SVG bar chart
  const topGDPRecords = [...economyList]
    .sort((a, b) => b.gdp - a.gdp)
    .slice(0, 6);

  const maxGDP = topGDPRecords[0]?.gdp || 1;

  return (
    <div className="space-y-6 text-xs font-mono text-[#e0e6ed]">
      {/* Overview Block */}
      <div className="flex items-center gap-3 bg-[#06b6d4]/10 border border-[#06b6d4]/30 p-4 rounded-xl">
        <Coins className="w-5 h-5 text-[#06b6d4] animate-bounce" />
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Galactic Financial Telemetry Desk</h2>
          <p className="text-[10px] text-gray-400 mt-0.5">Real-time commercial index tracking and FTL market liquidity logs.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side: Top GDP Node rankings with custom glowing SVG Bar Chart */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
              <h3 className="text-[10px] font-bold text-[#06b6d4] uppercase tracking-wider flex items-center gap-1.5">
                <BarChart3 className="w-4 h-4" /> GDP Volume Comparisons (Credits)
              </h3>
              <span className="text-[8px] text-gray-500">REALTIME SCATTER</span>
            </div>

            {/* Glowing SVG Bar Chart */}
            <div className="w-full h-56 flex items-end justify-between bg-black/40 border border-white/5 rounded-lg p-6 relative overflow-hidden">
              {/* Grid Lines */}
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none p-6 text-[8px] text-gray-600">
                <div className="border-b border-white/5 w-full pb-1">MAX: {(maxGDP / 1e9).toFixed(1)}B Credits</div>
                <div className="border-b border-white/5 w-full pb-1">MID: {(maxGDP / 2e9).toFixed(1)}B Credits</div>
                <div className="border-b border-white/5 w-full pb-1">MIN: 0.0B Credits</div>
              </div>

              {topGDPRecords.map((rec, idx) => {
                const heightPercentage = Math.max(15, (rec.gdp / maxGDP) * 100);
                const colors = ["#06b6d4", "#8b5cf6", "#ec4899", "#10b981", "#3b82f6", "#f59e0b"];
                const color = colors[idx % colors.length];

                return (
                  <div key={idx} className="flex flex-col items-center z-10 w-1/6 group cursor-pointer" onClick={() => setSelectedRecord(rec)}>
                    <span className="text-[7px] text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 mb-1">
                      {(rec.gdp / 1e9).toFixed(2)}B
                    </span>
                    <div 
                      className="w-8 rounded-t transition-all duration-1000 ease-out"
                      style={{ 
                        height: `${heightPercentage * 1.2}px`, 
                        backgroundColor: color, 
                        boxShadow: `0 0 10px ${color}80`,
                        filter: `drop-shadow(0 0 4px ${color}40)` 
                      }}
                    />
                    <span className="text-[8px] text-gray-500 uppercase mt-2 text-center truncate w-full">
                      Civ #{rec.civilization_id.slice(0, 6)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
          <p className="text-[7px] text-gray-600 mt-4 uppercase">click any block columns to load their detailed treasury manifest</p>
        </div>

        {/* Right Side: Detailed Treasury Matrix */}
        <div className="glass-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
              <h3 className="text-[10px] font-bold text-yellow-500 uppercase tracking-wider flex items-center gap-1.5">
                <Award className="w-4 h-4" /> Treasury Audit Manifest
              </h3>
              {selectedRecord && (
                <span className="text-[8px] text-gray-500">CIV ID: #{selectedRecord.civilization_id.slice(0, 8)}</span>
              )}
            </div>

            {selectedRecord ? (
              <div className="space-y-3">
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Gross Product (GDP):</span>
                  <span className="text-white font-extrabold">{(selectedRecord.gdp / 1e9).toFixed(2)} Billion Credits</span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Growth Index:</span>
                  <span className={`font-extrabold flex items-center gap-1 ${selectedRecord.gdp_growth >= 0 ? "text-green-400" : "text-red-400"}`}>
                    <TrendingUp className="w-3 h-3" /> {selectedRecord.gdp_growth.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Capital Reserves:</span>
                  <span className="text-yellow-400 font-extrabold">{(selectedRecord.capital_reserves / 1e3).toFixed(1)}M Credits</span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Inflation Ratio:</span>
                  <span className="text-red-400 font-extrabold">{selectedRecord.inflation_rate.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Global Coin Supply:</span>
                  <span className="text-white">{(selectedRecord.money_supply / 1e6).toFixed(1)}M Credits</span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Market Trade Volume:</span>
                  <span className="text-[#06b6d4] font-extrabold">{(selectedRecord.trade_volume / 1e3).toFixed(1)}M Credits</span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-1.5">
                  <span className="text-gray-500 uppercase">Trade Net Balance:</span>
                  <span className={`font-extrabold ${selectedRecord.trade_balance >= 0 ? "text-green-400" : "text-red-400"}`}>
                    {(selectedRecord.trade_balance / 1e3).toFixed(1)}M Credits
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-gray-500">SELECT A CIV NODE TO HARVEST MANIFEST</div>
            )}
          </div>

          <div className="bg-[#0b1026] border border-yellow-500/10 p-3 rounded text-[9px] text-gray-400 leading-relaxed font-sans mt-4 flex items-start gap-2">
            <ShieldAlert className="w-3.5 h-3.5 text-yellow-500 shrink-0" />
            <p>Exchange rates calibrated to standard Galactic Core Reserves indexes. Extreme hyperlane tolls might cause inflation spikes.</p>
          </div>
        </div>
      </div>

      {/* Tabled ledger database */}
      <div className="glass-panel rounded-xl p-5 overflow-hidden">
        <h3 className="text-[10px] font-bold text-[#06b6d4] uppercase tracking-wider mb-3">Galactic Commercial Ledger (Tick Stats)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-[10px]">
            <thead>
              <tr className="border-b border-white/10 text-gray-500">
                <th className="py-2 uppercase">Year</th>
                <th className="py-2 uppercase">Civilization Node</th>
                <th className="py-2 uppercase">GDP (Credits)</th>
                <th className="py-2 uppercase">Inflation</th>
                <th className="py-2 uppercase">Exchange Rate</th>
                <th className="py-2 uppercase">Purchasing Index</th>
                <th className="py-2 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-gray-300">
              {economyList.slice(0, 10).map((record, idx) => (
                <tr key={idx} className="hover:bg-white/5 transition">
                  <td className="py-2">Yr {record.year}</td>
                  <td className="py-2 text-[#06b6d4] font-bold">#{record.civilization_id.slice(0,10)}</td>
                  <td className="py-2">{(record.gdp / 1e9).toFixed(2)}B</td>
                  <td className="py-2 text-red-400">{record.inflation_rate.toFixed(2)}%</td>
                  <td className="py-2">{record.exchange_rate.toFixed(2)}</td>
                  <td className="py-2">{record.purchasing_power_index.toFixed(3)}</td>
                  <td className="py-2">
                    <button 
                      onClick={() => setSelectedRecord(record)}
                      className="px-2 py-0.5 rounded bg-[#06b6d4]/10 border border-[#06b6d4]/20 text-[#06b6d4] hover:bg-[#06b6d4] hover:text-white transition flex items-center gap-0.5"
                    >
                      AUDIT <ArrowUpRight className="w-2.5 h-2.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default EconomyTrade;
