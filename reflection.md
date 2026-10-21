# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design is to focus on organizing the pet care system into seperate classes where they each have a clear responsibility. 
- What classes did you include, and what responsibilities did you assign to each?
I would include these classes:
   - Pet: Stores information about the pet, such as its name, species, and age.
   - CareTask: Represents individual care activities, such as walking, feeding, medication, and grooming. It includes each task’s duration, priority, and required frequency.
   - OwnerPreferences: Stores the owner’s available time, preferred task times, and other scheduling preferences.
   - DailyPlan: Stores the selected tasks and explanations for why they were included.
   - Planner: Selects and organizes tasks based on their priority and the owner’s constraints.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
    - Yes, my design changed during implementation. Based on the AI feedback, I added pet and date attributes to the DailyPlan class. The original design stored the tasks but did not specify which pet they were for or which day they should be completed. This change makes that information clear for each unique daily plan.
    Note: Later in implementation, the design changed further: CareTask, OwnerPreferences, DailyPlan and Planner became Task, Owner and Scheduler. Owner holds multiple pets, so the scheduler can work across all of them, and a separate per-pet plan object was no longer needed.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    - One tradeoff is conflict detection, as it only checks for exact matches (same start time and same due date). It does not check whether task durations overlap, so a 30-minute walk at 08:00 and a feeding at 08:15 are not flagged even though they could clash.
- Why is that tradeoff reasonable for this scenario?
    - This tradeoff is reasonable because checking for matching start times keeps the scheduler simple and easy to understand while catching obvious potential conflicts. However, it can miss tasks whose durations overlap. For this basic pet-care planner, this is a reasonable starting point, and checking both start and end times would be a useful future improvement.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    - I used AI to brainstorm possible test cases, review my class design, and make edits to the code.
- What kinds of prompts or questions were most helpful?
    - I think that prompts which described exactly what details I wanted changed were most helpful. I also asked AI to explain what it changed and why so I could understand its suggestions without making huge changes all at once.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    - I did not accept AI’s suggestion to create a PlanEntry class to connect each task to a pet because I could identify the pet using a pet_name attribute in the existing Task class, keeping the design simpler.
- How did you evaluate or verify what the AI suggested?
    - I checked whether the suggested changes matched the assignment and made logical sense. I ran the demo to check the schedule output and ran tests for marking a task complete and adding a task to a pet.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
The main areas I tested are basic functionality, sorting, recurrence, and conflict detection. I checked task completion and addition; chronological sorting, equal-time order, unchanged original lists, and empty lists; and priority sorting with time-based ties and unknown priorities last. I checked independent daily/weekly recurrences across month, year, and leap-day boundaries, no recurrence for one-off/unknown frequencies, and future tasks excluded from today’s plan. I also checked same-time/date conflicts within and across pets, excluding different times/dates and completed tasks, with warnings instead of errors. These tests were importnat because testing the edge cases (empty lists, equal times, date rollovers) meant I could change the code and know right away if something broke. I also wanted conflict handling to warn but not crash or remove a task.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    - I'm fairly confident in the Scheduler logic, because all 20 tests pass and main.py produces the schedule I expected. 
- What edge cases would you test next if you had more time?
    Two edge cases I would test next time if I had more time are: 
    - Considering conflicts only compare exact start times, so tasks whose durations overlap (a 30-minute walk at 08:00 and a nap at 08:15) aren't detected.
    - Also, considering that completing the same recurring task twice creates a duplicate next occurrence.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - I am most satisfied with the functioning final tool that I built with the help of AI. Also, implementing the sorting, filtering, and conflict-warning logic really made me think about how the tool’s functionality should work.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - If I had another iteration, I would add more features to make the tool more distinctive. For instance, I would consider adding an AI companion to guide users through the tool, help them add pet-care tasks, and explain their daily plan.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - One important thing I learned about designing systems is the importance of iteration, as I had to rethink my UML design, methods, and UI to build a useful pet-care tool. I also learned how to evaluate AI-generated code and decide which suggested changes to accept or reject.