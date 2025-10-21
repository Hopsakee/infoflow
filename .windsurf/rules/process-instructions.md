---
trigger: always_on
---

- Use `uv` for package management and environment management.
- Work in small steps. Only adjust one feature or solve one bug at a time.
- Always use a branch when building a feature or solving an issue.
- Use the `answer.ai` coding style.
- Use the `nbdev` coding approach, so use Jupyter Notebooks and do not use the python files.
- Write tests using the `fastcore.test` module from `fastcore`.
- If there are several good solutions or implemenations, explain why you chose the implemented option over the other options.
- When possible use Fastcore to make Python code more concise, readable, and expressive.

## FastCore Development Workflow

Check if FastCore can help us write more concise, readable and expressive code if one or more of the following cases applies.

### ✅ **When to Check FastCore**
- You’re writing boilerplate code (e.g., `self.x = x`).
- You need to extend built-in types or classes.
- You’re handling lists, files, or parallel tasks.
- You want cleaner tests or CLI scripts.
- You’re manually parsing arguments or writing XML.

Use this list as a **"red flag" checklist** while coding—when you spot one of these patterns, consider if FastCore has a tool to simplify it! 🚀


## FastHTML Development Workflow

**MANDATORY PROCESS**: Before writing ANY FastHTML code that can have more than one obvious implementation, you MUST:

1. Read [./aicontext/fasthtml.md](cci:7://file:///home/jelle/code/infoflow/aicontext/fasthtml.md:0:0-0:0) 
2. Identify which documentation webpage is relevant to the task
3. Read that specific webpage using the appropriate tool
4. Only then write the FastHTML code based on that documentation

This is a PROCESS RULE, not a context rule. It applies every single time a task has more than one obvious sollution. You may only skip this PROCESS RULE for simple tasks when you already know the best answer.