import { Handle, Position } from "@xyflow/react";
import type { NodeProps } from "@xyflow/react";
import type { FlowNode } from "../types";

const BASE_PORT_TOP = 54;
const PORT_GAP = 24;

export function FlowNode({ data, selected }: NodeProps<FlowNode>) {
  return (
    <div className={`flow-node ${selected ? "selected" : ""}`}>
      <div className="flow-node__header">
        <span className="flow-node__title">{data.label}</span>
        <span className="flow-node__type">{data.nodeType}</span>
      </div>

      <div className="flow-node__body">
        {data.inputPorts.map((port, index) => (
          <div key={`in:${port.key}`} className="flow-node__port flow-node__port--left">
            <Handle
              id={port.key}
              type="target"
              position={Position.Left}
              style={{ top: BASE_PORT_TOP + index * PORT_GAP }}
            />
            <span>{port.label}</span>
          </div>
        ))}

        {data.outputPorts.map((port, index) => (
          <div key={`out:${port.key}`} className="flow-node__port flow-node__port--right">
            <span>{port.label}</span>
            <Handle
              id={port.key}
              type="source"
              position={Position.Right}
              style={{ top: BASE_PORT_TOP + index * PORT_GAP }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
