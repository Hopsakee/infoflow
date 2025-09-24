from fasthtml.common import *
import monsterui.all as mui
from infoflow.classdb import *
from infoflow.creinst import *
from infoflow.viz import *
from infoflow.webapp import *

from pydantic import BaseModel, ValidationError

from fh_pydantic_form import PydanticForm, list_manipulation_js

app, rt = fast_app(
    hdrs=[
        Style(".node { cursor: pointer; }"),
        mui.Theme.blue.headers(),
        list_manipulation_js(),
    ],
    pico=False
)

tools_from_code()
informationitems_from_code()
info_items = InformationItem.get_instances()
tools = Tool.get_instances()

class SimpleModel(BaseModel):
    """Model representing a simple form"""
    name: str = "Default Name"
    age: int
    is_active: bool = True

form_renderer = PydanticForm("my_form", Tool)
form_renderer.register_routes(app)

@rt
def index():
    viz = create_workflow_viz(info_items, tools)
    viz_click = add_onclick_to_nodes(viz._repr_image_svg_xml())
    return Div(Title("This is how Jelle visualises his information flow"),
           H1("This is how Jelle visualises his information flow"),
           Div(P("Go to test form", hx_get="testform", hx_target="#main-content", hx_swap="outerHTML", id="test-form"),
           Div(NotStr(viz_click), id="infoflow-graph")), id="main-content")
            # Div(NotStr(viz._repr_image_svg_xml()), id="infoflow-graph")))

@rt
def testform():
    return Div(
        P("This is the test form", hx_get="/", hx_swap="outerHTML", hx_target="#main-content"),
        Div(
            mui.Container(
                mui.Card(
                    mui.CardHeader("Simple Pydantic Form"),
                    mui.CardBody(
                        mui.Form(
                            form_renderer.render_inputs(),
                            Div(
                                mui.Button("Submit", type="submit", cls=mui.ButtonT.primary),
                                form_renderer.refresh_button("🔄"),
                                form_renderer.reset_button("↩️"),
                                cls="mt-4 flex items-center gap-2"
                            ),
                            hx_post="submit_form",
                            hx_swap="innerHTML",
                            hx_target="#result",
                            id=f"{form_renderer.name}-form"
                        )
                    ),
                ),
                Div(id="result"),
            )
        ),
        id="main-content")

@rt
async def submit_form(req):
    try:
        print(f"ik ben hier met {req}")
        validated_data: Tool = await form_renderer.model_validate_request(req)
        return mui.Card(
            mui.CardHeader(H3("Validation Succesful")),
            mui.CardBody(
                Pre(
                    validated_data.model_dump_json(indent=2),
                )
            ),
            cls="mt-4"
        )
    except ValidationError as e:
        return mui.Card(
            mui.CardHeader(H3("Validation Error", cls="text-red-500")),
            mui.CardBody(
                Pre(
                    e.json(indent=2),
                )
            ),
            cls="mt-4"
        )

@rt
def toolphase(tool: str, phase: str):
    # Find the tool instance by name
    tool_obj = tools[tool]
    phase_obj = Phase(phase.lower())

    viz = create_workflow_viz(info_items, tools, tool_filter=tool_obj.name)
    viz_click = add_onclick_to_nodes(viz._repr_image_svg_xml())
    
    if tool_obj:
        return (Div(
            H1(f"{tool_obj.name} - {phase_obj.value}"),
            Div(NotStr(viz_click)), id="infoflow-graph"))
    else:
        return H1("Tool not found")

if __name__ == "__main__":
    serve()
