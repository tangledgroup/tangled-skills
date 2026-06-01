# User Journey Diagram

## Contents
- Sections
- Tasks and Scores
- Actors

## Overview

User journey diagrams describe steps users take to complete a task, revealing workflow areas for improvement.

```mermaid
journey
    title My Working Day
    section Go to Work
      Make tea: 5: Me
      Go upstairs: 3: Me
      Do work: 1: Me, Cat
    section Go Home
      Go downstairs: 5: Me
      Sit down: 5: Me
```

## Sections

Group tasks with `section <name>`:

```mermaid
journey
    title Shopping Experience
    section Browse
      Search products: 5: User
      Compare items: 3: User
    section Checkout
      Add to cart: 4: User
      Pay: 2: User, Payment Gateway
```

## Tasks and Scores

Syntax: `Task name: <score>: <actors>`

- **Score**: integer 1–5 (1 = worst experience, 5 = best)
- **Actors**: comma-separated list of involved actors

```
Login: 4: User, Admin
Process payment: 2: User
```

The score determines the visual height/thickness of the task bar for each actor.
