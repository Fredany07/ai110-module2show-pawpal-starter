# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One deliberate tradeoff is in **conflict detection** (`Scheduler.find_conflicts()`).
It sorts tasks by start time and only compares each task against the *next* one
in that order — an O(n log n) sweep-line check rather than an O(n²) comparison of
every possible pair. As a result, when three or more tasks all overlap, it reports
them as a chain of adjacent pairs (A–B, B–C) instead of every combination (A–C too).

This is reasonable for a single owner's daily plan: the task count is small, the
performance win is minor at this scale, but the *readability* win is real — the
owner fixes conflicts in chronological order, one neighbor at a time, which mirrors
how they'd actually rearrange their day. A second tradeoff: recurring tasks advance
by a fixed `timedelta` (today + 1 day / + 1 week) and don't account for calendar
skips like "weekdays only," which keeps the logic simple and predictable.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
