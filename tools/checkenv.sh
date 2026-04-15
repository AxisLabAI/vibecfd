#!/bin/bash
# VibeCFD Environment Check
# Verifies all required tools are installed and accessible.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
warn=0
fail=0

check() {
  local name="$1" cmd="$2" required="${3:-true}"
  if eval "$cmd" >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} $name"
    ((pass++))
  elif [ "$required" = "true" ]; then
    echo -e "  ${RED}✗${NC} $name (REQUIRED)"
    ((fail++))
  else
    echo -e "  ${YELLOW}○${NC} $name (optional)"
    ((warn++))
  fi
}

echo "VibeCFD Environment Check"
echo "========================="
echo ""

echo "Core tools:"
check "Python 3.10+"       "python3 -c 'import sys; assert sys.version_info >= (3,10)'"
check "pip"                "pip3 --version"
check "Git"                "git --version"

echo ""
echo "CFD Solvers:"
check "OpenFOAM"           "simpleFoam -help 2>&1 | grep -q Usage"  false
check "Palabos"            "test -n \"\${PALABOS_ROOT:-}\" && test -d \"\$PALABOS_ROOT\""  false
check "DualSPHysics"       "test -n \"\${DSPH_HOME:-}\" && test -d \"\$DSPH_HOME\""  false
check "FEniCS"             "python3 -c 'import fenics'"  false

echo ""
echo "Mesh tools:"
check "blockMesh"          "which blockMesh"  false
check "snappyHexMesh"      "which snappyHexMesh"  false
check "Gmsh"               "gmsh --version"  false
check "cfMesh"             "which cartesianMesh"  false

echo ""
echo "Post-processing:"
check "ParaView (pvpython)" "pvpython --version"  false
check "gnuplot"            "gnuplot --version"  false
check "matplotlib"         "python3 -c 'import matplotlib'"  false
check "numpy"              "python3 -c 'import numpy'"
check "pandas"             "python3 -c 'import pandas'"  false
check "PyYAML"             "python3 -c 'import yaml'"

echo ""
echo "LaTeX:"
check "pdflatex"           "pdflatex --version"  false
check "bibtex"             "bibtex --version"  false
check "latexmk"            "latexmk --version"  false

echo ""
echo "HPC:"
check "MPI (mpirun)"       "mpirun --version"  false
check "SLURM (sbatch)"     "sbatch --version"  false

echo ""
echo "========================="
echo -e "Results: ${GREEN}${pass} passed${NC}, ${YELLOW}${warn} optional missing${NC}, ${RED}${fail} required missing${NC}"

if [ $fail -gt 0 ]; then
  echo -e "\n${RED}Some required tools are missing. Install them before running VibeCFD.${NC}"
  exit 1
else
  echo -e "\n${GREEN}Environment is ready.${NC}"
  exit 0
fi
