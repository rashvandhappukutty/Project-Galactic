// frontend/src/layouts/AppLayout.tsx
import React, { useState } from "react";
import { 
  LayoutDashboard, Globe, Landmark, 
  Zap, Handshake, Calendar, BookOpen, Award, 
  FlaskConical, Settings, Search, Bell, ChevronLeft, ChevronRight, 
  User, Sun, Moon, AlertTriangle, Dna, Coins, Route, Orbit, Swords
} from "lucide-react";

interface AppLayoutProps {
  activeTab: string;
  setActiveTab: (tab: any) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  searchResults: any;
  showDropdown: boolean;
  setShowDropdown: (show: boolean) => void;
  onSelectStar: (star: any) => void;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  activeTab,
  setActiveTab,
  searchQuery,
  setSearchQuery,
  searchResults,
  showDropdown,
  setShowDropdown,
  onSelectStar,
  children
}) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [simulationSpeed, setSimulationSpeed] = useState<"PAUSED" | "1X" | "2X" | "4X">("1X");
  const [notifications] = useState<string[]>([
    "WARNING: Supernova threat detected in Sector 4",
    "DIPLOMACY: Peace Treaty signed between Zelis & Valan",
    "ECONOMY: Jump Gate network tolls increased by 5%"
  ]);
  const [showNotifications, setShowNotifications] = useState(false);

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard className="w-4 h-4 text-[#06b6d4]" /> },
    { id: "explorer", label: "Galaxy Explorer", icon: <Globe className="w-4 h-4 text-blue-400" /> },
    { id: "system", label: "Star Systems", icon: <Zap className="w-4 h-4 text-yellow-400" /> },
    { id: "species", label: "Species Catalog", icon: <Dna className="w-4 h-4 text-[#ec4899]" /> },
    { id: "civilizations", label: "Civilizations", icon: <Landmark className="w-4 h-4 text-indigo-400" /> },
    { id: "empires", label: "Empires", icon: <Landmark className="w-4 h-4 text-pink-400" /> },
    { id: "economy", label: "Economy", icon: <Coins className="w-4 h-4 text-emerald-400" /> },
    { id: "trade_routes", label: "Trade Routes", icon: <Route className="w-4 h-4 text-teal-400" /> },
    { id: "ftl", label: "FTL Network", icon: <Orbit className="w-4 h-4 text-cyan-400" /> },
    { id: "diplomacy", label: "Diplomacy", icon: <Handshake className="w-4 h-4 text-purple-400" /> },
    { id: "wars", label: "Wars", icon: <Swords className="w-4 h-4 text-red-400" /> },
    { id: "timeline", label: "Timeline Logs", icon: <Calendar className="w-4 h-4 text-amber-500" /> },
    { id: "stories", label: "Stories & Lore", icon: <BookOpen className="w-4 h-4 text-orange-400" /> },
    { id: "rankings", label: "Historical Figures", icon: <Award className="w-4 h-4 text-amber-300" /> },
    { id: "research", label: "Research Lab", icon: <FlaskConical className="w-4 h-4 text-teal-300" /> },
    { id: "settings", label: "Settings Core", icon: <Settings className="w-4 h-4 text-gray-400" /> }
  ];

  return (
    <div className="min-h-screen bg-[#050816] text-[#e0e6ed] font-mono flex relative overflow-hidden">
      
      {/* Scanline simulation Overlay */}
      <div className="absolute inset-0 bg-scanlines pointer-events-none opacity-5 z-40" />

      {/* LEFT SIDEBAR HUD */}
      <aside 
        className={`bg-[#0b1026]/90 border-r border-[#06b6d4]/20 backdrop-blur-xl flex flex-col justify-between transition-all duration-300 relative z-30 ${
          isSidebarCollapsed ? "w-16" : "w-64"
        }`}
      >
        {/* Toggle Collapse handle */}
        <button 
          onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          className="absolute -right-3 top-20 bg-[#0b1026] border border-[#06b6d4]/30 rounded-full p-1 text-[#06b6d4] hover:bg-[#06b6d4]/20 hover:text-white transition shadow-lg z-50"
        >
          {isSidebarCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
        </button>

        {/* Sidebar Header Brand */}
        <div className="p-4 border-b border-white/10 flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-[#8b5cf6]/20 border border-[#8b5cf6] flex items-center justify-center shrink-0 animate-pulse">
            <SparklesIcon className="w-4 h-4 text-[#06b6d4]" />
          </div>
          {!isSidebarCollapsed && (
            <div>
              <h1 className="text-xs font-bold tracking-widest text-[#06b6d4] uppercase">
                GALACTIC COMMAND
              </h1>
              <p className="text-[8px] text-gray-500 uppercase tracking-wider">Mission Telemetry v2.0</p>
            </div>
          )}
        </div>

        {/* Navigation list */}
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1 scrollbar-hide">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 p-2.5 rounded-lg text-xs tracking-wider transition-all relative group ${
                  isActive 
                    ? "bg-[#06b6d4]/10 text-white border-l-2 border-[#06b6d4]" 
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                {item.icon}
                {!isSidebarCollapsed && <span className="font-mono uppercase">{item.label}</span>}
                {isSidebarCollapsed && (
                  <div className="absolute left-16 bg-[#0b1026] border border-white/10 rounded px-2 py-1 text-[10px] uppercase hidden group-hover:block whitespace-nowrap shadow-xl">
                    {item.label}
                  </div>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer stats */}
        {!isSidebarCollapsed && (
          <div className="p-4 border-t border-white/10 bg-[#050816]/40 text-[9px] text-gray-500 space-y-1 font-mono uppercase">
            <div className="flex justify-between">
              <span>Simulation:</span>
              <span className="text-green-400">Online</span>
            </div>
            <div className="flex justify-between">
              <span>Wormholes:</span>
              <span className="text-[#ec4899]">153 Active</span>
            </div>
          </div>
        )}
      </aside>

      {/* RIGHT SIDE WORKSPACE VIEWPORT */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* TOP COMMAND BAR HUD */}
        <header className="bg-[#0b1026]/70 border-b border-[#06b6d4]/10 backdrop-blur-md px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4 relative z-30">
          
          {/* Simulation Status indicators */}
          <div className="flex items-center gap-6">
            {/* Speed control buttons */}
            <div className="flex items-center bg-black/40 border border-white/10 rounded px-2 py-1 text-[10px] gap-2">
              <span className="text-gray-500 font-bold">SPEED:</span>
              {(["PAUSED", "1X", "2X", "4X"] as const).map((spd) => (
                <button
                  key={spd}
                  onClick={() => setSimulationSpeed(spd)}
                  className={`px-1.5 py-0.5 rounded transition ${
                    simulationSpeed === spd 
                      ? "bg-[#06b6d4]/20 text-[#06b6d4] font-bold" 
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  {spd}
                </button>
              ))}
            </div>

            {/* Warning Beacon indicator */}
            <div className="flex items-center gap-2 text-[10px] text-yellow-500 animate-pulse bg-yellow-500/10 border border-yellow-500/20 px-2 py-1 rounded">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>SECTOR STABILITY: 94.2%</span>
            </div>
          </div>

          {/* Search Bar + Controls */}
          <div className="flex items-center gap-4 w-full md:w-auto">
            {/* Global Search Bar */}
            <div className="relative w-full md:w-64">
              <input
                type="text"
                placeholder="QUERY COGNITIVE CORE..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setShowDropdown(true)}
                className="w-full bg-black/40 border border-[#06b6d4]/25 rounded p-2 pl-9 text-[10px] text-white focus:outline-none focus:border-[#06b6d4] focus:ring-1 focus:ring-[#06b6d4] uppercase font-mono placeholder-gray-600"
              />
              <Search className="w-3.5 h-3.5 text-gray-500 absolute left-3 top-2.5" />

              {/* Autocomplete Dropdown overlay */}
              {showDropdown && searchResults && (
                <div className="absolute right-0 top-11 w-full bg-[#12161f]/95 border border-[#06b6d4]/30 rounded p-2 max-h-80 overflow-y-auto z-50 shadow-2xl backdrop-blur-md text-[10px] font-mono">
                  <div className="flex justify-between items-center border-b border-white/5 pb-1 mb-2">
                    <span className="text-[8px] text-gray-500">QUERY ENGINE SEARCH</span>
                    <button onClick={() => setShowDropdown(false)} className="text-gray-400 hover:text-white">CLOSE</button>
                  </div>

                  {/* Stars results */}
                  {searchResults.stars?.length > 0 && (
                    <div className="mb-2">
                      <p className="text-[9px] text-[#06b6d4] font-bold uppercase mb-1">Stars</p>
                      {searchResults.stars.map((s: any) => (
                        <button
                          key={s.name}
                          onClick={() => {
                            onSelectStar(s);
                            setActiveTab("system");
                            setShowDropdown(false);
                          }}
                          className="w-full text-left p-1 rounded hover:bg-white/5 text-white"
                        >
                          ✦ {s.name} ({s.star_type})
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Planets results */}
                  {searchResults.planets?.length > 0 && (
                    <div className="mb-2">
                      <p className="text-[9px] text-green-400 font-bold uppercase mb-1">Planets</p>
                      {searchResults.planets.map((p: any) => (
                        <button
                          key={p.planet_id}
                          onClick={() => {
                            onSelectStar({ id: p.star_id, star_id: p.star_id, name: p.planet_name.split("-")[0] });
                            setActiveTab("system");
                            setShowDropdown(false);
                          }}
                          className="w-full text-left p-1 rounded hover:bg-white/5 text-white"
                        >
                          🪐 {p.planet_name}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Empires results */}
                  {searchResults.empires?.length > 0 && (
                    <div className="mb-2">
                      <p className="text-[9px] text-[#ec4899] font-bold uppercase mb-1">Empires</p>
                      {searchResults.empires.map((e: any) => (
                        <button
                          key={e.empire_name}
                          onClick={() => {
                            setActiveTab("empires");
                            setShowDropdown(false);
                          }}
                          className="w-full text-left p-1 rounded hover:bg-white/5 text-white"
                        >
                          🛡️ {e.empire_name}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Events results */}
                  {searchResults.events?.length > 0 && (
                    <div className="mb-2">
                      <p className="text-[9px] text-purple-400 font-bold uppercase mb-1">Events</p>
                      {searchResults.events.map((e: any) => (
                        <button
                          key={e.event_id}
                          onClick={() => {
                            setActiveTab("timeline");
                            setShowDropdown(false);
                          }}
                          className="w-full text-left p-1 rounded hover:bg-white/5 text-gray-300 truncate"
                        >
                          🕒 Yr {e.year}: {e.event_type}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Notification alert hub */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className="bg-black/40 border border-white/10 rounded p-2 text-gray-400 hover:text-white hover:border-[#06b6d4]/50 transition relative"
              >
                <Bell className="w-3.5 h-3.5" />
                <span className="absolute -top-1 -right-1 bg-[#ec4899] text-white text-[8px] px-1 rounded-full animate-bounce">
                  {notifications.length}
                </span>
              </button>
              {showNotifications && (
                <div className="absolute right-0 top-11 w-64 bg-[#12161f] border border-[#06b6d4]/30 rounded p-2 z-50 text-[10px] space-y-1">
                  <p className="text-gray-500 border-b border-white/5 pb-1 uppercase font-bold">Galactic Feed Alerts</p>
                  {notifications.map((n, idx) => (
                    <div key={idx} className="p-1 rounded hover:bg-white/5 text-gray-300">
                      • {n}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Theme Toggle */}
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="bg-black/40 border border-white/10 rounded p-2 text-gray-400 hover:text-white transition"
            >
              {isDarkMode ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
            </button>

            {/* User Profile */}
            <div className="flex items-center gap-2 bg-black/40 border border-white/10 rounded px-2.5 py-1.5 text-[10px]">
              <User className="w-3.5 h-3.5 text-[#06b6d4]" />
              <span className="hidden sm:inline font-bold">ARCHITECT</span>
            </div>

          </div>
        </header>

        {/* MAIN BODY AREA */}
        <div className="flex-1 p-6 overflow-y-auto">
          {children}
        </div>

      </div>

    </div>
  );
};

// Custom Mini Sparkles icon inside layouts
const SparklesIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    fill="none" 
    viewBox="0 0 24 24" 
    strokeWidth={1.5} 
    stroke="currentColor" 
    {...props}
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 21l-.813-5.096L3 15l5.096-.813L9 9l.813 5.187L15 15l-5.187.904zM18 5.25L16.5 6 15 5.25 15.75 3.75 15 2.25 16.5 3 18 2.25l-.75 1.5L18 5.25zM22.5 10.5l-1.5.75-1.5-.75.75-1.5-1.5-1.5 1.5.75 1.5-.75-.75 1.5 1.5 1.5z" />
  </svg>
);
