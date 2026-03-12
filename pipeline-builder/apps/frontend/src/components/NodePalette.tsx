import { useMemo } from "react";
import { usePipelineStore } from "../store/usePipelineStore";

export function NodePalette() {
  const nodeDefinitions = usePipelineStore((state) => state.nodeDefinitions);
  const addNode = usePipelineStore((state) => state.addNode);

  const grouped = useMemo(() => {
    return {
      input: nodeDefinitions.filter((node) => node.category === "input"),
      transform: nodeDefinitions.filter((node) => node.category === "transform"),
      output: nodeDefinitions.filter((node) => node.category === "output"),
      utility: nodeDefinitions.filter((node) => node.category === "utility")
    };
  }, [nodeDefinitions]);

  const categories = useMemo(
    () =>
      (["input", "transform", "output", "utility"] as const).filter(
        (category) => grouped[category].length > 0
      ),
    [grouped]
  );

  return (
    <div className="panel">
      <h2>Node Palette</h2>
      {nodeDefinitions.length === 0 && <p className="muted">Loading node definitions...</p>}

      {categories.map((category) => (
        <div key={category} className="palette-group">
          <h3>{category}</h3>
          <div className="palette-grid">
            {grouped[category].map((definition) => (
              <button
                key={definition.type}
                type="button"
                className="palette-card"
                onClick={() => addNode(definition.type)}
                title={definition.description}
              >
                <span className="palette-card__label">{definition.label}</span>
                <span className="palette-card__type">{definition.type}</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
