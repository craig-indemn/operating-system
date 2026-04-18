#!/bin/bash
# =============================================================================
# Step 4: Define Entity Types
# =============================================================================
# These commands define the domain entities for the customer system.
# Each entity create stores a definition in the database. The OS
# auto-generates CLI commands, API endpoints, UI views, and skills
# from the definition.
#
# Syntax:
#   indemn entity create <Name> \
#     --fields '<JSON>' \
#     --state-machine '<JSON>'
#
# Field types: str, int, float, decimal, bool, datetime, date,
#              objectid, list, dict
#
# Type mappings from design to CLI:
#   entity_ref  -> objectid + is_relationship + relationship_target
#   actor_ref   -> objectid + is_relationship + relationship_target: "Actor"
#   enum        -> str + enum_values
#   list[X]     -> list (element typing not yet supported)
#   computed    -> REMOVED (handled separately)
# =============================================================================

# ---------------------------------------------------------------------------
# Reference Entities (defined first -- referenced by domain entities)
# ---------------------------------------------------------------------------

indemn entity create Stage \
  --fields '{
    "name": {"type": "str", "required": true},
    "probability": {"type": "decimal", "required": true},
    "stale_after_days": {"type": "int"},
    "definition": {"type": "str"},
    "order": {"type": "int", "required": true}
  }'

indemn entity create OutcomeType \
  --fields '{
    "name": {"type": "str", "required": true},
    "engine": {"type": "str", "required": true},
    "description": {"type": "str"},
    "key_metrics": {"type": "list"},
    "proof_points": {"type": "str"},
    "language_guidance": {"type": "str"}
  }'

indemn entity create AssociateType \
  --fields '{
    "name": {"type": "str", "required": true},
    "engine": {"type": "str", "enum_values": ["Revenue", "Efficiency", "Retention", "Control"], "required": true},
    "maturity": {"type": "str", "enum_values": ["Proven", "Ready", "In_Dev"], "required": true},
    "deployment_modes": {"type": "list"},
    "description": {"type": "str"},
    "proof_points": {"type": "str"},
    "standard_checklist": {"type": "str"},
    "required_inputs": {"type": "str"},
    "integration_requirements": {"type": "list"},
    "typical_timeline": {"type": "str"},
    "escalation_paths": {"type": "str"},
    "success_metrics": {"type": "str"},
    "notes": {"type": "str"}
  }'

# ---------------------------------------------------------------------------
# Core Domain Entities
# ---------------------------------------------------------------------------

indemn entity create Company \
  --fields '{
    "name": {"type": "str", "required": true},
    "type": {"type": "str", "enum_values": ["Broker", "MGA_MGU", "Carrier", "InsurTech", "VC", "Association", "Other"]},
    "cohort": {"type": "str", "enum_values": ["Core_Platform", "Graduating", "AI_Investments", "Prospect"]},
    "tier": {"type": "str", "enum_values": ["Enterprise", "Core"]},
    "icp_fit": {"type": "str", "enum_values": ["Strong", "Medium", "Low"]},
    "source": {"type": "str", "enum_values": ["Conference", "Inbound", "Referral", "Outbound", "Existing"]},
    "source_detail": {"type": "str"},
    "source_conference": {"type": "objectid", "is_relationship": true, "relationship_target": "Conference"},
    "owner": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "standin": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "engineering_lead": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "exec_sponsor": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "arr": {"type": "decimal"},
    "website": {"type": "str"},
    "domain": {"type": "str"},
    "linkedin_url": {"type": "str"},
    "industry": {"type": "str"},
    "hq_location": {"type": "str"},
    "employee_count": {"type": "int"},
    "annual_revenue": {"type": "decimal"},
    "founded_year": {"type": "int"},
    "ams_system": {"type": "str"},
    "technologies": {"type": "list"},
    "specialties": {"type": "list"},
    "drive_folder_url": {"type": "str"},
    "category": {"type": "str"},
    "champion": {"type": "str"},
    "health_score": {"type": "int"},
    "next_step": {"type": "str"},
    "next_step_owner": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "follow_up_date": {"type": "date"},
    "stage": {"type": "str", "is_state_field": true, "default": "prospect", "enum_values": ["prospect", "pilot", "customer", "expanding", "churned", "paused"]},
    "notes": {"type": "str"}
  }' \
  --state-machine '{
    "prospect": ["pilot", "churned", "paused"],
    "pilot": ["customer", "churned", "paused"],
    "customer": ["expanding", "churned", "paused"],
    "expanding": ["customer", "churned", "paused"],
    "paused": ["prospect", "pilot", "customer"],
    "churned": ["prospect"]
  }'

indemn entity create Contact \
  --fields '{
    "company": {"type": "objectid", "is_relationship": true, "relationship_target": "Company", "required": true},
    "name": {"type": "str", "required": true},
    "title": {"type": "str"},
    "email": {"type": "str"},
    "phone": {"type": "str"},
    "role": {"type": "str", "enum_values": ["Champion", "Decision_Maker", "Executive_Sponsor", "Technical", "Day_to_Day", "Influencer", "End_User", "Connector", "Contact"]},
    "is_primary": {"type": "bool"},
    "how_met": {"type": "str", "enum_values": ["Conference", "LinkedIn", "Email_Intro", "Referral", "Discovery_Call", "Inbound", "Cold_Outreach"]},
    "linkedin_url": {"type": "str"},
    "notes": {"type": "str"}
  }'

indemn entity create Conference \
  --fields '{
    "name": {"type": "str", "required": true},
    "location": {"type": "str"},
    "date_start": {"type": "date"},
    "date_end": {"type": "date"},
    "owner": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "cost": {"type": "decimal"},
    "attendee_list_ref": {"type": "str"},
    "attendee_count": {"type": "int"},
    "stage": {"type": "str", "is_state_field": true, "default": "planning", "enum_values": ["planning", "pre_event", "active", "follow_up", "complete"]},
    "notes": {"type": "str"}
  }' \
  --state-machine '{
    "planning": ["pre_event"],
    "pre_event": ["active"],
    "active": ["follow_up"],
    "follow_up": ["complete"]
  }'

indemn entity create AssociateDeployment \
  --fields '{
    "company": {"type": "objectid", "is_relationship": true, "relationship_target": "Company", "required": true},
    "associate_type": {"type": "objectid", "is_relationship": true, "relationship_target": "AssociateType", "required": true},
    "name": {"type": "str", "required": true},
    "outcome": {"type": "objectid", "is_relationship": true, "relationship_target": "Outcome"},
    "channels": {"type": "list"},
    "tier": {"type": "str", "enum_values": ["Tier_1", "Tier_2", "Tier_3"]},
    "owner": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "integration_requirements": {"type": "list"},
    "escalation_paths": {"type": "str"},
    "success_metrics": {"type": "str"},
    "stage": {"type": "str", "is_state_field": true, "default": "planned", "enum_values": ["planned", "building", "testing", "live", "paused", "retired"]},
    "notes": {"type": "str"}
  }' \
  --state-machine '{
    "planned": ["building"],
    "building": ["testing", "paused"],
    "testing": ["live", "building", "paused"],
    "live": ["paused", "retired"],
    "paused": ["building", "testing", "live", "retired"]
  }'

indemn entity create Outcome \
  --fields '{
    "company": {"type": "objectid", "is_relationship": true, "relationship_target": "Company", "required": true},
    "outcome_type": {"type": "objectid", "is_relationship": true, "relationship_target": "OutcomeType", "required": true},
    "associate_deployments": {"type": "list"},
    "notes": {"type": "str"}
  }'

indemn entity create Playbook \
  --fields '{
    "name": {"type": "str", "required": true},
    "associate_type": {"type": "objectid", "is_relationship": true, "relationship_target": "AssociateType"},
    "description": {"type": "str"},
    "steps": {"type": "str"},
    "required_inputs": {"type": "str"},
    "integration_requirements": {"type": "list"},
    "typical_timeline": {"type": "str"},
    "success_metrics": {"type": "str"},
    "escalation_paths": {"type": "str"},
    "stage": {"type": "str", "is_state_field": true, "default": "draft", "enum_values": ["draft", "active", "archived"]},
    "notes": {"type": "str"}
  }' \
  --state-machine '{
    "draft": ["active"],
    "active": ["archived", "draft"],
    "archived": ["draft"]
  }'

# ---------------------------------------------------------------------------
# Meeting Intelligence Entities
# ---------------------------------------------------------------------------

indemn entity create Meeting \
  --fields '{
    "company": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "contacts": {"type": "list"},
    "team_members": {"type": "list"},
    "title": {"type": "str", "required": true},
    "date": {"type": "datetime", "required": true},
    "duration_minutes": {"type": "int"},
    "source": {"type": "str", "enum_values": ["Gemini", "Granola", "Google_Meet", "Zoom", "Phone", "In_Person"]},
    "transcript_ref": {"type": "str"},
    "recording_ref": {"type": "str"},
    "summary": {"type": "str"},
    "stage": {"type": "str", "is_state_field": true, "default": "recorded", "enum_values": ["recorded", "processed", "intelligence_extracted"]},
    "notes": {"type": "str"}
  }' \
  --state-machine '{
    "recorded": ["processed"],
    "processed": ["intelligence_extracted"]
  }'

indemn entity create Task \
  --fields '{
    "company": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "title": {"type": "str", "required": true},
    "description": {"type": "str"},
    "assignee": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "owner_type": {"type": "str", "enum_values": ["Internal", "Customer"]},
    "due_date": {"type": "date"},
    "priority": {"type": "str", "enum_values": ["Low", "Medium", "High", "Critical"]},
    "category": {"type": "str", "enum_values": ["Technical", "Training", "Testing", "Compliance", "Sales", "Relationship", "Administrative"]},
    "source": {"type": "str", "enum_values": ["Meeting", "Implementation", "Playbook", "Manual"]},
    "source_meeting": {"type": "objectid", "is_relationship": true, "relationship_target": "Meeting"},
    "source_implementation": {"type": "objectid", "is_relationship": true, "relationship_target": "Implementation"},
    "effort": {"type": "str", "enum_values": ["Small", "Medium", "Large"]},
    "stage": {"type": "str", "is_state_field": true, "default": "open", "enum_values": ["open", "in_progress", "completed", "blocked", "cancelled"]},
    "notes": {"type": "str"}
  }' \
  --state-machine '{
    "open": ["in_progress", "cancelled"],
    "in_progress": ["completed", "blocked", "cancelled"],
    "blocked": ["in_progress", "cancelled"],
    "completed": [],
    "cancelled": []
  }'

indemn entity create Commitment \
  --fields '{
    "company": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "meeting": {"type": "objectid", "is_relationship": true, "relationship_target": "Meeting"},
    "description": {"type": "str", "required": true},
    "made_by": {"type": "str"},
    "made_by_side": {"type": "str", "enum_values": ["Indemn", "Customer"]},
    "made_to": {"type": "str"},
    "due_date": {"type": "date"},
    "due_date_precision": {"type": "str", "enum_values": ["Exact", "Approximate", "Unspecified"]},
    "stage": {"type": "str", "is_state_field": true, "default": "open", "enum_values": ["open", "fulfilled", "missed", "dismissed"]},
    "notes": {"type": "str"}
  }' \
  --state-machine '{
    "open": ["fulfilled", "missed", "dismissed"],
    "missed": ["fulfilled", "dismissed"],
    "fulfilled": [],
    "dismissed": []
  }'

indemn entity create Signal \
  --fields '{
    "company": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "meeting": {"type": "objectid", "is_relationship": true, "relationship_target": "Meeting"},
    "type": {"type": "str", "enum_values": ["Health_Positive", "Health_Negative", "Expansion", "Churn_Risk", "Blocker", "Champion_Identified", "Budget_Concern", "Competitor_Mentioned", "Escalation", "Satisfaction"]},
    "description": {"type": "str", "required": true},
    "source": {"type": "str", "enum_values": ["Meeting", "Email", "Slack", "Usage_Data", "Manual"]},
    "severity": {"type": "str", "enum_values": ["Low", "Medium", "High"]},
    "attributed_to": {"type": "str"},
    "notes": {"type": "str"}
  }'

indemn entity create Decision \
  --fields '{
    "company": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "meeting": {"type": "objectid", "is_relationship": true, "relationship_target": "Meeting"},
    "description": {"type": "str", "required": true},
    "decided_by": {"type": "str"},
    "participants": {"type": "list"},
    "rationale": {"type": "str"},
    "impact": {"type": "str", "enum_values": ["Customer_Scope", "Pricing", "Technical", "Timeline", "Staffing", "Strategy", "Process"]},
    "supersedes": {"type": "objectid", "is_relationship": true, "relationship_target": "Decision"},
    "notes": {"type": "str"}
  }'
