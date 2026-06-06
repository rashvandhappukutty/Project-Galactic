// frontend/src/App.tsx
import { useEffect, useState } from "react";
import { AppLayout } from "./layouts/AppLayout";
import { Dashboard } from "./pages/Dashboard";
import { GalaxyExplorer } from "./pages/GalaxyExplorer";
import { StarSystem } from "./pages/StarSystem";
import { EmpireExplorer } from "./pages/EmpireExplorer";
import { Timeline } from "./pages/Timeline";
import { StoryExplorer } from "./pages/StoryExplorer";
import { SpeciesCatalog } from "./pages/SpeciesCatalog";
import { Civilizations } from "./pages/Civilizations";
import { EconomyTrade } from "./pages/EconomyTrade";
import { TradeRoutes } from "./pages/TradeRoutes";
import { FtlNetwork } from "./pages/FtlNetwork";
import { Diplomacy } from "./pages/Diplomacy";
import { Wars } from "./pages/Wars";
import { HistoricalFigures } from "./pages/HistoricalFigures";
import { ResearchLab } from "./pages/ResearchLab";
import { SettingsPage } from "./pages/SettingsPage";
import api from "./services/api";

interface Star {
  id?: string;
  star_id?: string;
  name: string;
  x: number;
  y: number;
  z: number;
  star_type: string;
}

type TabType = 
  | "dashboard" | "explorer" | "system" | "species" | "civilizations" 
  | "empires" | "economy" | "trade_routes" | "ftl" | "diplomacy" 
  | "wars" | "timeline" | "stories" | "rankings" | "research" | "settings";

export default function App() {
  const [stars, setStars] = useState<Star[]>([]);
  const [selectedStar, setSelectedStar] = useState<Star | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any>(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    api.getStars()
      .then((data) => {
        setStars(data);
        if (data.length > 0) setSelectedStar(data[0]);
      })
      .catch((err) => console.error("Error loading stars:", err));
  }, []);

  // Global search handler
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults(null);
      return;
    }
    const delayDebounceFn = setTimeout(() => {
      api.search(searchQuery)
        .then((data) => {
          setSearchResults(data);
          setShowDropdown(true);
        })
        .catch((err) => console.error("Search error:", err));
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  return (
    <AppLayout
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      searchResults={searchResults}
      showDropdown={showDropdown}
      setShowDropdown={setShowDropdown}
      onSelectStar={(star) => setSelectedStar(star)}
    >
      {activeTab === "dashboard" && (
        <Dashboard 
          stars={stars}
          selectedStar={selectedStar}
          setSelectedStar={(star) => setSelectedStar(star)}
        />
      )}

      {activeTab === "explorer" && (
        <GalaxyExplorer
          stars={stars}
          selectedStar={selectedStar}
          setSelectedStar={(star) => setSelectedStar(star)}
        />
      )}

      {activeTab === "system" && (
        <StarSystem
          selectedStar={selectedStar}
          stars={stars}
          setSelectedStar={(star) => setSelectedStar(star)}
        />
      )}

      {activeTab === "species" && <SpeciesCatalog />}

      {activeTab === "civilizations" && <Civilizations />}

      {activeTab === "empires" && <EmpireExplorer />}

      {activeTab === "economy" && <EconomyTrade />}

      {activeTab === "trade_routes" && <TradeRoutes />}

      {activeTab === "ftl" && <FtlNetwork />}

      {activeTab === "diplomacy" && <Diplomacy />}

      {activeTab === "wars" && <Wars />}

      {activeTab === "timeline" && <Timeline />}

      {activeTab === "stories" && <StoryExplorer />}

      {activeTab === "rankings" && <HistoricalFigures />}

      {activeTab === "research" && <ResearchLab />}

      {activeTab === "settings" && <SettingsPage />}
    </AppLayout>
  );
}
