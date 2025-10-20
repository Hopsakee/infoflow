---
trigger: always_on
---

- Use Notebook driven development using the `nbdev` package by answer.ai.
- Always prefer simple solutions
- Avoid duplication of code whenever possible, which means checking for other areas of the codebase that might already have similar code and functionality
- When fixing an issue or bug, do not introduce a new pattern or technology without first exhausting all options for the existing implementation. And if you finally do this, make sure to remove the old implementation afterwards so we don't have duplicate logic.
- Keep the codebase very clean and organized
- Mocking data is only needed for tests, never mock data for dev or prod
- Use type hints for all code
- Use docmenst for all code as used in nbdev. So add a comment right after the parameter to describe the parameter