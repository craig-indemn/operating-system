# Slack OAuth Scopes Reference

The 30 user token scopes needed for full Slack API access. Add all of these under **User Token Scopes** when creating the Slack app.

## Complete Scope List

```
bookmarks:read
bookmarks:write
channels:history
channels:read
channels:write
chat:write
chat:write.public
files:read
files:write
groups:history
groups:read
groups:write
im:history
im:read
im:write
mpim:history
mpim:read
mpim:write
pins:read
pins:write
reactions:read
reactions:write
reminders:read
reminders:write
search:read
usergroups:read
usergroups:write
users:read
users:read.email
users.profile:read
users.profile:write
```

## Scope-to-Operation Mapping

| Scope | Enables |
|-------|---------|
| `bookmarks:read` | List bookmarks in channels |
| `bookmarks:write` | Add, edit, remove bookmarks |
| `channels:history` | Read public channel messages and threads |
| `channels:read` | List public channels, get channel info and members |
| `channels:write` | Create, archive, rename public channels; invite/kick users; set topic/purpose |
| `chat:write` | Send messages, edit own messages, delete own messages, schedule messages |
| `chat:write.public` | Send messages to public channels without joining them first |
| `files:read` | List files, get file info |
| `files:write` | Upload and delete files |
| `groups:history` | Read private channel messages and threads |
| `groups:read` | List private channels, get channel info and members |
| `groups:write` | Create, archive private channels; invite/kick users; set topic/purpose |
| `im:history` | Read DM message history |
| `im:read` | List DM channels |
| `im:write` | Open DMs, mark DMs as read |
| `mpim:history` | Read group DM message history |
| `mpim:read` | List group DM channels |
| `mpim:write` | Open group DMs, mark group DMs as read |
| `pins:read` | List pinned messages |
| `pins:write` | Pin and unpin messages |
| `reactions:read` | Get reactions on messages |
| `reactions:write` | Add and remove reactions |
| `reminders:read` | List reminders |
| `reminders:write` | Create, complete, delete reminders |
| `search:read` | Search messages and files (user token only — does not work with bot tokens) |
| `usergroups:read` | List user groups and their members |
| `usergroups:write` | Create user groups, update membership |
| `users:read` | List users, get user info |
| `users:read.email` | Access user email addresses |
| `users.profile:read` | Get user profiles |
| `users.profile:write` | Set own status and profile fields |

## Token Type Notes

- **User tokens (xoxp-)**: Support all 30 scopes above including `search:read`
- **Browser tokens (xoxc-)**: Same capabilities as user tokens (they represent a logged-in user session)
- **Bot tokens (xoxb-)**: Cannot use `search:read`, `users.profile:write`, or `users:read.email`. Use user tokens for these operations.
