# CLAUDE.md

VibeCFD — AI-powered CFD research automation toolkit.

## Project Structure

```
skills/          # Solver and tool skill definitions (rules, constraints, templates)
templates/       # LaTeX and report templates
examples/        # Example case configurations
docs/            # Documentation
```

## Skills System

Each skill is a YAML file that defines rules the AI agent must follow when working with a specific solver or tool. Skills are loaded on demand based on the simulation context.

- `skills/openfoam/rules.yaml` — OpenFOAM solver selection, boundary conditions, numerical schemes
- `skills/lbm/rules.yaml` — Lattice Boltzmann method constraints
- `skills/sph/rules.yaml` — SPH particle method rules
- `skills/mesh/rules.yaml` — Mesh generation guidelines
- `skills/post/rules.yaml` — Post-processing and visualization rules

## Key Rules

- All simulation cases must be validated against benchmark data before publication
- Mesh independence study is mandatory for any new geometry
- Convergence criteria: residuals < 1e-5 for steady-state, CFL < 1.0 for transient
- Results must include uncertainty quantification
- LaTeX output follows journal submission standards
