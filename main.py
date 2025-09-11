from fasthtml.common import *
from infoflow.webapp import *
from infoflow.creinst import *

TEMP_SVG = """\n<svg width="268pt" height="338pt"\n viewBox="0.00 0.00 267.84 338.16" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n<g id="graph0" class="graph" transform="scale(1 1) rotate(0) translate(4 334.16)">\n<title>%3</title>\n<polygon fill="white" stroke="transparent" points="-4,4 -4,-334.16 263.84,-334.16 263.84,4 -4,4"/>\n<!-- reader_collect -->\n<g id="node1" class="node" onclick="htmx.ajax(\'GET\', \'/reader_collect\', {target: \'#infoflow-graph\', swap: \'outerHTML\'})">\n<title>reader_collect</title>\n<polygon fill="lightgreen" stroke="black" points="120.76,-227.13 90.59,-258.19 30.25,-258.19 0.08,-227.13 30.25,-196.08 90.59,-196.08 120.76,-227.13"/>\n<text text-anchor="middle" x="60.42" y="-230.93" font-family="Times,serif" font-size="14.00">Reader</text>\n<text text-anchor="middle" x="60.42" y="-215.93" font-family="Times,serif" font-size="14.00">(collect)</text>\n</g>\n<!-- recall_retrieve -->\n<g id="node3" class="node" onclick="htmx.ajax(\'GET\', \'/recall_retrieve\', {target: \'#infoflow-graph\', swap: \'outerHTML\'})">\n<title>recall_retrieve</title>\n<polygon fill="lightgreen" stroke="black" points="198.09,-129.08 163.76,-160.13 95.08,-160.13 60.75,-129.08 95.08,-98.03 163.76,-98.03 198.09,-129.08"/>\n<text text-anchor="middle" x="129.42" y="-132.88" font-family="Times,serif" font-size="14.00">Recall</text>\n<text text-anchor="middle" x="129.42" y="-117.88" font-family="Times,serif" font-size="14.00">(retrieve)</text>\n</g>\n<!-- reader_collect&#45;&gt;recall_retrieve -->\n<g id="edge3" class="edge">\n<title>reader_collect&#45;&gt;recall_retrieve</title>\n<path fill="none" stroke="black" d="M82.06,-196.01C88.3,-187.33 95.18,-177.74 101.73,-168.63"/>\n<polygon fill="black" stroke="black" points="104.63,-170.6 107.62,-160.43 98.94,-166.51 104.63,-170.6"/>\n</g>\n<!-- recall_collect -->\n<g id="node2" class="node" onclick="htmx.ajax(\'GET\', \'/recall_collect\', {target: \'#infoflow-graph\', swap: \'outerHTML\'})">\n<title>recall_collect</title>\n<polygon fill="lightgreen" stroke="black" points="259.76,-227.13 229.59,-258.19 169.25,-258.19 139.08,-227.13 169.25,-196.08 229.59,-196.08 259.76,-227.13"/>\n<text text-anchor="middle" x="199.42" y="-230.93" font-family="Times,serif" font-size="14.00">Recall</text>\n<text text-anchor="middle" x="199.42" y="-215.93" font-family="Times,serif" font-size="14.00">(collect)</text>\n</g>\n<!-- recall_collect&#45;&gt;recall_retrieve -->\n<g id="edge4" class="edge">\n<title>recall_collect&#45;&gt;recall_retrieve</title>\n<path fill="none" stroke="black" d="M177.46,-196.01C171.14,-187.33 164.15,-177.74 157.51,-168.63"/>\n<polygon fill="black" stroke="black" points="160.26,-166.45 151.54,-160.43 154.6,-170.58 160.26,-166.45"/>\n</g>\n    </g>\n    </svg>"""

app, rt = fast_app(
    hdrs=[
        Style(".node { cursor: pointer; }")
    ]
)

@rt
def index():
    return (Title("This is how Jelle visualises his information flow"),
            Main(H1("This is how Jelle visualises his information flow"),
            Div(NotStr(TEMP_SVG), id="infoflow-graph")))

@rt
def toolphase(tool: str, phase: str):
    # Find the tool instance by name
    tool_obj = next((t for t in tools if t.name.lower() == tool.lower()), None)
    phase_obj = Phase(phase.upper())
    
    if tool_obj:
        return H1(f"{tool_obj.name} - {phase_obj.value}")
    else:
        return H1("Tool not found")

if __name__ == "__main__":
    serve()
