# aigen-studio

Config-driven AI content pipeline runner for repeatable article generation and publishing workflows.

You define instructions (YAML steps) to run GPT-driven and rule-based processing in one pipeline: collect data, store it, reuse it, combine it, and generate final outputs.  
It is built for template-based article production, but the same flow works for any structured text publishing workflow.

## Why Use It

- Build an end-to-end pipeline for text operations.
- Find a specific section in a page/template.
- Copy or merge specific data into it.
- Replace strings/placeholders.
- Generate and format new content with LLM prompts.
- Generate and format SEO/indexing metadata with LLM prompts.
- Inject SEO/indexing metadata.

Use one run to move from source text/data to final HTML with all required markup.
Reduce routine editing work in high-volume publishing workflows.

Example workflow real case:
- Input: article source text + images
- Output: ready-to-publish article page (content + metadata + formatting) in minutes
- Typical impact for batch content teams: large throughput gains (for example, from `~3 to 27 of articles and marketing content per day`, depending on pipeline and review policy)

## What It Is

`aigen-studio` executes YAML pipelines over per-article CSV rows.

A single run can:
- read article config from CSV
- resolve images, templates, and instruction files
- call GPT nodes
- transform/merge structured data in context
- render HTML templates with `${var}` placeholders
- write versioned outputs to `aigen/v001`, `v002`, ... per article

## Requirements

- Python `>=3.10`
- [`uv`](https://docs.astral.sh/uv/)
- `dotenv` CLI (optional, only if you want `dotenv run ...`)

## Install

Install `uv` first (pick one):

```bash
# macOS
brew install uv

# Linux/macOS (official installer)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Optional: install `dotenv` CLI for `.env` execution:

```bash
uv tool install python-dotenv
```

If you skip this, run commands with `uv run ...` directly (without `dotenv run`).

```bash
# 1) clone
cd /path/to
git clone <your-repo-url> aigen-studio
cd aigen-studio

# 2) install deps (choose one)
uv sync --dev
# or
make install
```

## Environment Variables

Only these are used:

- `OPENAI_API_KEY` (required for `GPTChat`)
- `CONFIGS_ROOT_DIR` (optional)
- `AIGEN_CACHE_DIR` (optional)

Optional convenience: create a local `.env` from template:

```bash
make create-env-file
```

Example:

```bash
export OPENAI_API_KEY="sk-..."
# optional
export CONFIGS_ROOT_DIR="/absolute/path/to/configs"
export AIGEN_CACHE_DIR="/absolute/path/to/cache"
```

If you prefer `.env`:

```bash
# .env file in repo root
OPENAI_API_KEY=sk-...
CONFIGS_ROOT_DIR=/absolute/path/to/configs
AIGEN_CACHE_DIR=/absolute/path/to/cache
```

Load from `.env` (optional):

```bash
dotenv run -- uv run aigen-article-generator examples/article_generator/articles.csv
```

## CLI

Installed entrypoint:

- `aigen-article-generator`

Usage:

```bash
aigen-article-generator [--instructions <instructions.yaml>] <articles.csv>
```

Common forms:

```bash
# Per-row Instructions column in CSV
dotenv run uv run aigen-article-generator path/to/articles.csv

# Fallback instructions for rows that do not define Instructions
dotenv run uv run aigen-article-generator --instructions path/to/instructions.yaml path/to/articles.csv

# short flag
dotenv run uv run aigen-article-generator -i path/to/instructions.yaml path/to/articles.csv
```

Without `dotenv`:

```bash
uv run aigen-article-generator path/to/articles.csv
```

## Full Example: Generate One Article (Step-by-Step)

This repo includes a complete example in:
- `examples/article_generator/articles.csv`
- `examples/article_generator/example_instructions.yaml`
- `examples/article_generator/example_html_template.html`
- `examples/article_generator/article_example/images/`

### Step 1: set API key

```bash
export OPENAI_API_KEY="sk-..."
```

### Step 2: run the generator with the example CSV

```bash
uv run aigen-article-generator examples/article_generator/articles.csv
```

Or with `.env`:

```bash
dotenv run uv run aigen-article-generator examples/article_generator/articles.csv
```

### Step 3: inspect outputs

Each run creates the next version folder under article path:

```bash
ls -la examples/article_generator/article_example/aigen
```

Example output files:
- `examples/article_generator/article_example/aigen/v00X/article.html`
- `examples/article_generator/article_example/aigen/v00X/article_description.txt`

### Step 4: rerun safely

Run the same command again. A new folder (`v00X+1`) is created automatically.

## CSV Format

Current supported columns (header names are case/space/hyphen tolerant):

- `Article` (required): article directory path
- `Images`: image dir or image file path
- `HTML Template`: HTML template path
- `Instructions`: instructions YAML path
- `Section`
- `Article Section`
- `Author Name`
- `Author Type` (`Person` or `Organization`)
- `Cover Image URL`
- `Prompt Step 1`

Example row:

```csv
Article,Images,HTML Template,Instructions,Section,Article Section,Author Name,Author Type,Cover Image URL,Prompt Step 1
examples/article_generator/article_example,images,examples/article_generator/example_html_template.html,examples/article_generator/example_instructions.yaml,visual,Visual Art,Example Author,Person,https://example.com/cover.jpg,Describe these images as an art critic in 4 concise bullet points.
```

### Path Resolution Rules

- `Article` relative path:
  - use `CWD/<Article>` if exists
  - else use `<CSV_DIR>/<Article>` if exists
  - else default to `CWD/<Article>` (new dir creation case)
- `Images` relative path: checks CWD, article dir, then CSV dir
- `Instructions` and `HTML Template` relative path:
  - if `CONFIGS_ROOT_DIR` is set, resolved from it
  - otherwise resolved from CWD/article/csv depending on existence

## Pipeline Format

Pipelines are YAML lists of steps:

```yaml
- node: SetVariable
  params:
    name: greeting
    value: hello

- node: PrintVariable
  params:
    input: greeting
```

Variables can reference context values via `${var}` in string params.

## Node Reference

Use these exact node names:

- `SetVariable`
- `CopyVariable`
- `ReadFile`
- `WriteFile`
- `PrintVariable`
- `GPTChat`
- `ParseJSON`
- `JsonToContext`
- `ReplaceBetween`
- `ResolveTemplateVars`

### SetVariable

Params:
- `name` (required)
- `value` (optional, default `""`)
- `if_missing` (optional, default `false`)

```yaml
- node: SetVariable
  params:
    name: greeting
    value: "hello"
    if_missing: true
```

### CopyVariable

Params:
- `input` (required)
- `output` (required)

```yaml
- node: CopyVariable
  params:
    input: greeting
    output: greeting_copy
```

### ReadFile

Params:
- `file_path` or `filepath` (required)
- `output` (required)

```yaml
- node: ReadFile
  params:
    file_path: ./cache/input.txt
    output: loaded_text
```

### WriteFile

Params:
- `file_path` (required)
- `input` (required; key name in context)

```yaml
- node: WriteFile
  params:
    file_path: ./cache/output.txt
    input: loaded_text
```

### PrintVariable

Params:
- `input` (required)

```yaml
- node: PrintVariable
  params:
    input: loaded_text
```

### GPTChat

Params:
- `output` (required)
- `prompt` (required; list of prompt items)
- `model` (optional; e.g. `gpt-4o-mini`)
- `max_tokens` (optional)
- `temperature` (optional)
- `chat_history` (optional; context key or file path)
- `input` (optional alias fallback for `chat_history`)

Prompt item types:
- text:
  - `type: text`
  - `content: <string or [string,...]>`
- image:
  - `type: image`
  - `content: <path key/string or [path,...]>`
  - `detailed: <bool>` (optional; default `true`)

```yaml
- node: GPTChat
  params:
    model: gpt-4o-mini
    max_tokens: 300
    temperature: 0.3
    prompt:
      - type: text
        content: prompt_step_1
      - type: image
        content: images_path
        detailed: true
    output: gpt_response
```

### ParseJSON

Params:
- `input` (required)
- `output` (optional; default `<input>_obj`)
- `normalize_keys` (optional; default `true`)

```yaml
- node: ParseJSON
  params:
    input: article_meta_json
    output: article_meta_obj
```

### JsonToContext

Params:
- `input` (required; dict in context)

```yaml
- node: JsonToContext
  params:
    input: article_meta_obj
```

### ReplaceBetween

Params:
- `input` (required)
- `output` (optional; defaults to `input`)
- `start_marker` (required)
- `end_marker` (required)
- `replacement` (required; context key or raw text)

```yaml
- node: ReplaceBetween
  params:
    input: html_template_raw
    output: html_template_with_body
    start_marker: "<!-- ARTICLE_BODY_START -->"
    end_marker: "<!-- ARTICLE_BODY_END -->"
    replacement: article_draft_html
```

### ResolveTemplateVars

Params:
- `input` (required)
- `output` (required)
- `strict` (optional; default `false`)

```yaml
- node: ResolveTemplateVars
  params:
    input: html_template_with_body
    output: rendered_html
    strict: true
```

## Python API Usage

You can also run pipelines directly from Python:

```python
from aigen.common.file_handler import FileHandler
from aigen.common.pipeline import process_actions

context = {
    "name": "world",
}
instructions = FileHandler.read_yaml("examples/article_generator/example_instructions.yaml")
process_actions(context, instructions)
```

## Tests

```bash
# unit
PYTHONPATH=src uv run pytest -q tests/unit

# integration (if configured)
PYTHONPATH=src uv run pytest -s -m integration tests/integration
```

Or use make:

```bash
make unit-test
make integration-test
```
