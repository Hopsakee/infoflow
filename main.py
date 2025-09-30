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


@rt
def index():
    tools_dict = dict_from_db(db.t.tools, Tool)
    inf_dict = dict_from_db(db.t.information_items, InformationItem)
    viz = create_workflow_viz(items=inf_dict, tools=tools_dict)
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
    
    tools_dict = dict_from_db(db.t.tools, Tool)
    inf_dict = dict_from_db(db.t.information_items, InformationItem)
    tool_viz = create_workflow_viz(tool_filter=slug, items=inf_dict, tools=tools_dict)
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
                    cls="space-y-2", style="align-items:flex-start;"
                ),
                style="width:55%;"
            ),
            style="display:flex; align-items:flex-start;"
        ),
        id="infoflow-graph"
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
            Button("← Back to Tool", hx_get=f"/tool?slug={slug}", hx_target="body", hx_swap="innerHTML"),
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
        )
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

serve()