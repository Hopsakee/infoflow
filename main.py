from __future__ import annotations
import re
import json
import graphviz
import xml.etree.ElementTree as ET

from enum import Enum
from typing import Union, ClassVar

from dataclasses import dataclass
from pydantic import BaseModel, field_serializer, field_validator, Field, computed_field
from fastlite import *
from fastcore.test import *
from hopsa import ossys
from fasthtml.common import *
from monsterui.all import *


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

# %% ../nbs/00_classes_db.ipynb 15
class PhaseQualityData(BaseModel):
    collect: PhaseQuality = Field(PhaseQuality.NA)
    retrieve: PhaseQuality = Field(PhaseQuality.NA)
    consume: PhaseQuality = Field(PhaseQuality.NA)
    extract: PhaseQuality = Field(PhaseQuality.NA)
    refine: PhaseQuality = Field(PhaseQuality.NA)

class Tool(BaseModel):
    name: str = Field(..., description="Name of the tool")
    organization_system: list[OrganizationSystem] = Field(..., description="Organization systems supported by the tool")
    phase_quality: PhaseQualityData = Field(..., description="Quality of the tool for each phase")
    collect: str | None = Field(default=None, description="Description how to use tool in collect phase")
    retrieve: str | None = Field(default=None, description="Description how to use tool in retrieve phase")
    consume: str | None = Field(default=None, description="Description how to use tool in consume phase")
    extract: str | None = Field(default=None, description="Description how to use tool in extract phase")
    refine: str | None = Field(default=None, description="Description how to use tool in refine phase")

    @computed_field
    @property
    def slug(self) -> str:
        return ossys.sanitize_name(self.name)

    def flatten_for_db(self):
        base = self.model_dump(exclude={'phase_quality', 'organization_system'})
        base.update({'organization_system': json.dumps([org.value for org in self.organization_system]), 'collect_quality': self.phase_quality.collect.value, 'retrieve_quality': self.phase_quality.retrieve.value, 'consume_quality': self.phase_quality.consume.value, 'extract_quality': self.phase_quality.extract.value, 'refine_quality': self.phase_quality.refine.value})
        return base

    _instances: ClassVar[Dict[str, Tool]] = {}

    def __init__(self, **data):
        super().__init__(**data)
        type(self)._instances[self.slug] = self
    
    @classmethod
    def get_instances(cls) -> Dict[str, Tool]:
        return cls._instances
    
  
    @classmethod
    def from_db(cls, db_record):
        phase_quality = PhaseQualityData(collect=PhaseQuality(db_record['collect_quality']), retrieve=PhaseQuality(db_record['retrieve_quality']), consume=PhaseQuality(db_record['consume_quality']), extract=PhaseQuality(db_record['extract_quality']), refine=PhaseQuality(db_record['refine_quality']))
        org_systems = [OrganizationSystem(s) for s in json.loads(db_record['organization_system'])]
        return cls(name=db_record['name'], organization_system=org_systems, phase_quality=phase_quality, collect=db_record['collect'], retrieve=db_record['retrieve'], consume=db_record['consume'], extract=db_record['extract'], refine=db_record['refine'])

# %% ../nbs/00_classes_db.ipynb 16
class PhaseMethodData(BaseModel):
    collect: Method | None = Field(default=None)
    retrieve: Method | None = Field(default=None)
    consume: Method | None = Field(default=None)
    extract: Method | None = Field(default=None)
    refine: Method | None = Field(default=None)

# %% ../nbs/00_classes_db.ipynb 18
class PhaseToolflowData(BaseModel):
    collect: Union[str, tuple[str, ...], None] = Field(default=None)
    retrieve: Union[str, tuple[str, ...], None] = Field(default=None)
    consume: Union[str, tuple[str, ...], None] = Field(default=None)
    extract: Union[str, tuple[str, ...], None] = Field(default=None)
    refine: Union[str, tuple[str, ...], None] = Field(default=None)

    @staticmethod
    def _san(v):
        if v is None: return None
        if isinstance(v, str): return ossys.sanitize_name(v)
        if isinstance(v, (list, tuple)):
            return tuple([ossys.sanitize_name(i) for i in v])
    
    @field_validator('collect', 'retrieve', 'consume', 'extract', 'refine', mode='before')
    def _val(cls, v): return cls._san(v)


# %% ../nbs/00_classes_db.ipynb 21
class InformationItem(BaseModel):
    name: str = Field(..., description="Name of the information item")
    info_type: InformationType = Field(..., description="Type of information item, e.g. book, article, video, etc.")
    method: PhaseMethodData = Field(..., description="Methods used at each phase")
    toolflow: PhaseToolflowData = Field(..., description="Tools used for this item at each phase")

    @computed_field
    @property
    def slug(self) -> str:
        return ossys.sanitize_name(self.name)

    def flatten_for_db(self):
        base = self.model_dump(exclude={'method', 'toolflow'})
        base.update({'collect_method': self.method.collect.value if self.method.collect else None, 'retrieve_method': self.method.retrieve.value if self.method.retrieve else None, 'consume_method': self.method.consume.value if self.method.consume else None, 'extract_method': self.method.extract.value if self.method.extract else None, 'refine_method': self.method.refine.value if self.method.refine else None, 'collect_toolflow': json.dumps(self.toolflow.collect) if isinstance(self.toolflow.collect, (list, tuple)) else self.toolflow.collect, 'retrieve_toolflow': json.dumps(self.toolflow.retrieve) if isinstance(self.toolflow.retrieve, (list, tuple)) else self.toolflow.retrieve, 'consume_toolflow': json.dumps(self.toolflow.consume) if isinstance(self.toolflow.consume, (list, tuple)) else self.toolflow.consume, 'extract_toolflow': json.dumps(self.toolflow.extract) if isinstance(self.toolflow.extract, (list, tuple)) else self.toolflow.extract, 'refine_toolflow': json.dumps(self.toolflow.refine) if isinstance(self.toolflow.refine, (list, tuple)) else self.toolflow.refine})
        return base

    _instances: ClassVar[Dict[str, InformationItem]] = {}

    def __init__(self, **data):
        super().__init__(**data)
        type(self)._instances[self.slug] = self
    
    @classmethod
    def get_instances(cls) -> Dict[str, InformationItem]:
        return cls._instances
    
    @field_serializer('info_type')
    def db_serialize(self, v):
        return v.value


# %% ../nbs/00_classes_db.ipynb 22
class Improvement(BaseModel):
    title: str = Field(..., description="Title of the improvement")
    what: str = Field(..., description="What needs to be improved")
    why: str = Field(..., description="Why is this improvement needed")
    prio: int = Field(..., description="Priority of the improvement")
    tool: str = Field(..., description="Tool that needs improvement")
    phase: Phase = Field(..., description="Phase that needs improvement")

    @computed_field
    @property
    def slug(self) -> str:
        return ossys.sanitize_name(self.title)

    def flatten_for_db(self):
        return self.model_dump()

    _instances: ClassVar[Dict[str, Improvement]] = {}

    def __init__(self, **data):
        super().__init__(**data)
        type(self)._instances[self.slug] = self
    
    @classmethod
    def get_instances(cls) -> Dict[str, Improvement]:
        return cls._instances
    
    @field_serializer('phase')
    def db_serialize(self, v):
        return v.value
    
    @field_validator('tool')
    def validate_tool_names(cls, v):
        valid_tools = Tool.get_instances().keys()
        if v not in valid_tools: raise ValueError(f"Tool '{v}' does not exist")
        return v

# %% ../nbs/00_classes_db.ipynb 29
def create_db(loc="static/infoflow.db"):
    db = database(loc)
    db.execute("PRAGMA foreign_keys = ON;")
    return db


# %% ../nbs/00_classes_db.ipynb 32
def create_tables_from_pydantic(db):
    sample_tool = Tool(name="Sample", organization_system=[OrganizationSystem.TAGS], phase_quality=PhaseQualityData(collect=PhaseQuality.GREAT, retrieve=PhaseQuality.BAD, consume=PhaseQuality.OK, extract=PhaseQuality.NA, refine=PhaseQuality.GREAT))
    sample_item = InformationItem(name="Sample", info_type=InformationType.WEB_ARTICLE, method=PhaseMethodData(collect=Method.MANUAL, retrieve=None, consume=None, extract=None, refine=None), toolflow=PhaseToolflowData(collect="Reader", retrieve="Recall", consume=None, extract=None, refine=None))
    sample_imp = Improvement(title="Sample", what="Test", why="Test", prio=1, tool="sample", phase=Phase.COLLECT)
    
    db["tools"].insert(sample_tool.flatten_for_db(), pk="slug")
    db["information_items"].insert(sample_item.flatten_for_db(), pk="slug") 
    db["improvements"].insert(sample_imp.flatten_for_db(), pk="slug")
    
    db["tools"].delete("sample")
    db["information_items"].delete("sample")
    db["improvements"].delete("sample")
    
    return db.t.tools, db.t.information_items, db.t.improvements

def tools_from_code():
    """Create all Tool instances as defined in the code."""
    reader = Tool(
        name="Reader",
        organization_system=[OrganizationSystem.TAGS],
        phase_quality=PhaseQualityData(
            collect=PhaseQuality.GREAT,
            retrieve=PhaseQuality.BAD,
            consume=PhaseQuality.GREAT,
        )
    )

    recall = Tool(
        name="Recall",
        organization_system=[OrganizationSystem.LINKS],
        phase_quality=PhaseQualityData(
            collect=PhaseQuality.GREAT,
            retrieve=PhaseQuality.GREAT,
            consume=PhaseQuality.NA,
            extract=PhaseQuality.NA,
            refine=PhaseQuality.GREAT
        )
    )

    readwise = Tool(
        name="Readwise",
        organization_system=[OrganizationSystem.TAGS],
        phase_quality=PhaseQualityData(
            collect=PhaseQuality.NA,
            retrieve=PhaseQuality.OK,
            consume=PhaseQuality.NA,
            extract=PhaseQuality.GREAT,
            refine=PhaseQuality.OK
        )
    )

    obsidian = Tool(
        name="Obsidian",
        organization_system=[OrganizationSystem.JOHNNY_DECIMAL, OrganizationSystem.LINKS],
        phase_quality=PhaseQualityData(
            collect=PhaseQuality.NA,
            retrieve=PhaseQuality.OK,
            consume=PhaseQuality.OK,
            extract=PhaseQuality.GREAT,
            refine=PhaseQuality.GREAT
        )
    )

    librarything = Tool(
        name="LibraryThing",
        organization_system=[OrganizationSystem.TAGS],
        phase_quality=PhaseQualityData(
            collect=PhaseQuality.OK,
            retrieve=PhaseQuality.BAD,
            consume=PhaseQuality.NA,
            extract=PhaseQuality.NA,
            refine=PhaseQuality.NA
        )
    )

    snipd = Tool(
        name="Snipd",
        organization_system=[OrganizationSystem.FOLDERS],
        phase_quality=PhaseQualityData(
            collect=PhaseQuality.OK,
            retrieve=PhaseQuality.BAD,
            consume=PhaseQuality.GREAT,
            extract=PhaseQuality.NA,
            refine=PhaseQuality.NA
        )
    )

    neoreader = Tool(
        name="NeoReader",
        organization_system=[OrganizationSystem.FOLDERS],
        phase_quality=PhaseQualityData(
            collect=PhaseQuality.OK,
            retrieve=PhaseQuality.BAD,
            consume=PhaseQuality.GREAT,
            extract=PhaseQuality.NA,
            refine=PhaseQuality.NA
        )
    )

    youtube = Tool(
        name="YouTube",
        organization_system=[OrganizationSystem.FOLDERS],
        phase_quality=PhaseQualityData(
            collect=PhaseQuality.OK,
            retrieve=PhaseQuality.BAD,
            consume=PhaseQuality.OK,
            extract=PhaseQuality.NA,
            refine=PhaseQuality.NA
        )
    )


# %% ../nbs/01_create_instances.ipynb 12
def informationitems_from_code():
    """Create all InformationItem instances as defined in the code."""
    web_article_item = InformationItem(
        name="Web Article",
        info_type=InformationType.WEB_ARTICLE,
        method=PhaseMethodData(
            collect=Method.MANUAL
        ),
        toolflow=PhaseToolflowData(
            collect=("Reader", "Recall"),
            retrieve="Recall",
            consume="Reader"
        )
    )

    annotation_item = InformationItem(
        name="Annotation",
        info_type=InformationType.ANNOTATION,
        method=PhaseMethodData(
            collect=Method.AUTOMATIC
        ),
        toolflow=PhaseToolflowData(
            extract="Readwise",
            refine=("Recall", "Obsidian")
        )
    )

    note_item = InformationItem(
        name="Note",
        info_type=InformationType.NOTE,
        method=PhaseMethodData(
            collect=Method.MANUAL
        ),
        toolflow=PhaseToolflowData(
            retrieve="Obsidian",
            consume="Obsidian",
            extract="Obsidian",
            refine="Obsidian"
        )
    )

    book_item = InformationItem(
        name="Book",
        info_type=InformationType.BOOK,
        method=PhaseMethodData(
            collect=Method.MANUAL
        ),
        toolflow=PhaseToolflowData(
            collect="LibraryThing",
            retrieve="LibraryThing",
            consume="NeoReader",
            extract="Readwise",
            refine="Obsidian"
        )
    )

    podcast_item = InformationItem(
        name="Podcast",
        info_type=InformationType.PODCAST,
        method=PhaseMethodData(
            collect=Method.AUTOMATIC
        ),
        toolflow=PhaseToolflowData(
            collect="Snipd",
            retrieve="Snipd",
            consume="Snipd",
            extract="Readwise",
            refine="Obsidian"
        )
    )

    research_paper_item = InformationItem(
        name="Research Paper",
        info_type=InformationType.RESEARCH_PAPER,
        method=PhaseMethodData(
            collect=Method.MANUAL
        ),
        toolflow=PhaseToolflowData(
            collect=("Recall", "NeoReader"),
            retrieve=("Recall", "NeoReader"),
            consume="NeoReader",
            extract="Readwise",
            refine=("Obsidian", "Recall")
        )
    )

    document_item = InformationItem(
        name="Document",
        info_type=InformationType.DOCUMENT,
        method=PhaseMethodData(
            collect=Method.MANUAL
        ),
        toolflow=PhaseToolflowData(
            collect="NeoReader",
            retrieve="NeoReader",
            consume="NeoReader",
            extract="Readwise",
            refine=("Obsidian", "Recall")
        )
    )

    youtube_video_item = InformationItem(
        name="YouTube Video",
        info_type=InformationType.YOUTUBE_VIDEO,
        method=PhaseMethodData(
            collect=Method.AUTOMATIC
        ),
        toolflow=PhaseToolflowData(
            collect="YouTube",
            retrieve="YouTube",
            consume="YouTube",
            extract="Obsidian",
            refine="Obsidian"
        )
    )

db = create_db(":memory:")
tools_tbl, inf_tbl, imp_tbl = create_tables_from_pydantic(db)

tool_inst = tools_from_code()
inf_inst = informationitems_from_code()

def get_info_items_for_tool(tool_name: str, info_items: dict[InformationItem]) -> dict[InformationItem]:
    """Filters all the instances of the class InformationItem based on which information items can be processed by the given tool."""
    if isinstance(info_items, dict): info_items = info_items.values()
    phases = ['collect', 'retrieve', 'consume', 'extract', 'refine']
    tool_name = tool_name.lower()
    
    res = {}
    for i in info_items:
        tf = getattr(i, 'toolflow', None)
        if tf is None: continue
        for ph in phases:
            ts = getattr(tf, ph, None)
            if ts is None: continue
            if isinstance(ts, (list, tuple)):
                if tool_name in ts: res[i.name] = i; break
            elif ts == tool_name:
                res[i.name] = i; break
    
    return res

# %% ../nbs/02_create_vizualisation.ipynb 17
# New function based on updated dataclasses
def build_graphiz_from_intances(info_items, tools) -> graphviz.graphs.Digraph:
    """Create a graphviz visualisation using the updated dataclasses for InformationItem and Tool.
    Produces the same layout as build_graphiz_from_instances.
    """
    if isinstance(info_items, dict): info_items = list(info_items.values())
    elif not isinstance(info_items, list): info_items = [info_items]
    if isinstance(tools, dict): tools = list(tools.values())

    dot = graphviz.Digraph(comment='PKM Workflow')
    dot.attr(rankdir='TB')

    phases = ['collect', 'retrieve', 'consume', 'extract', 'refine']
    all_nodes = set()
    edges = {}

    quality_colors = {PhaseQuality.GREAT: 'lightgreen', PhaseQuality.OK: 'lightblue', PhaseQuality.BAD: 'orange', PhaseQuality.NA: 'lightgray'}

    # Create tool nodes per phase
    for phase in phases:
        with dot.subgraph() as s:
            s.attr(rank='same')
            for info_item in info_items:
                tool_entry = getattr(getattr(info_item, 'toolflow', None), phase, None)
                if tool_entry is None: continue
                tools_in_phase = tool_entry if isinstance(tool_entry, (tuple)) else (tool_entry,)
                for tool_slug in tools_in_phase:
                    if tool_slug is None: continue
                    node_id = f"{tool_slug}_{phase}"
                    if node_id in all_nodes: continue
                    tool = next((t for t in tools if getattr(t, 'slug', None) == tool_slug), None)
                    q = getattr(getattr(tool, 'phase_quality', None), phase, PhaseQuality.NA) if tool else PhaseQuality.NA
                    color = quality_colors.get(q, 'white')
                    s.node(node_id, f"{tool_slug}\n({phase})", shape='hexagon', fillcolor=color, style='filled')
                    all_nodes.add(node_id)

    # Create source nodes for each InformationItem type (label with item.name, id by info_type)
    with dot.subgraph() as s:
        s.attr(rank='same')
        for info_item in info_items:
            it = getattr(info_item, 'info_type', None)
            val = it.value if hasattr(it, 'value') else str(it)
            source_id = f"source_{val}"
            s.node(source_id, getattr(info_item, 'name', (val or '').replace('_', ' ').title()), shape='box')

    # Connect edges along the flow
    for info_item in info_items:
        it = getattr(info_item, 'info_type', None)
        val = it.value if hasattr(it, 'value') else str(it)
        source_id = f"source_{val}"
        prev_nodes = [source_id]
        for phase in phases:
            tool_entry = getattr(getattr(info_item, 'toolflow', None), phase, None)
            if tool_entry is None: continue
            curr_nodes = []
            tools_in_phase = tool_entry if isinstance(tool_entry, (list, tuple)) else (tool_entry,)
            for tool_name in tools_in_phase:
                if tool_name is None: continue
                node_id = f"{str(tool_name).lower()}_{phase}"
                curr_nodes.append(node_id)
                for prev in prev_nodes:
                    key = (prev, node_id)
                    if key in edges: continue
                    dot.edge(prev, node_id)
                    edges[key] = True
            if curr_nodes: prev_nodes = curr_nodes

    return dot

# %% ../nbs/02_create_vizualisation.ipynb 18
def create_workflow_viz(items: None | InformationItem | dict[str, InformationItem] = None,
                        tools: None | Tool | dict[str, Tool] =None,
                        tool_filter: None | str = None) -> graphviz.graphs.Digraph:
    """Create workflow visualization with flexible filtering options."""
    # Default to all items and tools if none specified
    if items is None: items = InformationItem.get_instances()
    if tools is None: tools = Tool.get_instances()
    
    # Filter by tool if specified
    if tool_filter:
        items = get_info_items_for_tool(tool_filter, items)
    
    return build_graphiz_from_intances(items, tools)

for tool in Tool.get_instances().values(): db.t.tools.insert(tool.flatten_for_db())
for item in InformationItem.get_instances().values(): db.t.information_items.insert(item.flatten_for_db())

from fasthtml.common import *
from fasthtml.jupyter import *
from monsterui.all import *

def dict_svgnodes(svg_str: str):
   # Remove all xmlns declarations to get rid of namespace declaration when using .findall
   cln_svg = re.sub(r'xmlns[^=]*="[^"]*"', '', svg_str)
   root = ET.fromstring(cln_svg)

   nodes = {}

   for g in root.findall(".//g[@class='node']"):
      nte = g.find('title')
      nt = nte.text if nte is not None else None
      ni = g.get('id')
      nc = g.get('class')

      # I assume every element only has one polygon
      nfc = g.find('polygon').get('fill')
      nsc = g.find('polygon').get('stroke')

      # Text can have multiple lines
      nts = [t.text for t in g.findall('text')]
    
      nodes[nt] = {
         'id': ni,
         'class': nc,
         'fill': nfc,
         'stroke': nsc,
         'text': nts
         }

   return nodes

# %% ../nbs/03_create_webapp.ipynb 21
def add_onclick_to_nodes(svg_str: str):
    # Get node information
    nodes = dict_svgnodes(svg_str)
    
    # Add onclick to each Tool-node's <g> element
    for n, d in nodes.items():
        if d['fill'] != 'none': # Skipp all info-items
            node_id = d['id']
            tool_phase = n.split('_')
            tool = ossys.sanitize_name(tool_phase[0])
            phase = ossys.sanitize_name(tool_phase[1])
            onclick_attr = f'onclick="htmx.ajax(\'GET\', \'/toolphase?tool={tool}&phase={phase}\', {{target: \'#infoflow-graph\', swap: \'outerHTML\'}})"'
        
        # Replace the <g> tag to add onclick
        old_pattern = f'<g id="{node_id}" class="node">'
        new_pattern = f'<g id="{node_id}" class="node" {onclick_attr}>'
        svg_str = svg_str.replace(old_pattern, new_pattern)
    
    return svg_str

def add_onclick_to_nodes(svg_str: str):
    nodes = dict_svgnodes(svg_str)
    
    for n, d in nodes.items():
        node_id = d['id']
        if d['fill'] != 'none':
            tool_name = n.split('_')[0]
            tool_slug = ossys.sanitize_name(tool_name)
            onclick_attr = f'onclick="htmx.ajax(\'GET\', \'/tool?slug={tool_slug}\', {{target: \'body\', swap: \'innerHTML\'}})"'
        else:
            item_name = ' '.join(d['text'])
            item_slug = ossys.sanitize_name(item_name)
            onclick_attr = f'onclick="htmx.ajax(\'GET\', \'/item?slug={item_slug}\', {{target: \'body\', swap: \'innerHTML\'}})"'
        
        old_pattern = f'<g id="{node_id}" class="node">'
        new_pattern = f'<g id="{node_id}" class="node" {onclick_attr} style="cursor:pointer;">'
        svg_str = svg_str.replace(old_pattern, new_pattern)
    
    return svg_str

app, rt = fast_app(
    hdrs=[
        Style(".node { cursor: pointer; }"),
        Theme.blue.headers(),
    ],
    pico=False
)

@rt
def index():
    viz = create_workflow_viz()
    svg_str = viz._repr_image_svg_xml()
    interactive_svg = add_onclick_to_nodes(svg_str)
    
    return Div(
        H1("Information Flow Dashboard", style="text-align:center; margin:20px;"),
        Div(NotStr(interactive_svg), id="infoflow-graph", style="text-align:center; margin:20px;")
    )

@rt
def tool(slug: str):
    tool_row = db.t.tools[slug]
    tool = Tool.from_db(tool_row)
    
    tool_viz = create_workflow_viz(tool_filter=slug)
    svg_str = tool_viz._repr_image_svg_xml()
    svg_str = add_onclick_to_nodes(svg_str)
    
    return Titled(f"Tool: {tool.name}",
        DivFullySpaced(
            Button("← Back to Index", hx_get="/", hx_target="body", hx_swap="innerHTML"),
            Button("Edit", hx_get=f"/tool_edit?slug={slug}", hx_target="body", hx_swap="innerHTML"),
            cls="uk-margin-bottom"
        ),
        DivLAligned(
            Card(
                H3("Workflow Visualization"),
                Div(NotStr(svg_str), style="text-align:center;"),
                style="width:45%; margin-right:20px;"
            ),
            Card(
                H3("Tool Details"),
                DivVStacked(
                    P(Strong("Name: "), tool.name),
                    P(Strong("Organization System: "), ", ".join([org.value for org in tool.organization_system])),
                    Hr(),
                    H4("Phase Quality"),
                    *[P(Strong(f"{phase.title()}: "), getattr(tool.phase_quality, phase).value.title()) for phase in ["collect", "retrieve", "consume", "extract", "refine"]],
                    Hr(),
                    H4("Phase Descriptions"),
                    *[Div(Strong(f"{phase.title()}: "), P(getattr(tool, phase) or "Not specified")) for phase in ["collect", "retrieve", "consume", "extract", "refine"] if getattr(tool, phase)],
                    cls="space-y-2"
                ),
                style="width:55%;"
            ),
            style="display:flex; align-items:flex-start;"
        )
    )

@rt
def tool_edit(slug: str):
    tool_row = db.t.tools[slug]
    tool = Tool.from_db(tool_row)
    
    phase_selects = []
    for phase in ["collect", "retrieve", "consume", "extract", "refine"]:
        options = [Option(q.value.title(), value=q.value, selected=(q.value==getattr(tool.phase_quality, phase).value)) for q in PhaseQuality]
        phase_selects.append(LabelSelect(*options, label=f"{phase.title()}", name=f"{phase}_quality"))
    
    return Titled(f"Edit Tool: {tool.name}",
        DivFullySpaced(
            Button("← Back to Tool", hx_get=f"/tool?slug={slug}", hx_target="body", hx_swap="innerHTML"),
            cls="uk-margin-bottom"
        ),
        Card(
            H3("Edit Tool Details"),
            Form(
                LabelInput("Name", name="name", value=tool.name, required=True),
                DivVStacked(
                    Label("Organization System"),
                    *[LabelCheckboxX(org.value.replace("_", " ").title(), name="organization_system", value=org.value, checked=org in tool.organization_system) for org in OrganizationSystem],
                    cls="uk-margin-small"
                ),
                Hr(),
                H4("Single Phase Quality"),
                Grid(phase_selects[0]),
                Hr(),
                H4("Phase Quality"),
                DivHStacked(*phase_selects, cls="uk-margin-small"),
                Hr(),
                H4("Phase Descriptions"),
                DivVStacked(
                    *[LabelTextArea(f"{phase.title()}", name=phase, value=getattr(tool, phase) or "", placeholder=f"Description for {phase} phase") for phase in ["collect", "retrieve", "consume", "extract", "refine"]],
                    cls="uk-margin-small"
                ),
                DivLAligned(
                    Button("Save Changes", type="submit", cls=ButtonT.primary),
                    Button("Cancel", hx_get=f"/tool?slug={slug}", hx_target="body", hx_swap="innerHTML"),
                    cls="uk-margin-top"
                ),
                hx_post=f"/tool_save?slug={slug}",
                hx_target="body",
                hx_swap="innerHTML"
            )
        )
    )

@rt
async def tool_save(slug: str, req):
    form_data = await req.form()
    print(f"Form data: {dict(form_data)}")
    print(type(form_data))
    print(form_data.getlist("organization_system"))
    
    try:
        org_systems = [OrganizationSystem(val) for val in form_data.getlist("organization_system")]
        print(org_systems)
        phase_quality_data = {}
        for phase in ["collect", "retrieve", "consume", "extract", "refine"]:
            quality_val = form_data.get(f"{phase}_quality")
            if quality_val and quality_val.strip(): phase_quality_data[phase] = PhaseQuality(quality_val)
            else: phase_quality_data[phase] = PhaseQuality.NA
        
        phase_quality = PhaseQualityData(**phase_quality_data)

        print(phase_quality)
        
        updated_tool = Tool(
            name=form_data.get("name"),
            organization_system=org_systems,
            phase_quality=phase_quality,
            **{phase: form_data.get(phase) or None for phase in ["collect", "retrieve", "consume", "extract", "refine"]}
        )

        print(updated_tool)
        print(f"Flattened: {updated_tool.flatten_for_db()}")
        
        db.t.tools.update(updated_tool.flatten_for_db())
        return RedirectResponse(url=f"/tool?slug={updated_tool.slug}", status_code=303)
        
    except Exception as e:
        return Titled("Validation Error",
            Card(
                P(f"Error validating form data: {str(e)}"),
                Button("Back to Edit", hx_get=f"/tool_edit?slug={slug}", hx_target="body", hx_swap="innerHTML")
            )
        )

serve()
# %%
