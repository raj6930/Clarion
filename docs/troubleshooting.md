# Clarion Troubleshooting Guide

## Common Issues

### Cannot log in
- Verify your credentials (check for caps lock)
- If you're a new user, your account may be pending admin approval
- Clear browser cache and cookies, then retry
- Check that the API is running: visit `/api/v1/health`

### Dashboard shows no data
- Check if Salesforce sync has run: Settings → Sync Config → Last Sync
- Trigger a manual sync: Settings → Sync → Trigger Sync
- Verify your team members are correctly configured
- Check the sync log for errors: Settings → Sync → History

### AI features not working
- Check Ollama status: Settings → System Health → Ollama Status
- Verify the Ollama container is running: `docker ps | grep ollama`
- Pull the model if missing: `docker exec clarion-ollama ollama pull gemma2`
- For external engines (Claude/OpenAI): verify API key in Settings → AI Config

### Anonymisation false positives
- Mark the entity as a false positive in the review interface
- Add the term to the passthrough dictionary: Settings → Anonymisation → Dictionary
- Product names, project codes, and technical terms often trigger false positives

### Notifications not arriving
- Check notification settings: Settings → Notifications
- Verify the alert rule is active: Settings → Alert Rules
- Check quiet hours configuration
- For email: verify SMTP settings in Settings → Notifications → Email Config
- For Teams/Slack: verify webhook URL

### Slow performance
- Check system health: Settings → System Health
- High memory: Ollama uses ~8GB for Gemma4 inference
- Slow sync: reduce sync frequency or check Salesforce API limits
- Large case volume: ensure PostgreSQL has adequate resources

## Getting Help
Use the Clarion AI Assistant (chatbot) for quick answers. For issues not covered here, contact your Clarion administrator.
