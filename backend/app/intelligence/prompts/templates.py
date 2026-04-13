"""
Prompt templates for all AI tasks.
Each template is a function that accepts structured data and returns a prompt string.
Templates are engine-agnostic — the router handles engine selection.
"""


def case_summary_prompt(case_data: dict, events: list[dict]) -> tuple[str, str]:
    """Generate a case summary prompt. Returns (system_prompt, user_prompt)."""
    system = (
        "You are Clarion, an expert support case analyst. "
        "Produce a concise, actionable summary of the support case. "
        "Structure: Current Status, Key Events (chronological), Root Cause (if identified), "
        "Next Steps (recommended), Risk Assessment."
    )
    events_text = "\n".join(
        f"[{e.get('timestamp', '?')}] {e.get('event_type', '?')}: {e.get('body', '')[:200]}"
        for e in events[:50]  # Limit to 50 most recent events
    )
    user = (
        f"Case: {case_data.get('sf_case_number', 'N/A')}\n"
        f"Subject: {case_data.get('subject', 'N/A')}\n"
        f"Priority: {case_data.get('priority', 'N/A')}\n"
        f"Status: {case_data.get('status', 'N/A')}\n"
        f"Product: {case_data.get('product', 'N/A')}\n"
        f"Age: {case_data.get('case_age_days', 0)} days\n"
        f"Owner: {case_data.get('case_owner_name', 'N/A')}\n\n"
        f"Event Timeline:\n{events_text}\n\n"
        f"Provide a structured summary."
    )
    return system, user


def sentiment_prompt(text: str) -> tuple[str, str]:
    """Analyse sentiment of a case communication."""
    system = (
        "You are a sentiment analysis specialist for enterprise support. "
        "Analyse the customer's emotional state and satisfaction level. "
        "Respond with JSON: {\"sentiment\": \"positive|neutral|negative|frustrated\", "
        "\"score\": 0.0-1.0, \"evidence\": \"brief quote or observation\"}"
    )
    return system, f"Analyse the sentiment of this support communication:\n\n{text}"


def escalation_prediction_prompt(case_data: dict, events: list[dict]) -> tuple[str, str]:
    """Predict escalation risk for a case."""
    system = (
        "You are an escalation prediction specialist. "
        "Assess the probability this support case will escalate. "
        "Consider: case age, priority, customer sentiment, response gaps, "
        "complexity indicators, and SLA status. "
        "Respond with JSON: {\"risk\": \"high|medium|low\", "
        "\"confidence\": 0.0-1.0, \"factors\": [\"factor1\", \"factor2\"], "
        "\"recommendation\": \"brief action recommendation\"}"
    )
    events_summary = "\n".join(
        f"- [{e.get('event_type')}] {e.get('body', '')[:100]}"
        for e in events[-10:]  # Last 10 events
    )
    user = (
        f"Case: {case_data.get('sf_case_number')}, Priority: {case_data.get('priority')}, "
        f"Age: {case_data.get('case_age_days')}d, Status: {case_data.get('status')}, "
        f"SLA: {case_data.get('sla_status', 'Unknown')}\n"
        f"Recent events:\n{events_summary}\n\n"
        f"Assess escalation risk."
    )
    return system, user


def review_draft_prompt(case_data: dict, events: list[dict], rubric: list[dict]) -> tuple[str, str]:
    """Generate a complete case quality review draft."""
    system = (
        "You are an expert support quality reviewer. Generate a complete case review "
        "following the provided rubric. For each question: assign a score (1-5), "
        "provide specific evidence from the case timeline, write constructive coaching comments, "
        "and suggest improvements. Be fair but thorough. "
        "Respond with JSON array of: {\"question_id\": str, \"score\": int, "
        "\"evidence\": str, \"comment\": str, \"coaching\": str}"
    )
    rubric_text = "\n".join(
        f"- [{q.get('id')}] {q.get('text')} (weight: {q.get('weight', 1)})"
        for q in rubric
    )
    events_text = "\n".join(
        f"[{e.get('timestamp')}] {e.get('event_type')}: {e.get('body', '')[:300]}"
        for e in events[:30]
    )
    user = (
        f"Case: {case_data.get('sf_case_number')}\n"
        f"Subject: {case_data.get('subject')}\n"
        f"Priority: {case_data.get('priority')}, Status: {case_data.get('status')}\n"
        f"Product: {case_data.get('product')}, Age: {case_data.get('case_age_days')}d\n\n"
        f"Rubric:\n{rubric_text}\n\n"
        f"Case Timeline:\n{events_text}\n\n"
        f"Generate the complete review."
    )
    return system, user


def anon_context_review_prompt(text: str, detected_entities: list[dict]) -> tuple[str, str]:
    """Stage 4: LLM context-aware PII sweep (runs locally on Gemma4)."""
    system = (
        "You are a PII detection specialist. Review the text below. "
        "Other detection stages have already found these entities. "
        "Your job: find ANY additional personally identifiable information that was missed. "
        "Look for: informal names, nicknames, partial addresses, internal project names "
        "that could identify people, phone extensions, building/floor references. "
        "Respond with JSON array: [{\"value\": \"the PII text\", \"type\": \"person|org|location|custom\"}] "
        "If no additional PII found, respond with empty array: []"
    )
    already = "\n".join(f"- [{e.get('entity_type')}] {e.get('value')}" for e in detected_entities)
    user = (
        f"Already detected:\n{already}\n\n"
        f"Text to review:\n{text}\n\n"
        f"List any additional PII not yet detected."
    )
    return system, user


def chatbot_query_prompt(query: str, context: dict) -> tuple[str, str]:
    """Chatbot query with page context injection."""
    system = (
        "You are Clarion AI Assistant, a support analytics chatbot. "
        "You help support managers understand their team's performance, "
        "find cases, interpret analytics, and take actions. "
        "Be concise and actionable. Reference specific data when possible."
    )
    ctx_parts = []
    if context.get("active_page"):
        ctx_parts.append(f"User is viewing: {context['active_page']}")
    if context.get("selected_case"):
        ctx_parts.append(f"Selected case: {context['selected_case']}")
    if context.get("filters"):
        ctx_parts.append(f"Active filters: {context['filters']}")

    ctx_text = "\n".join(ctx_parts) if ctx_parts else "No specific context."
    user = f"Context:\n{ctx_text}\n\nUser query: {query}"
    return system, user
