#!/usr/bin/env python3
"""
Generate a fixed 125-day NeetCode study plan that includes ALL 250 problems.
Uses same category per day with spaced repetition and intelligent category ordering.
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict, deque

def load_problems():
    """Load all 250 problems from JSON file."""
    with open('neetcode_250_complete.json', 'r') as f:
        data = json.load(f)
    return data['problems']

def organize_problems_by_category_and_difficulty(problems):
    """Organize problems by category and difficulty."""
    category_problems = defaultdict(lambda: {'Easy': [], 'Medium': [], 'Hard': []})

    for problem in problems:
        category = problem['category']
        difficulty = problem['difficulty']
        category_problems[category][difficulty].append(problem)

    return category_problems

def calculate_category_weights(day, category_order, category_problems, category_usage_history, category_progress):
    """
    Calculate weights for category selection based on:
    1. Day progression (easier categories get higher weight early)
    2. Spaced repetition (categories used recently get lower weight)
    3. Category availability (categories with remaining problems)
    """
    weights = {}

    # Base weight based on category difficulty order and day progression
    for i, category in enumerate(category_order):
        # Early days favor easier categories, later days favor harder ones
        position_in_order = i / len(category_order)
        day_progress = day / 125

        # Calculate base weight based on category difficulty and day
        if day_progress < 0.25:  # First 25% of days (1-31)
            base_weight = 1.0 - (position_in_order * 0.8)  # Heavily favor early categories
        elif day_progress < 0.5:  # Second 25% of days (32-62)
            base_weight = 1.0 - (position_in_order * 0.6)  # Moderate favor to early categories
        elif day_progress < 0.75:  # Third 25% of days (63-93)
            base_weight = 0.3 + (position_in_order * 0.5)  # Gradual transition to later categories
        else:  # Final 25% of days (94-125)
            base_weight = position_in_order + 0.2  # Favor later categories

        # Check remaining problems in category
        remaining_problems = 0
        for difficulty in ['Easy', 'Medium', 'Hard']:
            available = len(category_problems[category][difficulty])
            used = category_progress[category][difficulty]
            remaining_problems += max(0, available - used)

        # Boost weight if category has many remaining problems
        if remaining_problems > 4:
            base_weight *= 1.2
        elif remaining_problems == 0:
            base_weight = 0  # No problems left

        weights[category] = max(0.05, base_weight)  # Minimum weight of 0.05

    # Apply spaced repetition penalty
    recent_usage_penalty = 0.6
    for i, recent_category in enumerate(category_usage_history):
        if i < 6:  # Last 6 uses get penalty (more recent = higher penalty)
            penalty = recent_usage_penalty * (1 - i/6)
            if recent_category in weights:
                weights[recent_category] = max(0.02, weights[recent_category] - penalty)

    return weights

def select_category_for_day(day, category_order, category_problems, category_usage_history, category_progress, used_problems):
    """
    Select a single category for the day. Tries to find categories with 2+ problems,
    but will accept categories with 1 problem if needed to ensure all problems are used.
    """
    # Calculate category weights
    category_weights = calculate_category_weights(day, category_order, category_problems, category_usage_history, category_progress)

    # First, try to find categories that have at least 2 available problems
    available_categories_2plus = []
    available_categories_1plus = []

    for category in category_order:
        total_available = 0
        for difficulty in ['Easy', 'Medium', 'Hard']:
            available_problems = category_problems[category][difficulty]
            progress = category_progress[category][difficulty]

            # Count problems not yet used
            for problem in available_problems[progress:]:
                if problem['name'] not in used_problems:
                    total_available += 1

        if total_available >= 2:
            available_categories_2plus.append(category)
        elif total_available >= 1:
            available_categories_1plus.append(category)

    # Prefer categories with 2+ problems, fallback to 1+ if needed
    if available_categories_2plus:
        available_categories = available_categories_2plus
    elif available_categories_1plus:
        available_categories = available_categories_1plus
    else:
        return None

    # Weight-based selection from available categories
    available_weights = [category_weights.get(cat, 0.05) for cat in available_categories]

    # Normalize weights and select
    total_weight = sum(available_weights)
    if total_weight > 0:
        probabilities = [w/total_weight for w in available_weights]
        selected_category = random.choices(available_categories, weights=probabilities)[0]
    else:
        selected_category = random.choice(available_categories)

    return selected_category

def select_problems_for_day(day, selected_category, category_problems, used_problems, category_progress):
    """
    Select up to 2 problems from the selected category for the day.
    Maintains difficulty progression and ensures no duplicates.
    """
    day_problems = []

    # Determine difficulty preference based on day
    if day < 30:  # First 30 days: mostly easy with some medium
        difficulty_preferences = [
            ['Easy', 'Medium', 'Hard'],  # First problem preference
            ['Easy', 'Easy', 'Medium'] if day % 3 != 0 else ['Medium', 'Easy', 'Hard']  # Second problem
        ]
    elif day < 80:  # Days 30-80: mix of easy/medium with some hard
        difficulty_preferences = [
            ['Easy', 'Medium', 'Hard'],  # First problem preference
            ['Medium', 'Easy', 'Hard']   # Second problem preference
        ]
    else:  # Final days: more medium/hard
        difficulty_preferences = [
            ['Medium', 'Hard', 'Easy'],  # First problem preference
            ['Medium', 'Hard', 'Easy']   # Second problem preference
        ]

    # Select up to 2 problems from the category
    for problem_num in range(2):
        selected_problem = None

        if problem_num < len(difficulty_preferences):
            difficulty_order = difficulty_preferences[problem_num]
        else:
            difficulty_order = ['Easy', 'Medium', 'Hard']

        # Try to find a problem with preferred difficulty
        for difficulty in difficulty_order:
            available_problems = category_problems[selected_category][difficulty]

            # Look through all problems in this difficulty, not just from progress point
            for problem in available_problems:
                if problem['name'] not in used_problems:
                    selected_problem = problem
                    used_problems.add(problem['name'])
                    break

            if selected_problem:
                break

        # If no problem found with preferred difficulty, try any remaining problem in category
        if not selected_problem:
            for difficulty in ['Easy', 'Medium', 'Hard']:
                available_problems = category_problems[selected_category][difficulty]
                for problem in available_problems:
                    if problem['name'] not in used_problems:
                        selected_problem = problem
                        used_problems.add(problem['name'])
                        break
                if selected_problem:
                    break

        if selected_problem:
            day_problems.append(selected_problem)
        else:
            break  # No more problems available in this category

    return day_problems

def generate_fixed_125_day_plan(problems, start_date):
    """Generate a fixed 125-day plan that includes ALL 250 problems."""

    # Define category order (from easiest to hardest)
    category_order = [
        "Arrays & Hashing",
        "Two Pointers",
        "Sliding Window",
        "Stack",
        "Binary Search",
        "Linked List",
        "Trees",
        "Heap / Priority Queue",
        "Backtracking",
        "Tries",
        "Graphs",
        "Advanced Graphs",
        "1-D Dynamic Programming",
        "2-D Dynamic Programming",
        "Greedy",
        "Intervals",
        "Math & Geometry",
        "Bit Manipulation"
    ]

    # Organize problems
    category_problems = organize_problems_by_category_and_difficulty(problems)

    # Initialize tracking variables
    plan = []
    used_problems = set()
    category_usage_history = deque(maxlen=10)  # Track recent category usage
    category_progress = {cat: {'Easy': 0, 'Medium': 0, 'Hard': 0} for cat in category_order}

    # Generate plan - continue until all problems are used
    day = 0
    max_days = 150  # Safety limit to prevent infinite loops

    while len(used_problems) < 250 and day < max_days:
        current_date = start_date + timedelta(days=day)

        # Select category for this day
        selected_category = select_category_for_day(
            day, category_order, category_problems, category_usage_history, category_progress, used_problems
        )

        if selected_category:
            # Select problems from this category
            day_problems = select_problems_for_day(
                day, selected_category, category_problems, used_problems, category_progress
            )

            if day_problems:
                plan.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'day': day + 1,
                    'problems': day_problems,
                    'category': selected_category
                })

                # Update category usage history
                if selected_category in category_usage_history:
                    category_usage_history.remove(selected_category)
                category_usage_history.appendleft(selected_category)

                day += 1
            else:
                # No problems found, try a different approach
                print(f"Warning: No problems found for {selected_category} on day {day + 1}")
                day += 1
        else:
            # No category available, this shouldn't happen if we have problems left
            print(f"Warning: No category available on day {day + 1}, {250 - len(used_problems)} problems remaining")
            break

    # If we still have problems left, add them to remaining days
    if len(used_problems) < 250 and day < max_days:
        remaining_problems = []
        for category, difficulties in category_problems.items():
            for difficulty, problems_list in difficulties.items():
                for problem in problems_list:
                    if problem['name'] not in used_problems:
                        remaining_problems.append(problem)

        # Add remaining problems, 2 per day
        while remaining_problems and day < max_days:
            current_date = start_date + timedelta(days=day)
            day_problems = []

            # Take up to 2 problems
            for _ in range(min(2, len(remaining_problems))):
                problem = remaining_problems.pop(0)
                day_problems.append(problem)
                used_problems.add(problem['name'])

            if day_problems:
                # Determine category (use first problem's category or "Mixed" if different)
                categories = list(set(p['category'] for p in day_problems))
                category = categories[0] if len(categories) == 1 else "Mixed"

                plan.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'day': day + 1,
                    'problems': day_problems,
                    'category': category
                })

                day += 1

    return plan

def analyze_plan_distribution(plan):
    """Analyze the distribution of categories and difficulties throughout the plan."""

    # Track category distribution over time
    category_by_phase = {'Early (1-30)': defaultdict(int),
                        'Middle (31-80)': defaultdict(int),
                        'Late (81-125)': defaultdict(int)}

    difficulty_by_phase = {'Early (1-30)': defaultdict(int),
                          'Middle (31-80)': defaultdict(int),
                          'Late (81-125)': defaultdict(int)}

    category_progression = []

    for day_plan in plan:
        day_num = day_plan['day']
        problems = day_plan['problems']
        category = day_plan.get('category', 'Unknown')

        # Track category progression
        category_progression.append((day_num, category))

        # Determine phase
        if day_num <= 30:
            phase = 'Early (1-30)'
        elif day_num <= 80:
            phase = 'Middle (31-80)'
        else:
            phase = 'Late (81-125)'

        # Track categories and difficulties
        category_by_phase[phase][category] += 1
        for problem in problems:
            difficulty_by_phase[phase][problem['difficulty']] += 1

    return category_by_phase, difficulty_by_phase, category_progression

def generate_markdown_plan(plan):
    """Generate markdown for the fixed 125-day plan."""
    markdown = "# NeetCode 250 - Complete 125-Day Study Plan (All 250 Problems)\n\n"
    markdown += "**Enhanced Study Strategy:**\n"
    markdown += "- 2 problems per day for 125 days (both from the same category when possible)\n"
    markdown += "- ALL 250 problems included with no gaps\n"
    markdown += "- Spaced repetition: Categories cycle with intelligent spacing to optimize retention\n"
    markdown += "- Progressive difficulty: Early days focus on Easy, gradually increasing complexity\n"
    markdown += "- Category focus: Daily concentration on single topics for deeper pattern recognition\n"
    markdown += "- Intelligent timing: Easier categories appear earlier, advanced topics later in the plan\n\n"
    markdown += "---\n\n"

    for day_plan in plan:
        date = day_plan['date']
        day_num = day_plan['day']
        problems = day_plan['problems']
        category = day_plan.get('category', 'Mixed')

        markdown += f"## Day {day_num} - {date}\n"
        markdown += f"**Topic:** {category}\n\n"
        markdown += "**Problems:**\n"

        for problem in problems:
            difficulty_emoji = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}[problem['difficulty']]
            markdown += f"- [ ] {difficulty_emoji} [{problem['name']}]({problem['leetcode_url']}) - *{problem['category']}*\n"

        markdown += "\n"

    return markdown

def get_start_date():
    """Get the start date from user input."""
    print("📅 When would you like to start your 125-day study plan?")
    print("Examples:")
    print("  - 2025-01-01 (New Year)")
    print("  - today (starts today)")
    print("  - monday (starts next Monday)")
    print("  - Press Enter for default (next Monday)")

    while True:
        try:
            date_input = input("\nEnter start date (YYYY-MM-DD, 'today', 'monday', or Enter for default): ").strip().lower()

            if date_input == '' or date_input == 'monday':
                # Default to next Monday
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                days_ahead = 0 - today.weekday()  # Monday is 0
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                return today + timedelta(days=days_ahead)
            elif date_input == 'today':
                return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                # Try to parse as YYYY-MM-DD
                return datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD, 'today', 'monday', or press Enter for default")
            continue
        except (EOFError, KeyboardInterrupt):
            # Handle non-interactive environments or Ctrl+C
            print("\n📅 Using default start date (next Monday)")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            days_ahead = 0 - today.weekday()  # Monday is 0
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            return today + timedelta(days=days_ahead)

def main():
    print("🔧 Generating 125-day plan with ALL 250 problems...")

    # Set random seed for reproducible results
    # random.seed(42)  # Uncomment for reproducible results

    # Get start date from user
    start_date = get_start_date()
    print(f"📅 Study plan will start on: {start_date.strftime('%A, %B %d, %Y')}")

    # Load all problems
    all_problems = load_problems()
    print(f"📚 Loaded {len(all_problems)} total problems")

    # Generate fixed plan
    print(f"\n🗓️ Generating complete plan...")
    plan = generate_fixed_125_day_plan(all_problems, start_date)

    # Count total problems in plan
    total_problems_in_plan = sum(len(day['problems']) for day in plan)
    print(f"\n✅ Plan includes {total_problems_in_plan} problems out of 250 total")

    if total_problems_in_plan < 250:
        print(f"❌ WARNING: Missing {250 - total_problems_in_plan} problems!")
        return

    # Analyze distribution
    print(f"\n📊 Analyzing plan distribution...")
    category_by_phase, difficulty_by_phase, category_progression = analyze_plan_distribution(plan)

    # Generate markdown
    markdown_content = generate_markdown_plan(plan)

    # Check if file already exists and find next available filename
    import os
    base_filename = f'NeetCode_250_Study_Plan_{start_date.strftime("%Y-%m-%d")}'
    filename = f'{base_filename}.md'
    counter = 1

    while os.path.exists(filename):
        filename = f'{base_filename}_{counter}.md'
        counter += 1

    # Save to file
    with open(filename, 'w') as f:
        f.write(markdown_content)

    print(f"✅ Generated complete 125-day plan with {len(plan)} days")
    print(f"📄 Saved to: {filename}")

    # Summary statistics
    print(f"\n📈 Plan Statistics:")
    print(f"  Total days: {len(plan)}")
    print(f"  Total problems: {total_problems_in_plan}")
    print(f"  Average problems per day: {total_problems_in_plan / len(plan):.1f}")

    # Category focus statistics
    same_category_days = sum(1 for day in plan if day.get('category') != 'Mixed')
    mixed_category_days = len(plan) - same_category_days

    print(f"\n🎯 Category Focus:")
    print(f"  Same category days: {same_category_days} ({same_category_days/len(plan)*100:.1f}%)")
    print(f"  Mixed category days: {mixed_category_days} ({mixed_category_days/len(plan)*100:.1f}%)")

    # Difficulty distribution by phase
    print(f"\n📊 Difficulty Distribution by Phase:")
    for phase, difficulties in difficulty_by_phase.items():
        total_phase = sum(difficulties.values())
        if total_phase > 0:
            print(f"  {phase}:")
            for diff, count in difficulties.items():
                percentage = (count / total_phase) * 100
                print(f"    {diff}: {count} ({percentage:.1f}%)")

    # Verify all problems are included
    used_problem_names = set()
    for day in plan:
        for problem in day['problems']:
            used_problem_names.add(problem['name'])

    all_problem_names = set(p['name'] for p in all_problems)
    missing_problems = all_problem_names - used_problem_names

    if missing_problems:
        print(f"\n❌ Missing Problems ({len(missing_problems)}):")
        for problem in sorted(missing_problems):
            print(f"  - {problem}")
    else:
        print(f"\n✅ All 250 problems successfully included!")

if __name__ == "__main__":
    main()
