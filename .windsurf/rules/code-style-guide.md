---
trigger: always_on
---

- Use the fast.ai code style guide. This is given in the file `.aicontext/code-style-guide-fastai.md`. Read this `.aicontext/code-style-guide-fastai.md` to know how to properly style the code everytime when:
    - you write a new function,
    - you rewrite more than 25 lines of code,
    - you are asked to refactor or review the code.
- Use Notebook driven development using the `nbdev` package by answer.ai. Use the file `./aicontext/nbdev.md` to understand `nbdev`.
- Always prefer simple solutions
- Avoid duplication of code whenever possible, which means checking for other areas of the codebase that might already have similar code and functionality
- When fixing an issue or bug, do not introduce a new pattern or technology without first exhausting all options for the existing implementation. And if you finally do this, make sure to remove the old implementation afterwards so we don't have duplicate logic.
- Keep the codebase very clean and organized
- Mocking data is only needed for writing tests, never mock data for the actual application
- Use type hints for all code
- Use docmenst for all code as used in `nbdev`. So add a comment right after the parameter to describe the parameter