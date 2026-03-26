# 9 to 5

A 2D top-down, grid-based puzzle game where you control **two office workers simultaneously** with a single input. Navigate through themed office environments — bathrooms, elevators, offices, break rooms, and parking lots — to guide both characters to their goal tiles.

The twist: both characters move in the same direction at the same time. Walls block individually, but if either character steps off the grid, both fall and the level resets. Think ahead, plan asymmetric paths, and reach both goals to advance.

---

## Features

- **Dual-character synchronised movement** — one input controls both workers
- **5 handcrafted puzzle levels** across themed environments (Bathroom, Office, Elevator, Break Room, Parking Lot)
- **Procedural level generator** — press `G` for an infinite supply of new puzzles, each validated as solvable by a BFS solver
- **Star rating system** — complete levels at or under par for 3 stars
- **Themed pixel art** — custom backgrounds, obstacles, goals, and character sprites per environment
- **Main menu** with Start Screen, Controls overlay, and Rules overlay
- **Auto-fit display** — adapts to your screen resolution
- **Zoom controls** — scale the grid up or down to your preference

---

## Installation

### Prerequisites

- **Python 3.10+** (tested on Python 3.13)
- **pip** (comes with Python)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/TiyahSingh/GameJam9To5.git
   cd GameJam9To5
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python main.py
   ```

> **Windows note:** If `python` is not recognised, try `py main.py` instead.

---

## Controls

| Input | Action |
|-------|--------|
| `WASD` / Arrow Keys | Move both characters one tile |
| Mouse Click | Move relative to Character A (click direction) |
| `R` | Reset current level (no penalty) |
| `G` | Generate a new procedural level |
| `+` / `-` | Zoom in / out |
| `Esc` | Quit game |

---

## Game Rules

1. **Both characters respond to every input** — movement is synchronous and step-based.
2. **Wall/blocker collision** is per-character: if one is blocked, only that one stays; the other still moves.
3. **Off-grid fall** — if **either** character would move outside the grid boundary, **both** fall and the level resets. This is the only fail condition.
4. **No overlap** — characters cannot occupy the same tile. If a move would place both on the same square, neither moves for that step.
5. **Win condition** — Character A stands on Goal A **and** Character B stands on Goal B simultaneously.

---

## Project Structure

```
main.py                 Entry point
requirements.txt        Python dependencies
plan.md                 Development plan and milestones
refinements-changes.md  Running changelog of design decisions

game/                   Core game package
  app.py                Game loop, rendering, HUD, input
  level.py              Level & Character data models
  levels.py             5 handcrafted static levels
  movement.py           Dual-character movement logic
  solver.py             BFS solver for validation & par
  generator.py          Procedural level generator
  assets.py             Recursive art loader
  menu.py               Main menu system
  types.py              Shared types (Vec2, Tile, directions)

GameArtImages/          Art assets organised by theme
  Backrounds & Menus/   Menu screen backgrounds
  Bathroom Levels/      Bathroom theme tiles
  Breakroom Levels/     Break room theme tiles
  Elevator Level Characters/  Elevator theme + characters
  Office Levels/        Office theme tiles
  Parking Lot Levels/   Parking lot theme tiles
  UI and Buttons/       Button sprites (Play, Rules, etc.)
  UI Mockup Template/   UI design reference mockups
  Usual Characters/     Default character sprites
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pygame-ce` / `pygame` | >= 2.5.2 | 2D game framework — windowing, rendering, input, image loading |

See `requirements.txt` for the full dependency specification.

---

## Credits

- **Tiyah Singh** — Game design, programming, level design, project lead
- Art assets created for the Game Jam 9-to-5 project

---

## AI Tools Used

This project was developed with assistance from **Cursor (Claude AI)**. The AI agent was used for:

- Code exploration and refactoring
- Documentation generation and maintenance
- Git operations and repository management
- Iterative bug fixing and feature development

All game design decisions, level design, art direction, and creative vision are original human work. AI was used as a development accelerator, not a replacement for design thinking.

---

## AI Reflection

### Where did AI excel, and where did it mislead or limit you?

AI excelled at handling basic coding tasks, quickly generating functional scripts and class structures. It was especially useful for automating time consuming tasks, like fixing minor bugs, maintaining project structure, and helping me organize files and commits on GitHub (Liz, 2025). By handling these routine tasks, AI significantly reduced the time it took me to implement features, debug and run tests. However, when it came to implementing my custom UI designs and artwork, it often fell short. Despite providing detailed it with mock-up templates and labelling all images and folders, AI stretched images incorrectly, misaligned elements, or linked actions to the wrong buttons even when the instructions were clearly labelled and explained. As a result, I had to rely heavily on one AI tool, Cursor, to handle much of the UI so that it could more easily interpret its own logic throughout. While this sped up implementation, I felt that it limited my creative freedom, as altering the look and feel of the game beyond what AI produced often broke functionality or caused inconsistencies (Alharthi, 2025). AI was useful for executing technical tasks efficiently, however, it constrained my ability to fully shape the game's visual identity and interactive experience.

### How did AI alter your creative or technical process?

AI helped me finish repetitive coding tasks faster, which cut down the development process significantly, proving why developers using AI tools can significantly shorten review cycles and speed delivery of features when integrated well into workflows. However, AI assistants frequently struggle with structured outputs and can produce errors in complex interfaces, meaning human verification remains essential (Udinmwen, 2026). This was especially clear in my UI work despite detailed templates, the AI often misaligned images or connected logic to the wrong controls, forcing me to intervene continuously. Creatively, AI influenced how I ideated and shaped my workflow more than I wanted at times. I found myself adapting to what the AI could do rather than purely driving the vision myself, which can be counterproductive for a game with the goal of individuality and originality, however in this case helped give me a complete working game in a short time frame. Thus, I have found that overreliance on AI can inhibit deep skill formation unless balanced thoughtfully, it was highly helpful on the technical front however from creative standpoint, I do feel my vision got lost somewhere along the way and although a significant amount of the art in the game was created by myself, it still didn't reflect the exact way in which I would have designed the look and feel of the game if I were making this game un-assisted (Klimova and Pikhart, 2025). AI pushed me to rethink how I split creative and technical work, using it to accelerate simple tasks while guarding against overdependence that could disrupt my own creative input.

### What would you change about your collaboration with AI next time?

For my next AI collaboration, I'd definitely work in a language and environment I am more experienced with – for example, Unity and C# instead of Python. I struggled with Python in this task because I didn't feel confident making my own changes, and that made me rely more on AI. AI tools are most effective when developers already have experience with the language and task at hand as AI tends to help most with basic code and repetitive work, not unfamiliar or highly context specific issues (Li et al., 2024). I'd also use AI more selectively to generate scripts like character controllers, utility classes, or repetitive systems while keeping full control over UI design, core architecture, and specialised scripts. The goal would be for AI to handle the repetitive and simpler parts efficiently, while I maintain overall control for decision making and creative direction, as AI can boost developer output on simple tasks, but it also requires careful oversight and critical thinking (Kapuściński, 2024). I'd balance my workflow better by allowing AI to aid in my time management by completing time intensive mundane tasks, but lean on my own knowledge for important aspects of the game, asking for advice from AI rather than having it complete the task for me.

### Ethical considerations: Did your use of AI respect originality, transparency, and fair use?

Yes. Throughout the project, I made a conscious effort to use AI responsibly, ensuring that all outputs respected originality, transparency, and fair use. AI was a tool for coding, saving time on repetitive tasks, generating scripts, and assisting with documentation (Onix React, 2026). I treated its contributions as drafts rather than final outputs, carefully reviewing and editing it to ensure it aligned with my own creative vision. For example, with my imagery and game assets, I asked AI to create images based off, of my mood board that I sent it, then I took AI's images into Canva and further edited them into my vision. Transparency was another key consideration, as I documented the exact parts of the project that were AI-assisted, making it clear when AI played a role and referencing the AI and direct conversation I had with the AI. This way, a review of the project would depict how AI was integrated without misleading anyone into thinking it was purely done on my own (Blaszczyk, McGovern and Stanley, 2024). Fair use was also respected as no copyrighted assets were used without permission, and AI was not asked to generate content that would infringe on others' work even when aspects were inspired by other works' I explicitly maintained that both myself and the AI avoided directly copying outputs without modification, ensuring that the final project remained authentic.

### Did you credit AI-generated assets appropriately?

Yes, I made sure to properly credit all AI-generated content throughout my project. I followed the Harvard IIE Anglia Style Reference Guide and included citations for each AI-generated asset, along with the chat links. This made everything traceable and clear in terms of where the content came from. I also created tables showing which AI tools were used for different parts of the project, including planning, documentation, and development. The tables depicted how these AI's were used and how exactly they were refined through human collaboration. Additionally, I included an AI disclaimer at the beginning of any written documentation that used AI. I felt this was important as it makes it obvious that AI was used, and where it was used as a support tool, not to replace my own work. Overall, I tried to be as transparent as possible. To avoid any confusion on what parts of the project were AI-assisted and what were my own.

### Were there moments were relying on AI felt ethically questionable?

Yes, at times it did feel ethically questionable to rely on AI as much as I did. Throughout the project, I often found myself double checking the rubric to ensure that I was not misunderstanding the requirements or using AI in a way that went beyond what was expected. It felt unusual to use AI so openly across multiple parts of the project, and I was not always completely comfortable with it having so much control over my work, thus I did change a lot of it to make sure it was a collaboration instead of AI alone. There were also moments where it made me question my own abilities as a developer. AI was able to generate large parts of the game in a couple minutes, which would have taken me weeks to complete on my own. This s felt like I was taking an unfair shortcut or cheating, even if it was technically allowed. Because of this, I made a strong effort to include detailed referencing and clearly document all AI contributions.

I also made sure not to rely on AI completely. I continued to contribute my own work, ideas, and improvements, as I did not feel it was appropriate to submit something that I had not meaningfully worked on myself. Overall, while AI was helpful and permitted, I remained conscious of using it in a way that was fair, transparent, and aligned with my own learning. Although, I learnt a lot from working with AI during this game jam, in terms of how to utilise AI beneficially, I did not have the same feeling of pride after completing the development portions of the game like in previous game jams, as AI had a significant impact on that section.

### How can you ensure your future work with AI remains responsible and authentic?

In order to ensure that my use of AI in the future is responsible and authentic, I need to be more aware and careful about how I use AI and where I use it. It is known that AI tools have a significant impact on how fast development tasks can be accomplished. GitHub Co-pilot is an example of an AI tool used for development tasks. It reduces the time required to complete tasks by around 55%. As a result, I plan to use AI for simple and repetitive tasks such as script development and debugging (FIT Instituto de Tecnologia, 2026). However, I will maintain full control of complex tasks such as UI development and creative direction. Additionally, I will ensure that I comprehend and understand the code developed by AI before using it, as although AI-generated code is widely used by developers, there is still a requirement for it to reviewed and verified. This is due to the fact that almost half of developers do not entirely trust its accuracy (Kothiyal, 2026). Thus, I need to verify and adapt the code developed by AI rather than relying on it. Moreover, I will document and reference AI usage clearly to maintain transparency. AI already generates a large portion of modern code, with estimates showing around 40–46% of code is AI-assisted, therefore being clear about its role is important.

---

## AI Attribution, Ethical & Fair Use Declaration

This project makes use of artificial intelligence (AI) tools as part of the design and development process. Such tools were utilised to support ideation, documentation writing, prototyping, code assistance, and the generation of preliminary visual assets. All AI-assisted outputs have been subject to considerable human review, modification, and integration, and do not constitute final work in their original generated form. AI-generated content is transparently credited, and no copyrighted material was used without proper permission. This approach ensures the project remains authentic and ethical.

In accordance with academic integrity standards and principles of responsible AI use, Tiyah Singh affirms that:

1. **Authorship & Originality:** All submitted work represents the author's own intellectual contribution. AI-generated material has been transformed, adapted, and incorporated in a manner that constitutes original work under applicable academic guidelines.
2. **Attribution & Transparency:** The use of AI tools has been clearly disclosed within this document and associated development materials. AI has been used as an assistive instrument rather than a substitute for independent design, analysis, or implementation.
3. **Intellectual Property Compliance:** Reasonable steps have been taken to ensure that AI-generated content does not knowingly infringe upon existing copyrights, trademarks, or other protected intellectual property. Any assets or outputs used have been reviewed and, where necessary, modified to ensure compliance with fair use/fair dealing principles and originality requirements.
4. **Human Oversight & Accountability:** All design decisions, system implementations, and final outputs remain the sole responsibility of the author. AI-generated suggestions or content have not been accepted without critical evaluation.

This declaration aligns with Emeris Vega expectations regarding academic honesty, as well as broader ethical standards for the responsible and transparent use of AI.

**Project:** GADS7331 Part 1 – Game Jam
**Name:** Tiyah Singh
**Student Number:** ST10453245

---

## References

- Alharthi, S.A., 2025. Generative AI in Game Design: Enhancing Creativity or Constraining Innovation? *Journal of Intelligence*, [e-journal] 13(6), p.60. Available at: <https://doi.org/10.3390/jintelligence13060060> [Accessed 25 March 2026].
- Blaszczyk, M., McGovern, G. and Stanley, K.D., 2024. Artificial Intelligence Impacts on Copyright Law. [online] Available at: <https://www.rand.org/pubs/perspectives/PEA3243-1.html> [Accessed 25 March 2026].
- FIT Instituto de Tecnologia, 2026. Using Artificial Intelligence — AI to Facilitate and Accelerate the Software Development Process…. [online] Available at: <https://medium.com/@fitinstitutodetecnologia/using-artificial-intelligence-ai-to-facilitate-and-accelerate-the-software-development-process-cd5160640705> [Accessed 25 March 2026].
- Kapuściński, M., 2024. Boosting Productivity: Using AI to Automate Routine Business Tasks | TTMS. [online] Available at: <https://ttms.com/boosting-productivity-using-ai-to-automate-routine-business-tasks/> [Accessed 25 March 2026].
- Klimova, B. and Pikhart, M., 2025. Exploring the effects of artificial intelligence on student and academic well-being in higher education: A mini-review. *Frontiers in Psychology*, [e-journal] 16(16). Available at: <https://doi.org/10.3389/fpsyg.2025.1498132> [Accessed 25 March 2026].
- Kothiyal, P., 2026. Most Developers Don't Fully Trust AI-Generated Code. [online] Available at: <https://talent500.com/blog/ai-generated-code-trust-and-verification-gap/> [Accessed 25 March 2026].
- Li, Z.S., Arony, N.N., Awon, A.M., Damian, D. and Xu, B., 2024. AI Tool Use and Adoption in Software Development by Individuals and Organizations: A Grounded Theory Study. [e-journal] Available at: <https://doi.org/10.48550/arXiv.2406.17325> [Accessed 25 March 2026].
- Liz, B., 2025. AI Coding Tools: Productivity Game-Changer or Overhyped Assistant? [online] Available at: <https://medium.com/@b.lizdias/ai-coding-tools-productivity-game-changer-or-overhyped-assistant-2803c9d3d206> [Accessed 25 March 2026].
- Onix React, 2026. Everyday Coding Tasks You Should Automate with AI. [online] Available at: <https://medium.com/@onix_react/everyday-coding-tasks-you-should-automate-with-ai-73e64173ab05> [Accessed 25 March 2026].
- Udinmwen, E., 2026. Even the most advanced AI models fail more often than you think on structured outputs — raising doubts about the effectiveness of coding assistants. [online] Available at: <https://www.techradar.com/pro/even-the-most-advanced-ai-models-fail-more-often-than-you-think-on-structured-outputs-raising-doubts-about-the-effectiveness-of-coding-assistants> [Accessed 25 March 2026].
