import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import { CytoscapeNode, CytoscapeEdge, expandNode } from '../api/agent';

try {
  cytoscape.use(coseBilkent);
} catch (e) {
  // already registered
}

const NODE_COLORS: Record<string, string> = {
  Spec: '#1d9bf0',
  Feature: '#00ba7c',
  Whitepaper: '#f97316',
  Vendor: '#a855f7',
  Release: '#6b7280',
  Section: '#6b7280',
  ASN1Type: '#ef4444',
  Unknown: '#6b7280',
};

interface Props {
  nodes: CytoscapeNode[];
  edges: CytoscapeEdge[];
  onNodeExpand: (nodes: CytoscapeNode[], edges: CytoscapeEdge[]) => void;
}

export default function FeatureCloud({ nodes, edges, onNodeExpand }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'background-color': '#6b7280',
            color: '#e7e9ea',
            'font-size': '10px',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            width: 30,
            height: 30,
          },
        },
        {
          selector: 'edge',
          style: {
            label: 'data(label)',
            'line-color': '#4b5563',
            'target-arrow-color': '#4b5563',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'font-size': '8px',
            color: '#9ca3af',
          },
        },
        // Color-coded node types
        ...Object.entries(NODE_COLORS).map(([type, color]) => ({
          selector: `node[type="${type}"]`,
          style: { 'background-color': color },
        })),
      ],
      layout: { name: 'cose-bilkent', animate: false, nodeDimensionsIncludeLabels: true } as any,
    });

    cy.on('tap', 'node', async (evt) => {
      const nodeId = evt.target.data('id');
      try {
        const { nodes: newNodes, edges: newEdges } = await expandNode(nodeId);
        onNodeExpand(newNodes, newEdges);
      } catch (e) {
        console.error('Expand failed:', e);
      }
    });

    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      node.style('border-width', 3);
      node.style('border-color', '#fff');
    });

    cy.on('mouseout', 'node', (evt) => {
      evt.target.style('border-width', 0);
    });

    cyRef.current = cy;
    return () => { cy.destroy(); };
  }, []);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || (nodes.length === 0 && edges.length === 0)) return;

    // Add new elements without full re-render
    const existingNodeIds = new Set(cy.nodes().map(n => n.id()));
    const existingEdgeIds = new Set(cy.edges().map(e => e.id()));

    const newElements: cytoscape.ElementDefinition[] = [];

    for (const n of nodes) {
      if (!existingNodeIds.has(n.data.id)) {
        newElements.push({ group: 'nodes', data: n.data });
      }
    }
    for (const e of edges) {
      const edgeId = `${e.data.source}-${e.data.target}-${e.data.label}`;
      if (!existingEdgeIds.has(edgeId)) {
        newElements.push({ group: 'edges', data: { ...e.data, id: edgeId } });
      }
    }

    if (newElements.length > 0) {
      cy.add(newElements);
      cy.layout({ name: 'cose-bilkent', animate: true, animationDuration: 500, nodeDimensionsIncludeLabels: true } as any).run();
    }
  }, [nodes, edges]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
}
