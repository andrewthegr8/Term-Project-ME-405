"""
Generate finite state machine diagrams for the ME405 term project.

This script is called from Sphinx (see conf.py) and writes SVG files
into docs/source/_static/images.
"""

import os
from graphviz import Digraph

# Output directory for images
HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "_static", "images")
os.makedirs(OUT_DIR, exist_ok=True)


def make_talker_fsm():
    dot = Digraph("TalkerFSM")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")

    # States
    dot.node("S0", "State 0: \nListen / Transmit Packets")
    dot.node("S1", "State 1: \nParse command")

    # Transitions
    dot.edge(
        "S0", "S1",
        label="btcomm.check() = True"
    )
    dot.edge(
        "S1", "S0",
        label="Always"
    )

    dot.render(os.path.join(OUT_DIR, "talker_fsm"),
               format="svg", cleanup=True)


def make_linefollow_fsm():
    dot = Digraph("LineFollowFSM")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")

    # States
    dot.node("S0", "State 0: \nLine Follower Active")
    dot.node("S1", "State 1: \nLine Follower Stopped")

    # Transitions
    dot.edge(
        "S0", "S1",
        label="lf_stop.get() == 1/\n"
              "SENS_LED.value(0)"
    )

    dot.render(os.path.join(OUT_DIR, "linefollow_fsm"),
               format="svg", cleanup=True)


def make_pursuer_fsm():
    dot = Digraph("PursuerFSM")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")

    # States
    dot.node("S0", "State 0: \nLine Follow Mode \n(do nothing)")
    dot.node("S1", "State 1: \nPoint Pursuit Mode")

    # Transitions
    dot.edge(
        "S0", "S1",
        label="Past \"Y\"/ \n"
              "lf_stop.put(1)"
    )

    dot.render(os.path.join(OUT_DIR, "pursuer_fsm"),
               format="svg", cleanup=True)


def make_controller_fsm():
    dot = Digraph("ControllerFSM")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")

    # States
    dot.node("S0", "State 0: \n Initalize Timing \n(for integrators)")
    dot.node("S1", "State 1: \n Run Controllers")
    dot.node("S2", "State 2: \n Stop Robot")

    # Transitions
    dot.edge(
        "S0", "S1",
        label="Always"
    )
    dot.edge(
        "S1", "S2",
        label="velo_set.get() == 0.0\n/"
              "cmd_L,cmd_R = 0"
    )
    dot.edge(
        "S2", "S1",
        label="cmd = velo_set.get() != 0.0\n"
              "Reset integrators \n"
              "and encoders"
    )
    dot.render(os.path.join(OUT_DIR, "controller_fsm"),
               format="svg", cleanup=True)


def main():
    make_talker_fsm()
    make_linefollow_fsm()
    make_pursuer_fsm()
    make_controller_fsm()


if __name__ == "__main__":
    main()
