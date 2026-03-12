import { useCallback, useEffect } from "react";
import {
  Background,
  ConnectionLineType,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider
} from "@xyflow/react";
import type { Connection } from "@xyflow/react";
import type { PortDefinition } from "@pipeline-builder/schema";
import { DiagnosticsPanel } from "./components/DiagnosticsPanel";
import { FlowNode } from "./components/FlowNode";
import { InspectorPanel } from "./components/InspectorPanel";
import { NodePalette } from "./components/NodePalette";
import { usePipelineStore } from "./store/usePipelineStore";
import type { FlowEdge, FlowNode as FlowNodeType } from "./types";

const nodeTypes = {
  pipelineNode: FlowNode
};

function isPortTypeCompatible(sourcePort: PortDefinition, targetPort: PortDefinition): boolean {
  if (sourcePort.type === "any" || targetPort.type === "any") {
    return true;
  }

  return sourcePort.type === targetPort.type;
}

function Canvas() {
  const nodes = usePipelineStore((state) => state.nodes);
  const edges = usePipelineStore((state) => state.edges);
  const apiStatus = usePipelineStore((state) => state.apiStatus);
  const loadNodeDefinitions = usePipelineStore((state) => state.loadNodeDefinitions);
  const applyNodeChanges = usePipelineStore((state) => state.applyNodeChanges);
  const applyEdgeChanges = usePipelineStore((state) => state.applyEdgeChanges);
  const addConnection = usePipelineStore((state) => state.addConnection);
  const selectNode = usePipelineStore((state) => state.selectNode);

  useEffect(() => {
    void loadNodeDefinitions();
  }, [loadNodeDefinitions]);

  const isValidConnection = useCallback(
    (connection: Connection | FlowEdge) => {
      if (!connection.source || !connection.target || !connection.sourceHandle || !connection.targetHandle) {
        return false;
      }

      const sourceNode = nodes.find((node) => node.id === connection.source);
      const targetNode = nodes.find((node) => node.id === connection.target);

      if (!sourceNode || !targetNode) {
        return false;
      }

      const sourcePort = sourceNode.data.outputPorts.find(
        (port) => port.key === connection.sourceHandle
      );
      const targetPort = targetNode.data.inputPorts.find(
        (port) => port.key === connection.targetHandle
      );

      if (!sourcePort || !targetPort) {
        return false;
      }

      return isPortTypeCompatible(sourcePort, targetPort);
    },
    [nodes]
  );

  return (
    <div className="canvas-wrapper">
      <ReactFlow<FlowNodeType, FlowEdge>
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={applyNodeChanges}
        onEdgesChange={applyEdgeChanges}
        onConnect={addConnection}
        onSelectionChange={({ nodes: selectedNodes }) => selectNode(selectedNodes[0]?.id)}
        onPaneClick={() => selectNode(undefined)}
        isValidConnection={isValidConnection}
        connectionLineType={ConnectionLineType.SmoothStep}
        fitView
      >
        <Background color="#d0c2ad" gap={20} />
        <MiniMap pannable zoomable />
        <Controls />
      </ReactFlow>

      {apiStatus !== "idle" && <div className="canvas-overlay">{apiStatus}...</div>}
    </div>
  );
}

export function App() {
  return (
    <ReactFlowProvider>
      <div className="app-shell">
        <aside className="column column--left">
          <NodePalette />
        </aside>

        <main className="column column--center">
          <Canvas />
        </main>

        <aside className="column column--right">
          <InspectorPanel />
          <DiagnosticsPanel />
        </aside>
      </div>
    </ReactFlowProvider>
  );
}
