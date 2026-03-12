import { useMemo, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import yaml from "js-yaml";
import { usePipelineStore } from "../store/usePipelineStore";

type ExportFormat = "json" | "yaml";

function downloadText(filename: string, text: string) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function DiagnosticsPanel() {
  const [format, setFormat] = useState<ExportFormat>("yaml");
  const [importMessage, setImportMessage] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validation = usePipelineStore((state) => state.validation);
  const instructions = usePipelineStore((state) => state.instructions);
  const apiStatus = usePipelineStore((state) => state.apiStatus);
  const apiError = usePipelineStore((state) => state.apiError);
  const validateCurrentGraph = usePipelineStore((state) => state.validateCurrentGraph);
  const compileCurrentGraph = usePipelineStore((state) => state.compileCurrentGraph);
  const loadInstructionsDocument = usePipelineStore((state) => state.loadInstructionsDocument);

  const instructionList = instructions?.instructions ?? null;

  const exportedText = useMemo(() => {
    if (!instructionList) {
      return "";
    }

    if (format === "yaml") {
      return yaml.dump(instructionList, { noRefs: true, lineWidth: 120 });
    }

    return JSON.stringify(instructionList, null, 2);
  }, [format, instructionList]);

  const handleLoadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";

    if (!file) {
      return;
    }

    try {
      const rawText = await file.text();
      const document = yaml.load(rawText);
      await loadInstructionsDocument(document);
      setImportMessage(`Loaded ${file.name} into graph.`);
    } catch (error) {
      setImportMessage(error instanceof Error ? error.message : "Failed to load YAML file.");
    }
  };

  return (
    <div className="panel diagnostics">
      <h2>Validate & Export</h2>

      <div className="actions-row">
        <button type="button" onClick={() => void validateCurrentGraph()} disabled={apiStatus !== "idle"}>
          Validate
        </button>
        <button type="button" onClick={() => void compileCurrentGraph()} disabled={apiStatus !== "idle"}>
          Compile
        </button>
        <button type="button" onClick={handleLoadClick} disabled={apiStatus !== "idle"}>
          Load YAML
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".yaml,.yml,text/yaml,application/x-yaml"
          onChange={(event) => void handleFileChange(event)}
          style={{ display: "none" }}
        />
      </div>

      {apiError && <p className="error-text">{apiError}</p>}
      {importMessage && <p className="muted">{importMessage}</p>}

      {validation && (
        <div className="validation-summary">
          <p className={validation.valid ? "ok-text" : "error-text"}>
            {validation.valid ? "Graph is valid." : `Graph has ${validation.errors.length} error(s).`}
          </p>
          {validation.warnings.length > 0 && (
            <p className="warn-text">Graph has {validation.warnings.length} warning(s).</p>
          )}

          {(validation.errors.length > 0 || validation.warnings.length > 0) && (
            <ul>
              {validation.errors.map((issue, index) => (
                <li key={`error:${issue.code}:${index}`} className="error-text">
                  {issue.message}
                </li>
              ))}
              {validation.warnings.map((issue, index) => (
                <li key={`warning:${issue.code}:${index}`} className="warn-text">
                  {issue.message}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="actions-row">
        <button
          type="button"
          className={format === "yaml" ? "active" : ""}
          onClick={() => setFormat("yaml")}
        >
          YAML
        </button>
        <button
          type="button"
          className={format === "json" ? "active" : ""}
          onClick={() => setFormat("json")}
        >
          JSON
        </button>
        <button
          type="button"
          disabled={!exportedText}
          onClick={() => downloadText(`instructions.${format}`, exportedText)}
        >
          Save
        </button>
      </div>

      <textarea
        className="export-textarea"
        readOnly
        value={
          exportedText ||
          "Click Compile to generate instructions. Save exports runtime-compatible instruction lists. Load YAML rebuilds the graph from instruction steps."
        }
      />
    </div>
  );
}
