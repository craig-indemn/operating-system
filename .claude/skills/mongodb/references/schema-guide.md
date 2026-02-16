# MongoDB Schema Guide

All databases on the prod-indemn Atlas cluster. Organized by domain. Grep for `## COLLECTION:` to find any collection.

## DATABASE MAP

| Database | Size | Collections | Purpose |
|----------|------|-------------|---------|
| tiledesk | 11.4 GB | 103 (90 with data, 13 empty) | Primary operational — orgs, bots, conversations, KBs, billing |
| chat21 | 2.5 GB | 3 | Chat engine — conversations, groups, messages |
| observatory | 0.9 GB | 13 | Analytics — processed conversations, traces, snapshots |
| bf-wedding | 0.5 GB | — | Legacy botfront project |
| quotes | 0.2 GB | 3 | Insurance quote data |
| middleware | 0.06 GB | 1 | Session sync data |
| airtable_sync | small | 8 | Cached Airtable data for bots |
| evaluations | small | 5 | Evaluation service data (separate from tiledesk evals) |

---

# DATABASE: tiledesk

## DOMAIN: Core Platform

## COLLECTION: organizations
- count: 65
- purpose: Customer accounts (GIC Underwriters, Insurica, Indemn, etc.)
- owner: copilot-server (write), all services (read)
- fields:
  - _id: ObjectId (PK)
  - name: string
  - active: boolean
  - inactive: boolean (legacy inverse of active)
  - isEnterpriseAccount: boolean
  - infiniteSubscription: boolean
  - numOfUsers: number
  - maxUsers: number|null (null = unlimited)
  - hosts: Array[string] — allowed host patterns
  - modules: Array — enabled modules
  - logoUrl: string
  - createdBy: string
  - updatedBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_
- links: → projects (via id_organization), → bot_kb_mappings, → knowledge_bases, → voice_configurations, → requests, → faq_kbs, → organization_configurations, → organization_streams

## COLLECTION: projects
- count: 38
- purpose: Workspace within an organization — holds bot configs, channels, AI model settings
- owner: copilot-server
- fields:
  - _id: ObjectId (PK)
  - name: string
  - status: number
  - id_organization: string → organizations._id
  - aiModelConfigurations: Object{models, usecase, insuranceProducts, allowModelChanges, allowPromptChanges}
  - profile: Object{name, trialDays, agents, type}
  - channels: Array
  - ipFilterEnabled: boolean
  - ipFilter: Array
  - activeOperatingHours: boolean
  - jwtSecret: string
  - privateKey: string
  - publicKey: string
  - settings: Object{email}
  - versions: number
  - bannedUsers: Array
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, status_1, profile.name_1, _id_1_status_1, id_organization_1

## COLLECTION: users
- count: 142
- purpose: Platform user accounts (operators, admins)
- owner: copilot-server
- fields:
  - _id: ObjectId (PK)
  - email: string
  - password: string (hashed)
  - firstname: string
  - lastname: string
  - status: number
  - emailverified: boolean
  - authProviders: Array
  - firebaseUid: string
  - mfaEnabled: boolean
  - mfaMethod: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, email_1, authUrl_1, status_1, firebaseUid_1

## COLLECTION: project_users
- count: 97,644
- purpose: User-project membership — maps users to projects with roles
- owner: copilot-server
- fields:
  - _id: ObjectId (PK)
  - id_project: ObjectId → projects._id
  - id_user: ObjectId → users._id
  - id_organization: ObjectId → organizations._id
  - role: string (owner, agent, admin)
  - status: string
  - user_available: boolean
  - number_assigned_requests: number
  - last_login_at: Date
  - profileStatus: string
  - productModules: Array
  - workListTabs: Array
  - tags: Array
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, id_project_1, id_user_1, uuid_user_1, role_1, user_available_1, presence.status_1, number_assigned_requests_1, tags.tag_1, status_1, id_project_1_id_user_1, id_project_1_uuid_user_1, id_project_1_role_1, id_project_1_id_user_1_role_1, id_project_1_role_1_status_1_createdAt_1, id_organization_1

## COLLECTION: departments
- count: 45
- purpose: Routing departments within a project — each can have a default bot
- owner: copilot-server
- fields:
  - _id: ObjectId (PK)
  - name: string
  - id_project: string → projects._id
  - id_bot: string → faq_kbs._id
  - routing: string
  - default: boolean
  - status: number
  - tags: Array
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, name_1, id_project_1, default_1, tags.tag_1, status_1, id_project_1_default_1

## COLLECTION: leads
- count: 77,511
- purpose: End-user/visitor records captured during conversations
- owner: copilot-server, conversation-service
- fields:
  - _id: ObjectId (PK)
  - lead_id: string (unique visitor ID)
  - fullname: string
  - id_project: string → projects._id
  - status: number
  - tags: Array
  - attributes: Object{departmentId, departmentName, ipAddress, client, sourcePage, sourceTitle, projectId, widgetVer, payload, userFullname, requester_id, subtype, decoded_jwt}
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, lead_id_1, email_1, id_project_1, status_1, lead_fulltext, status_1_id_project_1_createdAt_-1

## COLLECTION: settings
- count: 1
- purpose: Global platform settings — migration version control
- fields:
  - _id: ObjectId (PK)
  - identifier: string
  - databaseSchemaVersion: number
  - installationVersion: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, identifier_1

## COLLECTION: pending-invitations
- count: 14
- purpose: Pending user invitations to projects/organizations
- fields:
  - _id: ObjectId (PK)
  - email: string
  - role: string
  - id_project: string
  - id_organization: string
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, email_1, id_project_1, id_organization_1

## COLLECTION: mfa_tokens
- count: 20
- purpose: Multi-factor authentication tokens
- fields:
  - _id: ObjectId (PK)
  - userId: ObjectId → users._id
  - email: string
  - codeHash: string
  - type: string
  - attempts: number
  - maxAttempts: number
  - verified: boolean
  - expiresAt: Date
  - pendingAuthToken: string
  - ipAddress: string
  - userAgent: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, userId_1, email_1, expiresAt_1

## COLLECTION: counters
- count: 35
- purpose: Auto-increment counters (e.g., ticket numbers)
- fields:
  - _id: ObjectId (PK)
  - id: string
  - reference_value: Object{id_project}
  - seq: number
- indexes: _id_, id_1_reference_value_1

## COLLECTION: schemaMigrations
- count: 14
- purpose: Database migration tracking
- fields:
  - _id: ObjectId (PK)
  - state: string
  - name: string
  - createdAt: Date
- indexes: _id_

## COLLECTION: audit_logs
- count: 9,267
- purpose: Platform audit trail — user actions, logins, config changes
- fields:
  - _id: ObjectId (PK)
  - id_user: ObjectId → users._id
  - event_type: string
  - action: string
  - resource_type: string
  - resource_id: string
  - resource_display: string
  - ip: string
  - user_agent: string
  - status: string
  - status_code: string
  - metadata: Object{email}
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

---

## DOMAIN: Agent/Bot Configuration

## COLLECTION: faq_kbs
- count: 386
- purpose: V1 bot/agent definitions — the primary "bot" entity in the platform
- owner: copilot-server (write), bot-service (read)
- fields:
  - _id: ObjectId (PK) — this IS the bot_id used throughout the system
  - name: string
  - description: string
  - id_project: string → projects._id
  - id_organization: string → organizations._id
  - type: string (internal, external, tilebot)
  - language: string
  - secret: string (API secret)
  - public: boolean
  - certified: boolean
  - trained: boolean
  - trashed: boolean (soft delete)
  - channels: Array
  - tags: Array
  - intentsEngine: string
  - webhook_enabled: boolean
  - score: number
  - certifiedTags: Array
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, name_1, id_project_1, type_1, trashed_1, public_1, certified_1, score_1, certified_1_public_1, faqkb_fulltext
- links: → bot_configurations (via bot_id), → bot_tools (via bot_id), → llm_configurations (via id_bot), → bot_kb_mappings (via id_bot)

## COLLECTION: bot_configurations
- count: 375
- purpose: V1 agent behavior config — system prompt, first message, AI settings
- owner: copilot-server (write), bot-service (read)
- fields:
  - _id: ObjectId (PK)
  - bot_id: ObjectId → faq_kbs._id
  - bot_name: string
  - socket_url: string
  - init_payload: string
  - first_message: Object{text, quick_replies}
  - is_button_enabled: boolean
  - ai_config: Object{kb_configuration, system_prompt, summary_config, use_default_prompt, identify_next_step_enabled, is_reranking_enabled}
  - botfront_config: Object{root_url, bf_project_id}
  - airtable_config: Object{airtable_base_id, airtable_table_id}
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, bot_id_1

## COLLECTION: bot_tools
- count: 2,481
- purpose: Tool instances per agent — REST APIs, handoffs, KB retrieval
- owner: copilot-server (write), bot-service (read)
- fields:
  - _id: ObjectId (PK)
  - bot_id: ObjectId → faq_kbs._id
  - name: string
  - toolName: string
  - type: string (custom_tool, human_handoff, rest_api, transfer_call, faqs-retriever, end_call, offline_human_handoff, user_feedback_tool)
  - description: string
  - executionSchema: Object{actions, return_direct}
  - configurationSchema: Object{humanHandoffFallback, sendTranscriptEmails}
  - systemDeveloped: boolean
  - isDeleted: boolean (soft delete)
  - createdBy: ObjectId
  - updatedBy: ObjectId
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: bot_tools_parameters
- count: 6,489
- purpose: Parameter definitions for bot tools
- owner: copilot-server
- fields:
  - _id: ObjectId (PK)
  - tool_id: ObjectId → bot_tools._id
  - name: string
  - type: string
  - description: string
  - question_title: string
  - is_required: boolean
  - order: number
  - isEnumsEnabled: boolean
  - enums: Array
  - createdBy: ObjectId
  - updatedBy: ObjectId
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: bot_master_tools
- count: 8
- purpose: System-wide tool type definitions — templates that bot_tools derive from
- fields:
  - _id: ObjectId (PK)
  - name: string (Live handoff, REST API, Capture lead info, Call transfer, etc.)
  - type: string (human_handoff, rest_api, capture_lead, transfer_call, offline_human_handoff, user_feedback_tool, end_call, faqs-retriever)
  - description: string
  - executionSchema: Object{actions, return_direct}
  - configurationSchema: Object{humanHandoffFallback, sendTranscriptEmails}
  - parameters: Array
  - channel_exclusion: Array
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: bot_kb_mappings
- count: 678
- purpose: Junction table — links bots to knowledge bases within an organization
- owner: copilot-server
- fields:
  - _id: ObjectId (PK)
  - id_bot: ObjectId → faq_kbs._id
  - id_kb: ObjectId → knowledge_bases._id
  - id_organization: ObjectId → organizations._id
  - createdBy: ObjectId
  - updatedBy: ObjectId
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, id_kb_1_id_bot_1_id_organization_1

## COLLECTION: llm_configurations
- count: 357
- purpose: LLM provider/model settings per bot (one per bot)
- owner: copilot-server (write), bot-service (read)
- fields:
  - _id: ObjectId (PK)
  - id_bot: ObjectId → faq_kbs._id
  - name: string
  - description: string
  - provider: string (openai)
  - model: string (gpt-4.1, etc.)
  - parameters: Object{temperature}
  - status: string (active)
  - created_at: Date
  - updated_at: Date
- indexes: _id_, uniq_id_bot (unique)

## COLLECTION: llm_models
- count: 8
- purpose: Available LLM provider/model catalog
- fields:
  - _id: ObjectId (PK)
  - provider: string
  - display_name: string
  - logo: string
  - models: Array (list of model names)
- indexes: _id_, provider_1

## COLLECTION: bot_previews
- count: 223
- purpose: Preview configurations for testing bots
- fields:
  - _id: ObjectId (PK)
  - id_bot: ObjectId → faq_kbs._id
  - id_organization: ObjectId → organizations._id
  - additional_context: string
  - first_message: Object{text, quick_replies}
  - preview_url: string
  - custom_data: null|Object
  - createdBy: ObjectId
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: bot_event_actions
- count: 8
- purpose: Webhook actions triggered by bot events
- fields:
  - _id: ObjectId (PK)
  - event: string
  - action: Object{type, method, url, headers, body}
  - id_bot: ObjectId → faq_kbs._id
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: bot_external_event_logs
- count: 933
- purpose: Log of external webhook calls made by bots
- fields:
  - _id: ObjectId (PK)
  - external_conversation_id: string
  - request_payload: Object{method, url, headers, body, timeout}
  - api_response: Object{status, headers, text, json, content_type}
  - event_type: string
  - create_time: Date
- indexes: _id_

## COLLECTION: ai_models
- count: 3
- purpose: AI model definitions with API configs
- fields:
  - _id: ObjectId (PK)
  - name: string
  - description: string
  - iconUrl: string
  - apiConfiguration: Object{apiKey, apiUrl}
  - default: boolean
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: default_prompts
- count: 3
- purpose: System default prompt templates
- fields:
  - _id: ObjectId (PK)
  - name: string
  - description: string
  - iconUrl: string
  - configuration: Object{systemPrompt}
  - order: number
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: insurance_products
- count: 3
- purpose: Insurance product definitions with system prompts
- fields:
  - _id: ObjectId (PK)
  - name: string
  - description: string
  - iconUrl: string
  - configuration: Object{systemPrompt}
  - order: number
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: validation_criteria
- count: 1
- purpose: Bot quality validation rules
- fields:
  - _id: ObjectId (PK)
  - bot_id: ObjectId → faq_kbs._id
  - name: string
  - description: string
  - version: number
  - active: boolean
  - criteria: Array (17 items)
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: jarvis_jobs
- count: 2
- purpose: Jarvis (V2 agent builder) background jobs
- fields:
  - _id: ObjectId (PK)
  - job_id: string
  - job_type: string
  - bot_ids: Array
  - organization_id: ObjectId
  - user_id: ObjectId
  - status: string
  - progress: Object{completed, total, current_bot_id, results}
  - error: null|string
  - triggered_by: string
  - created_at: Date
  - started_at: Date
  - completed_at: Date
- indexes: _id_

---

## DOMAIN: Knowledge Bases

## COLLECTION: knowledge_bases
- count: 515
- purpose: KB definitions — QNA, URL, or FILE type
- owner: kb-service (write), copilot-server (read)
- fields:
  - _id: ObjectId (PK)
  - name: string
  - type: string (QNA, URL, FILE)
  - id_organization: ObjectId → organizations._id
  - isTrashed: boolean (soft delete)
  - createdBy: string
  - updatedBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_
- links: → bot_kb_mappings (via id_kb), → knowledge_bases_data_sources (via id_kb)

## COLLECTION: knowledge_bases_data_sources
- count: 109,729
- purpose: Individual KB content entries — Q&A pairs, scraped content, files
- owner: kb-service
- fields:
  - _id: ObjectId (PK)
  - id_kb: ObjectId → knowledge_bases._id
  - id_organization: ObjectId → organizations._id
  - name: string
  - type: string
  - question: string
  - answer: string
  - token: number (token count)
  - chunks: Array
  - trained: boolean
  - totalUsage: number
  - isTrashed: boolean
  - isManual: boolean
  - createdBy: string
  - updatedBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, id_kb_1_isTrashed_1_type_1_createdAt_-1

## COLLECTION: knowledge_bases_tracking
- count: 20,075
- purpose: Tracks KB-assisted LLM responses per message — for quality monitoring
- owner: bot-service
- fields:
  - _id: ObjectId (PK)
  - id_organization: ObjectId
  - id_bot: ObjectId → faq_kbs._id
  - id_request: string → requests.request_id
  - id_message: string
  - user_query: string
  - llm_response: string
  - llm_generated_user_query: string
  - context: Array (retrieved KB chunks)
  - is_dismissed: boolean
  - is_resolved: boolean
  - id_kb_source: null|ObjectId
  - id_kb: null|ObjectId
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: knowledge_bases_scrapped_faqs
- count: 212
- purpose: FAQs extracted from scraped web content
- fields:
  - _id: ObjectId (PK)
  - id_kb: ObjectId → knowledge_bases._id
  - id_organization: ObjectId
  - kb_scrape_request_id: ObjectId → knowledge_base_scrape_request_details._id
  - extracted_faqs: Array
  - created_at: Date
  - created_by: string
- indexes: _id_, id_organization_1, kb_scrape_request_id_1, id_kb_1

## COLLECTION: knowledge_base_scrape_request_details
- count: 2,684
- purpose: Web scraping job records for KB content
- fields:
  - _id: ObjectId (PK)
  - id_kb: ObjectId → knowledge_bases._id
  - id_organization: ObjectId
  - type: string
  - status: string
  - payload: Object{url, max_pages, max_depth, selected_urls, exclude_urls, crawl_mode}
  - id_data_source: null|ObjectId
  - message: string
  - created_at: Date
  - completed_at: Date
  - created_by: string
- indexes: _id_, id_organization_1, id_kb_1

## COLLECTION: faqs
- count: 514
- purpose: Legacy FAQ entries (standalone, separate from knowledge_bases system)
- fields:
  - _id: ObjectId (PK)
  - id_faq_kb: string → faq_kbs._id
  - id_project: string → projects._id
  - question: string
  - answer: string
  - vector_id: string
  - language: string
  - topic: string
  - status: string
  - enabled: boolean
  - trained: boolean
  - actions: Array
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, id_faq_kb_1, intent_id_1, intent_display_name_1, id_project_1, topic_1, status_1, language_1, id_project_1_id_faq_kb_1_question_1, faq_fulltext, vector_id_1, id_project_1_id_faq_kb_1_vector_id_1

## COLLECTION: kb_scrapped_data
- count: 1
- purpose: Raw bulk scrape output (single large document)
- fields:
  - _id: ObjectId (PK)
  - url: string
  - markdown_data: Array (2,185 items)
  - extracted_faqs: Array (2,185 items)
  - total_tokens: number
  - id_organization: ObjectId
  - id_kb: ObjectId
  - kb_scrape_request_id: null|ObjectId
  - created_at: Date
  - created_by: string
- indexes: _id_

## COLLECTION: knowledge_bases_export_events
- count: 231
- purpose: KB export audit trail
- fields:
  - _id: ObjectId (PK)
  - id_kb: ObjectId → knowledge_bases._id
  - id_organization: ObjectId
  - fileName: string
  - fileUrl: string
  - fileType: string
  - totalRecords: number
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

---

## DOMAIN: Conversations

## COLLECTION: requests
- count: 142,849
- purpose: Core conversation records — each request is one conversation session
- owner: copilot-server (write), all services (read)
- fields:
  - _id: ObjectId (PK)
  - request_id: string (unique conversation ID)
  - ticket_id: number
  - id_project: string → projects._id
  - id_organization: ObjectId → organizations._id
  - status: number (100=pending, 200=assigned, 1000=closed)
  - preflight: boolean
  - hasBot: boolean
  - first_text: string
  - language: string
  - sourcePage: string
  - userAgent: string
  - requester: ObjectId → leads._id
  - lead: ObjectId → leads._id
  - department: ObjectId → departments._id
  - participants: Array (user IDs)
  - participantsAgents: Array (human agent IDs)
  - participantsBots: Array (bot IDs)
  - channel: Object{name}
  - channelOutbound: Object{name}
  - snapshot: Object{department, agents, availableAgentsCount, requester, lead}
  - attributes: Object{departmentId, departmentName, ipAddress, client, sourcePage, sourceTitle, is_user_msg_sent, isTestMode, ...}
  - aiModelConfigurations: Object{modelId, usecaseId, insuranceProductId, defaultPrompt, customPrompt}
  - location: Object{city, country, geometry, ipAddress, region}
  - tags: Array
  - notes: Array
  - priority: string
  - smartAssignment: boolean
  - isTestMode: boolean
  - isStripeEventCreated: boolean
  - streams: Array
  - depth: number
  - lastMsgTimestamp: Date
  - assigned_at: Date
  - closed_at: Date
  - closed_by: string
  - lastMessage: null|Object
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, request_id_1, ticket_id_1, preflight_1, hasBot_1, participants_1, priority_1, department_1, tags.tag_1, notes.text_1, location.country_1, location.city_1, id_project_1, createdAt_-1, updatedAt_-1, id_project_1_request_id_1, request_fulltext, id_project_1_status_1_updatedAt_-1, hasBot_1_createdAt_1, hasBot_1_status_1_createdAt_1, attributes.is_user_msg_sent_1_hasBot_1_id_organization_1_status_1, attributes.CallSid_1, + many more compound indexes
- links: → messages (via recipient = request_id)

## COLLECTION: messages
- count: 2,065,500
- purpose: Individual messages within conversations
- owner: copilot-server, conversation-service
- fields:
  - _id: ObjectId (PK)
  - id_project: string → projects._id
  - sender: string (user/bot ID)
  - senderFullname: string
  - recipient: string (= request_id, links to requests)
  - text: string
  - type: string
  - channel_type: string
  - channel: Object{name}
  - status: number
  - language: string
  - attributes: Object{departmentId, departmentName, ipAddress, client, sourcePage, sendnotification, ...}
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, sender_1, recipient_1, type_1, channel_type_1, language_1, id_project_1, status_1, recipient_1_createdAt_1, id_project_1_recipient_1_createdAt_1, message_fulltext, id_project_1_sender_1_createdAt_1, senderType_1, timelineOf_1_message_id_1, timelineOf_1_conversWith_1

## COLLECTION: traces
- count: 500,529
- purpose: LangSmith LLM trace data synced from LangSmith — token usage, costs, run hierarchy
- owner: indemn-observability (sync)
- fields:
  - _id: ObjectId (PK)
  - id: string (LangSmith run ID)
  - run_id: string
  - name: string
  - run_type: string
  - start_time: string
  - end_time: string
  - status: string
  - conversation_id: string → requests.request_id
  - thread_id: string
  - trace_id: string
  - parent_run_id: string|null
  - parent_run_ids: Array
  - session_id: string
  - inputs: Object{messages}
  - outputs: Object{generations, llm_output, run, type}
  - extra: Object{batch_size, invocation_params, metadata, options, runtime}
  - tags: Array
  - prompt_tokens: number
  - completion_tokens: number
  - total_tokens: number
  - total_cost: string
  - prompt_cost: string
  - completion_cost: string
  - prompt_token_details: Object{cache_read}
  - completion_token_details: Object{reasoning}
  - prompt_cost_details: Object{cache_read}
  - completion_cost_details: Object{reasoning}
  - dotted_order: string
  - in_dataset: boolean
  - app_path: string
  - _synced_at: Date
- indexes: _id_, run_id_1, thread_id_1, trace_id_1, conversation_id_1_start_time_1, bot_id_start_time_desc

## COLLECTION: observatory_conversations
- count: 7,545
- purpose: Enriched/classified conversations for analytics — the observability view layer
- owner: indemn-observability
- fields:
  - _id: ObjectId (PK)
  - conversation_id: string → requests.request_id
  - scope: Object{platform_id, customer_id, project_id, agent_id, agent_name, agent_version, agent_config_hash, distribution_id}
  - time: Object{started_at, ended_at, duration_seconds, last_activity_at, closed_by, closed_at}
  - user: Object{user_id, language, client, device_type, agency_code, agency_name, user_email, user_name}
  - entry: Object{channel, source_url, referrer_url, first_text}
  - metrics: Object{message_count, user_message_count, depth, self_served_depth, self_served_steps, csr_intervention_depth, csr_intervention_steps, csr_name, csr_time_to_join_seconds}
  - categories: Object{status, system_tags}
  - classifications: Object{sentiment, resolution_quality, frustrated_user, explicit_handoff_request, inferred_resolution, intent, sub_intent}
  - derived: Object{handoff_precursors, dropoff_precursors}
  - stages: Object{platform_customer, platform_channel, customer_agent, entry, intent, resolution_path, tool_outcome, outcome}
  - outcome_group: string
  - mongodb: Object{raw_category, raw_subcategory, summary, transcript}
  - attributes: Object{...many fields}
  - langsmith: Object{has_traces, trace_ids, total_tokens, llm_call_count, tool_call_count, kb_queries, kb_empty_results}
  - trace_events: Array
  - trace_summary: Object{llm_calls, tool_calls, total_tokens, total_cost, errors}
  - processing: Object{created_at, classification_version, schema_version}
- indexes: _id_, conversation_id_1, scope.customer_id_1_time.started_at_-1, scope.agent_id_1_time.started_at_-1, stages.outcome_1_scope.customer_id_1, scope.customer_id_1_stages.outcome_1, scope.customer_id_1_outcome_group_1, scope.customer_id_1_stages.resolution_path_1, scope.customer_id_1_classifications.sentiment_1, scope.customer_id_1_classifications.intent_1, stages.outcome_1, stages.resolution_path_1, stages.tool_outcome_1, outcome_group_1, classifications.sentiment_1, categories.system_tags_1

## COLLECTION: csr_feedbacks
- count: 937
- purpose: Customer service rep feedback/reviews on conversations
- fields:
  - _id: ObjectId (PK)
  - id_project: string
  - id_organization: string
  - id_bot: ObjectId
  - request_id: string → requests.request_id
  - request_url: string
  - reviewUrl: string
  - review: string
  - reviewer: ObjectId → users._id
  - messages: Array
  - lastUserMessages: Array
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: csr_requests
- count: 173
- purpose: CSR request assignments per user/project
- fields:
  - _id: ObjectId (PK)
  - id_organization: string
  - id_project: string
  - id_user: string
  - requests: Array
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: rlhf_suggestions
- count: 9
- purpose: RLHF training data — suggested improvements to bot responses
- fields:
  - _id: ObjectId (PK)
  - id_bot: ObjectId
  - request_id: string
  - question: string
  - llm_response: string
  - generated_suggestions: Object{question, answer}
  - knowledge_base_context: Array
  - reviews: Array
  - created_at: Date
  - updated_at: Date
  - created_by: ObjectId
- indexes: _id_

## COLLECTION: failed_conversations
- count: 91
- purpose: Conversations that failed observatory processing — debug data
- fields:
  - _id: ObjectId (PK)
  - conversation_id: string
  - job_id: string
  - error: string
  - raw_mongodb: Object{...full request document}
  - raw_langsmith: Array
  - failed_at: Date
- indexes: _id_, conversation_id_1, job_id_1

---

## DOMAIN: Channel & Distribution

## COLLECTION: channels
- count: 3
- purpose: Master channel type definitions
- values: WEB, EMAIL, VOICE
- fields:
  - _id: ObjectId (PK)
  - name: string
  - type: string
  - description: string
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: channel_configurations
- count: 100
- purpose: Channel-specific settings per bot (phone numbers, voice settings)
- fields:
  - _id: ObjectId (PK)
  - id_bot: ObjectId → faq_kbs._id
  - id_channel: ObjectId → channels._id
  - configurations: Object{phone, voice, transfer_number}
  - createdBy: string
  - updatedBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: voice_configurations
- count: 99
- purpose: Voice/phone number configurations for organizations
- owner: voice-service
- fields:
  - _id: ObjectId (PK)
  - id_organization: ObjectId → organizations._id
  - phoneNumber: string (E.164 format)
  - friendlyName: string
  - voice: string (shimmer, etc.)
  - greetingMessage: string
  - type: string (local)
  - isoCountry: string
  - isTestNumber: boolean
  - isTrashed: boolean
  - additionalDetails: Object{friendlyName, phoneNumber, lata, locality, rateCenter, latitude, longitude, region, postalCode, isoCountry, addressRequirements, beta, capabilities}
  - createdBy: ObjectId
  - updatedBy: ObjectId
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, id_organization_1, phoneNumber_1, createdBy_1, isTrashed_1, isTestNumber_1, id_organization_1_phoneNumber_1, id_organization_1_isTrashed_1, phoneNumber_1_isTrashed_1

## COLLECTION: voice_settings
- count: 1
- purpose: Global voice provider settings
- fields:
  - _id: ObjectId (PK)
  - provider: string
  - service: string
  - settings: Object{languages, genders}
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, provider_1, service_1

## COLLECTION: voices
- count: 8
- purpose: Available voice options
- fields:
  - _id: ObjectId (PK)
  - name: string
  - voice: string
  - url: string
  - createdBy: ObjectId
  - updatedBy: ObjectId
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: distributions
- count: 116
- purpose: Bot deployment configurations — maps bots to URLs/hosts
- owner: copilot-server
- fields:
  - _id: ObjectId (PK)
  - id_bot: ObjectId → faq_kbs._id
  - id_organization: ObjectId → organizations._id
  - id_style_configuration: ObjectId → style_configurations._id
  - host_name: string
  - path_expression: string
  - path_name: string
  - first_message: Object{text, quick_replies}
  - show_summary: boolean
  - default_to_fullscreen: boolean
  - auto_open: boolean
  - persist_conversation: boolean
  - user_tools: Object{start_new_conversation, end_conversation, upload_attachment}
  - launcher_config: Object{useLauncher, launcherSize, launcherType, launcherLabel, botPosition, launcherIcon}
  - nudge_config: Object{nudgeMessage, preNudgeInactivity, showNudge}
  - additional_context: null|string
  - createdBy: string
  - updatedBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, host_name_1_path_expression_1_id_organization_1

## COLLECTION: discovery_preferences
- count: 161
- purpose: Landing page / discovery portal configurations per bot
- fields:
  - _id: ObjectId (PK)
  - id_bot: ObjectId → faq_kbs._id
  - id_style_configuration: ObjectId → style_configurations._id
  - id_airtable: string
  - slug: string
  - bot_style: string
  - default_template: string
  - first_message: Object{text, quick_replies}
  - show_summary: boolean
  - display_branding: boolean
  - persist_conversation: boolean
  - brand_color: Array
  - brand_font_family: string
  - brand_font_family_url: string
  - logo_url: string
  - t1_hero_title: string
  - t1_hero_paragraph: string
  - t1_hero_cta: string
  - t1_hero_cta_utterance: string
  - t1_hero_img_url: string
  - t1_features_show: boolean
  - t1_leadership: boolean
  - t1_why_choose_us: boolean
  - t1_testimonials: boolean
  - t1_trusted_by: boolean
  - voice_agent_number: null|string
  - voice_cta_button: null|Object
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: style_configurations
- count: 209
- purpose: CSS theme configurations for widget rendering
- fields:
  - _id: ObjectId (PK)
  - version: string
  - name: string
  - configurations: Object{...200+ CSS variable keys for launcher, conversation, quote, payment UI}
  - is_default_preview_style: boolean
  - allow_update: boolean
- indexes: _id_

## COLLECTION: organization_configurations
- count: 74
- purpose: Org-level settings — handoff rules, business hours, feature flags
- fields:
  - _id: ObjectId (PK)
  - id_organization: ObjectId → organizations._id
  - humanHandoffConfig: Object{joinTimeThreshold, fallbackResponse, successResponse, failureResponse}
  - businessHoursConfig: Object{businessHours, businessHoursEnabled, businessHoursUtterance, holidays}
  - timezone: string
  - resolvedToArchivedDays: number
  - unassignedInactiveDays: number
  - autoResolutionTime: number
  - displayBranding: boolean
  - summaryEnabled: boolean
  - isSSLVerificationEnabled: boolean
  - closeConversationEventEnabled: boolean
  - cannedResponsesEnabled: boolean
  - enableInternalToolForCSR: boolean
  - enableRLHF: boolean
  - enableLiveKit: boolean
  - ccInvoiceEmails: Array
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: organization_streams
- count: 164
- purpose: Dashboard stream configurations per organization
- fields:
  - _id: ObjectId (PK)
  - id_organization: ObjectId → organizations._id
  - name: string
  - csrFeedbackConfig: Object{airtable_base_id, airtable_table_id}
  - emailTranscriptConfig: Object{sendTranscript, recipientEmails, endUserLabel}
  - durationRepresentation: string
  - primaryInfo: Object{function, root, path, valueType, displayFormat}
  - secondaryInfo: Object{function, root, path, displayFormat, valueType}
  - topSection: Object{title, atoms}
  - subMenu: Array
  - condition: Object{isTestMode}
  - summarySections: Array
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, name_1_id_organization_1

---

## DOMAIN: Billing & Payments

## COLLECTION: subscriptions
- count: 60
- purpose: Webhook subscriptions (NOT billing) — event notification targets
- fields:
  - _id: ObjectId (PK)
  - event: string
  - target: string (URL)
  - id_project: string
  - secret: string
  - global: boolean
  - createdBy: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, event_1, target_1, id_project_1, global_1, event_1_id_project_1_global_1, id_project_1_event_1_target_1

## COLLECTION: subscriptionlogs
- count: 1,093,870
- purpose: Webhook delivery logs
- fields:
  - _id: ObjectId (PK)
  - event: string
  - target: string
  - response: string
  - body: string
  - jsonRequest: string
  - err: null|string
  - id_project: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, id_project_1

## COLLECTION: billing_subscriptions
- count: 31
- purpose: Actual billing subscriptions — Stripe integration
- fields:
  - _id: ObjectId (PK)
  - id_organization: string → organizations._id
  - id_plan: ObjectId → subscription_plans._id
  - stripe: Object{subscription, customer, latestInvoice, collectionMethod}
  - seats: number
  - startDate: Date
  - currentPeriodStart: Date
  - currentPeriodEnd: Date
  - status: string
  - isCanceled: boolean
  - cancel: Object{canceledAt, comment, endedAt, feedback, reason}
  - upcomingInvoice: Object{total}
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, id_organization_1, id_plan_1

## COLLECTION: subscription_plans
- count: 22
- purpose: Plan definitions with pricing tiers
- fields:
  - _id: ObjectId (PK)
  - title: string
  - description: string
  - tier: string
  - price: number
  - currency: string
  - billingInterval: string
  - isEnterprise: boolean
  - showPlan: boolean
  - trialEnabled: boolean
  - trialEndsOn: Date
  - stripePriceId: Array
  - meters: Object{chatLimit, chatUnitCost}
  - inclusions: Array
  - order: number
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_, tier_1

## COLLECTION: invoices
- count: 342
- purpose: Invoice records
- fields:
  - _id: ObjectId (PK)
  - id_subscription: string → billing_subscriptions._id
  - id_organization: string → organizations._id
  - stripe: Object{invoiceId, customer, invoiceNumber}
  - customer: Object{name, email, address}
  - paid: boolean
  - periodStart: Date
  - periodEnd: Date
  - amount: number
  - currency: string
  - status: string
  - hostedInvoiceUrl: string
  - invoicePdfUrl: string
  - invoiceCreatedAt: Date
  - invoicePaidAt: Date
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: payment_logs
- count: 5,613
- purpose: Payment event log from Stripe webhooks
- fields:
  - _id: ObjectId (PK)
  - stripe: Object{paymentId, customerId}
  - amount: number
  - currency: string
  - status: string
  - event: string
  - metadata: Object{session_id, bot_type, name, email, phone_number, platform}
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: stripe_meters
- count: 28,873
- purpose: Usage metering records for Stripe billing
- fields:
  - _id: ObjectId (PK)
  - id_request: string
  - identifier: string
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: stripe_prices
- count: 30
- purpose: Stripe price configurations
- fields:
  - _id: ObjectId (PK)
  - priceId: string
  - amount: number
  - showQuantity: boolean
  - tiers: Array
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

## COLLECTION: metric-ai-suggestions
- count: 59,791
- purpose: AI suggestion usage metrics — tracks when AI suggestions are shown
- fields:
  - _id: ObjectId (PK)
  - id_user: ObjectId
  - id_organization: ObjectId
  - id_request: string
  - id_bot: ObjectId
  - createdAt: Date
  - updatedAt: Date
- indexes: _id_

---

## DOMAIN: Evaluation & Testing

## COLLECTION: evaluation_runs
- count: 41
- purpose: Evaluation run records (newer system, string IDs)
- owner: evaluations service
- fields:
  - _id: ObjectId (PK)
  - run_id: string
  - dataset_id: string → datasets.dataset_id
  - agent_id: string
  - status: string
  - langsmith_experiment_id: null|string
  - total: number
  - completed: number
  - passed: number
  - failed: number
  - concurrency: number
  - started_at: Date
  - completed_at: Date
  - error: string
  - created_at: Date
- indexes: _id_

## COLLECTION: evaluation_results
- count: 380
- purpose: Individual evaluation test results
- fields:
  - _id: ObjectId (PK)
  - result_id: string
  - run_id: string → evaluation_runs.run_id
  - test_case_id: string → test_cases.test_case_id
  - langsmith_run_id: string
  - input: Object{bot_id, message, max_turns, conversation_id, initial_message, simulated_user_persona}
  - output: Object{output}
  - scores: Object{wrapper}
  - duration_ms: number
  - created_at: Date
- indexes: _id_

## COLLECTION: evaluator_configs
- count: 10
- purpose: Evaluator configurations per agent
- fields:
  - _id: ObjectId (PK)
  - config_id: string
  - agent_id: string
  - template_id: null|string
  - evaluators: Array
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: test_cases
- count: 681
- purpose: Test case definitions for evaluation
- fields:
  - _id: ObjectId (PK)
  - test_case_id: string
  - dataset_id: string → datasets.dataset_id
  - type: string
  - input: Object{bot_id, message, initial_message, simulated_user_persona, max_turns, conversation_id}
  - expected: Object{answer, sources, parameters_collected, outcome}
  - created_at: Date
- indexes: _id_

## COLLECTION: test_sets
- count: 8
- purpose: Grouped sets of test items per agent
- fields:
  - _id: ObjectId (PK)
  - test_set_id: string
  - agent_id: string
  - version: number
  - name: string
  - description: string
  - items: Array
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: question_sets
- count: 6
- purpose: Question sets for evaluation
- fields:
  - _id: ObjectId (PK)
  - question_set_id: string
  - agent_id: string
  - version: number
  - name: string
  - description: string
  - questions: Array
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: rubrics
- count: 14
- purpose: Evaluation rubrics with severity definitions and rules
- fields:
  - _id: ObjectId (PK)
  - rubric_id: string
  - agent_id: string
  - version: number
  - name: string
  - description: string
  - severity_definitions: Object{high, medium, low}
  - changelog: Object
  - rules: Array
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: datasets
- count: 35
- purpose: Evaluation datasets linked to LangSmith
- fields:
  - _id: ObjectId (PK)
  - dataset_id: string
  - name: string
  - description: string
  - agent_id: null|string
  - langsmith_dataset_id: string
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: testcases (LEGACY)
- count: 34
- purpose: Legacy test case definitions (ObjectId-based, RAGAS metrics)
- fields:
  - _id: ObjectId (PK)
  - name: string
  - type: string
  - id_bot: ObjectId
  - id_organization: ObjectId
  - created_by: ObjectId
  - updated_by: ObjectId
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: testcase_details (LEGACY)
- count: 7,301
- purpose: Legacy test case Q&A pairs
- fields:
  - _id: ObjectId (PK)
  - id_testcase: ObjectId → testcases._id
  - id_bot: ObjectId
  - id_kb: ObjectId
  - id_kb_source: ObjectId
  - id_organization: ObjectId
  - question: null|string
  - answer: null|string
  - createdAt: Date
- indexes: _id_

## COLLECTION: testcase_evaluation_results (LEGACY)
- count: 12,893
- purpose: Legacy eval results with RAGAS metrics
- fields:
  - _id: ObjectId (PK)
  - id_testcase: ObjectId → testcases._id
  - id_evaluation: ObjectId
  - id_bot: ObjectId
  - id_organization: ObjectId
  - id_kb: ObjectId
  - id_kb_source: ObjectId
  - question: string
  - answer: string
  - ground_truth: string
  - contexts: Array
  - score: number
  - metrics_result: Object{semantic_similarity, answer_correctness, faithfulness, answer_relevancy, final_score}
  - created_at: Date
  - updated_at: Date
- indexes: _id_

## COLLECTION: testcase_results (LEGACY)
- count: 42
- purpose: Legacy test case aggregate scores
- fields:
  - _id: ObjectId (PK)
  - id_testcase: ObjectId → testcases._id
  - id_organization: ObjectId
  - score: number
  - metrics_result: Object{semantic_similarity, answer_correctness, faithfulness, answer_relevancy, final_score}
  - report_url: string
  - created_at: Date
  - updated_at: Date
- indexes: _id_

---

## DOMAIN: Observatory Analytics (tiledesk)

## COLLECTION: category_distributions
- count: 13,032
- purpose: Distribution of conversation categories over time
- fields:
  - _id: ObjectId (PK)
  - date: string
  - scope: Object{level, customer_id, agent_id}
  - category: string
  - value: string
  - count: number
  - percentage: number
- indexes: _id_

## COLLECTION: daily_snapshots
- count: 553
- purpose: Daily aggregate analytics per scope (platform/customer/agent)
- fields:
  - _id: ObjectId (PK)
  - date: string
  - scope: Object{level, customer_id, agent_id}
  - volume: Object{total_conversations, total_users, avg_message_count, avg_duration_seconds, by_channel, by_device, by_hour, by_day_of_week}
  - outcomes: Object{resolved_autonomous, resolved_with_handoff, partial_then_left, unresolved_abandoned, resolution_rate, autonomous_resolution_rate, handoff_rate, bounce_rate, abandonment_rate, ...}
  - experience: Object{positive_sentiment_count, neutral_sentiment_count, negative_sentiment_count, liked_count, disliked_count, ...rates}
  - operations: Object{handoff_requests, handoff_completed, missed_handoffs, early_handoffs, avg_time_to_handoff_seconds, ...}
  - performance: Object{total_tokens, total_cost, avg_tokens_per_conversation, error_count, error_rate, kb_gap_count, tool_calls_total, ...}
  - content: Object{intent_counts, top_intents}
  - processing: Object{computed_at, conversation_count, schema_version}
- indexes: _id_, date_-1_scope.level_1_scope.customer_id_1

## COLLECTION: flow_links
- count: 6,136
- purpose: Sankey flow link data (source → target with count)
- fields: _id, date, scope, source, target, value
- indexes: _id_

## COLLECTION: flow_paths
- count: 4,101
- purpose: Conversation flow paths through stages
- fields: _id, date, scope, id, stages{entry, platform_customer, outcome}, count, percentage
- indexes: _id_

## COLLECTION: flow_stage_totals
- count: 631
- purpose: Total counts per flow stage
- fields: _id, date, scope, totals{entry, platform_customer, outcome}
- indexes: _id_

## COLLECTION: precursor_lifts
- count: 20,147
- purpose: Factor lift analysis — which factors predict which outcomes
- fields: _id, date, scope, outcome, outcome_count, factor{category, value}, factor_in_outcome_count, factor_in_outcome_rate, factor_baseline_count, factor_baseline_rate, lift, is_significant
- indexes: _id_

## COLLECTION: processing_runs
- count: 121
- purpose: Observatory data processing job tracking
- fields: _id, job_id, job_type, status, params{organization_id, date_from, date_to, force}, progress{total, processed, failed}, started_at, completed_at, error, created_at
- indexes: _id_, job_id_1, status_1_started_at_-1

## COLLECTION: structure_agents
- count: 273
- purpose: Denormalized agent structure view
- fields: _id, id, name, channel, customer_id, customer_name, tool_count, kb_count, tool_types, kb_names, tools, kbs, llm_config{provider, model, status}
- indexes: _id_, id_1, customer_id_1

## COLLECTION: structure_customers
- count: 32
- purpose: Denormalized customer structure view
- fields: _id, customer_id, customer_name, computed_at, agents (Array up to 92), tool_types, kb_types, total_agents, total_tools, total_kbs
- indexes: _id_, customer_id_1

## COLLECTION: structure_platform
- count: 1
- purpose: Denormalized platform-wide structure view (single document)
- fields: _id, computed_at, organizations (Array of 32), tool_types, kb_types, total_organizations, total_agents, total_tools, total_kbs
- indexes: _id_

---

## DOMAIN: Miscellaneous (tiledesk)

## COLLECTION: apps
- count: 36
- purpose: App store/marketplace entries
- fields: _id, title, description, installActionType, installActionURL, runURL, learnMore, logo, where{dashboard, webchat, widget, appsstore}, version, score, status, visibleForUserIds, createdBy, createdAt, updatedAt
- indexes: _id_, title_1, description_1, category_1, status_1

## COLLECTION: triggers
- count: 63
- purpose: Event-driven automation rules
- fields: _id, name, description, enabled, trigger{key, name, description}, conditions{all, any}, actions, code, type, version, id_project, createdBy, updatedBy, createdAt, updatedAt
- indexes: _id_, trigger.key_1, actions.key_1, enabled_1, id_project_1, id_project_1_trigger.key_1_enabled_1

## COLLECTION: labels
- count: 9
- purpose: UI label translations per project
- fields: _id, id_project, data, createdBy, createdAt, updatedAt
- indexes: _id_, data.lang_1, data.category_1, data.default_1, id_project_1

## COLLECTION: events
- count: 28
- purpose: Platform events
- fields: _id, name, status, attributes, id_project, project_user, createdBy, createdAt, updatedAt
- indexes: _id_, name_1, project_user_1, id_project_1, status_1, createdBy_1, id_project_1_name_1_createdAt_-1

## COLLECTION: cannedresponses
- count: 3
- purpose: Pre-written response templates for CSRs
- fields: _id, title, text, id_project, shared, status, createdBy, createdAt, updatedAt
- indexes: _id_, title_1, id_project_1, status_1, isTrashed_1

## COLLECTION: canned-response-usage-metrics
- count: 187
- purpose: Usage tracking for canned responses
- fields: _id, id_cannedResponse, id_user, id_project, id_request, lastUserMessage, csrMessage, actualCannedResponse, action, createdAt, updatedAt
- indexes: _id_

## COLLECTION: whitepaper_requests
- count: 51
- purpose: Marketing whitepaper download requests
- fields: _id, fullName, businessEmail, phoneNumber, company, segment, privacyConsent, marketingConsent, date
- indexes: _id_

## COLLECTION: web_push_subscriptions
- count: 56
- purpose: Browser push notification subscriptions
- fields: _id, email, id_user, pushNotifications{endpoint, expirationTime, keys}, createdAt, updatedAt
- indexes: _id_

---

## DOMAIN: Platform V2

## COLLECTION: platform_agents
- count: 1
- purpose: V2 agent definitions (new platform)
- fields: _id, agent_id, name, description, version, template_id, organization_id, status, is_v2, overrides, connector_bindings, embed_config, capabilities, use_cases, created_at, updated_at
- indexes: _id_

## COLLECTION: platform_components
- count: 5
- purpose: V2 agent component definitions
- fields: _id, component_id, name, description, version, category, state_schema, config_schema, ui_component, created_at, updated_at
- indexes: _id_

## COLLECTION: platform_conversations
- count: 54
- purpose: V2 agent conversations (Jarvis)
- fields: _id, conversation_id, thread_id, user_id, organization_id, title, is_archived, message_count, created_at, updated_at
- indexes: _id_

## COLLECTION: platform_templates
- count: 9
- purpose: V2 agent templates (LangGraph definitions)
- fields: _id, template_id, name, description, version, pattern, visibility, organization_id, graph{state_schema, nodes, edges, conditional_edges}, llm_config{provider, model, max_tokens}, ui_config{theme, side_panel_components}, created_at, updated_at
- indexes: _id_

---

## EMPTY COLLECTIONS (tiledesk)

activities, auths, bots, groups, instances, kvstore, master_integrations, notes, org_integrations, profiles, properties, router_loggers, stripe_connect_accounts, stripe_connect_states, tags

---

# DATABASE: observatory

Same schema as tiledesk observatory domain but with more data:
- conversations: 28,087 (vs 7,545 in tiledesk.observatory_conversations)
- traces: 74,985
- daily_snapshots: 1,368 (vs 553)
- category_distributions: 22,740 (vs 13,032)
- flow_links: 7,633 (vs 6,136)
- flow_paths: 5,170 (vs 4,101)
- flow_stage_totals: 1,393 (vs 631)
- precursor_lifts: 31,812 (vs 20,147)
- failed_conversations: 4,950 (vs 91)
- processing_runs: 58 (vs 121)
- structure_agents: 243 (vs 273)
- structure_customers: 29 (vs 32)
- structure_platform: 1 (vs 1)

Note: Observatory database is the observability service's own store. Tiledesk observatory_* collections are denormalized copies.

---

# DATABASE: middleware

## COLLECTION: tiledesksyncs
- count: 86,898
- purpose: Session sync data between middleware and tiledesk
- fields: _id, unique_user_id, session_id, jwt_token, request_id, bot_type, bot_id, project_id, attributes{ipAddress, client, language}, createdAt, updatedAt
- indexes: _id_, unique_user_id_1, request_id_1, project_id_1, session_id_1

---

# DATABASE: quotes

## COLLECTION: quotes
- count: 50,256
- purpose: Insurance quote results per conversation
- fields: _id, conversation_id, created_at, valid_till, raw_response{id, alcohol_bool, budget, cancellationCoverageAmount, carrier, covers, currentPremium, discountLabel, doesNotCover, liabilityAggregateAmount, liabilityPerOccurrenceAmount, package_config, policyTitle, previousPremium, require_cancellation, require_liability, state_code}
- indexes: _id_

## COLLECTION: quote_configs
- count: 2
- purpose: Quote display configuration
- fields: _id, name, options, setup{narration, price, facets, carrier, coverages}
- indexes: _id_

## COLLECTION: style_configs
- count: 5
- purpose: Quote widget style configurations
- fields: _id, version, name, configuration{...CSS variable map}
- indexes: _id_

---

# DATABASE: airtable_sync

## COLLECTION: venue_details
- count: 4,480
- purpose: Cached venue data from Airtable
- fields: _id, id, venue_name, venue_address, venue_phone, venue_website_url, venue_legal_name, state_code, slug, bot, package_config, first_message, faq_list, faq_table, cancellation_available, mandate_cancellation, mandate_liability, faqs, buttons, show_summary, hero_heading, hero_body, hero_img, cta_label, additional_slots, created, last_updated
- indexes: _id_

## COLLECTION: quote_details
- count: 333
- purpose: Quote configuration details from Airtable
- fields: _id, id, carrier, currentPremium, previousPremium, discountLabel, budget, covers, doesNotCover, liabilityAggregateAmount, liabilityPerOccurrenceAmount, cancellationCoverageAmount, event_host_type, state_code, package_config, policyTitle, require_cancellation, require_liability, wed_ins_cov_preference, alcohol_bool, +cancellation breakdown fields
- indexes: _id_

## COLLECTION: multiple_quote_config
- count: 24
- purpose: Multi-quote configurations
- fields: _id, id, insurance_coverage, cancellation_available, mandate_cancellation, mandate_liability, quote_config
- indexes: _id_

## COLLECTION: marketing_pricing_pages
- count: 10
- purpose: Pricing page content from Airtable
- fields: _id, id, page_title, page_description, slug, cta_label, cta_type, cta_utterance, faqs, recommended, show_tiers, inactive
- indexes: _id_

## COLLECTION: ring_engagement_quote_details
- count: 3
- purpose: Ring/engagement insurance quote details
- fields: _id, id, carrier, product, title, subtitle, coverages, currentPremium, deductiblePerClaim, indicationChoice, policyLimit, retention, contractLength
- indexes: _id_

## COLLECTION: silent_sport_quote_details
- count: 3
- purpose: Silent sport insurance quote details
- fields: _id, id, carrier, product, title, subtitle, coverages, currentPremium, deductiblePerClaim, indicationChoice, policyLimit, retention, contractLength
- indexes: _id_

## COLLECTION: zurich_quote_details
- count: 3
- purpose: Zurich insurance quote details
- fields: _id, id, carrier, product, title, subtitle, coverages, currentPremium, deductiblePerClaim, indicationChoice, policyLimit, retention, contractLength
- indexes: _id_

## COLLECTION: quote_configs
- count: 2
- purpose: Quote configuration (duplicate of quotes.quote_configs)
- fields: _id, name, options, setup
- indexes: _id_
