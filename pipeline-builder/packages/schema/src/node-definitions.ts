import { z } from "zod";

export const portTypeSchema = z.enum(["text", "json", "any"]);
export type PortType = z.infer<typeof portTypeSchema>;

export const paramKindSchema = z.enum([
  "string",
  "text",
  "number",
  "boolean",
  "select",
  "json"
]);
export type ParamKind = z.infer<typeof paramKindSchema>;

export const nodeParamDefinitionSchema = z.object({
  key: z.string().min(1),
  label: z.string().min(1),
  kind: paramKindSchema,
  required: z.boolean().default(false),
  description: z.string().optional(),
  defaultValue: z.unknown().optional(),
  options: z.array(z.string().min(1)).optional()
});
export type NodeParamDefinition = z.infer<typeof nodeParamDefinitionSchema>;

export const portDefinitionSchema = z.object({
  key: z.string().min(1),
  label: z.string().min(1),
  type: portTypeSchema,
  required: z.boolean().default(true)
});
export type PortDefinition = z.infer<typeof portDefinitionSchema>;

export const bindingDefinitionSchema = z.object({
  portKey: z.string().min(1),
  paramKey: z.string().min(1)
});
export type BindingDefinition = z.infer<typeof bindingDefinitionSchema>;

export interface NodeDefinition {
  type: string;
  label: string;
  description: string;
  category: "input" | "transform" | "output" | "utility";
  inputPorts: PortDefinition[];
  outputPorts: PortDefinition[];
  inputBindings: BindingDefinition[];
  outputBindings: BindingDefinition[];
  params: NodeParamDefinition[];
  paramSchema: z.ZodObject<Record<string, z.ZodTypeAny>>;
}

function makeFieldSchema(definition: NodeParamDefinition): z.ZodTypeAny {
  let field: z.ZodTypeAny;

  switch (definition.kind) {
    case "string":
    case "text": {
      field = z.string();
      break;
    }
    case "number": {
      field = z.number();
      break;
    }
    case "boolean": {
      field = z.boolean();
      break;
    }
    case "json": {
      field = z.union([z.record(z.unknown()), z.array(z.unknown())]);
      break;
    }
    case "select": {
      if (!definition.options || definition.options.length === 0) {
        throw new Error(`Node param ${definition.key} requires at least one option`);
      }
      field = z.enum(definition.options as [string, ...string[]]);
      break;
    }
  }

  if (definition.required) {
    return field;
  }

  if (definition.defaultValue !== undefined) {
    return field.optional().default(definition.defaultValue);
  }

  return field.optional();
}

function makeParamSchema(params: NodeParamDefinition[]) {
  const shape: Record<string, z.ZodTypeAny> = {};
  for (const param of params) {
    shape[param.key] = makeFieldSchema(param);
  }

  return z.object(shape).strict();
}

const gptPromptItemSchema = z
  .object({
    type: z.enum(["text", "image"]),
    content: z.union([z.string(), z.array(z.string())]),
    detailed: z.boolean().optional()
  })
  .strict();

const definitions = [
  {
    type: "SetVariable",
    label: "Set Variable",
    description: "Set a context variable to a value.",
    category: "input",
    inputPorts: [],
    outputPorts: [{ key: "value", label: "Value", type: "any", required: true }],
    inputBindings: [],
    outputBindings: [{ portKey: "value", paramKey: "name" }],
    params: [
      {
        key: "name",
        label: "Variable Name",
        kind: "string",
        required: true,
        description: "Context variable key to set."
      },
      {
        key: "value",
        label: "Value",
        kind: "text",
        defaultValue: "",
        description: "Variable value. Supports ${var} templates."
      },
      {
        key: "if_missing",
        label: "Only If Missing",
        kind: "boolean",
        defaultValue: false,
        description: "Skip setting when variable already exists."
      }
    ]
  },
  {
    type: "CopyVariable",
    label: "Copy Variable",
    description: "Copy one context variable into another.",
    category: "transform",
    inputPorts: [{ key: "in", label: "Input", type: "any", required: true }],
    outputPorts: [{ key: "out", label: "Output", type: "any", required: true }],
    inputBindings: [{ portKey: "in", paramKey: "input" }],
    outputBindings: [{ portKey: "out", paramKey: "output" }],
    params: [
      {
        key: "input",
        label: "Input Variable",
        kind: "string",
        description: "Source context variable name."
      },
      {
        key: "output",
        label: "Output Variable",
        kind: "string",
        description: "Target context variable name."
      }
    ]
  },
  {
    type: "ReadFile",
    label: "Read File",
    description: "Read text file content into context.",
    category: "input",
    inputPorts: [],
    outputPorts: [{ key: "out", label: "Text", type: "text", required: true }],
    inputBindings: [],
    outputBindings: [{ portKey: "out", paramKey: "output" }],
    params: [
      {
        key: "filepath",
        label: "File Path",
        kind: "string",
        description: "Path to read. Alias of file_path."
      },
      {
        key: "file_path",
        label: "File Path (Alias)",
        kind: "string",
        description: "Optional alias. filepath is preferred."
      },
      {
        key: "output",
        label: "Output Variable",
        kind: "string",
        description: "Context variable to store file content."
      }
    ]
  },
  {
    type: "WriteFile",
    label: "Write File",
    description: "Write context text to a file.",
    category: "output",
    inputPorts: [{ key: "in", label: "Input", type: "any", required: true }],
    outputPorts: [],
    inputBindings: [{ portKey: "in", paramKey: "input" }],
    outputBindings: [],
    params: [
      {
        key: "file_path",
        label: "File Path",
        kind: "string",
        required: true,
        description: "Target file path."
      },
      {
        key: "input",
        label: "Input Variable",
        kind: "string",
        description: "Context variable to write."
      }
    ]
  },
  {
    type: "PrintVariable",
    label: "Print Variable",
    description: "Print a context variable to stdout.",
    category: "output",
    inputPorts: [{ key: "in", label: "Input", type: "any", required: true }],
    outputPorts: [],
    inputBindings: [{ portKey: "in", paramKey: "input" }],
    outputBindings: [],
    params: [
      {
        key: "input",
        label: "Input Variable",
        kind: "string",
        description: "Context variable to print."
      }
    ]
  },
  {
    type: "GPTChat",
    label: "GPT Chat",
    description: "Call OpenAI chat completion with text/image prompt items.",
    category: "transform",
    inputPorts: [{ key: "history_in", label: "History", type: "json", required: false }],
    outputPorts: [
      { key: "response", label: "Response", type: "text", required: true },
      { key: "history_out", label: "History", type: "json", required: false }
    ],
    inputBindings: [{ portKey: "history_in", paramKey: "chat_history" }],
    outputBindings: [
      { portKey: "response", paramKey: "output" },
      { portKey: "history_out", paramKey: "chat_history" }
    ],
    params: [
      {
        key: "model",
        label: "Model",
        kind: "string",
        defaultValue: "gpt-4o-mini",
        description: "OpenAI model name."
      },
      {
        key: "temperature",
        label: "Temperature",
        kind: "number",
        defaultValue: 0.2,
        description: "Sampling temperature."
      },
      {
        key: "max_tokens",
        label: "Max Tokens",
        kind: "number",
        defaultValue: 4096,
        description: "Token limit for completion."
      },
      {
        key: "prompt",
        label: "Prompt Items (JSON)",
        kind: "json",
        required: true,
        defaultValue: [
          {
            type: "text",
            content: "Describe the current context"
          }
        ],
        description: "Array of prompt objects. Example: [{type: 'text', content: 'hello'}]."
      },
      {
        key: "chat_history",
        label: "Chat History Key or File Path",
        kind: "string",
        description: "Context key or YAML file path for history."
      },
      {
        key: "output",
        label: "Output Variable",
        kind: "string",
        description: "Context variable for response text."
      }
    ]
  },
  {
    type: "ParseJSON",
    label: "Parse JSON",
    description: "Parse JSON text into an object variable.",
    category: "transform",
    inputPorts: [{ key: "in", label: "Input", type: "text", required: true }],
    outputPorts: [{ key: "out", label: "Object", type: "json", required: true }],
    inputBindings: [{ portKey: "in", paramKey: "input" }],
    outputBindings: [{ portKey: "out", paramKey: "output" }],
    params: [
      {
        key: "input",
        label: "Input Variable",
        kind: "string",
        description: "Context variable with JSON string."
      },
      {
        key: "output",
        label: "Output Variable",
        kind: "string",
        description: "Parsed object variable name."
      },
      {
        key: "normalize_keys",
        label: "Normalize Keys",
        kind: "boolean",
        defaultValue: true,
        description: "Normalize object keys to lowercase underscore format."
      }
    ]
  },
  {
    type: "JsonToContext",
    label: "JSON To Context",
    description: "Merge object variable fields into root context.",
    category: "transform",
    inputPorts: [{ key: "in", label: "Input", type: "json", required: true }],
    outputPorts: [],
    inputBindings: [{ portKey: "in", paramKey: "input" }],
    outputBindings: [],
    params: [
      {
        key: "input",
        label: "Input Variable",
        kind: "string",
        description: "Object variable to merge."
      }
    ]
  },
  {
    type: "ReplaceBetween",
    label: "Replace Between",
    description: "Replace text between two markers.",
    category: "transform",
    inputPorts: [
      { key: "template_in", label: "Template", type: "text", required: true },
      { key: "replacement_in", label: "Replacement", type: "any", required: true }
    ],
    outputPorts: [{ key: "out", label: "Output", type: "text", required: true }],
    inputBindings: [
      { portKey: "template_in", paramKey: "input" },
      { portKey: "replacement_in", paramKey: "replacement" }
    ],
    outputBindings: [{ portKey: "out", paramKey: "output" }],
    params: [
      {
        key: "input",
        label: "Input Variable",
        kind: "string",
        description: "Template text variable name."
      },
      {
        key: "output",
        label: "Output Variable",
        kind: "string",
        description: "Output variable name. Defaults to input when omitted."
      },
      {
        key: "start_marker",
        label: "Start Marker",
        kind: "string",
        required: true,
        description: "Marker where replacement starts."
      },
      {
        key: "end_marker",
        label: "End Marker",
        kind: "string",
        required: true,
        description: "Marker where replacement ends."
      },
      {
        key: "replacement",
        label: "Replacement Variable or Text",
        kind: "text",
        description: "Context key or literal replacement text."
      }
    ]
  },
  {
    type: "ResolveTemplateVars",
    label: "Resolve Template Vars",
    description: "Resolve ${var} placeholders in a template string.",
    category: "transform",
    inputPorts: [{ key: "in", label: "Input", type: "text", required: true }],
    outputPorts: [{ key: "out", label: "Output", type: "text", required: true }],
    inputBindings: [{ portKey: "in", paramKey: "input" }],
    outputBindings: [{ portKey: "out", paramKey: "output" }],
    params: [
      {
        key: "input",
        label: "Input Variable",
        kind: "string",
        description: "Template string variable."
      },
      {
        key: "output",
        label: "Output Variable",
        kind: "string",
        description: "Rendered output variable."
      },
      {
        key: "strict",
        label: "Strict",
        kind: "boolean",
        defaultValue: false,
        description: "Fail when unresolved placeholders remain."
      }
    ]
  }
] as const;

export const nodeDefinitions: NodeDefinition[] = definitions.map((definition) => {
  const parsedParams = z.array(nodeParamDefinitionSchema).parse(definition.params);
  const parsedInputs = z.array(portDefinitionSchema).parse(definition.inputPorts);
  const parsedOutputs = z.array(portDefinitionSchema).parse(definition.outputPorts);
  const parsedInputBindings = z.array(bindingDefinitionSchema).parse(definition.inputBindings);
  const parsedOutputBindings = z.array(bindingDefinitionSchema).parse(definition.outputBindings);

  const schema = makeParamSchema(parsedParams);

  const customSchema =
    definition.type === "GPTChat"
      ? schema.extend({ prompt: z.array(gptPromptItemSchema) })
      : schema;

  return {
    ...definition,
    inputPorts: parsedInputs,
    outputPorts: parsedOutputs,
    inputBindings: parsedInputBindings,
    outputBindings: parsedOutputBindings,
    params: parsedParams,
    paramSchema: customSchema
  };
});

export const nodeDefinitionByType = new Map(nodeDefinitions.map((definition) => [definition.type, definition]));

export type SerializableNodeDefinition = Omit<NodeDefinition, "paramSchema">;

export function serializeNodeDefinition(definition: NodeDefinition): SerializableNodeDefinition {
  const { paramSchema: _paramSchema, ...rest } = definition;
  return rest;
}

export function getSerializableNodeDefinitions(): SerializableNodeDefinition[] {
  return nodeDefinitions.map(serializeNodeDefinition);
}
