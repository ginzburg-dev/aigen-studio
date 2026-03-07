// web/src/App.jsx
import { useCallback, useMemo, useState, useEffect, useRef } from 'react'
import ReactFlow, {
  Background, Controls, MiniMap,
  addEdge, useEdgesState, useNodesState, ReactFlowProvider
} from 'reactflow'
import 'reactflow/dist/style.css'
import * as yaml from 'js-yaml'
import { NODE_DEFS } from './nodeSchema'
import ParamNode from './ParamNode'

const nodeTypes = { param: ParamNode }
const uid = (() => { let i = 1; return () => `n${i++}` })()

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const [runResult, setRunResult] = useState(null)
  const [runLogs, setRunLogs] = useState('')
  const [runError, setRunError] = useState(null)

  const [batchText, setBatchText] = useState('')
  const [batchVar, setBatchVar] = useState('input_text_variable')

  const [logsVisible, setLogsVisible] = useState(true) // close/open logs panel

  // success flag to style the log panel green
  const lastOkRef = useRef(false)

  // Light theme
  useEffect(() => {
    document.body.style.background = '#ffffff'
    document.body.style.color = '#111111'
    document.body.style.fontFamily = 'Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif'
    return () => {
      document.body.style.background = ''
      document.body.style.color = ''
      document.body.style.fontFamily = ''
    }
  }, [])

  const addNode = (type) => {
    const def = NODE_DEFS[type]
    const id = uid()
    setNodes(ns => ns.concat({
      id, type: 'param',
      position: { x: 60 + ns.length * 40, y: 60 + ns.length * 30 },
      data: { nodeType: type, params: JSON.parse(JSON.stringify(def.params)) }
    }))
  }

  const onParamChange = useCallback((id, key, value) => {
    setNodes(ns => ns.map(n =>
      n.id === id ? { ...n, data: { ...n.data, params: { ...n.data.params, [key]: value } } } : n
    ))
  }, [setNodes])

  const nodesWithHandlers = useMemo(
    () => nodes.map(n => ({ ...n, data: { ...n.data, onParamChange } })),
    [nodes, onParamChange]
  )

  // reconnect: replace conflicting edges (one-in/one-out feel)
  const onConnect = useCallback((params) => {
    setEdges(eds => {
      const filtered = eds.filter(e => e.source !== params.source && e.target !== params.target)
      return addEdge(params, filtered)
    })
  }, [setEdges])

  const isValidConnection = useCallback((c) => {
    const src = nodes.find(n => n.id === c.source)
    const dst = nodes.find(n => n.id === c.target)
    if (!src || !dst) return false
    if (src.data.nodeType === 'End') return false
    if (dst.data.nodeType === 'Start') return false
    return true
  }, [nodes])

  // Build linear YAML from Start -> End
  const buildLinearYaml = () => {
    const mapOut = new Map(), mapIn = new Map()
    edges.forEach(e => { mapOut.set(e.source, e.target); mapIn.set(e.target, e.source) })

    const start = nodes.find(n => n.data.nodeType === 'Start') || nodes.find(n => !mapIn.has(n.id))
    const end = nodes.find(n => n.data.nodeType === 'End') || nodes.find(n => !mapOut.has(n.id))
    if (!start || !end) throw new Error('Need Start and End (or a clear single-chain head and tail).')

    const order = [], seen = new Set()
    let cur = start.id
    while (cur) {
      if (seen.has(cur)) throw new Error('Cycle detected; chain must be linear.')
      seen.add(cur); order.push(cur)
      const next = mapOut.get(cur); if (!next) break; cur = next
    }
    if (order[order.length - 1] !== end.id) throw new Error('Chain must end at End.')

    const nodeMap = new Map(nodes.map(n => [n.id, n]))
    const list = order
      .map(id => nodeMap.get(id))
      .filter(n => n && !['Start', 'End'].includes(n.data.nodeType))
      .map(n => ({ node: n.data.nodeType, params: n.data.params }))
    if (list.length === 0) throw new Error('No executable nodes between Start and End.')
    return yaml.dump(list)
  }

  // Detect batch var placeholder literally
  function yamlHasCurrentBatchVar(yamlText, varName) {
    if (!varName) return false
    const brace = `{{${varName}}}`
    const dollar = `\${${varName}}`
    return yamlText.includes(brace) || yamlText.includes(dollar)
  }

  async function runOnce(yamlText) {
    const r = await fetch('http://localhost:8000/run', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ yaml_text: yamlText })
    })
    const out = await r.json()
    lastOkRef.current = !!out.ok

    if (out.ok) {
      setRunResult(out.outputs || null)
      const logsCombined = [out.logs, out.errors].filter(Boolean).join('\n')
      setRunLogs(logsCombined.trim() || '') // keep empty; UI shows success fallback
      setRunError(null)
    } else {
      setRunResult(null)
      const logsCombined = [out.error?.logs, out.error?.stderr].filter(Boolean).join('\n')
      setRunLogs(logsCombined.trim() || '')
      setRunError(out.error || { message: 'Unknown error' })
    }
    setLogsVisible(true) // show dock after each run
    return out
  }

  const runRemote = async () => {
    try {
      const y = buildLinearYaml()
      if (batchVar && yamlHasCurrentBatchVar(y, batchVar)) {
        setRunError({ message: `“Run” is disabled: batch variable "${batchVar}" is present. Use “Run Batch”.` })
        setLogsVisible(true)
        return
      }
      await runOnce(y)
    } catch (e) {
      setRunError({ message: String(e) })
      setLogsVisible(true)
    }
  }

  // Client-side batch: literal replace; no parsing
  const runBatch = async () => {
    try {
      const baseYaml = buildLinearYaml()
      const lines = batchText.split('\n').map(s => s.trim()).filter(Boolean)
      if (!batchVar || lines.length === 0) { alert('Set variable name and provide batch lines.'); return }
      const results = []
      let anyFail = false
      let combinedLogs = []

      for (const val of lines) {
        const y = baseYaml
          .replaceAll(`{{${batchVar}}}`, val)
          .replaceAll(`\${${batchVar}}`, val)
        const r = await runOnce(y)
        results.push(r)
        if (!r.ok) anyFail = true
        const logs = [r.logs, r.errors, r.error?.logs, r.error?.stderr].filter(Boolean).join('\n')
        if (logs) combinedLogs.push(logs)
      }

      lastOkRef.current = !anyFail
      setRunResult({ batch_count: lines.length, items: results.map(r => ({ ok: r.ok, outputs: r.outputs || null })) })

      const finalLogs = combinedLogs.join('\n').trim()
      setRunLogs(finalLogs || '')
      if (!anyFail) setRunError(null)
      setLogsVisible(true)
    } catch (e) {
      setRunError({ message: String(e) })
      setLogsVisible(true)
    }
  }

  // Local save/load
  const saveLocal = () => {
    localStorage.setItem('graph', JSON.stringify({ nodes, edges, batchVar, batchText }))
    alert('saved')
  }
  const loadLocal = () => {
    const raw = localStorage.getItem('graph')
    if (!raw) return
    const g = JSON.parse(raw)
    setNodes(g.nodes || [])
    setEdges(g.edges || [])
    setBatchVar(g.batchVar || '')
    setBatchText(g.batchText || '')
  }

  // Export/Import to file (includes batch settings)
  const exportState = () => {
    const data = { nodes, edges, batchVar, batchText }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'aigen-graph.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  const importState = (file) => {
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const g = JSON.parse(reader.result)
        setNodes(g.nodes || [])
        setEdges(g.edges || [])
        setBatchVar(g.batchVar || '')
        setBatchText(g.batchText || '')
      } catch (e) {
        alert('Invalid file')
      }
    }
    reader.readAsText(file)
  }

  const runDisabled = (() => {
    try {
      const y = buildLinearYaml()
      return batchVar && yamlHasCurrentBatchVar(y, batchVar)
    } catch {
      return false
    }
  })()

  return (
    <ReactFlowProvider>
      <div style={{ height: '100vh', width: '100vw' }}>
        {/* toolbar */}
        <div
          style={{
            position: 'absolute', zIndex: 11, padding: 10, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center',
            background: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(6px)', border: '1px solid #ccc', borderRadius: 12
          }}
        >
          <button onClick={() => addNode('Start')} style={btn()}>+ Start</button>
          <button onClick={() => addNode('SetVariable')} style={btn()}>+ SetVariable</button>
          <button onClick={() => addNode('CopyVariable')} style={btn()}>+ CopyVariable</button>
          <button onClick={() => addNode('PrintVariable')} style={btn()}>+ PrintVariable</button>
          <button onClick={() => addNode('ReadFile')} style={btn()}>+ ReadFile</button>
          <button onClick={() => addNode('SaveFile')} style={btn()}>+ SaveFile</button>
          <button onClick={() => addNode('GPTChat')} style={btn()}>+ GPTChat</button>
          <button onClick={() => addNode('End')} style={btn()}>+ End</button>

          <button onClick={runRemote} disabled={runDisabled} title={runDisabled ? 'Disabled when batch var present' : ''} style={btn(runDisabled)}>
            Run (server)
          </button>
          <button onClick={saveLocal} style={btn()}>Save</button>
          <button onClick={loadLocal} style={btn()}>Load</button>
          <button onClick={exportState} style={btn()}>Export</button>
          <label style={{ display: 'inline-block' }}>
            <span style={btn(false, true)}>Import</span>
            <input
              type="file" accept="application/json" style={{ display: 'none' }}
              onChange={(e) => e.target.files?.[0] && importState(e.target.files[0])}
            />
          </label>

          {/* batch */}
          <div style={{ marginLeft: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
            <span style={{ fontSize: 12, color: '#555' }}>Batch var</span>
            <input
              className="nodrag nowheel"
              onMouseDown={(e) => e.stopPropagation()}
              onPointerDown={(e) => e.stopPropagation()}
              value={batchVar}
              onChange={e => setBatchVar(e.target.value)}
              style={input()}
              placeholder="variable_name"
            />
            <textarea
              className="nodrag nowheel"
              onMouseDown={(e) => e.stopPropagation()}
              onPointerDown={(e) => e.stopPropagation()}
              placeholder={'one value per line\n(example)\nHello\nBonjour\nHola'}
              value={batchText}
              onChange={e => setBatchText(e.target.value)}
              style={{ ...input(), width: 220, height: 80 }}
            />
            <button onClick={runBatch} style={btn()}>Run Batch</button>
          </div>
        </div>

        {/* canvas */}
        <ReactFlow
          nodes={nodesWithHandlers}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          isValidConnection={isValidConnection}
          nodeTypes={nodeTypes}
          fitView
          style={{ width: '100%', height: '100%' }}
        >
          <MiniMap pannable zoomable />
          <Controls />
          <Background />
        </ReactFlow>

        {/* bottom docked logs */}
        {logsVisible && (
          <div style={{
            position: 'fixed', left: 0, right: 0, bottom: 0, zIndex: 10,
            maxHeight: '40vh', overflow: 'auto',
            background: '#ffffff', borderTop: '1px solid #ccc', color: '#111', padding: 10
          }}>
            <button
              onClick={() => setLogsVisible(false)}
              title="Close"
              style={{
                position: 'absolute', top: 6, right: 10, border: 'none',
                background: 'transparent', fontSize: 18, lineHeight: 1,
                cursor: 'pointer', color: '#666'
              }}
            >
              ×
            </button>

            {runError ? (
              // RED error panel
              <div style={{ background: '#ffecec', border: '1px solid #ffb3b3', padding: 8, borderRadius: 6 }}>
                <b style={{ color: '#cc0000' }}>Error:</b> {runError.message}
                {(runError.traceback || runLogs) && (
                  <details style={{ marginTop: 6 }}>
                    <summary>Trace / Logs</summary>
                    <pre style={{ whiteSpace: 'pre-wrap' }}>{runError.traceback || runLogs}</pre>
                  </details>
                )}
              </div>
            ) : lastOkRef.current ? (
              // GREEN success panel (shown even if logs are empty)
              <div style={{ background: '#eaffea', border: '1px solid #b3ffb3', padding: 8, borderRadius: 6 }}>
                <b style={{ color: '#00aa00' }}>Success</b>
                <pre style={{ whiteSpace: 'pre-wrap', marginTop: 6 }}>
                  {(runLogs && runLogs.trim()) ? runLogs : '✓ Completed successfully.'}
                </pre>
              </div>
            ) : runLogs ? (
              // Neutral logs (non-error, non-success)
              <div style={{ background: '#f7f7f7', border: '1px solid #ddd', padding: 8, borderRadius: 6 }}>
                <b style={{ color: '#333' }}>Logs</b>
                <pre style={{ whiteSpace: 'pre-wrap', marginTop: 6 }}>{runLogs}</pre>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </ReactFlowProvider>
  )
}

// light theme buttons / inputs
function btn(disabled = false, isLabel = false) {
  return {
    background: disabled ? '#e0e0e0' : '#f8f8f8',
    color: '#111111',
    border: '1px solid #ccc',
    padding: isLabel ? '6px 10px' : '6px 12px',
    borderRadius: 8,
    cursor: disabled ? 'not-allowed' : 'pointer'
  }
}

function input() {
  return {
    padding: '6px 8px',
    border: '1px solid #ccc',
    background: '#ffffff',
    color: '#111111',
    borderRadius: 8,
    outline: 'none'
  }
}
