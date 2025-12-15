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
    dot.node("S0", "Listen / TX")
    dot.node("S1", "Parse command")

    # Transitions
    dot.edge(
        "S0", "S1",
        label="btcomm.check()"
    )
    dot.edge(
        "S0", "S0",
        label="no command\n"
              "time_L,time_R\n"
              "pos_L,pos_R\n"
              "velo_L,velo_R\n"
              "cmd_L,cmd_R\n"
              "Eul_head,yaw_rate\n"
              "offset,X_pos,Y_pos\n"
              "p_v_R,p_v_L\n"
              "p_head,velo_set\n"
              "p_pos_L,p_pos_R"
    )
    dot.edge(
        "S1", "S0",
        label="rawcmd = btcomm.get_command()\n"
              "\"$SPD\"→velo_set\n"
              "\"$PNT\"→p_X,p_Y,p_head\n"
              "\"$WLL\"→wall"
    )

    dot.render(os.path.join(OUT_DIR, "talker_fsm"),
               format="svg", cleanup=True)


def make_linefollow_fsm():
    dot = Digraph("LineFollowFSM")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")

    # States
    dot.node("S0", "Active follow")
    dot.node("S1", "Follower stopped")

    # Transitions
    dot.edge(
        "S0", "S1",
        label="lf_stop.get() == 1\n"
              "SENS_LED.value(0)"
    )
    dot.edge(
        "S0", "S0",
        label="Line_sensor.read()\n"
              "Aixi_sum,Ai_sum,error\n"
              "kp_lf,ki_lf,esum\n"
              "velo_set,offset\n"
              "X_pos.view() bias\n"
              "SENS_LED.value(1)"
    )
    dot.edge(
        "S1", "S1",
        label="lf_stop.get() == 1\n"
              "SENS_LED.value(0)"
    )

    dot.render(os.path.join(OUT_DIR, "linefollow_fsm"),
               format="svg", cleanup=True)


def make_pursuer_fsm():
    dot = Digraph("PursuerFSM")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")

    # States
    dot.node("S0", "Line mode")
    dot.node("S1", "Pursue path")

    # Transitions
    dot.edge(
        "S0", "S1",
        label="p_X.view() >= 31.25\n"
              "lf_stop.put(1)"
    )
    dot.edge(
        "S0", "S0",
        label="p_X.view() < 31.25"
    )
    dot.edge(
        "S1", "S1",
        label="X_pos.view(),Y_pos.view()\n"
              "obst_sens,WALL_LED\n"
              "wall,wall_hit\n"
              "thepursuer.get_offset(\n"
              "  p_X,p_Y,p_head,wall)\n"
              "velo_set,offset"
    )

    dot.render(os.path.join(OUT_DIR, "pursuer_fsm"),
               format="svg", cleanup=True)


def make_controller_fsm():
    dot = Digraph("ControllerFSM")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")

    # States
    dot.node("S0", "Init timing")
    dot.node("S1", "Speed control")
    dot.node("S2", "Stopped hold")

    # Transitions
    dot.edge(
        "S0", "S1",
        label="l_ctrl.last_time = t_L\n"
              "r_ctrl.last_time = t_R"
    )
    dot.edge(
        "S1", "S2",
        label="cmd = velo_set.get() == 0.0\n"
              "leftmotor,rightmotor = 0\n"
              "cmd_L,cmd_R = 0"
    )
    dot.edge(
        "S1", "S1",
        label="cmd = velo_set.get() != 0.0\n"
              "off = offset.get()\n"
              "l_ctrl.get_ctrl_sig(\n"
              "  cmd+off,v_L,t_L)\n"
              "r_ctrl.get_ctrl_sig(\n"
              "  cmd-off,v_R,t_R)\n"
              "lastsig_L,lastsig_R\n"
              "MAXDELTA,cmd_L,cmd_R"
    )
    dot.edge(
        "S2", "S1",
        label="cmd = velo_set.get() != 0.0\n"
              "leftencoder.zero()\n"
              "rightencoder.zero()\n"
              "l_ctrl.reset(t_L)\n"
              "r_ctrl.reset(t_R)"
    )
    dot.edge(
        "S2", "S2",
        label="cmd = velo_set.get() == 0.0\n"
              "cmd_L,cmd_R = 0"
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
