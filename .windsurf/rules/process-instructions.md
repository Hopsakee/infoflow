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

## `nbdev` Development Workflow

**MANDATORY PROCESS**: Before writing ANY code, make sure you will write all code in the Jupyter Notebooks in the "./nbs" folder and that you will use the `nbdev` coding approach. Never write changes directly to the `*.py` files in the "./infoflow" folder. Only code that belongs in `main.py` can be written directly to the `main.py` file. Code that belongs in `main.py` is code that defines the `@route` for the FastHTML web application.
I you're not sure how you should create nbdev-style code, you MUST read the nbdev documentation that you can read using the MCP-server named "nbdev-docs". 

1. Read the nbdev documentation using the nbdev-docs MCP server 
2. Identify which part of the nbdev repo is relevant to the task
3. Read that specific parts of the nbdev repo using the nbdev-docs MCP server
4. Only then write the new code or alter existing code based on that documentation


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