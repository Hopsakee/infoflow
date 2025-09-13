from fasthtml.common import *
from infoflow.clasdef import *
from infoflow.creinst import *
from infoflow.viz import *
from infoflow.webapp import *

app, rt = fast_app(
    hdrs=[
        Style(".node { cursor: pointer; }")
    ]
)

info_items = InformationItem.get_instances()
tools = Tool.get_instances()

@rt
def index():
    viz = create_combined_infoflow_viz(info_items, tools)
    viz_click = add_onclick_to_nodes(viz._repr_image_svg_xml())
    return (Title("This is how Jelle visualises his information flow"),
            Main(H1("This is how Jelle visualises his information flow"),
            Div(NotStr(viz_click), id="infoflow-graph")))

@rt
def toolphase(tool: str, phase: str):
    # Find the tool instance by name
    tool_obj = next((t for t in tools if t.name.lower() == tool.lower()), None)
    phase_obj = Phase(phase.lower())

    viz = create_combined_infoflow_viz(info_items, [tool_obj])
    viz_click = add_onclick_to_nodes(viz._repr_image_svg_xml())
    
    if tool_obj:
        return (Div(
            H1(f"{tool_obj.name} - {phase_obj.value}"),
            Div(NotStr(viz_click)), id="infoflow-graph"))
    else:
        return H1("Tool not found")

if __name__ == "__main__":
    serve()
