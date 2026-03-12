import {
  addEdge,
  applyEdgeChanges as rfApplyEdgeChanges,
  applyNodeChanges as rfApplyNodeChanges
} from "@xyflow/react";
import type { Connection, EdgeChange, NodeChange } from "@xyflow/react";
import {
  graphFromInstructions,
  type GraphValidationResult,
  type PipelineGraph,
  type PipelineInstructions,
  type SerializableNodeDefinition
} from "@pipeline-builder/schema";
import { create } from "zustand";
import { apiRequest, ApiError } from "../lib/api";
import { toPipelineGraph } from "../lib/graph";
import type { FlowEdge, FlowNode } from "../types";

type ApiStatus = "idle" | "loading" | "validating" | "compiling";

interface PipelineStore {
  apiStatus: ApiStatus;
  apiError?: string;
  nodeDefinitions: SerializableNodeDefinition[];
  nodes: FlowNode[];
  edges: FlowEdge[];
  selectedNodeId?: string;
  validation: GraphValidationResult | null;
  instructions: PipelineInstructions | null;
  loadNodeDefinitions: () => Promise<void>;
  addNode: (nodeType: string) => void;
  applyNodeChanges: (changes: NodeChange<FlowNode>[]) => void;
  applyEdgeChanges: (changes: EdgeChange<FlowEdge>[]) => void;
  addConnection: (connection: Connection) => void;
  selectNode: (nodeId?: string) => void;
  updateNodeParam: (nodeId: string, key: string, value: unknown) => void;
  validateCurrentGraph: () => Promise<void>;
  compileCurrentGraph: () => Promise<void>;
  loadInstructionsDocument: (document: unknown) => Promise<void>;
}

function makeDefaultParamValue(param: SerializableNodeDefinition["params"][number]): unknown {
  if (param.defaultValue !== undefined) {
    return param.defaultValue;
  }

  switch (param.kind) {
    case "text":
      return "";
    case "number":
      return 0;
    case "boolean":
      return false;
    case "json":
      return {};
    case "select":
      return param.options?.[0] ?? "";
    case "string":
    default:
      return "";
  }
}

function parseValidationPayload(payload: unknown): GraphValidationResult | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  if (!("errors" in payload) || !("warnings" in payload) || !("valid" in payload)) {
    return null;
  }

  return payload as GraphValidationResult;
}

function materializeFlowGraph(
  graph: PipelineGraph,
  nodeDefinitions: SerializableNodeDefinition[]
): { nodes: FlowNode[]; edges: FlowEdge[] } {
  const definitionByType = new Map(nodeDefinitions.map((definition) => [definition.type, definition]));

  const depthByNode = new Map<string, number>();
  for (const node of graph.nodes) {
    depthByNode.set(node.id, 0);
  }

  // Relax edges to get a stable left-to-right DAG layout depth.
  for (let i = 0; i < graph.nodes.length; i += 1) {
    let changed = false;
    for (const edge of graph.edges) {
      const sourceDepth = depthByNode.get(edge.fromNodeId) ?? 0;
      const currentTargetDepth = depthByNode.get(edge.toNodeId) ?? 0;
      const nextTargetDepth = sourceDepth + 1;
      if (nextTargetDepth > currentTargetDepth) {
        depthByNode.set(edge.toNodeId, nextTargetDepth);
        changed = true;
      }
    }

    if (!changed) {
      break;
    }
  }

  const rowByDepth = new Map<number, number>();

  const nodes: FlowNode[] = graph.nodes.map((node) => {
    const definition = definitionByType.get(node.type);
    if (!definition) {
      throw new Error(`Unknown node type in graph: ${node.type}`);
    }

    const depth = depthByNode.get(node.id) ?? 0;
    const row = rowByDepth.get(depth) ?? 0;
    rowByDepth.set(depth, row + 1);

    return {
      id: node.id,
      type: "pipelineNode",
      position: {
        x: 120 + depth * 320,
        y: 80 + row * 220
      },
      data: {
        nodeType: definition.type,
        label: definition.label,
        inputPorts: definition.inputPorts,
        outputPorts: definition.outputPorts,
        params: node.params
      }
    };
  });

  const edges: FlowEdge[] = graph.edges.map((edge) => ({
    id: edge.id,
    source: edge.fromNodeId,
    sourceHandle: edge.fromPort,
    target: edge.toNodeId,
    targetHandle: edge.toPort,
    animated: true
  }));

  return { nodes, edges };
}

export const usePipelineStore = create<PipelineStore>((set, get) => ({
  apiStatus: "idle",
  nodeDefinitions: [],
  nodes: [],
  edges: [],
  validation: null,
  instructions: null,

  loadNodeDefinitions: async () => {
    set({ apiStatus: "loading", apiError: undefined });
    try {
      const data = await apiRequest<{ nodes: SerializableNodeDefinition[] }>("/node-definitions");
      set({ nodeDefinitions: data.nodes, apiStatus: "idle" });
    } catch (error) {
      set({
        apiStatus: "idle",
        apiError: error instanceof Error ? error.message : "Failed to load node definitions"
      });
    }
  },

  addNode: (nodeType: string) => {
    const definition = get().nodeDefinitions.find((nodeDefinition) => nodeDefinition.type === nodeType);
    if (!definition) {
      return;
    }

    const index = get().nodes.length;
    const id = `${nodeType.replace(/[^a-z0-9]/gi, "_")}_${crypto.randomUUID().slice(0, 8)}`;

    const params = Object.fromEntries(
      definition.params.map((param) => [param.key, makeDefaultParamValue(param)])
    );

    const node: FlowNode = {
      id,
      type: "pipelineNode",
      position: {
        x: 120 + (index % 3) * 280,
        y: 80 + Math.floor(index / 3) * 180
      },
      data: {
        nodeType: definition.type,
        label: definition.label,
        inputPorts: definition.inputPorts,
        outputPorts: definition.outputPorts,
        params
      }
    };

    set((state) => ({
      nodes: [...state.nodes, node],
      selectedNodeId: id,
      validation: null,
      instructions: null
    }));
  },

  applyNodeChanges: (changes) => {
    set((state) => ({
      nodes: rfApplyNodeChanges<FlowNode>(changes, state.nodes),
      validation: null,
      instructions: null
    }));
  },

  applyEdgeChanges: (changes) => {
    set((state) => ({
      edges: rfApplyEdgeChanges<FlowEdge>(changes, state.edges),
      validation: null,
      instructions: null
    }));
  },

  addConnection: (connection) => {
    if (!connection.source || !connection.target || !connection.sourceHandle || !connection.targetHandle) {
      return;
    }

    const nextEdge: FlowEdge = {
      ...connection,
      id: `e_${crypto.randomUUID().slice(0, 10)}`,
      animated: true
    };

    set((state) => {
      const withoutExistingInput = state.edges.filter(
        (edge) => !(edge.target === connection.target && edge.targetHandle === connection.targetHandle)
      );

      return {
        edges: addEdge<FlowEdge>(nextEdge, withoutExistingInput),
        validation: null,
        instructions: null
      };
    });
  },

  selectNode: (nodeId) => {
    set({ selectedNodeId: nodeId });
  },

  updateNodeParam: (nodeId, key, value) => {
    set((state) => ({
      nodes: state.nodes.map((node) => {
        if (node.id !== nodeId) {
          return node;
        }

        return {
          ...node,
          data: {
            ...node.data,
            params: {
              ...node.data.params,
              [key]: value
            }
          }
        };
      }),
      validation: null,
      instructions: null
    }));
  },

  validateCurrentGraph: async () => {
    set({ apiStatus: "validating", apiError: undefined });

    const graph = toPipelineGraph(get().nodes, get().edges);

    try {
      const validation = await apiRequest<GraphValidationResult>("/validate", {
        method: "POST",
        body: JSON.stringify(graph)
      });

      set({ validation, apiStatus: "idle" });
    } catch (error) {
      if (error instanceof ApiError) {
        const validation = parseValidationPayload(error.payload);
        if (validation) {
          set({ validation, apiStatus: "idle" });
          return;
        }
      }

      set({
        apiStatus: "idle",
        apiError: error instanceof Error ? error.message : "Failed to validate graph"
      });
    }
  },

  compileCurrentGraph: async () => {
    set({ apiStatus: "compiling", apiError: undefined });

    const graph = toPipelineGraph(get().nodes, get().edges);

    try {
      const response = await apiRequest<{
        validation: GraphValidationResult;
        instructions: PipelineInstructions;
      }>("/compile", {
        method: "POST",
        body: JSON.stringify(graph)
      });

      set({
        validation: response.validation,
        instructions: response.instructions,
        apiStatus: "idle"
      });
    } catch (error) {
      if (error instanceof ApiError) {
        const validation = parseValidationPayload(error.payload);
        if (validation) {
          set({ validation, instructions: null, apiStatus: "idle" });
          return;
        }
      }

      set({
        apiStatus: "idle",
        apiError: error instanceof Error ? error.message : "Failed to compile graph"
      });
    }
  },

  loadInstructionsDocument: async (document: unknown) => {
    set({ apiError: undefined });

    try {
      if (get().nodeDefinitions.length === 0) {
        await get().loadNodeDefinitions();
      }

      const definitions = get().nodeDefinitions;
      if (definitions.length === 0) {
        throw new Error("Node definitions are not loaded.");
      }

      const graph = graphFromInstructions(document);
      const flow = materializeFlowGraph(graph, definitions);

      set({
        nodes: flow.nodes,
        edges: flow.edges,
        selectedNodeId: undefined,
        validation: null,
        instructions: null,
        apiError: undefined,
        apiStatus: "idle"
      });
    } catch (error) {
      set({
        apiError: error instanceof Error ? error.message : "Failed to load instructions YAML",
        apiStatus: "idle"
      });
    }
  }
}));
