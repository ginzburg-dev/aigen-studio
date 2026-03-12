import { z } from "zod";
import { nodeDefinitionByType } from "./node-definitions";

export const graphNodeSchema = z.object({
  id: z.string().min(1),
  type: z.string().min(1),
  params: z.record(z.unknown()).default({})
});
export type GraphNode = z.infer<typeof graphNodeSchema>;

export const graphEdgeSchema = z.object({
  id: z.string().min(1),
  fromNodeId: z.string().min(1),
  fromPort: z.string().min(1),
  toNodeId: z.string().min(1),
  toPort: z.string().min(1)
});
export type GraphEdge = z.infer<typeof graphEdgeSchema>;

export const graphSchema = z.object({
  nodes: z.array(graphNodeSchema),
  edges: z.array(graphEdgeSchema)
});
export type PipelineGraph = z.infer<typeof graphSchema>;

export interface GraphValidationIssue {
  code:
    | "GRAPH_SHAPE"
    | "DUPLICATE_NODE_ID"
    | "UNKNOWN_NODE_TYPE"
    | "INVALID_PARAMS"
    | "UNKNOWN_EDGE_NODE"
    | "UNKNOWN_EDGE_PORT"
    | "INCOMPATIBLE_PORT_TYPES"
    | "MULTIPLE_INPUT_CONNECTIONS"
    | "MISSING_REQUIRED_INPUT"
    | "GRAPH_CYCLE"
    | "ISOLATED_NODE";
  message: string;
  nodeId?: string;
  edgeId?: string;
  path?: string;
}

export interface GraphValidationResult {
  valid: boolean;
  errors: GraphValidationIssue[];
  warnings: GraphValidationIssue[];
}

export const compiledInstructionSchema = z
  .object({
    node: z.string().min(1),
    params: z.record(z.unknown()).default({})
  })
  .strict();
export type CompiledInstruction = z.infer<typeof compiledInstructionSchema>;

export const compiledInstructionListSchema = z.array(compiledInstructionSchema);
export type CompiledInstructionList = z.infer<typeof compiledInstructionListSchema>;

export interface PipelineInstructions {
  format: "aigen.instructions.v1";
  generatedAt: string;
  instructions: CompiledInstruction[];
}

function hasValue(value: unknown): boolean {
  if (value === null || value === undefined) {
    return false;
  }
  if (typeof value === "string") {
    return value.trim().length > 0;
  }
  return true;
}

function portSignature(nodeId: string, port: string) {
  return `${nodeId}:${port}`;
}

function sanitizeName(value: string): string {
  return value
    .trim()
    .replace(/[^a-zA-Z0-9_]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .toLowerCase();
}

function getDerivedOutputVariable(params: Record<string, unknown>, nodeType: string, portKey: string) {
  if (nodeType === "ReplaceBetween" && portKey === "out" && hasValue(params.input)) {
    return String(params.input);
  }

  if (nodeType === "ParseJSON" && portKey === "out" && hasValue(params.input)) {
    return `${String(params.input)}_obj`;
  }

  return undefined;
}

function resolveOutputVariable(opts: {
  nodeId: string;
  nodeType: string;
  portKey: string;
  paramKey: string;
  params: Record<string, unknown>;
  hasOutgoingConnection: boolean;
  allowAutoFallback: boolean;
}): string | undefined {
  const existing = opts.params[opts.paramKey];
  if (hasValue(existing)) {
    return String(existing);
  }

  const derived = getDerivedOutputVariable(opts.params, opts.nodeType, opts.portKey);
  if (derived) {
    return derived;
  }

  const skipOptionalHistoryOutput =
    opts.nodeType === "GPTChat" && opts.portKey === "history_out" && !opts.hasOutgoingConnection;

  if (skipOptionalHistoryOutput || !opts.allowAutoFallback) {
    return undefined;
  }

  return `${sanitizeName(opts.nodeId) || "node"}_${sanitizeName(opts.portKey) || "out"}`;
}

function runTopologicalSort(graph: PipelineGraph): { orderedNodeIds: string[]; hasCycle: boolean } {
  const adjacency = new Map<string, string[]>();
  const indegree = new Map<string, number>();

  for (const node of graph.nodes) {
    adjacency.set(node.id, []);
    indegree.set(node.id, 0);
  }

  for (const edge of graph.edges) {
    if (!adjacency.has(edge.fromNodeId) || !adjacency.has(edge.toNodeId)) {
      continue;
    }
    adjacency.get(edge.fromNodeId)?.push(edge.toNodeId);
    indegree.set(edge.toNodeId, (indegree.get(edge.toNodeId) ?? 0) + 1);
  }

  const queue: string[] = [];
  for (const [nodeId, value] of indegree) {
    if (value === 0) {
      queue.push(nodeId);
    }
  }

  const orderedNodeIds: string[] = [];

  while (queue.length > 0) {
    const current = queue.shift();
    if (!current) {
      continue;
    }

    orderedNodeIds.push(current);
    for (const neighbor of adjacency.get(current) ?? []) {
      const next = (indegree.get(neighbor) ?? 0) - 1;
      indegree.set(neighbor, next);
      if (next === 0) {
        queue.push(neighbor);
      }
    }
  }

  return {
    orderedNodeIds,
    hasCycle: orderedNodeIds.length !== graph.nodes.length
  };
}

export function extractInstructionList(input: unknown): CompiledInstruction[] {
  if (Array.isArray(input)) {
    return compiledInstructionListSchema.parse(input);
  }

  if (!input || typeof input !== "object") {
    throw new Error("Instructions YAML must be a list or an object containing an instructions list");
  }

  const candidate = input as Record<string, unknown>;

  if (Array.isArray(candidate.instructions)) {
    return compiledInstructionListSchema.parse(candidate.instructions);
  }

  if (candidate.instructions && typeof candidate.instructions === "object") {
    const nested = candidate.instructions as Record<string, unknown>;
    if (Array.isArray(nested.instructions)) {
      return compiledInstructionListSchema.parse(nested.instructions);
    }
  }

  throw new Error("Unable to find instructions list in YAML. Expected '- node: ...' entries.");
}

export function graphFromInstructions(input: unknown): PipelineGraph {
  const instructions = extractInstructionList(input);

  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  const producerByVariable = new Map<string, { nodeId: string; portKey: string }>();

  for (const [index, instruction] of instructions.entries()) {
    const definition = nodeDefinitionByType.get(instruction.node);
    if (!definition) {
      throw new Error(`Unknown node in instructions: ${instruction.node}`);
    }

    const nodeId = `${sanitizeName(instruction.node) || "node"}_${String(index + 1).padStart(3, "0")}`;
    const params = { ...instruction.params };

    for (const binding of definition.inputBindings) {
      const rawValue = params[binding.paramKey];
      if (!hasValue(rawValue) || typeof rawValue !== "string") {
        continue;
      }

      const producer = producerByVariable.get(rawValue);
      if (!producer) {
        continue;
      }

      edges.push({
        id: `e_${edges.length + 1}`,
        fromNodeId: producer.nodeId,
        fromPort: producer.portKey,
        toNodeId: nodeId,
        toPort: binding.portKey
      });
    }

    for (const binding of definition.outputBindings) {
      const variable = resolveOutputVariable({
        nodeId,
        nodeType: definition.type,
        portKey: binding.portKey,
        paramKey: binding.paramKey,
        params,
        hasOutgoingConnection: true,
        allowAutoFallback: false
      });

      if (!variable) {
        continue;
      }

      producerByVariable.set(variable, {
        nodeId,
        portKey: binding.portKey
      });
    }

    nodes.push({
      id: nodeId,
      type: definition.type,
      params
    });
  }

  return {
    nodes,
    edges
  };
}

export function validateGraph(input: unknown): GraphValidationResult {
  const parsed = graphSchema.safeParse(input);
  if (!parsed.success) {
    const issue = parsed.error.issues[0];
    return {
      valid: false,
      errors: [
        {
          code: "GRAPH_SHAPE",
          message: `Graph shape is invalid: ${issue?.message ?? "unknown error"}`,
          path: issue?.path.join(".")
        }
      ],
      warnings: []
    };
  }

  const graph = parsed.data;
  const errors: GraphValidationIssue[] = [];
  const warnings: GraphValidationIssue[] = [];

  const nodeIdSet = new Set<string>();
  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));

  for (const node of graph.nodes) {
    if (nodeIdSet.has(node.id)) {
      errors.push({
        code: "DUPLICATE_NODE_ID",
        message: `Duplicate node id: ${node.id}`,
        nodeId: node.id
      });
      continue;
    }

    nodeIdSet.add(node.id);

    const definition = nodeDefinitionByType.get(node.type);
    if (!definition) {
      errors.push({
        code: "UNKNOWN_NODE_TYPE",
        message: `Unknown node type: ${node.type}`,
        nodeId: node.id
      });
      continue;
    }

    const paramsCheck = definition.paramSchema.safeParse(node.params);
    if (!paramsCheck.success) {
      const issue = paramsCheck.error.issues[0];
      errors.push({
        code: "INVALID_PARAMS",
        message: `Invalid params for node ${node.id}: ${issue?.message ?? "unknown error"}`,
        nodeId: node.id,
        path: issue?.path.join(".")
      });
    }

    if (node.type === "ReadFile") {
      const filepath = node.params.filepath;
      const filePath = node.params.file_path;
      if (!hasValue(filepath) && !hasValue(filePath)) {
        errors.push({
          code: "INVALID_PARAMS",
          message: `Node ${node.id} (ReadFile) requires filepath or file_path`,
          nodeId: node.id,
          path: "filepath"
        });
      }
    }
  }

  const incomingByNodePort = new Map<string, string[]>();
  const connectedNodes = new Set<string>();

  for (const edge of graph.edges) {
    const fromNode = nodeById.get(edge.fromNodeId);
    const toNode = nodeById.get(edge.toNodeId);

    if (!fromNode || !toNode) {
      errors.push({
        code: "UNKNOWN_EDGE_NODE",
        message: `Edge ${edge.id} references missing node`,
        edgeId: edge.id
      });
      continue;
    }

    const fromDefinition = nodeDefinitionByType.get(fromNode.type);
    const toDefinition = nodeDefinitionByType.get(toNode.type);
    if (!fromDefinition || !toDefinition) {
      continue;
    }

    const fromPort = fromDefinition.outputPorts.find((port) => port.key === edge.fromPort);
    const toPort = toDefinition.inputPorts.find((port) => port.key === edge.toPort);

    if (!fromPort || !toPort) {
      errors.push({
        code: "UNKNOWN_EDGE_PORT",
        message: `Edge ${edge.id} references unknown port`,
        edgeId: edge.id
      });
      continue;
    }

    if (toPort.type !== "any" && fromPort.type !== "any" && fromPort.type !== toPort.type) {
      errors.push({
        code: "INCOMPATIBLE_PORT_TYPES",
        message: `Edge ${edge.id} has incompatible port types: ${fromPort.type} -> ${toPort.type}`,
        edgeId: edge.id
      });
    }

    const key = portSignature(edge.toNodeId, edge.toPort);
    const incomingEdges = incomingByNodePort.get(key) ?? [];
    incomingEdges.push(edge.id);
    incomingByNodePort.set(key, incomingEdges);

    connectedNodes.add(edge.fromNodeId);
    connectedNodes.add(edge.toNodeId);
  }

  for (const [signature, incoming] of incomingByNodePort.entries()) {
    if (incoming.length > 1) {
      const [nodeId] = signature.split(":");
      errors.push({
        code: "MULTIPLE_INPUT_CONNECTIONS",
        message: `Node ${nodeId} has multiple incoming edges into the same input port`,
        nodeId
      });
    }
  }

  for (const node of graph.nodes) {
    const definition = nodeDefinitionByType.get(node.type);
    if (!definition) {
      continue;
    }

    for (const inputPort of definition.inputPorts) {
      if (!inputPort.required) {
        continue;
      }

      const signature = portSignature(node.id, inputPort.key);
      const edgeCount = incomingByNodePort.get(signature)?.length ?? 0;
      if (edgeCount > 0) {
        continue;
      }

      const binding = definition.inputBindings.find((entry) => entry.portKey === inputPort.key);
      if (binding && hasValue(node.params[binding.paramKey])) {
        continue;
      }

      errors.push({
        code: "MISSING_REQUIRED_INPUT",
        message: `Node ${node.id} is missing required input port: ${inputPort.key}`,
        nodeId: node.id
      });
    }

    if (!connectedNodes.has(node.id)) {
      warnings.push({
        code: "ISOLATED_NODE",
        message: `Node ${node.id} is isolated and may not affect downstream outputs`,
        nodeId: node.id
      });
    }
  }

  const sort = runTopologicalSort(graph);
  if (sort.hasCycle) {
    errors.push({
      code: "GRAPH_CYCLE",
      message: "Graph contains a cycle and cannot be compiled as a DAG"
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

export function compileGraph(input: unknown): PipelineInstructions {
  const validation = validateGraph(input);
  if (!validation.valid) {
    const formatted = validation.errors.map((error) => error.message).join("; ");
    throw new Error(`Cannot compile graph: ${formatted}`);
  }

  const graph = graphSchema.parse(input);
  const sort = runTopologicalSort(graph);

  const nodesById = new Map(graph.nodes.map((node) => [node.id, node]));
  const incomingEdgeByNodePort = new Map<string, GraphEdge>();
  const outgoingCountByNodePort = new Map<string, number>();

  for (const edge of graph.edges) {
    incomingEdgeByNodePort.set(portSignature(edge.toNodeId, edge.toPort), edge);

    const outKey = portSignature(edge.fromNodeId, edge.fromPort);
    outgoingCountByNodePort.set(outKey, (outgoingCountByNodePort.get(outKey) ?? 0) + 1);
  }

  const outputVariableByNodePort = new Map<string, string>();
  const instructions: CompiledInstruction[] = [];

  for (const nodeId of sort.orderedNodeIds) {
    const node = nodesById.get(nodeId);
    if (!node) {
      continue;
    }

    const definition = nodeDefinitionByType.get(node.type);
    if (!definition) {
      continue;
    }

    const compiledParams: Record<string, unknown> = { ...node.params };

    for (const binding of definition.inputBindings) {
      const edge = incomingEdgeByNodePort.get(portSignature(node.id, binding.portKey));
      if (!edge) {
        continue;
      }

      const sourceVar = outputVariableByNodePort.get(portSignature(edge.fromNodeId, edge.fromPort));
      if (!sourceVar) {
        throw new Error(`Cannot resolve source variable for edge ${edge.id}`);
      }

      compiledParams[binding.paramKey] = sourceVar;
    }

    for (const binding of definition.outputBindings) {
      const signature = portSignature(node.id, binding.portKey);
      const variable = resolveOutputVariable({
        nodeId: node.id,
        nodeType: definition.type,
        portKey: binding.portKey,
        paramKey: binding.paramKey,
        params: compiledParams,
        hasOutgoingConnection: (outgoingCountByNodePort.get(signature) ?? 0) > 0,
        allowAutoFallback: true
      });

      if (!variable) {
        continue;
      }

      compiledParams[binding.paramKey] = variable;
      outputVariableByNodePort.set(signature, variable);
    }

    instructions.push({
      node: node.type,
      params: compiledParams
    });
  }

  return {
    format: "aigen.instructions.v1",
    generatedAt: new Date().toISOString(),
    instructions
  };
}

export const exampleGraph: PipelineGraph = {
  nodes: [
    {
      id: "set_prompt",
      type: "SetVariable",
      params: {
        name: "prompt_step_1",
        value: "Describe each image in exactly 10 words.",
        if_missing: false
      }
    },
    {
      id: "ask_gpt",
      type: "GPTChat",
      params: {
        model: "gpt-4o-mini",
        max_tokens: 120,
        temperature: 0.2,
        prompt: [{ type: "text", content: "prompt_step_1" }],
        output: "image_description"
      }
    },
    {
      id: "print_output",
      type: "PrintVariable",
      params: {}
    }
  ],
  edges: [
    {
      id: "e1",
      fromNodeId: "ask_gpt",
      fromPort: "response",
      toNodeId: "print_output",
      toPort: "in"
    }
  ]
};
