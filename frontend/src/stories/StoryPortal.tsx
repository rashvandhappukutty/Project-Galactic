// frontend/src/components/StoryPortal.tsx
import React, { useEffect, useState } from "react";
import { BookOpen, Newspaper, FileText, Bookmark } from "lucide-react";

interface NewsArticle {
  article_id: string;
  year: number;
  category: string;
  headline: string;
  body: string;
  spokesperson: string;
}

interface LegendaryStory {
  legendary_type: string;
  year: number;
  empire_involved: string;
  description: string;
  prose_narrative: string;
  impact_score: number;
}

interface Lore {
  lore_type: string;
  title: string;
  text_content: string;
}

export const StoryPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"news" | "books" | "legendary" | "lore">("news");
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [legends, setLegends] = useState<LegendaryStory[]>([]);
  const [lore, setLore] = useState<Lore[]>([]);

  // Simple static sci-fi book database representing books written by story generator
  const books = [
    {
      title: "The Rise and Fall of the Great Unified Imperium",
      category: "Empire Chronicle",
      chapters: [
        { title: "Chapter 1: The Emergence", text: "Out of the star cluster, the citizens built the first FTL hulls, expanding their capital systems and establishing borders." },
        { title: "Chapter 2: The Peak Hegemony", text: "With a booming economy exceeding billions of credits, the empire constructed defensive fleets and research stations." },
        { title: "Chapter 3: The Decline", text: "Wars and hyperinflation drained the treasury. Factions splintered off, leaving only ruins and ancient lore." }
      ]
    },
    {
      title: "The Age of Exploration",
      category: "Era Anthology",
      chapters: [
        { title: "Chapter 1: The Silent Hulls", text: "Before the networks, scouts went alone into deep space, leaving behind beacons to guide future generations." },
        { title: "Chapter 2: The Wormhole Discoveries", text: "The mapping of dangerous sub-space rifts connected distant arms of the galaxy, sparking a colonization rush." }
      ]
    },
    {
      title: "The First Galactic War",
      category: "Military Journal",
      chapters: [
        { title: "Chapter 1: The Spark", text: "A border dispute near FTL gate systems triggered mobilization protocols. The Imperium clashed with their rivals." },
        { title: "Chapter 2: The Deep Space Engagement", text: "Dreadnought and Titan fleets engaged in massive system battles, causing millions of casualties." }
      ]
    }
  ];

  const [selectedBook, setSelectedBook] = useState<typeof books[0] | null>(books[0]);
  const [selectedChapter, setSelectedChapter] = useState<number>(0);

  useEffect(() => {
    // Load News
    fetch("http://localhost:8000/api/news?limit=100")
      .then((res) => res.json())
      .then((data) => setNews(data))
      .catch((err) => console.error("Error loading news:", err));

    // Load Legendary Stories
    fetch("http://localhost:8000/api/stories")
      .then((res) => res.json())
      .then((data) => setLegends(data))
      .catch((err) => console.error("Error loading legendary stories:", err));

    // Load Lore
    fetch("http://localhost:8000/api/lore")
      .then((res) => res.json())
      .then((data) => setLore(data))
      .catch((err) => console.error("Error loading lore database:", err));
  }, []);

  return (
    <div className="glass-panel p-6 rounded-xl flex flex-col h-full min-h-[500px]">
      
      {/* Navigation tabs */}
      <div className="flex border-b border-white/10 pb-3 mb-6 gap-2">
        <button
          onClick={() => setActiveTab("news")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono transition ${
            activeTab === "news" ? "bg-blue-500/20 text-blue-400 border border-blue-500/30" : "text-gray-400 hover:text-white"
          }`}
        >
          <Newspaper className="w-3.5 h-3.5" /> GNN Broadcasts
        </button>
        <button
          onClick={() => setActiveTab("books")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono transition ${
            activeTab === "books" ? "bg-blue-500/20 text-blue-400 border border-blue-500/30" : "text-gray-400 hover:text-white"
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" /> Fictional Library
        </button>
        <button
          onClick={() => setActiveTab("legendary")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono transition ${
            activeTab === "legendary" ? "bg-blue-500/20 text-blue-400 border border-blue-500/30" : "text-gray-400 hover:text-white"
          }`}
        >
          <Bookmark className="w-3.5 h-3.5" /> Legendary Sagas
        </button>
        <button
          onClick={() => setActiveTab("lore")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono transition ${
            activeTab === "lore" ? "bg-blue-500/20 text-blue-400 border border-blue-500/30" : "text-gray-400 hover:text-white"
          }`}
        >
          <FileText className="w-3.5 h-3.5" /> Myths & Legends
        </button>
      </div>

      {/* Tab Contents */}
      <div className="flex-1 overflow-y-auto max-h-[420px] pr-2">
        
        {/* 1. GNN News */}
        {activeTab === "news" && (
          <div className="space-y-4">
            {news.map((item) => (
              <div key={item.article_id} className="bg-space-dark/40 p-4 rounded-lg border border-white/5 font-sans">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] text-yellow-500 font-mono">Year {item.year}</span>
                  <span className="text-[9px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20 px-1.5 py-0.25 rounded">
                    {item.category}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white font-mono">{item.headline}</h4>
                <p className="text-xs text-gray-400 mt-2 leading-relaxed">{item.body}</p>
              </div>
            ))}
          </div>
        )}

        {/* 2. Fictional Library */}
        {activeTab === "books" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full min-h-[350px]">
            {/* Books selection */}
            <div className="border-r border-white/10 pr-4 space-y-2">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 font-mono">Select Book</h4>
              {books.map((b, idx) => (
                <button
                  key={idx}
                  onClick={() => { setSelectedBook(b); setSelectedChapter(0); }}
                  className={`w-full text-left p-2 rounded text-xs font-mono border transition ${
                    selectedBook?.title === b.title ? "bg-blue-500/20 text-blue-400 border-blue-500/25" : "bg-space-dark/20 text-gray-400 border-white/5 hover:text-white"
                  }`}
                >
                  <p className="font-bold">{b.title}</p>
                  <span className="text-[9px] text-gray-500">{b.category}</span>
                </button>
              ))}
            </div>

            {/* Book Reader */}
            {selectedBook && (
              <div className="md:col-span-2 space-y-4 flex flex-col h-full justify-between">
                <div>
                  <h3 className="text-base font-bold text-white mb-1">{selectedBook.title}</h3>
                  <div className="flex border-b border-white/5 pb-2 mb-4 gap-2">
                    {selectedBook.chapters.map((_, idx) => (
                      <button
                        key={idx}
                        onClick={() => setSelectedChapter(idx)}
                        className={`px-2 py-1 rounded text-[10px] font-mono transition ${
                          selectedChapter === idx ? "bg-yellow-500/20 text-yellow-400" : "text-gray-400 hover:text-white"
                        }`}
                      >
                        Chapter {idx + 1}
                      </button>
                    ))}
                  </div>
                  <h4 className="text-xs font-bold text-yellow-500 font-mono mb-2">
                    {selectedBook.chapters[selectedChapter].title}
                  </h4>
                  <p className="text-xs text-gray-300 leading-relaxed font-serif italic bg-space-dark/30 p-4 rounded border border-white/5">
                    {selectedBook.chapters[selectedChapter].text}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 3. Legendary Stories */}
        {activeTab === "legendary" && (
          <div className="space-y-4">
            {legends.map((l, idx) => (
              <div key={idx} className="bg-space-dark/40 p-4 rounded-lg border border-white/5">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] text-yellow-500 font-mono">Year {l.year}</span>
                  <span className="text-[9px] font-mono bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 px-1.5 py-0.25 rounded uppercase">
                    {l.legendary_type}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white font-mono">Epic Saga of {l.empire_involved}</h4>
                <p className="text-xs text-gray-300 mt-2 font-serif leading-relaxed italic">{l.prose_narrative}</p>
                <p className="text-[10px] text-gray-500 mt-2 font-mono">Impact Score: {l.impact_score.toFixed(1)}/100</p>
              </div>
            ))}
          </div>
        )}

        {/* 4. Lore */}
        {activeTab === "lore" && (
          <div className="space-y-4">
            {lore.map((item, idx) => (
              <div key={idx} className="bg-space-dark/40 p-4 rounded-lg border border-white/5">
                <span className="text-[9px] font-mono bg-purple-500/10 text-purple-400 border border-purple-500/20 px-1.5 py-0.25 rounded uppercase">
                  {item.lore_type}
                </span>
                <h4 className="text-sm font-bold text-white font-mono mt-2">{item.title}</h4>
                <p className="text-xs text-gray-400 mt-2 leading-relaxed italic font-serif bg-space-dark/20 p-3 rounded">{item.text_content}</p>
              </div>
            ))}
          </div>
        )}

      </div>

    </div>
  );
};
