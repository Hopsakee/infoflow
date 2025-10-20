# Actions to take for every step in the implementation plan

The document `PLAN.md` outlines a systematic approach to **document and visualize** my existing Personal Knowledge Management (PKM) workflow. This project creates a Python application to map out which tools I use for different information types, and which steps I follow when processing information through my four-phase workflow (Collect → Retrieve → Consume → Refine).

**Important:** This is NOT building a PKM system itself - it's building a documentation and visualization tool to understand and optimize my existing PKM workflow.

---

# Phase 1: Model Information Types and Current Tools (Foundation)

## Step 1.1: Define core information item types as Python classes ✅ COMPLETED

**Goal:** Create systematic model for all 12 item types (books, research papers, documents, annotations, notes, emails, discord messages, web articles, youtube videos, podcasts, product ideas, project ideas)

**What was done:**

- [x] Created `InformationType` enum class with values for: BOOK, RESEARCH_PAPER, DOCUMENT, ANNOTATION, NOTE, EMAIL, DISCORD_MESSAGE, WEB_ARTICLE, YOUTUBE_VIDEO, PODCAST, PRODUCT_IDEA, PROJECT_IDEA
- [x] Created `InformationItem` Pydantic BaseModel class with fields:
  - `id`: unique identifier
  - `name`: human-readable name
  - `info_type`: InformationType enum
  - `method`: PhaseMethodData (manual vs automatic collection)
  - `toolflow`: PhaseToolflowData (which tools handle this item in each phase)
  - `slug`: computed field for URL-friendly identifier
- [x] Implemented serialization/deserialization methods for SQLite compatibility
- [x] Created instance tracking mechanism using ClassVar
- [x] Implemented `flatten_for_db()` method to convert Pydantic models to SQLite-friendly format
- [x] Implemented `from_db()` classmethod to load data from SQLite back into Pydantic models

**Location:** `nbs/00_classes_db.ipynb` → exported to `infoflow/classdb.py`

---

## Step 1.2: Model your current tool ecosystem with capabilities ✅ COMPLETED

**Goal:** Map each tool's strengths/limitations for different item types and workflow phases

**What was done:**

- [x] Created `Tool` Pydantic BaseModel class with fields:
  - `id`: unique identifier
  - `name`: tool name
  - `organization_system`: list of OrganizationSystem enums (TAGS, FOLDERS, LINKS, JOHNNY_DECIMAL)
  - `phase_quality`: PhaseQualityData with quality ratings (NA, BAD, OK, GREAT) for each phase
  - Phase-specific description fields: `collect`, `retrieve`, `consume`, `extract`, `refine`
  - `slug`: computed field for URL-friendly identifier
- [x] Created `PhaseQualityData` class to track tool performance in each phase
- [x] Created `PhaseDescriptionData` class to store descriptions of how to use tool in each phase
- [x] Implemented serialization/deserialization for SQLite
- [x] Created instances for tools: Reader, Recall, Readwise, Obsidian, LibraryThing, Snipd, NeoReader, YouTube

**Location:** `nbs/00_classes_db.ipynb` → exported to `infoflow/classdb.py`

---

## Step 1.3: Create workflow routing logic for item types ✅ COMPLETED

**Goal:** Systematically determine which tool should handle which item type in which phase

**What was done:**

- [x] Created `PhaseToolflowData` class to define tool routing for each phase (collect, retrieve, consume, extract, refine)
- [x] Each InformationItem instance includes toolflow data specifying which tool(s) to use in each phase
- [x] Created instances for 8 information items with complete toolflow mappings:
  - Web Article: Reader → Reader → Reader → Readwise → Obsidian
  - Note: Manual collect → Obsidian → Obsidian → Obsidian → Obsidian
  - Book: LibraryThing → LibraryThing → NeoReader → Readwise → (Obsidian, Recall)
  - Podcast: Snipd (automatic) → Snipd → Snipd → Readwise → Obsidian
  - Research Paper: (Recall, NeoReader) → (Recall, NeoReader) → NeoReader → Readwise → (Obsidian, Recall)
  - Document: NeoReader → NeoReader → NeoReader → Readwise → (Obsidian, Recall)
  - YouTube Video: YouTube (automatic) → YouTube → YouTube → Obsidian → Obsidian
  - Email: (not yet fully defined)
- [x] Supports multiple tools per phase using tuples
- [x] Created `get_info_items_for_tool()` function to filter information items by tool

**Location:** `nbs/01_create_instances.ipynb` → exported to `infoflow/creinst.py`

---

# Phase 2: Design Collection Strategy (Capture Optimization)

## Step 2.1: Define manual vs automatic collection workflows ⚠️ PARTIALLY COMPLETED

**Goal:** Create clear pathways for high-quality manual additions vs bulk automatic feeds

**What was done:**

- [x] Created `Method` enum with MANUAL and AUTOMATIC values
- [x] Created `PhaseMethodData` class to track collection method for each information item
- [x] Defined collection methods for existing items:
  - Manual: Web Article, Note, Book, Research Paper, Document
  - Automatic: Podcast (via Snipd), YouTube Video

**What still needs to be done:**

- [ ] Define quality gates and filtering mechanisms for automatic feeds
- [ ] Create separate workflow branches visualization for manual vs automatic
- [ ] Document best practices for when to use manual vs automatic collection

---

## Step 2.2: Address current collection gaps 🔴 NOT STARTED

**Goal:** Identify missing storage solutions (YouTube annotations, Discord messages, project ideas, product ideas)

**What needs to be done:**

- [ ] Create InformationItem instances for missing types:
  - Discord messages
  - Product ideas
  - Project ideas
  - Emails (partially defined)
- [ ] Define toolflow for these missing items
- [ ] Document which tools you currently use (or plan to use) for these item types
- [ ] Add these to the database

---

## Step 2.3: Design tagging strategy for non-Obsidian tools 🔴 NOT STARTED

**Goal:** Create lightweight categorization system for Recall/Readwise Reader that doesn't require Johnny Decimal complexity

**What needs to be done:**

- [ ] Document your current tagging taxonomy based on 5-7 current interests + item type
- [ ] Add tagging strategy documentation to the Tool descriptions
- [ ] Create guidelines for consistent tagging across tools
- [ ] Consider implementing tag validation or suggestions in the visualization

---

# Phase 3: Build Retrieval System (Search Optimization)

## Step 3.1: Create unified search interface design 🔴 NOT STARTED

**Goal:** Address Readwise Reader's poor search by designing Python/SQL search system across all tools

**What needs to be done:**

- [ ] Document how you currently search across your tools
- [ ] Design search system architecture to query your existing tools
- [ ] Create database schema for searchable content
- [ ] Implement search across LibraryThing, Obsidian, Recall, and Readwise data
- [ ] Build search interface in the web application

---

## Step 3.2: Implement project-based retrieval logic 🔴 NOT STARTED

**Goal:** Enable finding relevant items based on current interests without over-categorizing

**What needs to be done:**

- [ ] Document your 5-7 current interests/projects
- [ ] Create "Current Interests" or "Projects" data model
- [ ] Link information items to interests/projects
- [ ] Implement filtering by current interests
- [ ] Add interest-based views to web application

---

## Step 3.3: Build workflow gap identification system ⚠️ PARTIALLY COMPLETED

**Goal:** Make missing pieces visible so you can prioritize building solutions

**What was done:**

- [x] Created `Improvement` class to track needed improvements for tools
- [x] Improvements include: title, what, why, how, priority, tool, phase
- [x] Web application has full CRUD interface for improvements
- [x] Can view all improvements grouped by tool
- [x] Can filter improvements by tool and phase

**What still needs to be done:**

- [ ] Automatically detect gaps in toolflow (e.g., information items without complete toolflow)
- [ ] Create dashboard showing coverage statistics
- [ ] Highlight unsupported item type/tool combinations

---

# Phase 4: Create Consumption Workflow (Processing Optimization)

## Step 4.1: Design annotation sync optimization 🔴 NOT STARTED

**Goal:** Streamline the Snipd → Readwise → Obsidian and Reader → Readwise → Obsidian flows

**What needs to be done:**

- [ ] Document your current annotation sync workflow (Snipd → Readwise → Obsidian)
- [ ] Document pain points in the current sync process
- [ ] Design optimized sync workflow
- [ ] Consider automation opportunities
- [ ] Update tool descriptions with sync best practices

---

## Step 4.2: Handle consumption method variations 🔴 NOT STARTED

**Goal:** Create systematic approach for items consumed in different tools

**What needs to be done:**

- [ ] Document your consumption preferences for each item type (e.g., books on Boox device, YouTube direct, papers in Reader)
- [ ] Create routing logic for consumption method variations
- [ ] Update toolflow definitions to reflect consumption preferences

---

## Step 4.3: Build processing workflow for Obsidian integration 🔴 NOT STARTED

**Goal:** Systematize how highlights/annotations become notes using Johnny Decimal system

**What needs to be done:**

- [ ] Document your current Obsidian processing workflow
- [ ] Document how highlights/annotations become notes in your Johnny Decimal system
- [ ] Define Johnny Decimal categories for different information types
- [ ] Consider documenting automation opportunities for common processing patterns

---

# Phase 5: Implementation and Validation (System Testing)

## Step 5.1: Build workflow visualization system ✅ COMPLETED

**Goal:** Create top-to-bottom Graphviz diagrams showing item type → tool routing with gap visibility

**What was done:**

- [x] Created `build_graphiz_from_intances()` function to generate workflow diagrams
- [x] Implemented phase-based visualization with color coding:
  - Collect: lightblue
  - Retrieve: orange
  - Consume: yellow
  - Extract: lightcoral
  - Refine: lightgreen
- [x] Created `create_workflow_viz()` function with optional tool filtering
- [x] Implemented SVG generation from Graphviz diagrams
- [x] Created `add_onclick_to_nodes()` function to make nodes clickable
- [x] Integrated interactive visualization into FastHTML web application
- [x] Nodes link to tool or resource detail pages

**Location:** `nbs/02_create_vizualisation.ipynb` → exported to `infoflow/viz.py`

---

## Step 5.2: Create workflow tracking prototype 🔴 NOT STARTED

**Goal:** Build system to monitor items through collect → retrieve → consume → refine phases

**What needs to be done:**

- [ ] Create data model for tracking actual information items (not just types)
- [ ] Track status of items through workflow phases
- [ ] Create dashboard showing bottlenecks and completion rates
- [ ] Implement analytics for workflow efficiency

---

## Step 5.3: Test with representative sample of each item type 🔴 NOT STARTED

**Goal:** Validate system handles real-world complexity before full deployment

**What needs to be done:**

- [ ] Create test cases for each of the 8 defined information item types
- [ ] Test workflows with real examples from your PKM system
- [ ] Measure performance and identify issues
- [ ] Document test results and improvements needed

---

# Phase 6: Scale and Maintain (System Optimization)

## Step 6.1: Deploy unified search system 🔴 NOT STARTED

**Goal:** Implement the Python/SQL search solution for Readwise Reader and cross-tool queries

**What needs to be done:**

- [ ] Build on Step 3.1 work
- [ ] Deploy search interface
- [ ] Test search across all information sources
- [ ] Optimize search performance

---

## Step 6.2: Create maintenance and review cycles 🔴 NOT STARTED

**Goal:** Ensure system stays current with tool changes and evolving needs

**What needs to be done:**

- [ ] Define review schedule (weekly, monthly, quarterly) for updating your workflow documentation
- [ ] Create automated health checks
- [ ] Set up monitoring for when your tools change
- [ ] Document review process

---

## Step 6.3: Document system for future adaptation 🔴 NOT STARTED

**Goal:** Create flexible documentation that can evolve as tools and needs change

**What needs to be done:**

- [ ] Expand README with comprehensive usage guide
- [ ] Document decision rationale for your tool choices
- [ ] Create troubleshooting guide
- [ ] Document how to add new tools and information types to the visualization
- [ ] Create video tutorials or walkthroughs

---

# Additional Completed Work (Not in Original Plan)

## Web Application with FastHTML ✅ COMPLETED

**What was done:**

- [x] Created full-featured web application using FastHTML and MonsterUI
- [x] Implemented pages:
  - Index page with interactive workflow visualization
  - Tool detail pages showing tool capabilities and phase quality
  - Tool edit pages for updating tool information
  - Resource (InformationItem) detail pages
  - Resource edit pages for updating toolflow
  - Improvements list page grouped by tool
  - Improvement detail pages
  - Improvement create/edit pages
  - Theme switcher
- [x] Implemented HTMX-based interactivity for seamless navigation
- [x] Created SQLite database integration with FastLite
- [x] Implemented full CRUD operations for Tools, InformationItems, and Improvements

**Location:** `nbs/03_create_webapp.ipynb` → exported to `infoflow/webapp.py`, main application in `main.py`

---

## Database Layer ✅ COMPLETED

**What was done:**

- [x] Created SQLite database schema using FastLite
- [x] Implemented tables for: tools, information_items, improvements
- [x] Created `create_db()` function
- [x] Created `create_tables_from_pydantic()` function
- [x] Created `dict_from_db()` function to load data from database
- [x] Implemented `db_from_instances()` function to populate fresh database

**Location:** `nbs/00_classes_db.ipynb` and `nbs/01_create_instances.ipynb`

---

# Summary

**Completed:**

- [x] Phase 1: Steps 1.1, 1.2, 1.3 (Foundation complete)
- [x] Phase 5: Step 5.1 (Visualization complete)
- [x] Web application with full CRUD interface
- [x] Database layer with SQLite
- [x] Phase 2: Step 2.1 (Partially - method tracking exists)
- [x] Phase 3: Step 3.3 (Partially - improvements tracking exists)

**Not Started:**

- [ ] Phase 2: Steps 2.2, 2.3 (Document collection gaps and tagging strategy)
- [ ] Phase 3: Steps 3.1, 3.2 (Search and project-based retrieval)
- [ ] Phase 4: All steps (Document consumption workflow)
- [ ] Phase 5: Steps 5.2, 5.3 (Tracking and testing)
- [ ] Phase 6: All steps (Scale and maintain)

**Next Priority Actions:**

- [ ] Complete missing information item types (Discord, Product Ideas, Project Ideas, Emails)
- [ ] Document unified search approach across your tools
- [ ] Create project/interest-based retrieval
- [ ] Build workflow tracking for actual items (not just types)
- [ ] Test with real data from your PKM system
