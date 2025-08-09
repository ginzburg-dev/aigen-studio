"""
Dear PyGui node editor (DPG >= 1.10)
- Boxes (nodes) with pins (attributes)
- Drag wires to connect
- Robust link callbacks (2-tuple or 3-tuple app_data)
- Run button (toy propagation)
- Save/Load graph to JSON with stable tags
"""
import json
import os
import itertools
import dearpygui.dearpygui as dpg

dpg.create_context()

# ---------- globals ----------
LINKS: list[tuple[str, str]] = []  # (src_attr_tag, dst_attr_tag)
EDITOR = None
NODE_SEQ = itertools.count(1)      # stable ids for tags


# ---------- helpers ----------
def rebuild_links_from_editor():
    """Rebuild LINKS from what's actually in the editor (slot=2 holds links)."""
    LINKS.clear()
    for link_id in dpg.get_item_children(EDITOR, 2) or []:
        cfg = dpg.get_item_configuration(link_id)
        src = cfg.get("attr_1")
        dst = cfg.get("attr_2")
        if src and dst:
            LINKS.append((src, dst))


def on_link(sender, app_data):
    """
    app_data can be:
      (src_attr, dst_attr)               -> we must create the link
      (link_id, src_attr, dst_attr)      -> editor already created it
    """
    if isinstance(app_data, (list, tuple)):
        if len(app_data) == 2:
            src, dst = app_data
            # Create link ourselves for this variant
            dpg.add_node_link(src, dst, parent=sender)
        # If len == 3, editor already added it — do nothing
    rebuild_links_from_editor()
    # print("LINKS:", LINKS)


def on_del_link(sender, app_data):
    """app_data is link_id that editor already deleted. Just resync."""
    rebuild_links_from_editor()
    # print("AFTER UNLINK:", LINKS)


def clear_graph():
    # delete links (slot=2) and nodes (slot=1)
    for child in (dpg.get_item_children(EDITOR, 2) or []):
        dpg.delete_item(child)
    for child in (dpg.get_item_children(EDITOR, 1) or []):
        dpg.delete_item(child)
    LINKS.clear()


# ---------- node factories (stable tags) ----------
def make_prompt_node(pos=(20, 30), preset_text="Sea + palms", tag=None):
    base = tag or f"node:{next(NODE_SEQ)}:prompt"
    with dpg.node(label="Prompt", parent=EDITOR, tag=base) as n:
        dpg.set_item_pos(n, pos)
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=f"{base}:out"):
            dpg.add_input_text(label="Prompt", default_value=preset_text, tag=f"{base}:prompt")
    return base


def make_plan_node(pos=(340, 30), tag=None):
    base = tag or f"node:{next(NODE_SEQ)}:plan"
    with dpg.node(label="Plan", parent=EDITOR, tag=base):
        dpg.set_item_pos(base, pos)
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=f"{base}:in"):
            dpg.add_text("plan input")
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=f"{base}:out"):
            dpg.add_text("plan:")
            dpg.add_text("", tag=f"{base}:plan_text")
    return base


def make_render_node(pos=(680, 30), tag=None):
    base = tag or f"node:{next(NODE_SEQ)}:render"
    with dpg.node(label="Render", parent=EDITOR, tag=base):
        dpg.set_item_pos(base, pos)
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=f"{base}:in"):
            dpg.add_text("image:")
            dpg.add_text("", tag=f"{base}:render_text")
    return base


# ---------- pipeline (toy) ----------
def run_pipeline():
    # Read any Prompt node text; propagate to Plan, fake Render output
    prompts = []
    for node in dpg.get_item_children(EDITOR, 1) or []:
        lbl = dpg.get_item_label(node)
        if lbl == "Prompt":
            txt = dpg.get_value(f"{node}:prompt")
            prompts.append(txt)

    txt = prompts[0] if prompts else ""
    for node in dpg.get_item_children(EDITOR, 1) or []:
        lbl = dpg.get_item_label(node)
        if lbl == "Plan":
            dpg.set_value(f"{node}:plan_text", f"plan: 64x64 pixel beach — {txt}")
        elif lbl == "Render":
            dpg.set_value(f"{node}:render_text", "image://1234.png")


# ---------- save/load ----------
def save_graph():
    rebuild_links_from_editor()
    data = {"nodes": [], "links": LINKS[:]}

    for node in dpg.get_item_children(EDITOR, 1) or []:
        label = dpg.get_item_label(node)
        pos = tuple(dpg.get_item_pos(node))
        entry = {"tag": node, "label": label, "pos": pos}
        # capture per-type fields
        if label == "Prompt" and dpg.does_item_exist(f"{node}:prompt"):
            entry["prompt"] = dpg.get_value(f"{node}:prompt")
        data["nodes"].append(entry)

    with open("graph.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Saved to graph.json")


def load_graph():
    if not os.path.exists("graph.json"):
        print("No graph.json found")
        return
    with open("graph.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    clear_graph()

    # Recreate nodes with SAME tags so saved links match
    for n in data.get("nodes", []):
        lbl = n["label"]
        pos = tuple(n.get("pos", (20, 30)))
        tag = n["tag"]
        if lbl == "Prompt":
            make_prompt_node(pos=pos, preset_text=n.get("prompt", "Sea + palms"), tag=tag)
        elif lbl == "Plan":
            make_plan_node(pos=pos, tag=tag)
        elif lbl == "Render":
            make_render_node(pos=pos, tag=tag)

    # Recreate links using saved attribute tags
    for src, dst in data.get("links", []):
        if dpg.does_item_exist(src) and dpg.does_item_exist(dst):
            dpg.add_node_link(src, dst, parent=EDITOR)

    rebuild_links_from_editor()
    print("Loaded graph.json")


# ---------- UI ----------
with dpg.window(label="Node Editor", width=1100, height=700):
    with dpg.group(horizontal=True):
        dpg.add_button(label="Run", callback=run_pipeline)
        dpg.add_button(label="Save", callback=save_graph)
        dpg.add_button(label="Load", callback=load_graph)

    dpg.add_spacer(height=6)
    EDITOR = dpg.add_node_editor(callback=on_link, delink_callback=on_del_link)

    # Starter graph
    p = make_prompt_node()
    pl = make_plan_node()
    r = make_render_node()
    # Optional prelink:
    # dpg.add_node_link(f"{p}:out", f"{pl}:in", parent=EDITOR)
    # dpg.add_node_link(f"{pl}:out", f"{r}:in", parent=EDITOR)
    rebuild_links_from_editor()

dpg.create_viewport(title="Aigen Node Graph GUI", width=1100, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
