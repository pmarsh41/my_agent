# Protein Intake Agent PRD

## Overview
A passive agentic system that helps users track their daily protein intake by analyzing images of their meals. The system estimates protein content from meal photos, infers personalized daily protein goals, and notifies users if they meet or miss their targets.

## User Stories
- As a user, I want to send meal photos to the agent and have it automatically log my estimated protein intake.
- As a user, I want the agent to estimate my daily protein goal based on my profile and historical data.
- As a user, I want to see a summary of my protein intake for the day.
- As a user, I want to be notified if I am on track, have met, or have missed my daily protein goal.
- As a user, I want to review my protein intake history over time.
- As a user, I want to update my profile (e.g., weight, activity level) to improve goal accuracy.

## Implementation Phases

### Phase 1: Passive Protein Logging
- Accept meal images via app or chat interface
- Use image recognition to identify foods and estimate protein content
- Log protein intake per meal
- Display daily protein intake summary

### Phase 2: Goal Estimation & Feedback
- Collect user profile data (weight, age, activity level, dietary preferences)
- Estimate daily protein goal using standard formulas (e.g., 1.2g/kg body weight)
- Compare logged intake to goal
- Notify user if they are on track, have met, or missed their goal

### Phase 3: Insights & History
- Show protein intake history (daily/weekly/monthly)
- Visualize trends and goal achievement rates
- Allow users to manually adjust entries or add missed meals
- Provide tips for improving protein intake

## Design System
- Colors:
  - Primary: Protein Blue (#3a86ff)
  - Secondary: Leaf Green (#43aa8b)
  - Background: White (#ffffff) / Dark (#181818)
  - Text: Charcoal (#222222)
- Typography:
  - Inter font family
- Spacing:
  - 8px/16px grid system
- Components:
  - Meal Card (with image, protein estimate, timestamp)
  - Daily Summary Bar
  - Goal Progress Indicator
  - Notification Banner
  - Profile Form

# Data Model

**User**
- id
- name
- email
- weight
- age
- activity_level
- dietary_preferences
- protein_goal (g/day, can be auto-calculated or user-set)

**Meal**
- id
- user_id
- image_url
- timestamp
- foods_detected (array of food items)
- protein_estimate (g)
- manual_adjustment (optional)

**DailySummary**
- user_id
- date
- total_protein (g)
- goal (g)
- status (enum: on_track, met, missed)

**Notification**
- id
- user_id
- date
- type (on_track, met, missed)
- message

---

