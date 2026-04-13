"""
Anonymisation module — PII detection, pseudonymisation, de-anonymisation.
Defence-in-depth: 4-stage pipeline (regex, dictionary, NER, LLM).
"""
MODULE_MANIFEST = {
    "name": "anonymisation",
    "version": "1.0.0",
    "description": "Multi-stage PII detection and anonymisation engine.",
    "dependencies": [],
    "feature_flag": "module_anonymisation",
    "routes_module": "app.modules.anonymisation.routes",
    "routes_prefix": "/api/v1",
    "events_produced": ["anon.session.created", "anon.session.confirmed"],
    "events_consumed": [],
    "chatbot_tools": [],
}
