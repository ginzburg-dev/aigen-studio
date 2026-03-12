import { useMemo } from "react";
import { usePipelineStore } from "../store/usePipelineStore";

export function InspectorPanel() {
  const selectedNodeId = usePipelineStore((state) => state.selectedNodeId);
  const nodes = usePipelineStore((state) => state.nodes);
  const definitions = usePipelineStore((state) => state.nodeDefinitions);
  const updateNodeParam = usePipelineStore((state) => state.updateNodeParam);

  const selectedNode = useMemo(
    () => nodes.find((node) => node.id === selectedNodeId),
    [nodes, selectedNodeId]
  );

  const definition = useMemo(
    () =>
      selectedNode
        ? definitions.find((item) => item.type === selectedNode.data.nodeType)
        : undefined,
    [definitions, selectedNode]
  );

  if (!selectedNode || !definition) {
    return (
      <div className="panel">
        <h2>Parameters</h2>
        <p className="muted">Select a node to edit its parameters.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Parameters</h2>
      <p className="node-caption">{definition.label}</p>

      <div className="form-grid">
        {definition.params.map((param) => {
          const current = selectedNode.data.params[param.key] ?? param.defaultValue;

          if (param.kind === "boolean") {
            return (
              <label key={param.key} className="field field--checkbox">
                <input
                  type="checkbox"
                  checked={Boolean(current)}
                  onChange={(event) =>
                    updateNodeParam(selectedNode.id, param.key, event.target.checked)
                  }
                />
                <span>{param.label}</span>
              </label>
            );
          }

          if (param.kind === "select") {
            return (
              <label key={param.key} className="field">
                <span>{param.label}</span>
                <select
                  value={String(current ?? "")}
                  onChange={(event) =>
                    updateNodeParam(selectedNode.id, param.key, event.target.value)
                  }
                >
                  {(param.options ?? []).map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
            );
          }

          if (param.kind === "number") {
            return (
              <label key={param.key} className="field">
                <span>{param.label}</span>
                <input
                  type="number"
                  value={Number(current ?? 0)}
                  onChange={(event) => {
                    const next = Number(event.target.value);
                    updateNodeParam(selectedNode.id, param.key, Number.isNaN(next) ? 0 : next);
                  }}
                />
              </label>
            );
          }

          if (param.kind === "text") {
            return (
              <label key={param.key} className="field">
                <span>{param.label}</span>
                <textarea
                  value={String(current ?? "")}
                  onChange={(event) =>
                    updateNodeParam(selectedNode.id, param.key, event.target.value)
                  }
                />
              </label>
            );
          }

          if (param.kind === "json") {
            const serialized =
              typeof current === "string" ? current : JSON.stringify(current ?? {}, null, 2);

            return (
              <label key={param.key} className="field">
                <span>{param.label}</span>
                <textarea
                  value={serialized}
                  onChange={(event) => {
                    const raw = event.target.value;
                    try {
                      const parsed = JSON.parse(raw);
                      updateNodeParam(selectedNode.id, param.key, parsed);
                    } catch {
                      updateNodeParam(selectedNode.id, param.key, raw);
                    }
                  }}
                />
              </label>
            );
          }

          return (
            <label key={param.key} className="field">
              <span>{param.label}</span>
              <input
                type="text"
                value={String(current ?? "")}
                onChange={(event) =>
                  updateNodeParam(selectedNode.id, param.key, event.target.value)
                }
              />
            </label>
          );
        })}
      </div>
    </div>
  );
}
