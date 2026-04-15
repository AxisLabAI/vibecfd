# VibeCFD

AI-powered auto research starter kit for computational fluid dynamics.

Discover CFD research problems and run simulations automatically. VibeCFD supports OpenFOAM, LBM, SPH — from mesh generation to publication-ready results, all AI-driven.

## Quick Start

```bash
# Clone
git clone https://github.com/axislabai/vibecfd.git
cd vibecfd

# Run a classic benchmark
vibecfd run examples/lid-driven-cavity.yaml

# Discover research problems
vibecfd discover --domain "turbulent-combustion" --limit 10

# Export results to LaTeX
vibecfd export --format latex --template templates/latex/article.tex
```

## Skills System

VibeCFD uses a modular **skills system** — each solver and tool has its own skill file defining rules, constraints, and best practices that the AI agent follows.

```
skills/
├── openfoam/       # OpenFOAM solver rules & case templates
│   ├── rules.yaml  # Solver selection, BC validation, scheme rules
│   └── templates/  # blockMeshDict, controlDict, fvSchemes templates
├── lbm/            # Lattice Boltzmann method constraints
├── sph/            # Smoothed Particle Hydrodynamics rules
├── fem/            # Finite Element method rules
├── mesh/           # Mesh generation rules (Gmsh, blockMesh, snappyHexMesh)
└── post/           # Post-processing rules (ParaView, gnuplot, matplotlib)
```

## Templates

```
templates/
└── latex/
    ├── article.tex       # Journal article template
    ├── report.tex        # Technical report template
    └── figures/          # Figure generation scripts
```

## Solver Support

| Solver | Method | Status | Best For |
|--------|--------|--------|----------|
| OpenFOAM | FVM | Active | General-purpose, industrial |
| Palabos | LBM | Active | Multiphase, porous media |
| DualSPHysics | SPH | Active | Free-surface, wave-structure |
| FEniCS | FEM | Planned | Structural coupling, FSI |

## License

MIT
