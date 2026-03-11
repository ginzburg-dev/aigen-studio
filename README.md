# aigen-studio

Config-driven AI content pipeline runner for repeatable generation and publishing workflows.

## Node-Based Pipeline

- Define ordered node steps in YAML (`SetVariable`, `GPTChat`, `WriteFile`, etc.).
- Feed article-level data from CSV rows into the same reusable pipeline.
- Generate drafts, metadata, SEO fields, and HTML fragments in one run.
- Render final HTML via template placeholders (`${var}`) from context.
- Save outputs as versioned artifacts (`aigen/v001`, `v002`, ...).

## Quick Start

```bash
uv sync --dev
```

Required tools:
- Python `>=3.10`
- [`uv`](https://docs.astral.sh/uv/)
- `dotenv`

Set env vars:

```bash
export OPENAI_API_KEY="..."
export CONFIGS_ROOT_DIR="/path/to/artcabbage-article-gen-configs"
# optional
export AIGEN_CACHE_DIR="/path/to/cache"
```

**Article Generator Command**

```bash
# Use Instructions column from CSV rows
dotenv run uv run aigen-article-generator path/to/csv.csv

# Use a default instructions file for rows that don't define Instructions
dotenv run uv run aigen-article-generator -i path/to/instructions.yaml path/to/csv.csv

# Same as above, long flag
dotenv run uv run aigen-article-generator --instructions path/to/instructions.yaml path/to/csv.csv
```

Run tests:

```bash
PYTHONPATH=src uv run pytest -q tests/unit
```

## Environment Variables

- `OPENAI_API_KEY`
  - Required for OpenAI/GPT nodes.
  - Default: empty.
- `CONFIGS_ROOT_DIR`
  - Optional.
  - Default: empty.
  - Used as root for relative config paths:
    - CLI `instructions` argument
    - CSV `Instructions`
    - CSV `Template` / `HTML Template`
- `AIGEN_CACHE_DIR`
  - Optional.
  - Default: system temp cache (`<tmp>/aigen_cache`).

## Pipeline Format

Pipelines are YAML lists of steps.

```yaml
- node: SetVariable
  params:
    name: greeting
    value: hello

- node: PrintVariable
  params:
    input: greeting
```

## Node Parameters (All Nodes)

### `SetVariable`
- `name` (required): context key to set.
- `value` (optional, default `""`): value to set.
- `if_missing` (optional, default `false`): if true, do not overwrite existing key.

```yaml
- node: SetVariable
  params:
    name: greeting
    value: "hello"
    if_missing: true
```

### `CopyVariable`
- `input` (required): source context key.
- `output` (required): target context key.

```yaml
- node: CopyVariable
  params:
    input: greeting
    output: greeting_copy
```

### `ReadFile`
- `file_path` or `filepath` (required): file path to read.
- `output` (required): context key to store file text.

```yaml
- node: ReadFile
  params:
    file_path: "./cache/input.txt"
    output: loaded_text
```

### `WriteFile`
- `file_path` (required): output file path.
- `input` (required): context key containing text to write.

```yaml
- node: WriteFile
  params:
    file_path: "./cache/output.txt"
    input: loaded_text
```

### `PrintVariable`
- `input` (required): context key to print.

```yaml
- node: PrintVariable
  params:
    input: greeting
```

### `GPTChat`
- `output` (required): context key for model response text.
- `prompt` (required): list of prompt items.
- `chat_history` (optional): context key or file path for chat history.
- `input` (optional): alias fallback for `chat_history`.
- `model` (optional): model name, e.g. `gpt-4o-mini`.
- `max_tokens` (optional): response max tokens.
- `temperature` (optional, default `0.7`): generation temperature.

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
    chat_history: article_workflow_history
    output: gpt_response
```

Prompt item formats:
- Text item:
  - `type: text`
  - `content: <string or [string,...]>`
- Image item:
  - `type: image`
  - `content: <path key/string or [path,...]>`
  - `detailed: <bool>` (optional, default `true`)

### `ParseJSON`
- `input` (required): context key containing JSON string.
- `output` (optional, default `<input>_obj`): context key for parsed dict.
- `normalize_keys` (optional, default `true`): normalize keys to snake_case.

```yaml
- node: ParseJSON
  params:
    input: article_meta_json
    output: article_meta_row
    normalize_keys: true
```

### `JsonToContext`
- `input` (required): context key containing a dict to merge into root context.

```yaml
- node: JsonToContext
  params:
    input: article_meta_row
```

### `ReplaceBetween`
- `input` (required): source template string key.
- `output` (optional, default same as `input`): output key.
- `start_marker` (required): marker text.
- `end_marker` (required): marker text.
- `replacement` (required): context key or raw text used as replacement block.

```yaml
- node: ReplaceBetween
  params:
    input: html_template
    output: article_html_with_fragment
    start_marker: "<!--Paste from here-->"
    end_marker: "<!--Paste to here-->"
    replacement: article_html_fragment
```

### `ResolveTemplateVars`
- `input` (required): template text key.
- `output` (required): rendered text key.
- `strict` (optional, default `false`): fail if unresolved `${var}` remains.

```yaml
- node: ResolveTemplateVars
  params:
    input: article_html_with_fragment
    output: article_html
    strict: true
```

## Usage Snippets

### 1) Variables + File IO

```yaml
- node: SetVariable
  params:
    name: source_text
    value: "hello from pipeline"

- node: WriteFile
  params:
    file_path: "./cache/example.txt"
    input: source_text

- node: ReadFile
  params:
    file_path: "./cache/example.txt"
    output: loaded_text

- node: PrintVariable
  params:
    input: loaded_text
```

### 2) GPTChat with `temperature`

```yaml
- node: SetVariable
  params:
    name: prompt_step_1
    value: "Describe this image in exactly 10 words."

- node: GPTChat
  params:
    model: gpt-4o-mini
    max_tokens: 120
    temperature: 0.3
    prompt:
      - type: text
        content: prompt_step_1
      - type: image
        content: images_path
        detailed: true
    chat_history: article_workflow_history
    output: gpt_response
```

### 3) Parse metadata JSON and expose keys to context

```yaml
- node: GPTChat
  params:
    model: gpt-4o-mini
    max_tokens: 500
    prompt:
      - type: text
        content: "Return JSON: {\"page_title\":\"...\",\"description\":\"...\"}"
    output: article_meta_json

- node: ParseJSON
  params:
    input: article_meta_json
    output: article_meta_row

- node: JsonToContext
  params:
    input: article_meta_row
```

### 4) Inject generated HTML fragment into template

```yaml
- node: ReadFile
  params:
    file_path: ${template_path}
    output: html_template

- node: ReplaceBetween
  params:
    input: html_template
    output: article_html_with_fragment
    start_marker: "<!--Paste from here-->"
    end_marker: "<!--Paste to here-->"
    replacement: article_html_fragment

- node: ResolveTemplateVars
  params:
    input: article_html_with_fragment
    output: article_html
    strict: true

- node: WriteFile
  params:
    file_path: ${html_output_path}
    input: article_html
```

## Registered Node Names

Use these exact `node:` values in YAML:

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

## CLI

Installed script:

- `aigen-article-generator`

Usage:

```bash
aigen-article-generator [--instructions <instructions.yaml>] <articles.csv>
aigen-article-generator path/to/csv.csv -i path/to/instructions.yaml

```
