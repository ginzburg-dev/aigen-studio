import type { Edge, Node } from "@xyflow/react";
import type { PortDefinition } from "@pipeline-builder/schema";

export interface FlowNodeData {
  [key: string]: unknown;
  nodeType: string;
  label: string;
  params: Record<string, unknown>;
  inputPorts: PortDefinition[];
  outputPorts: PortDefinition[];
}

export type FlowNode = Node<FlowNodeData, "pipelineNode">;
export type FlowEdge = Edge;
