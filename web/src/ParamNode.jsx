import { Handle, Position } from 'reactflow'

function stopBubbleProps() {
  // helper to keep nodes draggable normally, but NOT when you interact with inputs
  return {
    className: 'nodrag nowheel',
    onMouseDown: (e) => e.stopPropagation(),
    onPointerDown: (e) => e.stopPropagation(),
    onClick: (e) => e.stopPropagation(),
  }
}

function PromptArrayEditor({ value = [], onChange }) {
  const update = (i, patch) => {
    const next = value.slice()
    next[i] = { ...next[i], ...patch }
    onChange(next)
  }
  const remove = (i) => {
    const next = value.slice()
    next.splice(i, 1)
    onChange(next)
  }
  const add = () => onChange([...(value || []), { type: 'text', content: '' }])

  return (
    <div style={{ display:'grid', gap:8 }}>
      {(value || []).map((blk, i) => (
        <div key={i} style={{ border:'1px solid #eee', borderRadius:8, padding:8 }}>
          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <label style={{ fontSize:12 }}>type</label>
            <select
              {...stopBubbleProps()}
              value={blk.type || 'text'}
              onChange={(e)=>update(i, { type: e.target.value })}
            >
              <option value="text">text</option>
              <option value="image">image</option>
            </select>
            <button {...stopBubbleProps()} onClick={()=>remove(i)} style={{ marginLeft:'auto' }}>✕</button>
          </div>
          <label style={{ display:'grid', gap:4, marginTop:6 }}>
            <span style={{ fontSize:12 }}>content</span>
            <input
              {...stopBubbleProps()}
              value={blk.content || ''}
              onChange={(e)=>update(i, { content: e.target.value })}
              style={{ padding:'6px 8px', border:'1px solid #ddd', borderRadius:6 }}
            />
          </label>
          {blk.type === 'image' && (
            <label style={{ display:'flex', gap:6, alignItems:'center', marginTop:6 }}>
              <input
                {...stopBubbleProps()}
                type="checkbox"
                checked={!!blk.detailed}
                onChange={(e)=>update(i, { detailed: e.target.checked })}
              />
              <span style={{ fontSize:12 }}>detailed</span>
            </label>
          )}
        </div>
      ))}
      <button {...stopBubbleProps()} onClick={add}>+ add prompt block</button>
    </div>
  )
}

export default function ParamNode({ id, data }) {
  const { nodeType, params = {}, onParamChange } = data

  const renderField = (k, v) => {
    if (nodeType === 'Start' || nodeType === 'End') {
      return <div style={{ fontSize:12, color:'#666' }}>no params</div>
    }
    if (nodeType === 'GPTChat' && k === 'prompt') {
      return <PromptArrayEditor value={v} onChange={(val)=>onParamChange(id, k, val)} />
    }
    const t = typeof v
    if (t === 'boolean') {
      return (
        <label style={{ display:'flex', gap:8, alignItems:'center' }}>
          <input
            {...stopBubbleProps()}
            type="checkbox"
            checked={!!v}
            onChange={(e)=>onParamChange(id, k, e.target.checked)}
          />
          <span style={{ fontSize:12 }}>boolean</span>
        </label>
      )
    }
    if (t === 'number') {
      return (
        <input
          {...stopBubbleProps()}
          type="number"
          value={v}
          onChange={(e)=>onParamChange(id, k, Number(e.target.value))}
          style={{ padding:'6px 8px', border:'1px solid #ddd', borderRadius:6 }}
        />
      )
    }
    if (t === 'string') {
      return (
        <input
          {...stopBubbleProps()}
          value={v}
          onChange={(e)=>onParamChange(id, k, e.target.value)}
          style={{ padding:'6px 8px', border:'1px solid #ddd', borderRadius:6 }}
        />
      )
    }
    // fallback JSON editor
    return (
      <textarea
        {...stopBubbleProps()}
        value={JSON.stringify(v ?? {}, null, 2)}
        onChange={(e)=>{ try { onParamChange(id, k, JSON.parse(e.target.value)) } catch {} }}
        style={{ fontFamily:'monospace', minHeight:100, padding:8, border:'1px solid #ddd', borderRadius:6 }}
      />
    )
  }

  return (
    <div style={{ background:'#fff', border:'1px solid #ccc', borderRadius:10, boxShadow:'0 2px 8px rgba(0,0,0,.06)', padding:10, width:360 }}>
      <div style={{ fontWeight:700, marginBottom:8 }}>{nodeType}</div>

      {nodeType!=='Start' && <Handle id="in" type="target" position={Position.Left} />}
      {nodeType!=='End'   && <Handle id="out" type="source" position={Position.Right} />}

      {Object.keys(params).length>0 && (
        <div style={{ display:'grid', gap:10, marginTop:8 }}>
          {Object.entries(params).map(([k,v]) => (
            <div key={k}>
              <div style={{ marginBottom:4, fontSize:12, color:'#444' }}>{k}</div>
              {renderField(k, v)}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
