#!/usr/bin/env python3
"""Quick test to demonstrate the get_db_schema class method"""

from infoflow.classdb import Tool, InformationItem, Improvement
from dataclasses import fields

print("=== Tool Schema ===")
ToolSchema = Tool.get_db_schema()
print(f"Class: {ToolSchema.__name__}")
for field in fields(ToolSchema):
    print(f"  {field.name}: {field.type}")

print("\n=== InformationItem Schema ===")
InfoSchema = InformationItem.get_db_schema()
print(f"Class: {InfoSchema.__name__}")
for field in fields(InfoSchema):
    print(f"  {field.name}: {field.type}")

print("\n=== Improvement Schema ===")
ImprovementSchema = Improvement.get_db_schema()
print(f"Class: {ImprovementSchema.__name__}")
for field in fields(ImprovementSchema):
    print(f"  {field.name}: {field.type}")

print("\n=== SQLite Type Mapping ===")
print("Python int -> SQLite INTEGER")
print("Python str -> SQLite TEXT")
print("Python float -> SQLite REAL")
print("Python bytes -> SQLite BLOB")

print("\n=== Usage Example ===")
print("You can now instantiate the schema dataclass:")
print("tool_record = ToolSchema(id=1, name='Obsidian', ...)")
print("This gives you type checking and IDE autocomplete for database records!")
