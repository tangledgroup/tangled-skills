# User Management

## Contents
- Invitations
- Self-Registration
- User Update Page
- Security Groups
- Password Resets

## Invitations

Users are created exclusively through invitations. Admins (users in `auth_admins` group) create invitations from the sidebar under **Invitations**.

When creating an invitation:
- Set the future user's username and initial profile settings
- Either username or email must be pre-filled; remaining fields can be filled by the user upon acceptance
- Select initial security groups
- The invitation link is generated and displayed on the page
- Send via email (if SMTP configured) or copy and send directly

Invited users are always **approved**. If an admin set their email address, it is auto-verified when they accept the invitation. Users choose their own password upon acceptance.

## Self-Registration

Set `SIGNUP=true` to enable user self-registration without invitations. Control behavior with:

| Variable | Effect |
|----------|--------|
| `SIGNUP=true` + `SIGNUP_REQUIRES_APPROVAL=true` (default) | Users register but need admin approval before access |
| `SIGNUP=true` + `SIGNUP_REQUIRES_APPROVAL=false` | Open self-registration — use with caution |

## User Update Page

Admins can modify existing users from the sidebar under **Users**. The User Update page allows changing:
- Username and profile settings
- Security group membership
- Email verification status
- Approval status

## Security Groups

Security Groups are created from the admin **Groups** page. Users are added to groups from either the Group Update or User Update pages.

### Special Group: `auth_admins`

Users in the `auth_admins` group become VoidAuth administrators and are never denied access to any resource, regardless of other security group restrictions. After initial setup with the default `auth_admin` account, create your own user and add it to `auth_admins`.

### Group Options

- **MFA Required**: Users in this group must use Multi-Factor Authentication (authenticator token or passkey) to log in
- **Auto Assign**: This group is automatically added to new invitations by default

### Usage

Security Groups control access in both contexts:
- **ProxyAuth Domains**: Authorization checks and Trusted Header SSO (groups sent via `Remote-Groups` header)
- **OIDC Apps**: App-level authorization and token claims (groups included when the app requests the `groups` scope)

## Password Resets

Password reset requests are managed from the admin **Password Resets** page. Admins can:
- Search for a user and create a new password reset request
- Copy the reset link or send it via email
- View and delete existing reset requests

Users can also request their own password resets from the login page. If their email is not set or emails fail to send, an admin must manually create and deliver the reset link.
