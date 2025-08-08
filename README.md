# aigen-studio

**Visual pipeline builder and automation platform for scalable, AI-driven content and image generation.**  
Easily automate batch article and visual workflows with GPT/AI using configurable instructions.

---

## About

**aigen-studio** is an open-source toolkit for building and running content and image generation pipelines at scale, powered by GPT and extensible with other AI models through its modular system.  
Create workflows through config files or an interactive interface, process large batches of articles and images, and customize every step with simple instructions.

---

## Features

- **Visual pipeline builder** – Compose and manage workflows for text and image generation.
- **Batch automation** – Process multiple articles and images in a single workflow.
- **AI-powered** – Integrates GPT/LLMs for text, captions, and metadata.
- **Flexible configuration** – YAML or JSON instructions, easy to adapt.
- **Python API** – Use aigen-studio as a library in your own projects.
- **Modular & extensible** – Add new pipeline steps, models, or processors as plugins.
- **Open-source** – Free to use, extend, and contribute.

---

## Quick Start

1. **Clone the repo and install requirements:**
   ```sh
   git clone https://github.com/yourusername/aigen-studio.git
   cd aigen-studio
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

---

## Runners

**aigen-studio** supports several ways to run pipelines:

- **CLI runner:**   
    `python -m aigen.cli.main --config config/instructions.yaml`

- **Python API:**  
    ```python
    from aigen.core.pipeline import Pipeline
    pipeline = Pipeline.from_config("config/instructions.yaml")
    pipeline.run()

- **Web GUI:**  
    `streamlit run aigen/gui/web_gui.py`

