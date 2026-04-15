# CLAUDE.md

VibeCFD — Agent-friendly CFD research automation framework.

## How Agents Use This Repo

This repo is structured for AI agents to conduct CFD research autonomously. Every decision an agent makes is constrained by YAML rules files, validated against schemas, and follows pre-defined workflows.

### Decision Flow

```
User describes problem
  → Agent reads prompts/setup-case.md
  → Agent selects solver via adapters/{solver}.yaml → solver_map
  → Agent checks rules via skills/{solver}/rules.yaml
  → Agent generates case YAML conforming to schema/case.schema.yaml
  → Agent validates with tools/validate-case.py
  → Agent runs workflow (workflows/full-study.yaml)
  → Agent reviews results via prompts/review-results.md
  → Agent exports report via templates/latex/
```

### Key Principle: Rules > Intuition

Agents MUST NOT rely on training data for CFD parameters. Instead:
- **Solver selection** → `adapters/{solver}.yaml` → `solver_map`
- **Turbulence model** → `skills/openfoam/rules.yaml` → `turbulence_models`
- **Boundary conditions** → `skills/{solver}/rules.yaml` → `boundary_conditions`
- **Numerical schemes** → `skills/{solver}/rules.yaml` → `numerical_schemes`
- **Mesh quality** → `skills/mesh/rules.yaml` → `quality_thresholds`
- **Post-processing** → `skills/post/rules.yaml` → `visualization`
- **Validation data** → `benchmarks/{name}/benchmark.yaml`

## Directory Structure

```
schema/                    # Input validation schemas
├── case.schema.yaml       # Case definition schema (all fields, types, constraints)
└── workflow.schema.yaml   # Workflow pipeline schema

adapters/                  # Solver adapters (case schema → solver-specific files)
├── openfoam.yaml          # OpenFOAM: directory layout, commands, log parsing
├── lbm.yaml               # Palabos: unit conversion, compilation, execution
└── sph.yaml               # DualSPHysics: XML config, GPU/CPU execution

skills/                    # Solver and tool rules (AI agent constraints)
├── openfoam/rules.yaml    # Solver selection, turbulence, BCs, schemes, convergence
├── lbm/rules.yaml         # Lattice, collision, Ma constraint, resolution
├── sph/rules.yaml         # Kernel, spacing, time integration, EOS
├── fem/rules.yaml         # Elements, stabilization, solver strategy
├── mesh/rules.yaml        # y+ guidelines, generators, quality thresholds
└── post/rules.yaml        # Visualization, color maps, figure quality, LaTeX

benchmarks/                # Reference data for validation
├── ghia-1982/             # Lid-driven cavity (u,v profiles at Re=100-10000)
├── turek-1996/            # Cylinder flow (Cd, Cl, St at Re=20,100)
├── martin-moyce-1952/     # Dam break (front position, column height)
└── erturk-2005/           # High-Re cavity (vortex center locations)

workflows/                 # Pre-defined execution pipelines
├── full-study.yaml        # Mesh study + validation + post + report
├── quick-validate.yaml    # Single run + benchmark comparison
└── parameter-sweep.yaml   # Multi-case parameter exploration

prompts/                   # Agent instruction templates
├── discover.md            # Find under-explored CFD problems
├── setup-case.md          # Generate case YAML from problem description
├── diagnose.md            # Debug failed/diverging simulations
└── review-results.md      # Quality review before publication

tools/                     # CLI utilities
├── checkenv.sh            # Verify solver/tool installation
├── validate-case.py       # Validate case YAML against schema + rules
└── parse-residuals.py     # Extract convergence data from solver logs

templates/latex/           # Publication templates
├── article.tex            # Journal article (Elsevier-compatible)
└── report.tex             # Technical report with solver config appendix

examples/                  # Ready-to-run case configurations
├── lid-driven-cavity.yaml
├── cylinder-vortex-shedding.yaml
├── backward-facing-step.yaml
├── dam-break-sph.yaml
└── natural-convection.yaml
```

## Agent Commands

```bash
# Check environment
bash tools/checkenv.sh

# Validate a case before running
python3 tools/validate-case.py examples/lid-driven-cavity.yaml

# Parse solver output
python3 tools/parse-residuals.py log.simpleFoam --plot
python3 tools/parse-residuals.py log.simpleFoam --csv > residuals.csv
```

## Adding New Solvers

1. Create `skills/{solver}/rules.yaml` with selection rules and constraints
2. Create `adapters/{solver}.yaml` with command pipeline and log parsing
3. Add benchmark data to `benchmarks/` if available
4. Add example case to `examples/`
5. Test: `python3 tools/validate-case.py examples/{new-case}.yaml`

## Adding New Benchmarks

1. Create `benchmarks/{author-year}/benchmark.yaml`
2. Include: citation, DOI, problem type, validation data arrays, acceptance criteria
3. Data format: column names + array of [x, y] pairs
4. Reference the benchmark ID in example case `validation.benchmark` field
