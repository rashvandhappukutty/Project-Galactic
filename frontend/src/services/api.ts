// frontend/src/services/api.ts

const API_BASE_URL = "http://localhost:8000/api";

export async function fetchFromAPI(endpoint: string, params: Record<string, any> = {}) {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  Object.keys(params).forEach((key) => {
    if (params[key] !== undefined && params[key] !== null && params[key] !== "") {
      url.searchParams.append(key, String(params[key]));
    }
  });

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`API Error on ${endpoint}: ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  getDashboard: () => fetchFromAPI("/dashboard"),
  getStars: (limit?: number) => fetchFromAPI("/stars", { limit }),
  getStarById: (id: string) => fetchFromAPI(`/stars/${id}`),
  getPlanets: (starId?: string, limit?: number) => fetchFromAPI("/planets", { star_id: starId, limit }),
  getPlanetById: (id: string) => fetchFromAPI(`/planets/${id}`),
  getSpecies: (limit?: number) => fetchFromAPI("/species", { limit }),
  getCivilizations: (limit?: number) => fetchFromAPI("/civilizations", { limit }),
  getEmpires: (limit?: number) => fetchFromAPI("/empires", { limit }),
  getChronicles: (empireName?: string) => fetchFromAPI("/empires/chronicles", { empire_name: empireName }),
  getLifecycles: (empireName?: string) => fetchFromAPI("/empires/lifecycles", { empire_name: empireName }),
  getEconomy: (limit?: number) => fetchFromAPI("/economy", { limit }),
  getFtlRoutes: (limit?: number) => fetchFromAPI("/ftl", { limit }),
  getJumpGates: (limit?: number) => fetchFromAPI("/ftl/gates", { limit }),
  getWormholes: () => fetchFromAPI("/ftl/wormholes"),
  getWars: (limit?: number) => fetchFromAPI("/wars", { limit }),
  getWarReports: (limit?: number) => fetchFromAPI("/wars/reports", { limit }),
  getBattles: (limit?: number) => fetchFromAPI("/wars/battles", { limit }),
  getPeaceTreaties: () => fetchFromAPI("/wars/treaties"),
  getHistory: (category?: string, limit?: number, offset?: number) => fetchFromAPI("/history", { category, limit, offset }),
  getEras: () => fetchFromAPI("/history/eras"),
  getLegendaryStories: (limit?: number) => fetchFromAPI("/stories", { limit }),
  getNews: (limit?: number) => fetchFromAPI("/stories/news", { limit }),
  getLore: () => fetchFromAPI("/stories/lore"),
  getAnalytics: () => fetchFromAPI("/analytics"),
  getFigures: (limit?: number) => fetchFromAPI("/analytics/figures", { limit }),
  search: (query: string) => fetchFromAPI("/search", { q: query }),
  getHealth: () => fetchFromAPI("/health")
};
export default api;
