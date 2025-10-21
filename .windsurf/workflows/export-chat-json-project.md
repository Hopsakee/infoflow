---
description: Save a chat to json in the `.aichats` folder for learning and reference
auto_execution_mode: 1
---

**Export Current Chat to JSON**

Export this conversation to a JSON file in `.aichats/` using the filename format: `YYYY-MM-DD_descriptive-title.json`. Use the date of the chat and not the current date nor the date of an opened file.

Process the chat in chunks of at most 8 questions and 8 answers. Show each chunk in their own file. Distinguish between the chunks by adding `_a`, `_b`, etc. at the end of the filename. Also add that to the metadata in the json: {"metadata": { "part": "a" }}.


Use this exact structure:
```json
{
  "metadata": {
    "date": "YYYY-MM-DD",
    "title": "Brief descriptive title",
    "part": "a",
    "repository": "owner/repo",
    "session_start": "ISO timestamp",
    "session_end": "ISO timestamp"
  },
  "messages": [
    {
      "id": 1,
      "timestamp": "ISO timestamp",
      "role": "user",
      "content": "exact verbatim copy of what the user typed"
    },
    {
      "id": 2,
      "timestamp": "ISO timestamp",
      "role": "assistant",
      "content": "exact verbatim copy of what you explained to the user. Summarize 'Thoughts' and show which Tools you used.",
      "actions": [
        {
          "type": "tool_call",
          "tool": "tool_name",
          "parameters": {"key": "value"},
          "result_summary": "brief summary of what the tool did"
        }
      ]
    }
  ]
}
```

## What to Include

**User messages (`role: "user"`):**
- `content`: EXACT, COMPLETE, VERBATIM text of what the user typed
- No `actions` field for user messages

**Assistant messages (`role: "assistant"`):**
- `content`: EXACT, COMPLETE, VERBATIM text of what I displayed in the chat interface
  - Include all markdown formatting, code blocks, headings, lists, etc. exactly as shown
  - Include all visible text responses
  - DO NOT include file contents I read in the background
  - DO NOT include internal tool outputs unless I explicitly showed them in my response
- `actions`: Array of tool calls I made (summarized)
  - Tool name
  - Key parameters (not full file contents)
  - Brief result summary
  - For commands: include the actual command string

## Critical Rules

1. **VERBATIM CONTENT**: Copy user questions and my visible responses EXACTLY as they appeared in the chat
2. **NO BACKGROUND DATA**: Don't include file contents, grep results, or other data I read but didn't show you
3. **SUMMARIZE ACTIONS**: Tool calls should be brief summaries of what I did, not full outputs
4. **COMMANDS VERBATIM**: Include actual command strings I ran
5. **PRESERVE FORMATTING**: Keep all markdown, code blocks, and formatting from visible messages

## Example

If I said "I'll check the database" and ran a command showing you the output, include:
- My visible text: "I'll check the database"
- Action: `{"tool": "run_command", "parameters": {"CommandLine": "sqlite3 ..."}, "result_summary": "Found 5 items"}`
- If I showed you the command output in my response, include it in `content`