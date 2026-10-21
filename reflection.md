# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My intial UML design is to focus on organizing the pet care system into seperate classes where they each have a clear responsibility. 
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
Yes, my design changed during implementation. Based on the AI feedback, I added pet and date attributes to the DailyPlan class. The original design stored the tasks but did not specify which pet they were for or which day they should be completed. This change makes that information clear for each unique daily plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    - Conflict detection only checks for exact matches (same start time and same due date). It does not check whether task durations overlap, so a 30-minute walk at 08:00 and a feeding at 08:15 are not flagged even though they clash.
- Why is that tradeoff reasonable for this scenario?
    - Comparing two "HH:MM" strings is simple and cheap, so the check can run every time a task is added, and it only returns a warning instead of blocking the task. It never raises a false alarm, but it can miss real overlaps. For a small daily pet-care plan that is acceptable, and overlap detection (start < other end and other start < end) is a clear next improvement.

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
