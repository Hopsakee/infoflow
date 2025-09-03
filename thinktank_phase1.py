from enum import Enum
from dataclasses import dataclass

class InformationType(Enum):
    """Information content types that flow through the PKM workflow."""
    BOOK = "book"
    RESEARCH_PAPER = "research_paper"
    DOCUMENT = "document"
    ANNOTATION = "annotations&highlights"
    NOTE = "note"
    EMAIL = "email"
    DISCORD_MESSAGE = "discord_message"
    WEB_ARTICLE = "web_article"
    YOUTUBE_VIDEO = "youtube_video"
    PODCAST = "podcast"
    PRODUCT_IDEA = "product_idea"
    PROJECT_IDEA = "project_idea"

class Method(Enum):
    """How actions are performed - manually or automatically."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"

class Phase(Enum):
    """The five phases of the PKM workflow."""
    COLLECT = "collect"
    RETRIEVE = "retrieve"
    CONSUME = "consume"
    EXTRACT = "extract"
    REFINE = "refine"

class PhaseQuality(Enum):
    """Quality rating for how well a tool performs in each phase."""
    NA = "na"
    BAD = "bad"
    OK = "ok"
    GREAT = "great"

class OrganizationSystem(Enum):
    """How tools organize and structure information."""
    TAGS = "tags"
    FOLDERS = "folders"
    LINKS = "links"
    JOHNNY_DECIMAL = "johnny_decimal"

@dataclass
class InformationItem:
    """Represents an information item flowing through the PKM workflow."""
    info_type: InformationType
    method: list[Method]  # [collect, retrieve, consume, extract, refine]
    toolflow: list  # [collect, retrieve, consume, extract, refine]

@dataclass
class Tool:
    """Represents a PKM tool with supported information items."""
    name: str
    info_items: list[InformationItem]
    organization_system: list[OrganizationSystem]
    phase_quality: list[PhaseQuality]

@dataclass
class Improvement:
    """Tracks workflow improvements needed for better PKM effectiveness."""
    what: str
    why: str
    prio: int
    workflow_routes: list

web_article_item = InformationItem(
    info_type=InformationType.WEB_ARTICLE,
    method=[Method.MANUAL, None, None, None, None],
    toolflow=[("Reader", "Recall"), "Recall", "Reader", None, None]
)

# annotation_item = InformationItem(
#     info_type=InformationType.ANNOTATION,
#     method=[Method.AUTOMATIC, None, None, None, None],
#     toolflow=[None, None, None, "Readwise", ("Recall", "Obsidian")]
# )

note_item = InformationItem(
    info_type=InformationType.NOTE,
    method=[Method.MANUAL, None, None, None, None],
    toolflow=[None, "Obsidian", "Obsidian", "Obsidian", "Obsidian"]
)
book_item = InformationItem(
    info_type=InformationType.BOOK,
    method=[Method.MANUAL, None, None, None, None],
    toolflow=["LibraryThing", "LibraryThing", "NeoReader", "Readwise", "Obsidian"]
)

podcast_item = InformationItem(
    info_type=InformationType.PODCAST,
    method=[Method.AUTOMATIC, None, None, None, None],
    toolflow=["Snipd", "Snipd", "Snipd", "Readwise", "Obsidian"]
)

research_paper_item = InformationItem(
    info_type=InformationType.RESEARCH_PAPER,
    method=[Method.MANUAL, None, None, None, None],
    toolflow=[("Recall", "NeoReader"), ("Recall", "NeoReader"), "NeoReader", "Readwise", ("Obsidian", "Recall")]
)

document_item = InformationItem(
    info_type=InformationType.DOCUMENT,
    method=[Method.MANUAL, None, None, None, None],
    toolflow=["NeoReader", "NeoReader", "NeoReader", "Readwise", ("Obsidian", "Recall")]
)

youtube_video_item = InformationItem(
    info_type=InformationType.YOUTUBE_VIDEO,
    method=[Method.AUTOMATIC, None, None, None, None],
    toolflow=["YouTube", "YouTube", "YouTube", "Obsidian", "Obsidian"]
)
reader = Tool(
    name="Reader",
    info_items=[web_article_item],
    organization_system=[OrganizationSystem.TAGS],
    phase_quality=[PhaseQuality.GREAT, PhaseQuality.BAD, PhaseQuality.GREAT, PhaseQuality.NA, PhaseQuality.NA]
)

recall = Tool(
    name="Recall",
    info_items=[web_article_item],
    organization_system=[OrganizationSystem.LINKS],
    phase_quality=[PhaseQuality.GREAT, PhaseQuality.GREAT, PhaseQuality.NA, PhaseQuality.NA, PhaseQuality.GREAT]
)

readwise = Tool(
    name="Readwise",
    info_items=[annotation_item],
    organization_system=[OrganizationSystem.TAGS],
    phase_quality=[PhaseQuality.NA, PhaseQuality.OK, PhaseQuality.NA, PhaseQuality.GREAT, PhaseQuality.OK]
)

obsidian = Tool(
    name="Obsidian",
    info_items=[annotation_item, note_item],
    organization_system=[OrganizationSystem.JOHNNY_DECIMAL, OrganizationSystem.LINKS],
    phase_quality=[PhaseQuality.NA, PhaseQuality.OK, PhaseQuality.OK, PhaseQuality.GREAT, PhaseQuality.GREAT]
)
librarything = Tool(
    name="LibraryThing",
    info_items=[book_item],
    organization_system=[OrganizationSystem.TAGS],
    phase_quality=[PhaseQuality.OK, PhaseQuality.BAD, PhaseQuality.NA, PhaseQuality.NA, PhaseQuality.NA]
)

snipd = Tool(
    name="Snipd",
    info_items=[podcast_item],
    organization_system=[OrganizationSystem.FOLDERS],
    phase_quality=[PhaseQuality.OK, PhaseQuality.BAD, PhaseQuality.GREAT, PhaseQuality.NA, PhaseQuality.NA]
)

neoreader = Tool(
    name="NeoReader",
    info_items=[book_item, research_paper_item, document_item],
    organization_system=[OrganizationSystem.FOLDERS],
    phase_quality=[PhaseQuality.OK, PhaseQuality.BAD, PhaseQuality.GREAT, PhaseQuality.NA, PhaseQuality.NA]
)

youtube = Tool(
    name="YouTube",
    info_items=[youtube_video_item],
    organization_system=[OrganizationSystem.FOLDERS],
    phase_quality=[PhaseQuality.OK, PhaseQuality.BAD, PhaseQuality.OK, PhaseQuality.NA, PhaseQuality.NA]
)

import graphviz
def create_combined_workflow_viz(info_items, all_tools):
    if not isinstance(info_items, list): info_items = [info_items]
    
    dot = graphviz.Digraph(comment='PKM Workflow')
    dot.attr(rankdir='TB')
    
    phases = ['collect', 'retrieve', 'consume', 'extract', 'refine']
    all_nodes = set()
    edges = {}
    
    quality_colors = {PhaseQuality.GREAT: 'lightgreen', PhaseQuality.OK: 'lightblue', PhaseQuality.BAD: 'orange', PhaseQuality.NA: 'lightgray'}
    
    for phase in phases:
        with dot.subgraph() as s:
            s.attr(rank='same')
            for info_item in info_items:
                i = phases.index(phase)
                if i < len(info_item.toolflow) and info_item.toolflow[i] is not None:
                    tool_entry = info_item.toolflow[i]
                    if isinstance(tool_entry, tuple): tools_in_phase = tool_entry
                    else: tools_in_phase = (tool_entry,)
                    
                    for tool_name in tools_in_phase:
                        if tool_name is not None:
                            node_id = f"{tool_name.lower()}_{phase}"
                            if node_id not in all_nodes:
                                tool = next((t for t in all_tools if t.name == tool_name), None)
                                color = quality_colors[tool.phase_quality[i]] if tool else 'white'
                                s.node(node_id, f"{tool_name}\n({phase})", shape='hexagon', fillcolor=color, style='filled')
                                all_nodes.add(node_id)
    
    with dot.subgraph() as s:
        s.attr(rank='same')
        for info_item in info_items:
            source_id = f"source_{info_item.info_type.value}"
            s.node(source_id, info_item.info_type.value.replace('_', ' ').title(), shape='box')
    
    for info_item in info_items:
        source_id = f"source_{info_item.info_type.value}"
        previous_nodes = [source_id]
        
        for i, tool_entry in enumerate(info_item.toolflow):
            if i < len(phases) and tool_entry is not None:
                phase = phases[i]
                current_nodes = []
                
                if isinstance(tool_entry, tuple): tools_in_phase = tool_entry
                else: tools_in_phase = (tool_entry,)
                
                for tool_name in tools_in_phase:
                    if tool_name is not None:
                        node_id = f"{tool_name.lower()}_{phase}"
                        current_nodes.append(node_id)
                        
                        for prev_node in previous_nodes:
                            edge_key = (prev_node, node_id)
                            if edge_key not in edges:
                                dot.edge(prev_node, node_id)
                                edges[edge_key] = True
                
                if current_nodes: previous_nodes = current_nodes
    
    return dot
tools = [reader, recall, readwise, obsidian, librarything, snipd, neoreader, youtube]
items = [note_item, web_article_item, annotation_item, book_item, youtube_video_item, podcast_item, research_paper_item, document_item]
viz = create_combined_workflow_viz(items, tools)
viz