# Craig's Claude Code Setup — Full Stack Access

Get your Claude Code instance connected to Slack, Google Docs, and the meetings database.

# WHAT YOU'LL HAVE WHEN THIS IS DONE

\- Slack MCP — read and search all Slack channels, DMs, threads from your terminal  
\- Google Docs MCP — read, create, edit Google Docs and Sheets from your terminal  
\- Neon Postgres — direct access to the meetings intelligence database (3,211 meetings, 22K+ extracted items, 55 Prisma models)  
\- Context files — CLAUDE.md that orients your Claude Code to the projects and your role

# STEP 1: Google Docs MCP Server

Clone and build the server:

git clone https://github.com/a-bonus/google-docs-mcp.git mcp-googledocs-server  
cd mcp-googledocs-server  
npm install  
npm run build

Copy the credentials.json file below into the mcp-googledocs-server/ directory:

{  
  "web": {  
    "client\_id": "935362412674-q41ptbogu9u6e2l1dd82mdvela7t80dg.apps.googleusercontent.com",  
    "project\_id": "indemn-claude-mcp",  
    "auth\_uri": "https://accounts.google.com/o/oauth2/auth",  
    "token\_uri": "https://oauth2.googleapis.com/token",  
    "auth\_provider\_x509\_cert\_url": "https://www.googleapis.com/oauth2/v1/certs",  
    "client\_secret": "REDACTED_GOOGLE_CLIENT_SECRET",  
    "redirect\_uris": \["http://localhost:3000"\]  
  }  
}

Run the server once to generate your personal token:

node ./dist/server.js

It will print a Google OAuth URL. Open it in your browser, sign in with your @indemn.ai Google account, approve the permissions, and paste the authorization code back into the terminal. This creates your personal token.json file.

**REQUIRES KYLE: Kyle needs to add your @indemn.ai email as a test user** in the Google Cloud Console (project: indemn-claude-mcp) before the OAuth flow will work. If this step hasn't been done yet, the OAuth screen will show an error.

# STEP 2: Slack MCP Server

The Slack MCP runs via npx — no local install needed. You just need your own Slack user token.

**REQUIRES KYLE: Kyle needs to share the Slack app OAuth install URL** so you can authorize it with your own Slack account. This generates a personal xoxp- token. Once you have it, you're good.

The config (once you have the token):

claude mcp add slack \--env SLACK\_MCP\_XOXP\_TOKEN=xoxp-YOUR-TOKEN-HERE \--env SLACK\_MCP\_ADD\_MESSAGE\_TOOL=true \-- npx \-y slack-mcp-server@latest

This gives you 5 tools: channels\_list, conversations\_history, conversations\_add\_message, conversations\_replies, conversations\_search\_messages. You can read any channel, search all messages, and post.

# STEP 3: Neon Postgres — Meetings Intelligence Database

Connection string:

postgresql://neondb\_owner:npg\_nVu6YlOHwQ1p@ep-dark-hat-ah6i1mwb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require

This is the same database that both the meetings and pipeline systems use. Connect with any Postgres client (psql, pgAdmin, DataGrip, or just Claude Code with a script).

Key tables for the meetings intelligence system:

Core:  
\- meetings — 3,211 records. title, date, source (apollo/granola), duration, host, category  
\- meeting\_utterances — full transcripts. speaker\_name, text, start\_ms, end\_ms, sequence\_order  
\- meeting\_participants — name, email, role, speaking\_time\_ms, utterance\_count  
\- meeting\_analyses — AI-generated summaries, categories, key insights, action items

Extracted Intelligence:  
\- historical\_decisions — 5,515 records. decision text, category (strategic/technical/process/product), participants, rationale  
\- historical\_quotes — 3,681 records. quote text, speaker, sentiment, context, significance  
\- historical\_signals — 3,239 records. signal type (champion/expansion/churn/blocker/health), description, company, evidence  
\- historical\_objections — 1,608 records. objection text, category, response, whether response worked  
\- historical\_learnings — 5,099 records. learning text, category, context  
\- historical\_problems — 2,971 records. problem text, severity, customer

CRM-adjacent:  
\- people — name, email, company, role, interaction history  
\- customer\_profiles — aggregated intelligence per customer  
\- customer\_contacts, person\_companies — relationship mapping

Workflow:  
\- extraction\_runs — tracks what's been extracted  
\- action\_items, commitments — from meetings  
\- daily\_reviews, morning\_briefs — daily operational outputs

Full schema: 55 Prisma models. Run this to see everything:

psql "postgresql://neondb\_owner:npg\_nVu6YlOHwQ1p@ep-dark-hat-ah6i1mwb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require" \-c "\\dt"

# STEP 4: Register MCP Servers with Claude Code

After Steps 1-2 are complete:

claude mcp add google-docs node /full/path/to/mcp-googledocs-server/dist/server.js

claude mcp add slack \--env SLACK\_MCP\_XOXP\_TOKEN=xoxp-YOUR-TOKEN-HERE \--env SLACK\_MCP\_ADD\_MESSAGE\_TOOL=true \-- npx \-y slack-mcp-server@latest

Then restart Claude Code. Both servers will spawn automatically each session.

# STEP 5: Context Files

Create a CLAUDE.md in your working directory. This loads every turn and orients Claude Code to your context. Here's a starting point:

\# Craig's Claude Code — Indemn

\#\# Role  
Technical lead. You own the production platform (copilot-server, bot-service, discovery-chat-ui, voice-livekit) and the evaluation system. You're also evaluating the meetings intelligence architecture.

\#\# Current Priorities  
1\. Evaluation system — push to prod, run baselines across every customer  
2\. Meetings intelligence — review architecture, form technical questions (see Intelligence System Briefing)  
3\. Platform development — copilot dashboard, agent building, Jarvis

\#\# APIs & Integrations  
| Need | Access |  
|------|--------|  
| Slack | mcp\_\_slack\_\_\* tools |  
| Google Docs | mcp\_\_google-docs\_\_\* tools |  
| Meetings DB | Neon Postgres (connection string in setup doc) |  
| Pipeline API | https://indemn-pipeline.vercel.app/api/\* |  
| GitHub | indemn-ai org (you already have access) |

\#\# Key Docs  
\- Intelligence System Briefing: https://docs.google.com/document/d/1OkBWMpxhC7TgqvaaAqFme7iu3R5357xp6bg345o65Rc/edit  
\- Landing Page Request Template: https://docs.google.com/document/d/1Hkq-MjusuGNnF3eYJ8kvLLRBzwEL9PoBq3RUaB8sMBU/edit

\#\# Rules  
1\. Google Docs: ALWAYS use shared folders, never personal Drive  
2\. Slack: Use MCP tools, not Playwright  
3\. Check with Kyle before modifying shared infrastructure

# WHERE TO START

1\. Read the Intelligence System Briefing if you haven't already: https://docs.google.com/document/d/1OkBWMpxhC7TgqvaaAqFme7iu3R5357xp6bg345o65Rc/edit

2\. Connect to Postgres and explore the schema. Start with:  
   SELECT count(\*) FROM meetings;  
   SELECT type, count(\*) FROM historical\_signals GROUP BY type ORDER BY count DESC;  
   SELECT \* FROM historical\_quotes WHERE sentiment \= 'positive' LIMIT 10;

3\. Look at the extraction pipeline — how meetings go from raw transcript to structured intelligence. The models are in the meetings schema. The questions from the Briefing are the ones I want your perspective on:  
   \- Is the data model right? 55 models might be too many or too few.  
   \- Extraction pipeline runs Claude on every meeting. Right approach vs embeddings/RAG/hybrid?  
   \- How would you deploy this? Vercel config exists but migration is incomplete.  
   \- How does this relate to copilot-server? Should it merge or stay separate?  
   \- What's the right way to make this data accessible to other Claude Code instances?

4\. When you have questions or opinions, bring them back. We'll dig into specific code and session history based on what you want to understand.  
