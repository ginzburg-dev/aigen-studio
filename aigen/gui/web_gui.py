import streamlit as st
from PIL import Image
import os

st.set_page_config(layout="wide")
st.title("Aigen Pipeline Manager")

# --------- SIDEBAR: PIPELINE STEPS CONTROL ---------
st.sidebar.header("Pipeline Steps")

pipeline_steps = [
    "1. Load Data",
    "2. Process Images",
    "3. Build Article",
    "4. Preview/Export"
]
selected_steps = st.sidebar.multiselect(
    "Select which steps to run (order matters):",
    pipeline_steps, default=pipeline_steps
)
st.sidebar.markdown("---")

# --------- INPUT SECTION: SELECT SOURCES ---------
st.header("Step 1: Load Data")

col1, col2 = st.columns(2)

with col1:
    image_folder = st.text_input("Input Images Folder", "input/images")
    images = []
    if os.path.isdir(image_folder):
        images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        st.markdown(f"**{len(images)} images loaded**")
        if images:
            st.image([os.path.join(image_folder, img) for img in images], width=100)
        else:
            st.info("No images found in folder.")
    else:
        st.warning("Image folder not found.")

with col2:
    article_file = st.text_input("Article File", "input/article.md")
    article_text = ""
    if os.path.exists(article_file):
        with open(article_file, "r") as f:
            article_text = f.read()
    article_text = st.text_area("Article text", value=article_text, height=200)

# --------- STEP 2: PROCESS IMAGES ---------
if "2. Process Images" in selected_steps:
    st.header("Step 2: Image Processing")
    resize_width = st.number_input("Resize Width (px)", min_value=0, value=800)
    resize_height = st.number_input("Resize Height (px)", min_value=0, value=600)
    watermark = st.text_input("Watermark Text", value="Aigen Tool")
    # Dummy preview: just show images + options
    st.markdown("*Images would be resized and watermarked here (demo).*")

# --------- STEP 3: BUILD ARTICLE ---------
if "3. Build Article" in selected_steps:
    st.header("Step 3: Article Builder")
    st.markdown("**Image Placement:**")
    if images:
        img_to_place = st.selectbox("Choose image to insert", ["(None)"] + images)
        if img_to_place != "(None)":
            insert_at = st.number_input("Insert after paragraph #", min_value=1, value=1)
            caption = st.text_input("Caption for image", value="")
            if st.button("Insert Image"):
                # Not persistent demo, just info
                st.success(f"Would insert {img_to_place} after paragraph {insert_at} with caption '{caption}'.")
    # Instructions (edit YAML as text, or add form/GUI later)
    st.text_area("Instructions YAML", value="", height=100)

# --------- STEP 4: PREVIEW/EXPORT ---------
if "4. Preview/Export" in selected_steps:
    st.header("Step 4: Preview & Export")
    st.markdown("**Live Article Preview**")
    # Replace line breaks and show as simple HTML (demo)
    html_text = article_text.replace('\n', '<br>')
    st.markdown(f"<div style='background:#f9f9f9;padding:10px'>{html_text}</div>", unsafe_allow_html=True)
    # Show dummy export/log actions
    if st.button("Run Full Pipeline"):
        st.success("Pipeline executed (demo).")
    if st.button("Export to HTML"):
        st.success("Exported to HTML (demo).")

    # Show dummy logs/output
    st.markdown("**Pipeline Log:**")
    st.code("Loaded 3 images.\nResized and watermarked.\nImages placed in article.\nExported HTML.")

# --------- OPTIONAL: AI (CAPTION/REWRITE) ---------
st.sidebar.markdown("---")
st.sidebar.header("AI-powered Tools (Demo)")

if st.sidebar.button("Auto-generate Caption for Selected Image"):
    st.sidebar.info("Generated: 'Surreal ArtCabbage composition by Jane Doe.'")

if st.sidebar.button("Rewrite Article (AI Demo)"):
    st.sidebar.info("Rewritten article text (dummy).")

# --------- FOOTER ---------
st.markdown(
    """
    <hr>
    <small>
    Aigen Pipeline Manager &copy; 2025<br>
    <a href="https://github.com/your-repo" target="_blank">GitHub</a>
    </small>
    """,
    unsafe_allow_html=True
)

import streamlit as st

st.title("Aigen Visual Pipeline Editor")

if "pipeline" not in st.session_state:
    st.session_state.pipeline = [
        {"name": "Load Images", "params": {"folder": "input/images"}},
        {"name": "Process Images", "params": {"resize": (800,600)}},
        {"name": "Build Article", "params": {}},
        {"name": "Export HTML", "params": {"output": "output/article.html"}}
    ]

pipeline = st.session_state.pipeline

st.header("Pipeline Steps")
for i, step in enumerate(pipeline):
    st.subheader(f"Step {i+1}: {step['name']}")
    with st.expander("Parameters"):
        for k, v in step["params"].items():
            new_val = st.text_input(f"{step['name']} - {k}", value=str(v), key=f"{i}-{k}")
            step["params"][k] = new_val
    cols = st.columns([1,1,2,2])
    if cols[0].button("⬆️", key=f"up{i}") and i > 0:
        pipeline[i-1], pipeline[i] = pipeline[i], pipeline[i-1]
        st.experimental_rerun()
    if cols[1].button("⬇️", key=f"down{i}") and i < len(pipeline)-1:
        pipeline[i+1], pipeline[i] = pipeline[i], pipeline[i+1]
        st.experimental_rerun()
    if cols[2].button("❌ Remove", key=f"del{i}"):
        del pipeline[i]
        st.experimental_rerun()

# Add new step
with st.expander("➕ Add Step"):
    step_type = st.selectbox("Step Type", ["Load Images", "Process Images", "Build Article", "Export HTML"])
    add_params = st.text_area("Params (YAML or key:val per line)", "")
    if st.button("Add Step"):
        param_dict = {}
        for line in add_params.splitlines():
            if ":" in line:
                k,v = line.split(":",1)
                param_dict[k.strip()] = v.strip()
        pipeline.append({"name": step_type, "params": param_dict})
        st.experimental_rerun()

if st.button("Run Pipeline"):
    st.success(f"Pipeline would run now with steps: {[step['name'] for step in pipeline]}")
