#!/usr/bin/env python3
"""
Validate a VibeCFD case YAML against the schema and solver rules.

Usage:
    python3 tools/validate-case.py examples/lid-driven-cavity.yaml
    python3 tools/validate-case.py my-case.yaml --strict
"""

import argparse
import sys
from pathlib import Path

import yaml


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def validate_required_fields(case: dict) -> list[str]:
    """Check all required top-level fields exist."""
    errors = []
    required = ['name', 'description', 'type', 'regime', 'geometry',
                 'flow_conditions', 'solver', 'mesh', 'boundary_conditions']
    for field in required:
        if field not in case:
            errors.append(f"Missing required field: {field}")
    return errors


def validate_solver_consistency(case: dict, rules_dir: Path) -> list[str]:
    """Check solver config matches rules."""
    errors = []
    solver = case.get('solver', {})
    engine = solver.get('engine', solver.get('name', ''))

    # Check Re vs turbulence
    fc = case.get('flow_conditions', {})
    re = fc.get('reynolds_number', 0)
    turb = solver.get('turbulence', 'laminar')

    if re > 2300 and turb == 'laminar':
        errors.append(f"WARNING: Re={re} > 2300 but turbulence='laminar'. "
                      "Consider using a turbulence model.")

    if re < 500 and turb != 'laminar':
        errors.append(f"WARNING: Re={re} < 500 with turbulence='{turb}'. "
                      "Laminar is likely sufficient.")

    # Check CFL
    max_co = solver.get('max_courant', 1.0)
    if solver.get('type') == 'transient' and max_co > 1.0:
        if 'pimple' not in engine.lower():
            errors.append(f"CFL={max_co} > 1.0 with non-PIMPLE solver. "
                          "Reduce timestep or use PIMPLE.")

    return errors


def validate_mesh(case: dict) -> list[str]:
    """Check mesh configuration."""
    errors = []
    mesh = case.get('mesh', {})

    if 'refinement_levels' not in mesh:
        errors.append("WARNING: No refinement_levels defined. "
                      "Mesh independence study will not be possible.")
    elif len(mesh.get('refinement_levels', [])) < 3:
        errors.append("WARNING: Need at least 3 refinement levels for GCI study.")

    return errors


def validate_boundary_conditions(case: dict) -> list[str]:
    """Check boundary conditions are physically consistent."""
    errors = []
    bcs = case.get('boundary_conditions', {})

    has_inlet = any(bc.get('type') == 'inlet' for bc in bcs.values()) if isinstance(bcs, dict) else False
    has_outlet = any(bc.get('type') == 'outlet' for bc in bcs.values()) if isinstance(bcs, dict) else False
    has_wall = any(bc.get('type') in ('wall', 'movingWall', 'fixedWall')
                   for bc in bcs.values()) if isinstance(bcs, dict) else False

    dim = case.get('dimensionality', '3D')
    if dim == '2D':
        has_empty = any(bc.get('type') == 'empty' for bc in bcs.values()) if isinstance(bcs, dict) else False
        if not has_empty:
            errors.append("2D case must have 'empty' boundary condition on front/back patches.")

    return errors


def main():
    parser = argparse.ArgumentParser(description='Validate VibeCFD case YAML')
    parser.add_argument('case_file', help='Path to case YAML file')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    args = parser.parse_args()

    case_path = Path(args.case_file)
    if not case_path.exists():
        print(f"Error: {case_path} not found", file=sys.stderr)
        sys.exit(1)

    case = load_yaml(case_path)
    rules_dir = Path(__file__).parent.parent / 'skills'

    all_errors = []
    all_errors.extend(validate_required_fields(case))
    all_errors.extend(validate_solver_consistency(case, rules_dir))
    all_errors.extend(validate_mesh(case))
    all_errors.extend(validate_boundary_conditions(case))

    warnings = [e for e in all_errors if e.startswith('WARNING:')]
    errors = [e for e in all_errors if not e.startswith('WARNING:')]

    if args.strict:
        errors.extend(warnings)
        warnings = []

    for w in warnings:
        print(f"  ⚠ {w}")
    for e in errors:
        print(f"  ✗ {e}")

    if not errors and not warnings:
        print(f"  ✓ {case_path.name} is valid")

    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"\n0 errors, {len(warnings)} warning(s)")
        sys.exit(0)


if __name__ == '__main__':
    main()
