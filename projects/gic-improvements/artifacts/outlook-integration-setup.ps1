# Indemn Email Reader — Exchange Online Setup for GIC
# Scopes read-only email access to quote@gicunderwriters.com
#
# Prerequisites:
#   - Run PowerShell as Administrator
#   - Sign in with a Microsoft 365 admin account when prompted
#
# App Details:
#   App (Client) ID: 4bf2eacd-4869-4ade-890c-ba5f76c7cada
#   Object ID:       06ea725e-da27-445d-9873-2db1bde8e0aa
#   Mailbox:         quote@gicunderwriters.com
#   Permission:      Mail.Read (read-only)

# Step 1: Install the Exchange Online module (one-time, skip if already installed)
Install-Module -Name ExchangeOnlineManagement

# Step 2: Connect — a browser window will open for sign-in
Connect-ExchangeOnline

# Step 3: Register the app as a service principal in Exchange
New-ServicePrincipal -AppId "4bf2eacd-4869-4ade-890c-ba5f76c7cada" -ObjectId "06ea725e-da27-445d-9873-2db1bde8e0aa" -DisplayName "Indemn Email Reader"

# Step 4: Create a scope limited to the quote inbox
New-ManagementScope -Name "IndemnScope" -RecipientRestrictionFilter "UserPrincipalName -eq 'quote@gicunderwriters.com'"

# Step 5: Assign read-only mail access within that scope
New-ManagementRoleAssignment -App "4bf2eacd-4869-4ade-890c-ba5f76c7cada" -Role "Application Mail.Read" -CustomResourceScope "IndemnScope"

# Step 6: Disconnect
Disconnect-ExchangeOnline -Confirm:$false
