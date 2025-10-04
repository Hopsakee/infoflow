from __future__ import annotations
import re
import json
import graphviz
import xml.etree.ElementTree as ET

from enum import Enum
from typing import Union, ClassVar

from pydantic import BaseModel, field_serializer, field_validator, Field, computed_field
from fastlite import *
from fastcore.test import *
from hopsa import ossys
from fasthtml.common import *
from monsterui.all import *

from infoflow.classdb import *
from infoflow.viz import *
from infoflow.webapp import *

db = create_db("data/infoflow.db")

app, rt = fast_app(
    hdrs=[
        Style(".node { cursor: pointer; }"),
        Theme.blue.headers(),
    ],
)

def WorkflowViz(
        items: InformationItem | dict[str, InformationItem] = None,
        tools: Tool | dict[str, Tool] = None,
        tool_filter: str = None,
    ):
    if items is None: items = dict_from_db(db.t.information_items, InformationItem)
    if tools is None: tools = dict_from_db(db.t.tools, Tool)
    viz = create_workflow_viz(items=items, tools=tools, tool_filter=tool_filter)
    svg_str = viz._repr_image_svg_xml()
    interactive_svg = add_onclick_to_nodes(svg_str)
    return Div(NotStr(interactive_svg), id="infoflow-graph", style="text-align:center; margin:20px;")

def format_toolflow(toolflow_val):
    if toolflow_val is None: return "Not specified"
    if isinstance(toolflow_val, (list, tuple)): return ", ".join(toolflow_val)
    return toolflow_val

top_nav = NavBar(
            Button("← Back to Index", hx_get="/", hx_target="body", hx_swap="innerHTML", cls=ButtonT.text),
            Button("Theme Switcher", hx_get="/theme_switcher", hx_target="#main-content", hx_swap="innerHTML", cls=ButtonT.text),
            brand=H2("Information Flow Dashboard"),
        )

@rt
def index():
    return Title("Information Flow Dashboard"), Container(
        top_nav,
        DivCentered(WorkflowViz(), id="main-content"),
    )

@rt
def theme_switcher():
    return ThemePicker()

@rt
def tool(slug: str):
    tool_dict = db.t.tools[slug]
    tool = Tool.from_db(tool_dict)
    
    return Titled(f"Tool: {tool.name}",
        DivFullySpaced(
            Card(
                H3("Workflow Visualization"),
                WorkflowViz(tool_filter=slug),
                style="margin-right:20px;"
            ),
            Card(
                DivFullySpaced(
                    H3("Tool Details"),
                    Button("Edit", hx_get=f"/tool_edit?slug={slug}", hx_target="#main-content", hx_swap="innerHTML"),
                ),
                DivVStacked(
                    P(Strong("Name: "), tool.name),
                    P(Strong("Organization System: "), ", ".join([org.value for org in tool.organization_system])),
                    Hr(),
                    H4("Phase Quality"),
                    *[P(Strong(f"{phase.title()}: "), getattr(tool.phase_quality, phase).value.title()) for phase in ["collect", "retrieve", "consume", "extract", "refine"]],
                    Hr(),
                    H4("Phase Descriptions"),
                    *[Div(Strong(f"{phase.title()}: "), P(getattr(tool, phase) or "Not specified")) for phase in ["collect", "retrieve", "consume", "extract", "refine"] if getattr(tool, phase)],
                    cls="space-y-2", style="align-items:flex-start;"
                ),
            ),
            style="display:flex; align-items:flex-start;"
        ),
        id="main-content"
    )

@rt
def tool_edit(slug: str):
    tool_row = db.t.tools[slug]
    tool = Tool.from_db(tool_row)
    
    phase_selects = []
    for phase in ["collect", "retrieve", "consume", "extract", "refine"]:
        options = [Option(q.value.title(), value=q.value, selected=(q.value==getattr(tool.phase_quality, phase).value)) for q in PhaseQuality]
        phase_selects.append(LabelSelect(*options, label=f"{phase.title()}", name=f"{phase}_quality", cls="min-w-40"))
    
    return Titled(f"Edit Tool: {tool.name}",
        DivFullySpaced(
            Button("← Back to Tool", hx_get=f"/tool?slug={slug}", hx_target="#main-content", hx_swap="innerHTML"),
            cls="uk-margin-bottom"
        ),
        Card(
            H3("Edit Tool Details"),
            Form(
                H4("Name"),
                LabelInput("", name="name", value=tool.name, required=True),
                Hr(),
                H4("Organization System"),
                DivHStacked(
                    *[LabelCheckboxX(org.value.replace("_", " ").title(), name="organization_system", value=org.value, checked=org in tool.organization_system) for org in OrganizationSystem],
                    cls="space-x-4"
                ),
                Hr(),
                H4("Phase Quality"),
                DivHStacked(*phase_selects, cls="uk-margin-small"),
                Hr(),
                H4("Phase Descriptions"),
                DivVStacked(
                    *[LabelTextArea(f"{phase.title()}", name=phase, value=getattr(tool, phase) or "", placeholder=f"Description for {phase} phase", cls="w-full") for phase in ["collect", "retrieve", "consume", "extract", "refine"]],
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
        ),
        id="main-content"
    )

@rt
async def tool_save(slug: str, req):
    form_data = await req.form()
    
    try:
        org_systems = [OrganizationSystem(val) for val in form_data.getlist("organization_system")]
        phase_quality_data = {}
        for phase in ["collect", "retrieve", "consume", "extract", "refine"]:
            quality_val = form_data.get(f"{phase}_quality")
            if quality_val and quality_val.strip(): phase_quality_data[phase] = PhaseQuality(quality_val)
            else: phase_quality_data[phase] = PhaseQuality.NA
        
        phase_quality = PhaseQualityData(**phase_quality_data)

        updated_tool = Tool(
            name=form_data.get("name"),
            organization_system=org_systems,
            phase_quality=phase_quality,
            **{phase: form_data.get(phase) or None for phase in ["collect", "retrieve", "consume", "extract", "refine"]}
        )

        db.t.tools.update(updated_tool.flatten_for_db())
        return RedirectResponse(url=f"/tool?slug={updated_tool.slug}", status_code=303)
        
    except Exception as e:
        return Titled("Validation Error",
            Card(
                P(f"Error validating form data: {str(e)}"),
                Button("Back to Edit", hx_get=f"/tool_edit?slug={slug}", hx_target="body", hx_swap="innerHTML")
            )
        )
@rt
def resource(slug: str):
    item_dict = db.t.information_items[slug]
    item = InformationItem.from_db(item_dict)
    
    return Titled(f"Information Item: {item.name}",
        DivFullySpaced(
            Card(
                H3("Workflow Visualization"),
                WorkflowViz(items=item),
                style="margin-right:20px;"
            ),
            Card(
                DivFullySpaced(
                    H3("Information Item Details"),
                    Button("Edit", hx_get=f"/resource_edit?slug={slug}", hx_target="#main-content", hx_swap="innerHTML"),
                ),
                DivVStacked(
                    P(Strong("Name: "), item.name),
                    P(Strong("Information Type: "), item.info_type.value.replace("_", " ").title()),
                    Hr(),
                    H4("Phase Methods"),
                    *[P(Strong(f"{phase.title()}: "), getattr(item.method, phase).value.title() if getattr(item.method, phase) else "Not specified") for phase in ["collect", "retrieve", "consume", "extract", "refine"]],
                    Hr(),
                    H4("Phase Toolflow"),
                    *[P(Strong(f"{phase.title()}: "), format_toolflow(getattr(item.toolflow, phase))) for phase in ["collect", "retrieve", "consume", "extract", "refine"]],
                    cls="space-y-2", style="align-items:flex-start;"
                ),
            ),
            style="display:flex; align-items:flex-start;"
        ),
        id="main-content"
    )

@rt
def resource_edit(slug: str):
    item_row = db.t.information_items[slug]
    item = InformationItem.from_db(item_row)
    
    info_type_options = [Option(it.value.replace("_", " ").title(), value=it.value, selected=(it.value==item.info_type.value)) for it in InformationType]
    
    phase_method_selects = []
    for phase in ["collect", "retrieve", "consume", "extract", "refine"]:
        method_val = getattr(item.method, phase)
        options_val = [Option(m.value.title(), value=m.value, selected=(method_val and m.value==method_val.value)) for m in Method]
        phase_method_selects.append(LabelSelect(*options_val, label=f"{phase.title()}", name=f"{phase}_method", cls="min-w-40"))
    
    def toolflow_value(phase):
        val = getattr(item.toolflow, phase)
        if val is None: return ""
        if isinstance(val, (list, tuple)): return ", ".join(val)
        return val
    
    return Titled(f"Edit Information Item: {item.name}",
        DivFullySpaced(
            Button("← Back to Item", hx_get=f"/resource?slug={slug}", hx_target="#main-content", hx_swap="innerHTML"),
            cls="uk-margin-bottom"
        ),
        Card(
            H3("Edit Information Item Details"),
            Form(
                H4("Name"),
                LabelInput("", name="name", value=item.name, required=True),
                Hr(),
                H4("Information Type"),
                LabelSelect(*info_type_options, label="Type", name="info_type", cls="min-w-40"),
                Hr(),
                H4("Phase Methods"),
                DivHStacked(*phase_method_selects, cls="uk-margin-small"),
                Hr(),
                H4("Phase Toolflow"),
                DivVStacked(
                    *[LabelInput(f"{phase.title()}", name=f"{phase}_toolflow", value=toolflow_value(phase), placeholder=f"Tool(s) for {phase} phase (comma-separated for multiple)", cls="w-full") for phase in ["collect", "retrieve", "consume", "extract", "refine"]],
                    cls="uk-margin-small"
                ),
                DivLAligned(
                    Button("Save Changes", type="submit", cls=ButtonT.primary),
                    Button("Cancel", hx_get=f"/resource?slug={slug}", hx_target="body", hx_swap="innerHTML"),
                    cls="uk-margin-top"
                ),
                hx_post=f"/resource_save?slug={slug}",
                hx_target="body",
                hx_swap="innerHTML"
            )
        ),
        id="main-content"
    )

@rt
async def resource_save(slug: str, req):
    form_data = await req.form()
    
    try:
        info_type = InformationType(form_data.get("info_type"))
        
        phase_method_data = {}
        for phase in ["collect", "retrieve", "consume", "extract", "refine"]:
            method_val = form_data.get(f"{phase}_method")
            print(form_data)
            print(method_val)
            if method_val: phase_method_data[phase] = Method(method_val)
            else: phase_method_data[phase] = None
        
        method = PhaseMethodData(**phase_method_data)
        
        phase_toolflow_data = {}
        for phase in ["collect", "retrieve", "consume", "extract", "refine"]:
            toolflow_val = form_data.get(f"{phase}_toolflow")
            if toolflow_val and toolflow_val.strip():
                if "," in toolflow_val: phase_toolflow_data[phase] = tuple([t.strip() for t in toolflow_val.split(",") if t.strip()])
                else: phase_toolflow_data[phase] = toolflow_val.strip()
            else: phase_toolflow_data[phase] = None
        
        toolflow = PhaseToolflowData(**phase_toolflow_data)
        
        updated_item = InformationItem(
            name=form_data.get("name"),
            info_type=info_type,
            method=method,
            toolflow=toolflow
        )
        
        db.t.information_items.update(updated_item.flatten_for_db())
        return RedirectResponse(url=f"/resource?slug={updated_item.slug}", status_code=303)
        
    except Exception as e:
        return Titled("Validation Error",
            Card(
                P(f"Error validating form data: {str(e)}"),
                Button("Back to Edit", hx_get=f"/resource_edit?slug={slug}", hx_target="body", hx_swap="innerHTML")
            )
        )

serve()