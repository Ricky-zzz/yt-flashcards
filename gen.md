You’re at the **most important stage now: dataset cleaning**.
If you do this right, your model quality improves massively.

---

# 🔥 Goal of your cleaning prompt

You want the model to:

* fix **difficulty consistency**
* fix **question_type correctness**
* fix **topic alignment**
* remove **ambiguity**
* ensure **format consistency**
* avoid **overlap between levels**

---

# ✅ MASTER CLEANING PROMPT (use this)

Use this EXACT prompt for batch cleaning:

---

**PROMPT:**

Clean and standardize the following CSV rows for a flashcard classifier dataset.

Output ONLY corrected CSV rows.
No explanation. No header.

Format:
question,answer,difficulty,question_type,topic,chunk_index

Rules:

1. Difficulty must follow:

* easy: direct recall or simple fact
* medium: single-step rule or reasoning
* hard: multi-step reasoning or reasoning plus interpretation

2. Question type must match:

* identification: asking what something is
* definition: asking for meaning
* explanation: asking why or how
* comparison: asking difference between two ideas
* computation: applying rule, calculation, or transformation

3. Topic must strictly match content:

* english, math, science, technology, history, geography, health, business, arts, general

4. Fix these issues:

* wrong difficulty classification
* wrong question_type classification
* wrong topic assignment
* vague or ambiguous wording
* inconsistent answer formats
* duplicate or overly similar questions

5. For computation:

* math, business, health → numeric or formula based
* arts → rule-based transformation
* general → real-world reasoning

6. Answers must be:

* short
* consistent format
* deterministic (no vague terms like "many", "some", "nice")

7. Do NOT change meaning unless necessary to fix correctness.

8. chunk_index must remain 0

9. Ensure no overlap between easy, medium, and hard

10.  Replace vague answers with precise outputs

11.  Standardize units and wording (e.g., "hours", "pm", "percent")






validator

Validate the following CSV rows for a flashcard classifier dataset.

Output ONLY a validation report.
Do not rewrite the dataset unless I ask.

Check:
1. CSV format correctness
2. missing fields
3. invalid difficulty values
4. invalid question_type values
5. invalid topic values
6. chunk_index must be 0
7. duplicate questions
8. duplicate answers with same question_type and topic
9. wrong topic classification
10. wrong question_type classification
11. difficulty overlap
12. vague or non-deterministic answers
13. computation rows that are not topic-based
14. computation rows that are too similar across difficulty levels
15. answer format inconsistency

Allowed values:
difficulty: easy, medium, hard
question_type: identification, definition, explanation, comparison, computation
topic: english, math, science, technology, history, geography, health, business, arts, general

Difficulty rules:
easy = direct recall or simple fact
medium = single-step rule or reasoning
hard = multi-step reasoning or reasoning plus interpretation

Question type rules:
identification = asks what something is
definition = asks for meaning
explanation = asks why or how
comparison = asks difference between two ideas
computation = applies rule, calculation, or transformation

Return:
- total rows checked
- number of valid rows
- number of problematic rows
- list of exact problematic rows
- reason for each issue
- suggested fix for each issue