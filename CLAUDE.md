# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a NeetCode 250 study plan generator that creates a structured 125-day coding interview preparation schedule. The project processes the complete NeetCode 250 problem set and generates a markdown-formatted study plan with intelligent category distribution and spaced repetition.

## Core Architecture

### Data Structure
- **neetcode_250_complete.json**: Master dataset containing all 250 problems with metadata (name, difficulty, category, URLs, slug)
- **Problem categories**: Arrays & Hashing, Two Pointers, Sliding Window, Stack, Binary Search, Linked List, Trees, Heap/Priority Queue, Backtracking, Tries, Graphs, Advanced Graphs, 1-D Dynamic Programming, 2-D Dynamic Programming, Greedy, Intervals, Math & Geometry, Bit Manipulation

### Generator Scripts
- **generate_fixed_125_day_plan.py**: Main generator creating optimal 125-day plan with all 250 problems

### Plan Generation Strategy
1. **Same Category Focus**: Both daily problems from same category when possible for pattern recognition
2. **Spaced Repetition**: Categories cycle with intelligent spacing to optimize retention
3. **Difficulty Progression**: Days 1-30 focus on Easy problems, Days 30-80 mix Easy/Medium, Days 80+ emphasize Medium/Hard
4. **Category Weighting**: Easier categories appear earlier, advanced topics later in the plan
5. **Complete Coverage**: Algorithm ensures all 250 problems are included

## Common Commands

### Generate Study Plan
```bash
# Generate the complete 125-day plan
python3 generate_fixed_125_day_plan.py
```

### Data Inspection
```bash
# View problem data structure
head -n 50 neetcode_250_complete.json

# Check generated plan
ls -la *.md
```

## File Structure

- **Data**: `neetcode_250_complete.json` (master problem dataset)
- **Generated Plan**: `NeetCode_250_Complete_Fixed_125_Day_Plan.md` (final study plan)
- **Scripts**: `generate_fixed_125_day_plan.py`
- **Documentation**: `CLAUDE.md` (this file)

## Key Features

### Intelligent Category Distribution
- Categories weighted by difficulty and day progression
- Spaced repetition with 6-day penalty for recently used categories
- Preference for categories with 2+ available problems

### Difficulty Progression
- **Days 1-30**: Mostly Easy problems with some Medium
- **Days 31-80**: Mixed Easy/Medium with some Hard
- **Days 81-125**: Emphasis on Medium/Hard problems

### Quality Assurance
- Verification that all 250 problems are included
- Statistics on category focus and difficulty distribution
- Analysis of plan effectiveness across different phases

## Development Notes

- Uses `random.seed(42)` for reproducible plan generation
- All Python scripts use shebang `#!/usr/bin/env python3`
- Generated markdown includes checkboxes for progress tracking
- Plan starts from 2025-01-01 with sequential dating
- Problem difficulty indicated with emoji: 🟢 Easy, 🟡 Medium, 🔴 Hard