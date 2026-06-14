# User Journey Reference

## Description

User journey diagrams describe the steps different users take to complete a task within a system. They reveal the current workflow and areas for improvement.

## Basic Syntax

```mermaid
journey
    title My Working Day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me
      Do work: 1: Me, Cat
    section Go home
      Go downstairs: 5: Me
      Sit down: 5: Me
```

## Structure

```
journey
    title "Journey Title"
    section Section Name
        Task Name: <score>: <actor1>, <actor2>
```

### Task Syntax

```
Task name: <score>: <comma-separated actors>
```

- **Score:** Number between 1 and 5 (inclusive) — represents satisfaction/experience level
- **Actors:** Comma-separated list of participants in the task

## Examples

### Shopping Experience

```mermaid
journey
    title Online Shopping Experience
    section Browsing
        Search products: 5: Customer
        Filter results: 4: Customer
        Read reviews: 3: Customer
    section Purchase
        Add to cart: 5: Customer
        Checkout: 2: Customer, Payment Gateway
        Enter address: 3: Customer
    section Post-Purchase
        Order confirmation: 5: Customer, System
        Shipping notification: 4: Customer, System
        Delivery: 3: Customer, Courier
```

### Onboarding Flow

```mermaid
journey
    title New User Onboarding
    section Sign Up
        Visit website: 5: User
        Create account: 3: User
        Verify email: 2: User, System
    section First Use
        Complete profile: 4: User
        Explore features: 5: User
        Watch tutorial: 3: User
    section Engagement
        First purchase: 4: User
        Invite friends: 3: User
        Leave review: 2: User
```
