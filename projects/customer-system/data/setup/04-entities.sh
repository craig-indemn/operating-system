#!/bin/bash
# =============================================================================
# Step 4: Define Entity Types
# =============================================================================
# These commands define the domain entities for the customer system.
# Each entity create stores a definition in the database. The OS
# auto-generates CLI commands, API endpoints, UI views, and skills
# from the definition.
#
# Note: The exact CLI syntax for defining fields, state machines, and
# relationships will depend on the kernel implementation. This captures
# the intent and structure. May use --from-file with YAML definitions.
# =============================================================================

# ---------------------------------------------------------------------------
# Reference Entities (defined first — referenced by domain entities)
# ---------------------------------------------------------------------------

indemn entity create Stage \
  --fields '{
    "name": {"type": "string", "required": true},
    "probability": {"type": "decimal", "required": true},
    "stale_after_days": {"type": "integer"},
    "definition": {"type": "text"},
    "order": {"type": "integer", "required": true}
  }'

indemn entity create OutcomeType \
  --fields '{
    "name": {"type": "string", "required": true},
    "engine": {"type": "string", "required": true},
    "description": {"type": "text"},
    "key_metrics": {"type": "list[string]"},
    "proof_points": {"type": "text"},
    "language_guidance": {"type": "text"}
  }'

indemn entity create AssociateType \
  --fields '{
    "name": {"type": "string", "required": true},
    "engine": {"type": "enum", "values": ["Revenue", "Efficiency", "Retention", "Control"], "required": true},
    "maturity": {"type": "enum", "values": ["Proven", "Ready", "In_Dev"], "required": true},
    "deployment_modes": {"type": "list[enum]", "values": ["Voice", "Chat", "Email", "Copilot"]},
    "description": {"type": "text"},
    "proof_points": {"type": "text"},
    "standard_checklist": {"type": "text"},
    "required_inputs": {"type": "text"},
    "integration_requirements": {"type": "list[string]"},
    "typical_timeline": {"type": "string"},
    "escalation_paths": {"type": "text"},
    "success_metrics": {"type": "text"},
    "notes": {"type": "text"}
  }'

# ---------------------------------------------------------------------------
# Core Domain Entities
# ---------------------------------------------------------------------------

indemn entity create Company \
  --fields '{
    "name": {"type": "string", "required": true},
    "type": {"type": "enum", "values": ["Broker", "MGA_MGU", "Carrier", "InsurTech", "VC", "Association", "Other"]},
    "cohort": {"type": "enum", "values": ["Core_Platform", "Graduating", "AI_Investments", "Prospect"]},
    "tier": {"type": "enum", "values": ["Enterprise", "Core"]},
    "icp_fit": {"type": "enum", "values": ["Strong", "Medium", "Low"]},
    "source": {"type": "enum", "values": ["Conference", "Inbound", "Referral", "Outbound", "Existing"]},
    "source_detail": {"type": "string"},
    "source_conference": {"type": "entity_ref", "entity": "Conference"},
    "owner": {"type": "actor_ref"},
    "standin": {"type": "actor_ref"},
    "engineering_lead": {"type": "actor_ref"},
    "exec_sponsor": {"type": "actor_ref"},
    "arr": {"type": "decimal"},
    "website": {"type": "string"},
    "domain": {"type": "string"},
    "linkedin_url": {"type": "string"},
    "industry": {"type": "string"},
    "hq_location": {"type": "string"},
    "employee_count": {"type": "integer"},
    "annual_revenue": {"type": "decimal"},
    "founded_year": {"type": "integer"},
    "ams_system": {"type": "string"},
    "technologies": {"type": "list[string]"},
    "specialties": {"type": "list[string]"},
    "drive_folder_url": {"type": "string"},
    "category": {"type": "string"},
    "champion": {"type": "string"},
    "health_score": {"type": "integer"},
    "next_step": {"type": "string"},
    "next_step_owner": {"type": "actor_ref"},
    "follow_up_date": {"type": "date"},
    "notes": {"type": "text"}
  }' \
  --state-machine '{
    "field": "stage",
    "states": ["prospect", "pilot", "customer", "expanding", "churned", "paused"],
    "transitions": {
      "prospect": ["pilot", "churned", "paused"],
      "pilot": ["customer", "churned", "paused"],
      "customer": ["expanding", "churned", "paused"],
      "expanding": ["customer", "churned", "paused"],
      "paused": ["prospect", "pilot", "customer"],
      "churned": ["prospect"]
    },
    "initial": "prospect"
  }'

indemn entity create Contact \
  --fields '{
    "company": {"type": "entity_ref", "entity": "Company", "required": true},
    "name": {"type": "string", "required": true},
    "title": {"type": "string"},
    "email": {"type": "string"},
    "phone": {"type": "string"},
    "role": {"type": "enum", "values": ["Champion", "Decision_Maker", "Executive_Sponsor", "Technical", "Day_to_Day", "Influencer", "End_User", "Connector", "Contact"]},
    "is_primary": {"type": "boolean"},
    "how_met": {"type": "enum", "values": ["Conference", "LinkedIn", "Email_Intro", "Referral", "Discovery_Call", "Inbound", "Cold_Outreach"]},
    "linkedin_url": {"type": "string"},
    "notes": {"type": "text"}
  }'

indemn entity create Conference \
  --fields '{
    "name": {"type": "string", "required": true},
    "location": {"type": "string"},
    "date_start": {"type": "date"},
    "date_end": {"type": "date"},
    "owner": {"type": "actor_ref"},
    "cost": {"type": "decimal"},
    "attendee_list_ref": {"type": "string"},
    "attendee_count": {"type": "integer"},
    "notes": {"type": "text"}
  }' \
  --state-machine '{
    "field": "stage",
    "states": ["planning", "pre_event", "active", "follow_up", "complete"],
    "transitions": {
      "planning": ["pre_event"],
      "pre_event": ["active"],
      "active": ["follow_up"],
      "follow_up": ["complete"]
    },
    "initial": "planning"
  }'

indemn entity create AssociateDeployment \
  --fields '{
    "company": {"type": "entity_ref", "entity": "Company", "required": true},
    "associate_type": {"type": "entity_ref", "entity": "AssociateType", "required": true},
    "name": {"type": "string", "required": true},
    "outcome": {"type": "entity_ref", "entity": "Outcome"},
    "channels": {"type": "list[enum]", "values": ["Voice", "Chat", "Email", "Copilot"]},
    "tier": {"type": "enum", "values": ["Tier_1", "Tier_2", "Tier_3"]},
    "owner": {"type": "actor_ref"},
    "integration_requirements": {"type": "list[string]"},
    "escalation_paths": {"type": "text"},
    "success_metrics": {"type": "text"},
    "notes": {"type": "text"}
  }' \
  --state-machine '{
    "field": "stage",
    "states": ["planned", "building", "testing", "live", "paused", "retired"],
    "transitions": {
      "planned": ["building"],
      "building": ["testing", "paused"],
      "testing": ["live", "building", "paused"],
      "live": ["paused", "retired"],
      "paused": ["building", "testing", "live", "retired"]
    },
    "initial": "planned"
  }'

indemn entity create Outcome \
  --fields '{
    "company": {"type": "entity_ref", "entity": "Company", "required": true},
    "outcome_type": {"type": "entity_ref", "entity": "OutcomeType", "required": true},
    "associate_deployments": {"type": "list[entity_ref]", "entity": "AssociateDeployment"},
    "notes": {"type": "text"}
  }'

indemn entity create Playbook \
  --fields '{
    "name": {"type": "string", "required": true},
    "associate_type": {"type": "entity_ref", "entity": "AssociateType"},
    "description": {"type": "text"},
    "steps": {"type": "text"},
    "required_inputs": {"type": "text"},
    "integration_requirements": {"type": "list[string]"},
    "typical_timeline": {"type": "string"},
    "success_metrics": {"type": "text"},
    "escalation_paths": {"type": "text"},
    "notes": {"type": "text"}
  }' \
  --state-machine '{
    "field": "stage",
    "states": ["draft", "active", "archived"],
    "transitions": {
      "draft": ["active"],
      "active": ["archived", "draft"],
      "archived": ["draft"]
    },
    "initial": "draft"
  }'

# ---------------------------------------------------------------------------
# Meeting Intelligence Entities
# ---------------------------------------------------------------------------

indemn entity create Meeting \
  --fields '{
    "company": {"type": "entity_ref", "entity": "Company"},
    "contacts": {"type": "list[entity_ref]", "entity": "Contact"},
    "team_members": {"type": "list[actor_ref]"},
    "title": {"type": "string", "required": true},
    "date": {"type": "datetime", "required": true},
    "duration_minutes": {"type": "integer"},
    "source": {"type": "enum", "values": ["Gemini", "Granola", "Google_Meet", "Zoom", "Phone", "In_Person"]},
    "transcript_ref": {"type": "string"},
    "recording_ref": {"type": "string"},
    "summary": {"type": "text"},
    "notes": {"type": "text"}
  }' \
  --state-machine '{
    "field": "stage",
    "states": ["recorded", "processed", "intelligence_extracted"],
    "transitions": {
      "recorded": ["processed"],
      "processed": ["intelligence_extracted"]
    },
    "initial": "recorded"
  }'

indemn entity create Task \
  --fields '{
    "company": {"type": "entity_ref", "entity": "Company"},
    "title": {"type": "string", "required": true},
    "description": {"type": "text"},
    "assignee": {"type": "actor_ref"},
    "owner_type": {"type": "enum", "values": ["Internal", "Customer"]},
    "due_date": {"type": "date"},
    "priority": {"type": "enum", "values": ["Low", "Medium", "High", "Critical"]},
    "category": {"type": "enum", "values": ["Technical", "Training", "Testing", "Compliance", "Sales", "Relationship", "Administrative"]},
    "source": {"type": "enum", "values": ["Meeting", "Implementation", "Playbook", "Manual"]},
    "source_meeting": {"type": "entity_ref", "entity": "Meeting"},
    "source_implementation": {"type": "entity_ref", "entity": "Implementation"},
    "effort": {"type": "enum", "values": ["Small", "Medium", "Large"]},
    "notes": {"type": "text"}
  }' \
  --state-machine '{
    "field": "stage",
    "states": ["open", "in_progress", "completed", "blocked", "cancelled"],
    "transitions": {
      "open": ["in_progress", "cancelled"],
      "in_progress": ["completed", "blocked", "cancelled"],
      "blocked": ["in_progress", "cancelled"],
      "completed": [],
      "cancelled": []
    },
    "initial": "open"
  }'

indemn entity create Commitment \
  --fields '{
    "company": {"type": "entity_ref", "entity": "Company"},
    "meeting": {"type": "entity_ref", "entity": "Meeting"},
    "description": {"type": "text", "required": true},
    "made_by": {"type": "string"},
    "made_by_side": {"type": "enum", "values": ["Indemn", "Customer"]},
    "made_to": {"type": "string"},
    "due_date": {"type": "date"},
    "due_date_precision": {"type": "enum", "values": ["Exact", "Approximate", "Unspecified"]},
    "notes": {"type": "text"}
  }' \
  --state-machine '{
    "field": "stage",
    "states": ["open", "fulfilled", "missed", "dismissed"],
    "transitions": {
      "open": ["fulfilled", "missed", "dismissed"],
      "missed": ["fulfilled", "dismissed"],
      "fulfilled": [],
      "dismissed": []
    },
    "initial": "open"
  }'

indemn entity create Signal \
  --fields '{
    "company": {"type": "entity_ref", "entity": "Company"},
    "meeting": {"type": "entity_ref", "entity": "Meeting"},
    "type": {"type": "enum", "values": ["Health_Positive", "Health_Negative", "Expansion", "Churn_Risk", "Blocker", "Champion_Identified", "Budget_Concern", "Competitor_Mentioned", "Escalation", "Satisfaction"]},
    "description": {"type": "text", "required": true},
    "source": {"type": "enum", "values": ["Meeting", "Email", "Slack", "Usage_Data", "Manual"]},
    "severity": {"type": "enum", "values": ["Low", "Medium", "High"]},
    "attributed_to": {"type": "string"},
    "notes": {"type": "text"}
  }'

indemn entity create Decision \
  --fields '{
    "company": {"type": "entity_ref", "entity": "Company"},
    "meeting": {"type": "entity_ref", "entity": "Meeting"},
    "description": {"type": "text", "required": true},
    "decided_by": {"type": "string"},
    "participants": {"type": "list[string]"},
    "rationale": {"type": "text"},
    "impact": {"type": "enum", "values": ["Customer_Scope", "Pricing", "Technical", "Timeline", "Staffing", "Strategy", "Process"]},
    "supersedes": {"type": "entity_ref", "entity": "Decision"},
    "notes": {"type": "text"}
  }'
