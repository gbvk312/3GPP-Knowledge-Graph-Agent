import { useEffect, useRef, useCallback, useState, useImperativeHandle, forwardRef } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import { CytoscapeNode, CytoscapeEdge, expandNode } from '../api/agent';
import GraphSearch from './GraphSearch';
import ExportControls from './ExportControls';
import AccessibleGraphView from './AccessibleGraphView';

try { cytoscape.use(coseBilkent); } catch (_) { /* already registered */ }

const NODE_COLORS: Record<string, string> = {
  Spec: '#3b82f6',
  Feature: '#10b981',
  Whitepaper: '#f97316',
  Vendor: '#a855f7',
  Release: '#6b7280',
  ASN1Type: '#ef4444',
};

// Different shapes for colorblind accessibility
const NODE_SHAPES: Record<string, string> = {
  Spec: 'ellipse',
  Feature: 'diamond',
  Whitepaper: 'rectangle',
  Vendor: 'triangle',
  Release: 'ellipse',
  ASN1Type: 'star',
};

function getThemeColors() {
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  return {
    textColor: isLight ? '#1e293b' : '#7a8ba0',
    textOutline: isLight ? '#ffffff' : '#0a0e14',
    edgeColor: isLight ? '#94a3b8' : 'rgba(255,255,255,0.15)',
    edgeArrowColor: isLight ? '#64748b' : 'rgba(255,255,255,0.18)',
  };
}

function buildStyles() {
  const { textColor, textOutline, edgeColor, edgeArrowColor } = getThemeColors();
  return [
    {
      selector: 'node',
      style: {
        label: 'data(label)',
        'background-color': '#6b7280',
        color: textColor,
        'font-size': '9px',
        'font-weight': 500,
        'text-valign': 'bottom',
        'text-margin-y': 6,
        'text-outline-color': textOutline,
        'text-outline-width': 2,
        width: 'data(size)',
        height: 'data(size)',
        shape: 'ellipse',
        'border-width': 0,
        'border-color': '#fff',
        'transition-property': 'border-width, border-color, width, height, opacity',
        'transition-duration': 200,
      } as any,
    },
    {
      selector: 'edge',
      style: {
        'line-color': edgeColor,
        'target-arrow-color': edgeArrowColor,
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        width: 1.5,
        opacity: 0.75,
      },
    },
    {
      selector: 'edge:active, edge.hover',
      style: {
        label: 'data(label)',
        'font-size': '8px',
        color: textColor,
        'text-outline-color': textOutline,
        'text-outline-width': 1.5,
        opacity: 1,
        width: 2.5,
      } as any,
    },
    {
      selector: 'node:selected',
      style: { 'border-width': 3, 'border-color': '#fbbf24' },
    },
    {
      selector: 'node.highlighted',
      style: { 'border-width': 2, 'border-color': 'rgba(255,255,255,0.6)' },
    },
    {
      selector: 'node.search-match',
      style: { 'border-width': 3, 'border-color': '#fbbf24', 'border-opacity': 1 },
    },
    { selector: 'node.dimmed', style: { opacity: 0.15 } },
    { selector: 'edge.dimmed', style: { opacity: 0.05 } },
    ...Object.entries(NODE_COLORS).map(([type, color]) => ({
      selector: `node[type="${type}"]`,
      style: { 'background-color': color, shape: NODE_SHAPES[type] || 'ellipse' },
    })),
  ] as any[];
}

export interface FeatureCloudHandle {
  exportPng: () => void;
}

interface Props {
  nodes: CytoscapeNode[];
  edges: CytoscapeEdge[];
  onNodeSelect: (nodeId: string) => void;
  onNodeExpand: (nodes: CytoscapeNode[], edges: CytoscapeEdge[]) => void;
  responseSummary?: string;
}

const FeatureCloud = forwardRef<FeatureCloudHandle, Props>(({ nodes, edges, onNodeSelect, onNodeExpand, responseSummary }, ref) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; text: string } | null>(null);
  const [a11yView, setA11yView] = useState(false);

  const handleZoomIn = useCallback(() => { cyRef.current?.zoom(cyRef.current.zoom() * 1.3); }, []);
  const handleZoomOut = useCallback(() => { cyRef.current?.zoom(cyRef.current.zoom() * 0.7); }, []);
  const handleFit = useCallback(() => { cyRef.current?.fit(undefined, 50); }, []);
  const handleReset = useCallback(() => {
    const cy = cyRef.current;
    if (cy) cy.layout({ name: 'cose-bilkent', animate: true, animationDuration: 700, nodeDimensionsIncludeLabels: true, idealEdgeLength: 140, nodeRepulsion: 9000 } as any).run();
  }, []);

  const handleExportPng = useCallback(() => {
    const cy = cyRef.current;
    if (!cy) return;
    const png = cy.png({ full: true, scale: 2, bg: getThemeColors().textOutline });
    const link = document.createElement('a');
    link.href = png;
    link.download = '3gpp-graph.png';
    link.click();
  }, []);

  const handleCopyResponse = useCallback(() => {
    if (responseSummary) navigator.clipboard.writeText(responseSummary);
  }, [responseSummary]);

  const handleShareUrl = useCallback(() => {
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);
    const q = params.get('q');
    if (q) {
      navigator.clipboard.writeText(window.location.href);
    } else {
      navigator.clipboard.writeText(window.location.href);
    }
  }, []);

  const handleGraphSearch = useCallback((label: string) => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.elements().removeClass('search-match dimmed');
    const matched = cy.nodes().filter(n => n.data('label').toLowerCase().includes(label.toLowerCase()));
    if (matched.length > 0) {
      cy.elements().not(matched).addClass('dimmed');
      matched.addClass('search-match');
      cy.animate({ fit: { eles: matched, padding: 80 } } as any, { duration: 500 });
    }
  }, []);

  const handleGraphSearchClear = useCallback(() => {
    const cy = cyRef.current;
    if (cy) cy.elements().removeClass('search-match dimmed');
  }, []);

  useImperativeHandle(ref, () => ({ exportPng: handleExportPng }), [handleExportPng]);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      style: buildStyles(),
      layout: { name: 'cose-bilkent', animate: false, nodeDimensionsIncludeLabels: true, idealEdgeLength: 140, nodeRepulsion: 9000 } as any,
      minZoom: 0.2,
      maxZoom: 4,
    });

    cy.on('tap', 'node', (evt) => {
      const nodeId = evt.target.data('id');
      onNodeSelect(nodeId);
      cy.elements().removeClass('highlighted dimmed search-match');
      const neighborhood = evt.target.neighborhood().add(evt.target);
      cy.elements().not(neighborhood).addClass('dimmed');
      neighborhood.nodes().addClass('highlighted');
    });

    cy.on('dbltap', 'node', async (evt) => {
      const nodeId = evt.target.data('id');
      try {
        const { nodes: n, edges: e } = await expandNode(nodeId);
        onNodeExpand(n, e);
      } catch (err) {
        console.error('Expand failed:', err);
      }
    });

    cy.on('mouseover', 'edge', (evt) => {
      evt.target.addClass('hover');
      const edge = evt.target;
      const pos = edge.midpoint();
      const container = containerRef.current!.getBoundingClientRect();
      const pan = cy.pan();
      const zoom = cy.zoom();
      setTooltip({
        x: pos.x * zoom + pan.x + container.left,
        y: pos.y * zoom + pan.y + container.top - 30,
        text: `${edge.data('source')} → ${edge.data('label')} → ${edge.data('target')}`,
      });
    });
    cy.on('mouseout', 'edge', (evt) => {
      evt.target.removeClass('hover');
      setTooltip(null);
    });

    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      const pos = node.renderedPosition();
      const container = containerRef.current!.getBoundingClientRect();
      setTooltip({
        x: pos.x + container.left,
        y: pos.y + container.top - 40,
        text: `${node.data('label')} (${node.data('type')})`,
      });
    });
    cy.on('mouseout', 'node', () => { setTooltip(null); });

    cy.on('tap', (evt) => {
      if (evt.target === cy) cy.elements().removeClass('highlighted dimmed search-match');
    });

    cyRef.current = cy;
    return () => { cy.destroy(); };
  }, []);

  // Watch for theme changes
  useEffect(() => {
    const observer = new MutationObserver(() => {
      const cy = cyRef.current;
      if (cy) cy.style(buildStyles() as any);
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    return () => observer.disconnect();
  }, []);

  // Update graph data
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    const degree: Record<string, number> = {};
    edges.forEach(e => {
      degree[e.data.source] = (degree[e.data.source] || 0) + 1;
      degree[e.data.target] = (degree[e.data.target] || 0) + 1;
    });
    const maxDeg = Math.max(...Object.values(degree), 1);

    cy.elements().remove();
    const elements: cytoscape.ElementDefinition[] = [];
    for (const n of nodes) {
      const d = degree[n.data.id] || 0;
      const size = 22 + (d / maxDeg) * 38;
      elements.push({ group: 'nodes', data: { ...n.data, size } });
    }
    for (const e of edges) {
      elements.push({ group: 'edges', data: { ...e.data, id: `${e.data.source}-${e.data.target}-${e.data.label}` } });
    }

    if (elements.length > 0) {
      cy.add(elements);
      cy.layout({ name: 'cose-bilkent', animate: true, animationDuration: 900, nodeDimensionsIncludeLabels: true, idealEdgeLength: 140, nodeRepulsion: 9000 } as any).run();
    }
  }, [nodes, edges]);

  const nodeLabels = nodes.map(n => n.data.label);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {!a11yView && <div ref={containerRef} style={{ width: '100%', height: '100%' }} />}

      <AccessibleGraphView nodes={nodes} edges={edges} visible={a11yView} onToggle={() => setA11yView(!a11yView)} />

      {nodes.length > 0 && (
        <div className="graph-toolbar">
          <GraphSearch nodeLabels={nodeLabels} onHighlight={handleGraphSearch} onClear={handleGraphSearchClear} />
          <ExportControls
            onExportPng={handleExportPng}
            onCopyResponse={handleCopyResponse}
            onShareUrl={handleShareUrl}
            hasResponse={!!responseSummary}
          />
        </div>
      )}

      <div className="zoom-controls">
        <button onClick={handleZoomIn} title="Zoom in (Ctrl++)">+</button>
        <button onClick={handleZoomOut} title="Zoom out (Ctrl+-)">−</button>
        <button onClick={handleFit} title="Fit to view (Ctrl+0)">⊡</button>
        <button onClick={handleReset} title="Reset layout (Ctrl+R)">↻</button>
      </div>

      {tooltip && (
        <div className="graph-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
          {tooltip.text}
        </div>
      )}
    </div>
  );
});

FeatureCloud.displayName = 'FeatureCloud';
export default FeatureCloud;
