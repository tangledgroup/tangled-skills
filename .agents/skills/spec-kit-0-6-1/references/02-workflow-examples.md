# Workflow Examples

Complete walkthroughs demonstrating Spec Kit workflows from specification to implementation.

## Example 1: Taskify - Team Productivity Platform

This comprehensive example walks through building a Kanban-style task management application with user management, projects, and real-time collaboration features.

### Step 1: Initialize Project

```bash
# Create new project with Claude Code
specify init taskify --ai claude
cd taskify
```

### Step 2: Define Constitution

Establish core project principles:

```markdown
/speckit.constitution Taskify is a "Security-First" team productivity application. All user inputs must be validated server-side. We use microservices architecture with clear API boundaries. Code must be fully documented with inline comments and API documentation. The application follows RESTful design principles. We prioritize accessibility (WCAG 2.1 AA compliance) and performance (sub-second response times for core operations).
```

This creates `.specify/memory/constitution.md` with your project's guiding principles.

### Step 3: Create Feature Specification

Describe the first feature - user management and basic task boards:

```markdown
/speckit.specify Develop Taskify, a team productivity platform. It should allow users to create projects, add team members, assign tasks, comment and move tasks between boards in Kanban style. In this initial phase, let's have multiple users but they will be predefined - five users in two categories: one product manager and four engineers. Create three sample projects with standard Kanban columns: "To Do", "In Progress", "In Review", and "Done". No login required for this MVP as this is just testing basic features.
```

**What happens:**

1. **Branch creation**: Creates git branch `001-create-taskify`
2. **Directory structure**: Creates `specs/001-create-taskify/`
3. **Specification file**: Generates `specs/001-create-taskify/spec.md` with:
   - User scenarios (select user, view projects, manage tasks)
   - Functional requirements (project creation, task management, comments)
   - Success criteria (task completion rate, UI responsiveness)
   - Key entities (User, Project, Task, Comment)
   - Acceptance scenarios

4. **Quality validation**: Creates `specs/001-create-taskify/checklists/requirements.md`

**Generated spec includes:**

```markdown
# Feature Specification: Create Taskify

## User Scenarios & Testing

### Primary User Flow
1. User launches application → sees list of 5 predefined users
2. User clicks on a user → enters main view showing list of projects
3. User clicks on a project → opens Kanban board for that project
4. User sees columns: To Do, In Progress, In Review, Done
5. User can drag and drop cards between columns
6. Cards assigned to current user appear in different color

## Functional Requirements

### FR-1: User Selection
- System shall display list of 5 predefined users on launch
- Users are categorized as: 1 Product Manager, 4 Engineers
- No authentication required for MVP phase

### FR-2: Project Management
- System shall display 3 sample projects
- Each project has its own Kanban board
- Projects are visible to all users

### FR-3: Task Management
- Tasks can be created within projects
- Tasks can be moved between columns via drag-and-drop
- Each task has status, assignee, and comments
- Tasks assigned to current user highlighted visually

## Success Criteria

- Users can complete task creation in under 10 seconds
- Drag-and-drop operations respond within 200ms
- System supports 5 concurrent users without performance degradation
- 100% of tasks can be moved between all column states
```

### Step 4: Refine Specification

Clarify details interactively:

```markdown
/speckit.clarify I want to clarify task card details. For each task in the UI, you should be able to change status between columns via drag-and-drop. Unlimited comments per card. From task card, assign one of the valid users. When launching Taskify, show list of 5 users to pick from with no password. Click on user → main view displays projects. Click on project → open Kanban board with columns. Drag and drop cards between columns. Cards assigned to logged-in user shown in different color. Users can edit their own comments but not others'. Users can delete their own comments but not others'.
```

**Result:** Specification updated with clarified requirements, removing `[NEEDS CLARIFICATION]` markers.

### Step 5: Validate Specification

Run quality checklist:

```markdown
/speckit.checklist
```

This validates:
- No implementation details in specification
- All mandatory sections completed
- Requirements are testable and unambiguous
- Success criteria are measurable and technology-agnostic
- All acceptance scenarios defined

### Step 6: Generate Implementation Plan

Provide tech stack and architecture:

```markdown
/speckit.plan We are going to generate this using .NET Aspire with Postgres as the database. Frontend uses Blazor Server with drag-and-drop task boards and real-time updates via SignalR. Create REST API with three endpoints: Projects API (GET/POST /api/projects), Tasks API (GET/POST/PUT /api/tasks), Notifications API (WebSocket /api/notifications). Implement role-based access control for comments (users can only edit/delete their own).
```

**What happens:**

1. **Phase 0 - Research**: Generates `specs/001-create-taskify/research.md`
   - .NET Aspire best practices
   - Blazor Server drag-and-drop libraries
   - SignalR real-time communication patterns
   - PostgreSQL schema design for task boards

2. **Phase 1 - Design Artifacts**:
   - `data-model.md`: Entity schemas (User, Project, Task, Comment)
   - `contracts/`: API endpoint specifications
   - `quickstart.md`: Key validation scenarios
   - Updates agent context file with new technologies

3. **Implementation Plan**: `specs/001-create-taskify/plan.md` includes:

```markdown
# Implementation Plan: Create Taskify

## Technical Context

### Technology Stack
- **Frontend**: Blazor Server with Interact.js for drag-and-drop
- **Backend**: .NET 8.0 Aspire with minimal APIs
- **Database**: PostgreSQL 15+ with Npgsql
- **Real-time**: SignalR for live updates
- **Authentication**: Cookie-based session auth (MVP)

### Architecture Decisions

#### Decision 1: Blazor Server over WebAssembly
**Rationale**: Real-time updates via SignalR integrate seamlessly with server-side rendering, reducing complexity for MVP.

#### Decision 2: PostgreSQL over SQL Server
**Rationale**: Cross-platform compatibility, active community, better cloud-native support.

## Constitution Compliance

✅ **Security-First**: Input validation implemented at API boundary layer
✅ **Microservices**: Clear separation between Projects, Tasks, Notifications services
✅ **Documentation**: XML doc comments required for all public APIs
✅ **RESTful Design**: All endpoints follow REST conventions
⚠️ **Accessibility**: WCAG compliance deferred to Phase 2 (justification: MVP timeline)

## Data Model

### User Entity
```csharp
public class User
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public UserRole Role { get; set; } // ProductManager, Engineer
    public DateTime CreatedAt { get; set; }
}
```

### Task Entity
```csharp
public class Task
{
    public Guid Id { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }
    public TaskStatus Status { get; set; } // ToDo, InProgress, InReview, Done
    public Guid ProjectId { get; set; }
    public Guid? AssignedTo { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
}
```

## API Contracts

### Projects API
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project

### Tasks API
- `GET /api/projects/{id}/tasks` - Get tasks for project
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task (including status change)

### Notifications API
- `WebSocket /api/notifications` - Real-time task updates

## Quickstart Validation

1. Launch app → select user → verify project list displays
2. Click project → verify Kanban board loads with 4 columns
3. Create task → verify appears in "To Do" column
4. Drag task to "In Progress" → verify status updates via SignalR
5. Add comment → edit/delete own comment → verify others' comments read-only
```

### Step 7: Generate Task List

Break down into executable tasks:

```markdown
/speckit.tasks
```

**Generates `specs/001-create-taskify/tasks.md`:**

```markdown
# Tasks: Create Taskify

## Phase 1: Database Setup [P]

- [ ] **T1**: Create PostgreSQL migration for User table
  - Dependencies: None
  - Acceptance: Migration runs successfully, seeds 5 users
  
- [ ] **T2**: Create PostgreSQL migration for Project table
  - Dependencies: None
  - Acceptance: Migration runs successfully, seeds 3 projects
  
- [ ] **T3**: Create PostgreSQL migration for Task and Comment tables
  - Dependencies: T1, T2
  - Acceptance: Foreign keys properly configured

## Phase 2: API Implementation [P]

- [ ] **T4**: Implement Projects API endpoints
  - Dependencies: T2
  - Acceptance: All CRUD operations return correct HTTP status codes
  
- [ ] **T5**: Implement Tasks API endpoints
  - Dependencies: T3
  - Acceptance: Task status updates trigger SignalR notifications
  
- [ ] **T6**: Implement Notifications WebSocket endpoint
  - Dependencies: T4, T5
  - Acceptance: Real-time updates received by connected clients

## Phase 3: Frontend Implementation

- [ ] **T7**: Create Blazor user selection component
  - Dependencies: T4
  - Acceptance: User can select from 5 predefined users
  
- [ ] **T8**: Create project list component
  - Dependencies: T7, T4
  - Acceptance: Projects displayed with correct data
  
- [ ] **T9**: Implement Kanban board with drag-and-drop
  - Dependencies: T8, T5
  - Acceptance: Tasks can be dragged between columns, status updates via API
  
- [ ] **T10**: Implement comment system with RBAC
  - Dependencies: T9, T5
  - Acceptance: Users can only edit/delete own comments

## Parallelization Notes

- **[P]** marked tasks can run in parallel within phase
- Phase 2 depends on Phase 1 completion
- Phase 3 depends on corresponding Phase 2 tasks

## Estimated Effort

- Phase 1: 2 hours
- Phase 2: 4 hours
- Phase 3: 6 hours
- **Total**: 12 hours (can be reduced with parallel execution)
```

### Step 8: Validate Plan

Audit implementation plan:

```markdown
/speckit.analyze
```

This checks:
- Constitution compliance (flags WCAG deferral)
- API contract completeness
- Data model consistency
- Task dependency correctness

### Step 9: Implement

Execute code generation:

```markdown
/speckit.implement
```

**Result**: AI agent generates source code following the task list, creating:
- `src/Taskify.Server/` - .NET Aspire backend
- `src/Taskify.Client/` - Blazor Server frontend
- `src/Taskify.Shared/` - Shared models and contracts
- Database migrations with seed data
- API controllers and services
- Blazor components for Kanban board

## Example 2: Photo Organization App

A simpler example focusing on the specification workflow.

### Step 1: Quick Specification

```markdown
/speckit.specify Build a photo organization app where albums are grouped by date, can be reorganized via drag-and-drop on main page, and photos display in tile interface within each album. Albums are flat (no nested albums).
```

### Step 2: Clarify Details

```markdown
/speckit.clarify Albums should support unlimited photos. Drag-and-drop works across albums to reorder them. Photos auto-sort by date taken within albums. App stores only metadata locally, no image uploads. Use SQLite for local storage.
```

### Step 3: Generate Plan

```markdown
/speckit.plan Use vanilla HTML, CSS, and JavaScript with minimal libraries. Vite for bundling. SQLite database via sql.js for client-side storage. Images referenced by local file paths only, never uploaded. Implement drag-and-drop using native HTML5 Drag and Drop API.
```

### Step 4: Execute

```markdown
/speckit.tasks
/speckit.implement
```

## Example 3: Migration from Traditional Development

Migrating an existing project to Spec-Driven Development.

### Step 1: Initialize Spec Kit in Existing Repo

```bash
# In existing project directory
specify init --here --ai copilot --no-git
```

### Step 2: Define Constitution Based on Existing Code

```markdown
/speckit.constitution This is a legacy migration project. Existing codebase uses Express.js with MongoDB. New features must follow spec-driven workflow. Maintain backward compatibility with existing API endpoints. All new features require specifications before implementation.
```

### Step 3: Create Spec for New Feature

```markdown
/speckit.specify Add user authentication system with JWT tokens, password reset via email, and rate limiting on login attempts.
```

### Step 4: Generate Plan Aligned with Existing Stack

```markdown
/speckit.plan Use existing Express.js setup. Add jsonwebtoken for JWT generation, bcryptjs for password hashing, nodemailer for email, and express-rate-limit for rate limiting. MongoDB schema for User collection with hashed passwords and reset tokens. Maintain existing API versioning (/api/v1/auth/*).
```

## Best Practices from Examples

### 1. Be Specific in Specifications

**Good:**
```markdown
/speckit.specify Kanban board with 4 columns (To Do, In Progress, In Review, Done), drag-and-drop task movement, user assignment with visual highlighting for current user's tasks.
```

**Vague:**
```markdown
/speckit.specify A task management system
```

### 2. Clarify Early, Clarify Often

Don't wait until all clarifications are needed:

```markdown
/speckit.specify ... (initial spec)
/speckit.clarify ... (first round of clarifications)
/speckit.clarify ... (additional details as they come to mind)
```

### 3. Align Plan with Constitution

Ensure technical decisions respect project principles:

```markdown
/speckit.constitution Security-first, input validation required...
/speckit.plan ... implement validation middleware at API boundary ...
```

### 4. Use Phased Implementation for Complex Features

Break large features into phases:

```markdown
# In specification
## Phase 1 (MVP)
- Basic task creation and movement
- No comments or assignments

# Later
/speckit.specify Add comment system to Taskify with user attribution and edit permissions
```

### 5. Leverage Parallelization

Use `[P]` markers in tasks for parallel execution:

```markdown
# In plan
## Phase 1: Database Setup [P]
- All migrations can run in parallel if no dependencies
```

## Next Steps

- Read [Command Reference](references/03-command-reference.md) for detailed command documentation
- Explore [Extensions Guide](references/04-extensions.md) to enhance workflows
- Review [SDD Methodology](references/06-sdd-methodology.md) for deeper understanding
