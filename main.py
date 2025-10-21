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

[Tool.from_db(t) for t in db.t.tools()]

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

def _improvement_form_fields(imp=None, tool=None):
    """Build form fields for improvement (create or edit)"""
    all_tools = db.t.tools()
    tool_slug = imp.tool if imp else tool
    
    tool_options = [Option(t['name'], value=t['slug'], selected=t['slug']==tool_slug) for t in all_tools]
    phase_options = [Option(p.value.title(), value=p.value, selected=(imp and p.value==imp.phase.value)) for p in Phase]
    
    return (
        LabelInput("Title", name="title", value=imp.title if imp else "", required=True),
        LabelTextArea("What needs to be improved", name="what", value=imp.what if imp else "", required=True),
        LabelTextArea("Why is this improvement needed", name="why", value=imp.why if imp else "", required=True),
        LabelTextArea("How to build this improvement", name="how", value=imp.how if imp else "", required=True),
        LabelInput("Priority", name="prio", value=str(imp.prio) if imp else "1", type="number", required=True),
        LabelSelect(*tool_options, label="Tool", name="tool"),
        LabelSelect(*phase_options, label="Phase", name="phase"),
        LabelInput("ID", name="id", value=imp.id if imp else "", type="hidden"),
    )


async def _save_improvement(form_data, slug=None):
    """Save improvement (create new or update existing)"""
    imp_id = form_data.get("id")
    new_imp = Improvement(
        id=int(imp_id) if imp_id else None,
        title=form_data.get("title"),
        what=form_data.get("what"),
        why=form_data.get("why"),
        how=form_data.get("how"),
        prio=int(form_data.get("prio")),
        tool=form_data.get("tool"),
        phase=Phase(form_data.get("phase"))
    )
    
    if slug:
        db.t.improvements.update(new_imp.flatten_for_db())
    else:
        db.t.improvements.insert(new_imp.flatten_for_db())
    
    return new_imp

top_nav = NavBar(
            Button("← Back to Index", hx_get="/", hx_target="body", hx_swap="innerHTML", cls=ButtonT.text),
            Button("Improvements", hx_get="/all_tools_improvements", hx_target="#main-content", hx_swap="innerHTML", cls=ButtonT.text),
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
    tool_dict = db.t.tools("slug=?", (slug,))[0]
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
    tool_row = db.t.tools("slug=?", (slug,))[0]
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
                DivHStacked(
                    DivLAligned(
                        Button("Save Changes", type="submit", cls=ButtonT.primary),
                        Button("Cancel", hx_get=f"/tool?slug={slug}", hx_target="#main-content", hx_swap="innerHTML"),
                        cls="uk-margin-top"
                    ),
                    DivRAligned(
                        LabelInput(f"id: {tool.id}", name="id", value=tool.id, type="hidden"),
                        cls="uk-margin-top"
                    ),
                ),
                hx_post=f"/tool_save?slug={slug}",
                hx_target="#main-content",
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
            id=form_data.get("id"),
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
                Button("Back to Edit", hx_get=f"/tool_edit?slug={slug}", hx_target="#main-content", hx_swap="innerHTML")
            )
        )
@rt
def resource(slug: str):
    item_dict = db.t.information_items("slug=?", (slug,))[0]
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
                    Button("Edit", hx_get=f"/resource_edit?slug={item.slug}", hx_target="#main-content", hx_swap="innerHTML"),
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
    item_row = db.t.information_items("slug=?", (slug,))[0]
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
            Button("← Back to Item", hx_get=f"/resource?slug={item.slug}", hx_target="#main-content", hx_swap="innerHTML"),
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
                DivFullySpaced(
                    DivLAligned(
                        Button("Save Changes", type="submit", cls=ButtonT.primary),
                        Button("Cancel", hx_get=f"/resource?slug={item.slug}", hx_target="#main-content", hx_swap="innerHTML"),
                        cls="uk-margin-top"
                    ),
                    DivRAligned(
                        LabelInput(f"id: {item.id}", name="id", value=item.id, type="hidden"),
                        cls="uk-margin-top"
                    )
                ),
                hx_post=f"/resource_save?slug={item.slug}",
                hx_target="#main-content",
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
            id=form_data.get("id"),
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
                Button("Back to Edit", hx_get=f"/resource_edit?slug={slug}", hx_target="#main-content", hx_swap="innerHTML")
            )
        )

@rt
def all_tools_improvements():
    tools = db.t.tools()
    improvements = db.t.improvements()
    
    imp_by_tool = {}
    for imp in improvements:
        tool_slug = imp['tool']
        if tool_slug not in imp_by_tool: imp_by_tool[tool_slug] = []
        imp_by_tool[tool_slug].append(imp)
    
    tool_cards = []
    for tool in tools:
        tool_slug = tool['slug']
        tool_imps = sorted(imp_by_tool.get(tool_slug, []), key=lambda x: x['prio'])
        
        if tool_imps:
            imp_table = Table(
                    Thead(Tr(Th("Title"), Th("Priority", style="text-align:center"))),
                    Tbody(*[Tr(Td(imp['title']), Td(str(imp['prio']), style="text-align:center"), style="cursor:pointer;", hx_get=f"/improvement?slug={imp['slug']}", hx_target="#main-content", hx_swap="innerHTML") for imp in tool_imps])
            )
        else:
            imp_table = P("No improvements")
        
        tool_cards.append(
            Card(
                DivVStacked(
                    H3(tool['name'], style="cursor:pointer; text-align:center;", hx_get=f"/tool?slug={tool_slug}", hx_target="#main-content", hx_swap="innerHTML"),
                    imp_table,
                    Button("+ Add Improvement", hx_get=f"/improvement_add?tool={tool_slug}", hx_target="#main-content", hx_swap="innerHTML", cls=ButtonT.primary, style="margin-top:10px;"),
                    style="width:100%;"
                )
            )
        )
    
    return Titled("Improvements for every tool",
        Grid(*tool_cards, cols=3)
    )

@rt
def improvement(slug: str):
    imp_row = db.t.improvements("slug=?", (slug,))[0]
    imp = Improvement(**imp_row)
    
    prio_color = "#0066cc" if imp.prio == 1 else "#666666"
    
    return Titled(f"Improvement: {imp.title}",
        DivFullySpaced(
            Button("← Back to Tools List", hx_get="/all_tools_improvements", hx_target="#main-content", hx_swap="innerHTML"),
            Button("Edit", hx_get=f"/improvement_edit?slug={slug}", hx_target="#main-content", hx_swap="innerHTML"),
            cls="uk-margin-bottom"
        ),
        Card(
            DivVStacked(
                H2(imp.title, style="color:#0066cc;"),
                H4(f"Tool: {imp.tool.title()}", style="text-align:center; cursor:pointer;", hx_get=f"/tool?slug={imp.tool}", hx_target="#main-content", hx_swap="innerHTML"),
                Hr(),
                DivVStacked(
                    P(Strong("Priority: "), Span(str(imp.prio), style=f"background-color:{prio_color}; color:white; padding:4px 12px; border-radius:4px; font-weight:bold;")),
                    P(Strong("Phase: "), imp.phase.value.title()),
                    Hr(),
                    H4("What needs to be improved"),
                    P(imp.what),
                    Hr(),
                    H4("Why is this improvement needed"),
                    P(imp.why),
                    Hr(),
                    H4("How to build this improvement"),
                    P(imp.how),
                    I(f"id: {imp.id}"),
                    cls="space-y-3"
                ),
                style="width:100%;"
            )
        )
    )

@rt
def improvement_add(tool: str):
    return Titled("Add New Improvement",
        DivFullySpaced(
            Button("← Back to Tools List", hx_get="/all_tools_improvements", hx_target="#main-content", hx_swap="innerHTML"),
            cls="uk-margin-bottom"
        ),
        Card(
            H3("New Improvement Details"),
            Form(
                *_improvement_form_fields(tool=tool),
                DivLAligned(
                    Button("Create Improvement", type="submit", cls=ButtonT.primary),
                    Button("Cancel", hx_get="/all_tools_improvements", hx_target="#main-content", hx_swap="innerHTML"),
                    cls="uk-margin-top"
                ),
                hx_post="/improvement_create",
                hx_target="#main-content",
                hx_swap="innerHTML"
            )
        )
    )

@rt
def improvement_edit(slug: str):
    imp_row = db.t.improvements("slug=?", (slug,))[0]
    imp = Improvement(**imp_row)
    
    return Titled(f"Edit Improvement: {imp.title}",
        DivFullySpaced(
            Button("← Back to Improvement", hx_get=f"/improvement?slug={slug}", hx_target="#main-content", hx_swap="innerHTML"),
            cls="uk-margin-bottom"
        ),
        Card(
            H3("Edit Improvement Details"),
            Form(
                *_improvement_form_fields(imp=imp),
                DivLAligned(
                    Button("Save Changes", type="submit", cls=ButtonT.primary),
                    Button("Cancel", hx_get=f"/improvement?slug={slug}", hx_target="#main-content", hx_swap="innerHTML"),
                    cls="uk-margin-top"
                ),
                hx_post=f"/improvement_save?slug={slug}",
                hx_target="#main-content",
                hx_swap="innerHTML"
            )
        )
    )

@rt
async def improvement_create(req):
    form_data = await req.form()
    print(form_data)
    try:
        new_imp = await _save_improvement(form_data)
        return RedirectResponse(url=f"/improvement?slug={new_imp.slug}", status_code=303)
    except Exception as e:
        return Titled("Validation Error",
            Card(
                P(f"Error creating improvement: {str(e)}"),
                Button("Back", hx_get=f"/improvement_add?tool={form_data.get('tool')}", hx_target="#main-content", hx_swap="innerHTML")
            )
        )

@rt
async def improvement_save(slug: str, req):
    form_data = await req.form()
    print(form_data)
    try:
        updated_imp = await _save_improvement(form_data, slug=slug)
        return RedirectResponse(url=f"/improvement?slug={updated_imp.slug}", status_code=303)
    except Exception as e:
        return Titled("Validation Error",
            Card(
                P(f"Error validating form data: {str(e)}"),
                Button("Back to Edit", hx_get=f"/improvement_edit?slug={slug}", hx_target="#main-content", hx_swap="innerHTML")
            )
        )

serve()