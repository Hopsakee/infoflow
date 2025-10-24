---
trigger: always_on
---

- Use `uv` for package management and environment management.
- Work in small steps. Only adjust one feature or solve one bug at a time.
- Always create a new branch when building a new feature or when asked to solve one of the issues that is defined in the repo on Github, Gitlab or Azure Devops.
- Always ask to create a new branch if the given task will probably need a rewrite of more than 40 lines of code or addition of more than 20 lines of code.
- Use the `fast.ai` coding style as explained in `code-style-guide.md`.
- Use the `nbdev` coding approach, so use Jupyter Notebooks and do not use the python files and do not directly alter the python files.
- Write tests using the `fastcore.test` module from `fastcore`.
- If there are several good solutions or implemenations, explain why you chose the implemented option over the other options.
- When possible use Fastcore to make Python code more concise, readable, and expressive.
- Use `FastHTML` for webdevelopment as documented in `./aicontext/fasthtml.md`
- Use `MonsterUI` for creating the appearance of the web-application as documented in `./aicontext/monsterui.md`.

## git commit workflow

If `nbdev` is used in the codebase whenever making a git commit, assume nbdev’s hooks will run. If `git commit` fails because the hooks modified notebooks (e.g., `nbdev_clean` rewrote metadata), immediately re-run `git status`, re-stage the changed files, and repeat the commit. Do not bypass or disable the hooks; they ensure notebooks stay clean and merge-friendly.

## `nbdev` Development Workflow

**MANDATORY PROCESS**: Before writing ANY code, make sure you will write all code in the Jupyter Notebooks in the "./nbs" folder and that you will use the `nbdev` coding approach. Never write changes directly to the `*.py` files in the "./infoflow" folder. Only code that belongs in `main.py` can be written directly to the `main.py` file. Code that belongs in `main.py` is code that defines the `@route` for the FastHTML web application.
I you're not sure how you should create nbdev-style code, you MUST read the nbdev documentation that you can read using the file `./aicontext/nbdev.md`. This file gives a high level overview of how to use `nbdev`. It has information on which URLs give more detailed information. Read that detailed information by following the link given if it contains information applicable to your current task. 

1. Read the nbdev documentation using the file `./aicontext/nbdev.md` 
2. Identify which parts of this file are relevant to the task
3. Read those pecific parts of the nbdev following the links given in the file
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

### How to check FastCore

1. Read the FastCore documentation using the file `./aicontext/fastcore.md` 
2. Identify which parts of this file are relevant to the task
3. Read those pecific parts of the nbdev following the links given in the file
4. Only then write the new code or alter existing code based on that documentation


## FastHTML Development Workflow

**MANDATORY PROCESS**: Before writing ANY FastHTML code that can have more than one obvious implementation, you MUST:

1. Read [./aicontext/fasthtml.md](cci:7://file:///home/jelle/code/infoflow/aicontext/fasthtml.md:0:0-0:0) 
2. Identify which documentation webpages are relevant to the task
3. Read those specific webpages using the appropriate tool
4. Only then write the FastHTML code based on that documentation

This is a PROCESS RULE, not a context rule. It applies every single time a task has more than one obvious sollution. You may only skip this PROCESS RULE for simple tasks when you already know the best answer.

## MonsterUI Development Workflow

**MANDATORY PROCESS**: Before writing ANY MonsterUI code or code to create or alter the appearance of a web-application you MUST follow the next steps if the task can have more than one obvious code implementation:

1. Read `./aicontext/monsterui.md` file 
2. Identify which documentation webpages are relevant to the task
3. Read those specific webpages using the appropriate tool
4. Only then write the MonsterUI code based on that documentation

This is a PROCESS RULE, not a context rule. It applies every single time a task has more than one obvious sollution. You may only skip this PROCESS RULE for simple tasks when you already know the best answer.