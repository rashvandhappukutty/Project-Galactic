# The Galactic Dream Engine

> **Simulating Humanity's Journey Across the Milky Way.**

The Galactic Dream Engine is a large-scale, astrophysically grounded, procedural galactic civilization simulator designed to model the evolution, colonization, and expansion of civilizations across a procedurally generated Milky Way galaxy.

---

## Phase 1: Galaxy Generation Foundation

This repository contains the Phase 1 foundation, focusing on the astrophysical generation and 3D visualization of a spiral galaxy containing procedurally modeled stellar systems.

### Features
- **Procedural Galaxy Modeling**: Implements density-wave-inspired logarithmic spiral arms and central triaxial bar bulge dynamics.
- **Morgan-Keenan Classifications**: Distributes O, B, A, F, G, K, M stellar spectral classes based on realistic local Milky Way frequencies.
- **Correlated Physics**: Generates physically consistent mass, temperature, and luminosity scaling relationships for main sequence stars.
- **Deterministic Registries**: Seed-based generation ensures reproducibility, featuring hybrid catalog nomenclature (Bayer, HD, HIP, Kepler, GDE, and legendary lore designations).
- **Interactive Visualizations**: High-fidelity 3D and 2D matplotlib plotting, and a fully interactive WebGL-based Plotly 3D HTML space visualization.
- **Stellar Database**: Exports structured tabular catalogs to `datasets/stars.csv`.
- **Validation Suite**: 100% test coverage for physical boundaries, coordinate bounds, serialization, and deterministic generation.

---

## Directory Structure

```
Galactic-Dream-Engine/
├── backend/                  # API and backend service architecture
├── frontend/                 # Web interface and interactive canvases
├── simulation/               # Core physics engine
│   └── galaxy/               # Galaxy generation, stars database & visuals
├── datasets/                 # Tabular stellar registers and visual plots
├── notebooks/                # Architectural analysis and prototyping
├── docs/                     # Physics models and specifications
├── tests/                    # Simulation validation suites
└── run_simulation.py         # Entry point runner script
```

---

## Getting Started

### Prerequisites
- Python 3.8+ (tested on Python 3.13.9)

### Setup & Installation

1. **Clone the Repository**:
   ```bash
   git clone git@github.com:rashvandhappukutty/Project-Galactic-.git
   cd Project-Galactic-
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   # On Unix/macOS
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Simulator

Execute the main pipeline runner to generate the database and recreate visual reports:
```bash
python run_simulation.py
```

Outputs will be saved in the `datasets/` folder:
- **Tabular Stars Database**: `datasets/stars.csv`
- **Static Orthographic Top-Down View**: `datasets/galaxy_top_down.png`
- **Population Distribution Stats Dashboard**: `datasets/galaxy_stats.png`
- **Interactive WebGL 3D Viewer**: `datasets/galaxy_interactive_3d.html`

### Running the Test Suite

Validate the astrophysical equations and code stability using `unittest`:
```bash
python -m unittest discover -s tests
```
