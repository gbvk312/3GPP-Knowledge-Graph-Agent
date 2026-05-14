import { useEffect, useRef, useCallback } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import { CytoscapeNode, CytoscapeEdge, expandNode } from '../api/agent';

try { cytoscape.use(coseBilkent); } catch (_) { /* already registered */ }

const NODE_COLORS: Record<string, string> = {
  Spec: '#1d9bf0',
  Feature: '#00ba7c',
  Whitepaper: '#f97316',
  Vendor: '#a855f7',
  Release: '#6b7280',
  ASN1Type: '#ef4444',
};

function getThemeColors() {
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  return {
    textColor: isLight ? '#111827' : '#e7e9ea',
    textOutline: isLight ? '#ffffff' : '#0f1419',
    edgeColor: isLight ? '#d1d5db' : '#374151',
  };
}

interface Props {
  nodes: CytoscapeNode[];
  edges: CytoscapeEdge[];
  onNodeSelect: (nodeId: string) => void;
  onNodeExpand: (nodes: CytoscapeNode[], edges: CytoscapeEdge[]) => void;
}

export default function FeatureCloud({ nodes, edges, onNodeSelect, onNodeExpand }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  const handleZoomIn = useCallback(() => { cyRef.current?.zoom(cyRef.current.zoom() * 1.3); }, []);
  const handleZoomOut = useCallback(() => { cyRef.current?.zoom(cyRef.current.zoom() * 0.7); }, []);
  const handleFit = useCallback(() => { cyRef.current?.fit(undefined, 40); }, []);
  const handleReset = useCallback(() => {
    const cy = cyRef.current;
    if (cy) cy.layout({ name: 'cose-bilkent', animate: true, animationDuration: 600, nodeDimensionsIncludeLabels: true } as any).run();
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    const { textColor, textOutline, edgeColor } = getThemeColors();

    const cy = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'background-color': '#6b7280',
            color: textColor,
            'font-size': '9px',
            'text-valign': 'bottom',
            'text-margin-y': 5,
            'text-outline-color': textOutline,
            'text-outline-width': 2,
            width: 'data(size)',
            height: 'data(size)',
            'border-width': 0,
            'border-color': '#fff',
            'transition-property': 'border-width, border-color, width, height',
            'transition-duration': 150,
          } as any,
        },
        {
          selector: 'edge',
          style: {
            'line-color': edgeColor,
            'target-arrow-color': edgeColor,
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            width: 1.5,
            opacity: 0.6,
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
          style: {
            'border-width': 3,
            'border-color': '#fbbf24',
          },
        },
        {
          selector: 'node.highlighted',
          style: {
            'border-width': 2,
            'border-color': '#fff',
          },
        },
        {
          selector: 'node.dimmed',
          style: { opacity: 0.2 },
        },
        {
          selector: 'edge.dimmed',
          style: { opacity: 0.08 },
        },
        ...Object.entries(NODE_COLORS).map(([type, color]) => ({
          selector: `node[type="${type}"]`,
          style: { 'background-color': color },
        })),
      ],
      layout: { name: 'cose-bilkent', animate: false, nodeDimensionsIncludeLabels: true, idealEdgeLength: 120, nodeRepulsion: 8000 } as any,
      minZoom: 0.2,
      maxZoom: 4,
    });

    // Node click → select
    cy.on('tap', 'node', (evt) => {
      const nodeId = evt.target.data('id');
      onNodeSelect(nodeId);
      // Highlight neighbors
      cy.elements().removeClass('highlighted dimmed');
      const selected = evt.target;
      const neighborhood = selected.neighborhood().add(selected);
      cy.elements().not(neighborhood).addClass('dimmed');
      neighborhood.nodes().addClass('highlighted');
    });

    // Double-click → expand
    cy.on('dbltap', 'node', async (evt) => {
      const nodeId = evt.target.data('id');
      try {
        const { nodes: n, edges: e } = await expandNode(nodeId);
        onNodeExpand(n, e);
      } catch (err) {
        console.error('Expand failed:', err);
      }
    });

    // Edge hover → show label
    cy.on('mouseover', 'edge', (evt) => { evt.target.addClass('hover'); });
    cy.on('mouseout', 'edge', (evt) => { evt.target.removeClass('hover'); });

    // Background click → clear selection
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass('highlighted dimmed');
      }
    });

    cyRef.current = cy;
    return () => { cy.destroy(); };
  }, []);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    // Compute degree for sizing
    const degree: Record<string, number> = {};
    edges.forEach(e => {
      degree[e.data.source] = (degree[e.data.source] || 0) + 1;
      degree[e.data.target] = (degree[e.data.target] || 0) + 1;
    });
    const maxDeg = Math.max(...Object.values(degree), 1);

    // Clear and rebuild
    cy.elements().remove();

    const elements: cytoscape.ElementDefinition[] = [];
    for (const n of nodes) {
      const d = degree[n.data.id] || 0;
      const size = 20 + (d / maxDeg) * 35;
      elements.push({ group: 'nodes', data: { ...n.data, size } });
    }
    for (const e of edges) {
      const edgeId = `${e.data.source}-${e.data.target}-${e.data.label}`;
      elements.push({ group: 'edges', data: { ...e.data, id: edgeId } });
    }

    if (elements.length > 0) {
      cy.add(elements);
      cy.layout({ name: 'cose-bilkent', animate: true, animationDuration: 800, nodeDimensionsIncludeLabels: true, idealEdgeLength: 120, nodeRepulsion: 8000 } as any).run();
    }
  }, [nodes, edges]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      <div className="zoom-controls">
        <button onClick={handleZoomIn} title="Zoom in">+</button>
        <button onClick={handleZoomOut} title="Zoom out">−</button>
        <button onClick={handleFit} title="Fit to view">⊡</button>
        <button onClick={handleReset} title="Reset layout">↻</button>
      </div>
    </div>
  );
}
