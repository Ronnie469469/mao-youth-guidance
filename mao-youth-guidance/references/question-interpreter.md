# Question interpreter

The interpreter runs before thought retrieval. It never silently treats a one-line symptom as a fully specified problem.

## Six dimensions

- `topic`: learning, work, family/relationships, emotion, social structure, public issue, ideology, or other.
- `direction`: explanation, evaluation, decision, action plan, encouragement, emotional support, social analysis, or public writing.
- `emotion`: calm, confused, anxious, discouraged, angry, grieving, urgent-risk, or unknown.
- `constraints`: time, money, health, location, authority, skills, evidence, or unknown.
- `stakeholders`: self, family, peers, employer/school, institution, public, and responsibility boundaries.
- `desired_result`: understand, choose, act, communicate, recover, or publish.

Each label receives a confidence and an evidence note. Also record the main problem, secondary problem, principal contradiction, missing facts, risk level, and recommended theme blocks.

## Interaction rules

- Complex or multi-intent requests: show the decomposition and wait for confirmation.
- Personal and social questions together: answer the actionable personal main problem first, then cover the social secondary problem; ask whether the user wants the secondary analysis expanded.
- User corrections apply immediately to the current answer and are recorded as anonymized feedback. They do not modify approved thought cards.
- After five similar corrections, show a proposal to update the classification dictionary. Do not apply it without explicit confirmation.

## Output schema

```json
{
  "topic": [{"label": "learning", "confidence": 0.8, "evidence": "..."}],
  "direction": [],
  "emotion": [],
  "constraints": [],
  "stakeholders": [],
  "desired_result": [],
  "main_problem": "",
  "secondary_problems": [],
  "principal_contradiction": "",
  "missing_facts": [],
  "risk_level": "low|medium|high|urgent",
  "recommended_themes": [],
  "needs_confirmation": true
}
```
