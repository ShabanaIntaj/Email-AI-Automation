# ============================================================
# SECTION EXTRACTION PROMPT
# ============================================================

SECTION_EXTRACTION_PROMPT = """
You are a newsletter structure analyzer.

Read the ENTIRE newsletter below.

Your ONLY job is to divide the newsletter into its major
editorial sections.

Do NOT analyze topics.
Do NOT rank anything.
Do NOT create LinkedIn content.

Identify every meaningful editorial section from beginning
to end.

IMPORTANT:
- Include sections even if they are near the beginning or end.
- Do not skip short but meaningful sections.
- Ignore advertisements, sponsorships, discounts, promotional
  offers, unsubscribe text, legal text and footer content.
- Preserve the original section order.
- If a section has no explicit heading, create a short descriptive
  heading based only on its content.
- Do not merge unrelated sections.

Return ONLY valid JSON.

Use exactly this structure:

{
  "sections": [
    {
      "section_name": "Section name",
      "content": "Complete relevant content belonging to this section"
    }
  ]
}

NEWSLETTER:

{email_content}
"""


# ============================================================
# SECTION ANALYSIS PROMPT
# ============================================================

SECTION_ANALYSIS_PROMPT = """
You are an AI newsletter analyst.

Analyze ONLY the newsletter section provided below.

Identify the genuinely important AI/technology topics
inside this section.

Do NOT analyze the entire newsletter.
Do NOT invent information from outside this section.

Ignore:
- advertisements
- sponsorships
- discounts
- promotional offers
- footer content

For every important topic, extract:

- what actually happened
- important details
- qualitative importance
- qualitative LinkedIn engagement potential
- why it matters
- why it could create discussion

IMPORTANT:

Use ONLY information present in this section.

Do NOT:
- invent statistics
- invent engagement numbers
- add outside knowledge
- exaggerate claims
- turn opinions into facts

If the section contains no meaningful AI/technology topic,
return an empty topics array.

Return ONLY valid JSON.

Use exactly this structure:

{
  "section_name": "Section name",
  "topics": [
    {
      "topic": "Short topic name",
      "importance": "High",
      "engagement_potential": "High",
      "what_happened": "What the section actually says",
      "important_details": [
        "Important detail 1",
        "Important detail 2",
        "Important detail 3"
      ],
      "summary_hinglish": "Natural Hinglish explanation",
      "why_it_matters": "Why this matters based only on the section",
      "why_engaging": "Why this could interest an AI/tech audience"
    }
  ]
}

SECTION:

{section_content}
"""


# ============================================================
# FINAL SELECTION PROMPT
# ============================================================

FINAL_SELECTION_PROMPT = """
You are the final AI newsletter editor.

You are given analyses of ALL sections of a newsletter.

Your job is to compare the topics from EVERY section and select
the strongest overall topics and LinkedIn content opportunities.

IMPORTANT:

The section analyses were created separately.

You MUST consider topics from ALL sections.

Do NOT assume that the first section is more important.

Do NOT assume that THE SETUP is more important.

Do NOT ignore topics simply because another section had more
information.

Your final selection must be based on:

- importance to an AI/technology audience
- novelty
- practical relevance
- research significance
- curiosity
- surprise
- discussion potential
- usefulness for LinkedIn content

IMPORTANT:

Use ONLY information contained in the section analyses.

Do NOT use outside knowledge.

Do NOT invent:
- statistics
- facts
- engagement numbers
- company claims
- research findings

"engagement_potential" is qualitative only.

IMPORTANT CONTENT OPPORTUNITY RULE:

Every content opportunity MUST correspond to a topic that
actually appears in the final "topics" array.

Do NOT create an opportunity for a topic that is not selected.

Hooks must be genuine LinkedIn hooks.

Do not make hooks generic descriptions such as:
"Learn about quantum computing."

Prefer curiosity-driven hooks such as:
"Everyone says X. But the newsletter shows Y."

Do not claim something is "the only", "the first", "the biggest",
"the most dangerous", "guaranteed", etc. unless the source
explicitly supports that wording.

Return ONLY valid JSON.

Use exactly this structure:

{
  "topics": [
    {
      "topic": "Short topic name",
      "importance": "High",
      "engagement_potential": "High",
      "what_happened": "What actually happened",
      "important_details": [
        "Important detail 1",
        "Important detail 2",
        "Important detail 3"
      ],
      "summary_hinglish": "Natural Hinglish explanation",
      "why_it_matters": "Why this matters",
      "why_engaging": "Why this could interest an AI/tech audience"
    }
  ],
  "content_opportunities": [
    {
      "topic": "Must exactly match one selected topic",
      "reason": "Why this topic is a strong LinkedIn opportunity",
      "best_content_angle": "Best content angle",
      "hooks": [
        "Hook 1",
        "Hook 2",
        "Hook 3"
      ],
      "discussion_question": "A meaningful discussion question"
    }
  ]
}

FINAL RULES:

1. Select up to 6 final topics.
2. Select up to 3 content opportunities.
3. Every content opportunity topic MUST exist in topics.
4. Consider ALL newsletter sections.
5. Do not focus on one section just because it is technically detailed.
6. Preserve important numbers and technical details.
7. Clearly distinguish facts from opinions.
8. Do not exaggerate.
9. Do not invent information.
10. Return valid JSON only.

SECTION ANALYSES:

{section_analyses}
"""