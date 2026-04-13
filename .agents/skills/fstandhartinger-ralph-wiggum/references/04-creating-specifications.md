# Creating Specifications

Complete guide to writing effective specifications for Ralph Wiggum, including templates, acceptance criteria, and examples.

## Spec Structure

### Directory Layout

```
specs/
├── 001-user-auth/
│   ├── spec.md              # Main specification
│   └── checklists/
│       └── requirements.md  # Quality checklist (optional)
├── 002-user-profile/
│   ├── spec.md
│   └── checklists/
│       └── requirements.md
└── 003-dashboard/
    ├── spec.md
    └── checklists/
        └── requirements.md
```

### Numbering Convention

- Use 3-digit zero-padded numbers: `001-`, `002-`, `003-`
- Lower number = higher priority
- Ralph processes specs in numerical order
- Gap in numbers is OK (e.g., 001, 005, 010)

### Folder Naming

Format: `NNN-short-name`

Examples:
- `001-user-auth`
- `002-api-integration`
- `003-billing-dashboard`
- `010-oauth-providers`

**Tips:**
- 2-4 words max
- Action-noun format when possible
- Preserve technical terms (OAuth, JWT, API)
- Hyphens between words

## Spec Template

### Basic Template

```markdown
# [Feature Name]

## Overview

[1-2 paragraphs describing what this feature does and why it's needed]

## Requirements

### Functional Requirements

- [Requirement 1: What the system should do]
- [Requirement 2: Another capability]
- [Requirement 3: Edge case handling]

### Non-Functional Requirements

- [Performance: Response time, throughput]
- [Security: Authentication, authorization]
- [Usability: Accessibility, UX guidelines]

## Acceptance Criteria

### Criterion 1: [Specific testable condition]

**Given** [initial context]
**When** [action is performed]
**Then** [observable outcome]

**Verification:**
```bash
# Command or steps to verify
curl -X POST https://api.example.com/login -d '{"email":"test@example.com"}'
# Should return 200 with JWT token
```

### Criterion 2: [Another testable condition]

**Given** [context]
**When** [action]
**Then** [outcome]

**Verification:**
```bash
# Verification steps
npm test -- --grep "specific test name"
```

### Criterion N: [Continue for all criteria]

[Each criterion must be specific and verifiable]

## Technical Implementation

### Architecture

[Describe the technical approach, components, data flow]

### Dependencies

- [Package/library name] - [Purpose]
- [External service] - [How it's used]

### Database Changes

```sql
-- Any schema migrations needed
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Authenticate user |
| GET | /api/user/profile | Get current user profile |
| PUT | /api/user/profile | Update user profile |

## Testing Requirements

### Unit Tests

- [ ] Test authentication flow
- [ ] Test token generation and validation
- [ ] Test error handling for invalid credentials

### Integration Tests

- [ ] Test full login flow with database
- [ ] Test OAuth callback handling
- [ ] Test session persistence

### Browser/Visual Tests

- [ ] Login form renders correctly
- [ ] Error messages display properly
- [ ] Success redirect works as expected

### Console Checks

- [ ] No JavaScript errors in browser console
- [ ] No unhandled promise rejections
- [ ] No 404/500 errors in network tab

## Completion Signal

The spec is complete when ALL of the following are true:

### Implementation Checklist

- [ ] All functional requirements implemented
- [ ] Database migrations run successfully
- [ ] API endpoints return correct responses
- [ ] Error handling covers edge cases

### Testing Checklist

- [ ] All unit tests pass (`npm test`)
- [ ] All integration tests pass (`npm run test:integration`)
- [ ] Browser tests pass (manual or automated)
- [ ] No console errors
- [ ] Code coverage >= 80% for new code

### Quality Checklist

- [ ] Code follows project style guide
- [ ] No TODO comments left behind
- [ ] Documentation updated (README, API docs)
- [ ] Type definitions added (if TypeScript)

### Final Verification

1. Run full test suite: `npm test`
2. Check browser for errors
3. Verify API responses with curl/Postman
4. Review code changes
5. Commit and push changes

**When all above are complete, output:**
```
<promise>DONE</promise>
```

## Notes

[Any additional context, assumptions, or considerations]

---

<!-- NR_OF_TRIES: 0 -->
```

## Writing Effective Acceptance Criteria

### Bad Examples (Too Vague)

❌ "Login works correctly"
- Not testable - what does "correctly" mean?

❌ "User can view dashboard"
- What should they see? Under what conditions?

❌ "API is fast"
- How fast? What metrics?

### Good Examples (Specific and Testable)

✅ "User can log in with email/password and receive JWT token"

**Given** a registered user with email `test@example.com` and password `SecurePass123`
**When** POST `/api/auth/login` with credentials
**Then** response is `200 OK` with JSON body containing valid JWT token

**Verification:**
```bash
curl -X POST https://api.example.com/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}' | jq '.token'
# Should return non-empty string
```

✅ "Dashboard displays user's name and email on load"

**Given** authenticated user with name "John Doe" and email "john@example.com"
**When** visiting `/dashboard`
**Then** page shows "Welcome, John Doe" and displays email in profile section

**Verification:**
```bash
# Using Playwright or similar
await expect(page.locator('.welcome-text')).toContainText('Welcome, John Doe')
await expect(page.locator('.email-display')).toContainText('john@example.com')
```

✅ "Invalid login attempts are rate-limited to 5 per minute"

**Given** username `test@example.com`
**When** 6 failed login attempts in 60 seconds
**Then** 6th attempt returns `429 Too Many Requests`

**Verification:**
```bash
for i in {1..6}; do
  curl -X POST https://api.example.com/login \
    -d '{"email":"test@example.com","password":"wrong"}' \
    -w "%{http_code}\n" -o /dev/null
done
# Last request should return 429
```

## Spec Creation Workflow

### Using Cursor Command

```bash
/speckit.specify Add user authentication with OAuth
```

This creates:
1. Folder `specs/NNN-user-auth/`
2. File `spec.md` with full template
3. Checklist at `checklists/requirements.md`

### Using AI Agent

Tell your AI agent:

> "Create a specification for [feature description]. Include clear acceptance criteria with Given/When/Then format and verification steps."

The agent will:
1. Determine next spec number
2. Create folder structure
3. Write comprehensive spec
4. Add quality checklist

### Manual Creation

```bash
# Find next number
ls -d specs/[0-9]*/ | sort | tail -1
# Output: specs/003-dashboard/

# Create next spec (004)
mkdir -p specs/004-feature-name/checklists
cp templates/spec-template.md specs/004-feature-name/spec.md
cp templates/checklist-template.md specs/004-feature-name/checklists/requirements.md

# Edit the spec
nano specs/004-feature-name/spec.md
```

## Checklist Template

Create `specs/NNN-feature/checklists/requirements.md`:

```markdown
# Requirements Checklist: [Feature Name]

## Before Implementation

- [ ] Reviewed constitution and project principles
- [ ] Understood all acceptance criteria
- [ ] Identified required dependencies
- [ ] Checked existing code for conflicts
- [ ] Reviewed history for related work

## During Implementation

- [ ] Following technical approach from spec
- [ ] Adding tests as code is written
- [ ] Keeping commits small and focused
- [ ] Documenting complex decisions

## Before Marking Complete

- [ ] All acceptance criteria verified
- [ ] All tests passing
- [ ] No console errors
- [ ] Code reviewed against style guide
- [ ] Documentation updated
- [ ] Changes committed and pushed

## Quality Gates

- [ ] No TODO comments
- [ ] No hardcoded secrets
- [ ] Type definitions complete (if TypeScript)
- [ ] Error handling comprehensive
- [ ] Edge cases covered
```

## Spec Examples

### Example 1: User Authentication

```markdown
# User Authentication with OAuth

## Overview

Implement user authentication using OAuth 2.0 with Google and GitHub providers. Users can sign up or log in using their existing accounts.

## Requirements

### Functional Requirements

- Users can authenticate with Google OAuth
- Users can authenticate with GitHub OAuth
- New users are automatically registered
- Existing users are logged in on return visits
- JWT tokens issued for authenticated sessions

### Non-Functional Requirements

- Authentication flow completes in < 3 seconds
- OAuth secrets stored in environment variables
- Compliant with OAuth 2.0 security best practices

## Acceptance Criteria

### Criterion 1: Google OAuth login works

**Given** user has a Google account
**When** clicking "Sign in with Google" and completing OAuth flow
**Then** user is authenticated and redirected to `/dashboard`

**Verification:**
```bash
# Manual browser test or automated with Playwright
# 1. Visit /login
# 2. Click "Sign in with Google"
# 3. Complete Google authentication
# 4. Verify redirect to /dashboard
# 5. Check localStorage contains valid JWT
```

### Criterion 2: GitHub OAuth login works

**Given** user has a GitHub account
**When** clicking "Sign in with GitHub" and completing OAuth flow
**Then** user is authenticated and redirected to `/dashboard`

**Verification:**
```bash
# Same as Criterion 1 but with GitHub button
```

### Criterion 3: New users are registered automatically

**Given** first-time user authenticating via OAuth
**When** OAuth flow completes successfully
**Then** user record created in database with email, name, and avatar

**Verification:**
```bash
# Check database after new OAuth signup
psql -c "SELECT email, name FROM users WHERE email='newuser@gmail.com';"
# Should return 1 row
```

## Technical Implementation

### Dependencies

- `passport` - OAuth strategy framework
- `passport-google-oauth20` - Google OAuth strategy
- `passport-github2` - GitHub OAuth strategy
- `jsonwebtoken` - JWT token generation

### Database Changes

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  avatar_url VARCHAR(500),
  provider VARCHAR(50) NOT NULL,
  provider_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_provider ON users(provider, provider_id);
```

## Testing Requirements

### Unit Tests

- [ ] JWT token generation and validation
- [ ] User creation logic
- [ ] OAuth callback parsing

### Integration Tests

- [ ] Full Google OAuth flow (mocked)
- [ ] Full GitHub OAuth flow (mocked)
- [ ] Database user lookup by provider_id

### Browser Tests

- [ ] Login page renders OAuth buttons
- [ ] OAuth redirects work correctly
- [ ] Dashboard shows user info after login

## Completion Signal

[... same structure as template ...]
```

### Example 2: API Rate Limiting

```markdown
# API Rate Limiting

## Overview

Implement rate limiting for API endpoints to prevent abuse and ensure fair usage.

## Acceptance Criteria

### Criterion 1: Unauthenticated requests limited to 100 per hour

**Given** IP address `192.168.1.100`
**When** making 101 requests within 60 minutes
**Then** 101st request returns `429 Too Many Requests` with retry-after header

**Verification:**
```bash
# Script to make 101 requests
for i in {1..101}; do
  code=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/data)
  if [ $i -eq 101 ]; then
    [ "$code" = "429" ] && echo "PASS" || echo "FAIL: got $code"
  fi
done
```

### Criterion 2: Authenticated users get 1000 requests per hour

**Given** authenticated user with valid JWT
**When** making 1001 requests within 60 minutes
**Then** 1001st request returns `429` with message "Rate limit exceeded"

**Verification:**
```bash
token=$(curl -s -X POST https://api.example.com/login -d '{"email":"test@example.com"}' | jq -r '.token')

for i in {1..1001}; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $token" \
    https://api.example.com/data)
  
  if [ $i -eq 1001 ]; then
    [ "$code" = "429" ] && echo "PASS" || echo "FAIL: got $code"
  fi
done
```

[... rest of spec ...]
```

## Common Mistakes to Avoid

### ❌ Vague Acceptance Criteria

**Bad:**
```markdown
## Acceptance Criteria
- Login works
- Dashboard loads
- API is fast
```

**Good:**
```markdown
## Acceptance Criteria
### Criterion 1: User can log in with valid credentials

**Given** registered user with email `test@example.com` and password `SecurePass123`
**When** POST `/api/auth/login` with correct credentials
**Then** response is `200 OK` with JWT token

**Verification:**
```bash
curl -X POST https://api.example.com/login \
  -d '{"email":"test@example.com","password":"SecurePass123"}' | jq '.token'
# Should return non-empty string
```
```

### ❌ Missing Verification Steps

**Bad:**
```markdown
### Criterion: Email validation works
User emails must be valid format
```

**Good:**
```markdown
### Criterion: Email validation rejects invalid formats

**Given** registration form
**When** submitting email `invalid-email` without @ symbol
**Then** error message "Please enter a valid email address"

**Verification:**
```bash
curl -X POST https://api.example.com/register \
  -d '{"email":"invalid-email","password":"Secure123"}' | jq '.error'
# Should return "Invalid email format"
```
```

### ❌ Too Broad Scope

**Bad:** One spec trying to do everything:
- User authentication
- Profile management
- Password reset
- Email verification
- Two-factor authentication

**Good:** Split into focused specs:
- `001-user-auth` - Basic email/password login
- `002-oauth-providers` - OAuth with Google/GitHub
- `003-password-reset` - Forgot password flow
- `004-email-verification` - Confirm email addresses
- `005-two-factor-auth` - 2FA with TOTP

## Best Practices

1. **One feature per spec** - Keep scope focused and achievable
2. **Testable criteria** - Each criterion must have verification steps
3. **Include edge cases** - What happens with invalid input, errors, etc.
4. **Specify testing requirements** - Unit tests, integration tests, browser checks
5. **Add completion checklist** - Clear items to verify before DONE
6. **Document technical approach** - Helps agent make informed decisions
7. **Keep NR_OF_TRIES counter** - Track attempts and detect stuck specs

## Next Steps

After creating specs:
1. Review [Running Ralph Loops](03-running-ralph-loops.md) to start implementation
2. Explore [Advanced Features](05-advanced-features.md) for notifications and integrations
3. Monitor progress using logging and NR_OF_TRIES tracking
