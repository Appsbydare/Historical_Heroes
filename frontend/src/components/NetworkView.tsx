import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Network, Users, Calendar, Info, Database } from 'lucide-react';
import type { NetworkData, NetworkNode } from '../types';
import apiService from '../services/api';

const NetworkView = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [networkData, setNetworkData] = useState<NetworkData | null>(null);
  const [selectedSession, setSelectedSession] = useState<number | null>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (selectedSession) {
      loadNetworkData(selectedSession);
    }
  }, [selectedSession]);

  const loadSessions = async () => {
    try {
      const sessionsData = await apiService.getSessions();
      setSessions(sessionsData);
      if (sessionsData.length > 0) {
        setSelectedSession(sessionsData[0].id);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      setError('Failed to load sessions. Please check if the backend server is running.');
    }
  };

  const loadNetworkData = async (sessionId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getNetworkData(sessionId);
      setNetworkData(data);
      setExpandedNodes(new Set()); // Reset expanded nodes when loading new session
    } catch (error) {
      console.error('Failed to load network data:', error);
      setError('Failed to load network data. Please check if the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!networkData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;

    // Create zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        svg.select('g').attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Create main group for zoom/pan
    const g = svg.append('g');

    // Create force simulation
    const simulation = d3.forceSimulation(networkData.nodes)
      .force('link', d3.forceLink(networkData.links).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Create links
    const links = g.append('g')
      .selectAll('line')
      .data(networkData.links)
      .enter()
      .append('line')
      .attr('class', 'link')
      .attr('stroke-width', 1);

    // Create nodes
    const nodes = g.append('g')
      .selectAll('circle')
      .data(networkData.nodes)
      .enter()
      .append('circle')
      .attr('r', (d) => d.node_type === 'Event' ? 12 : 8)
      .attr('class', (d) => `node-${d.node_type.toLowerCase()}`)
      .style('cursor', 'pointer')
      .on('click', async (event, d) => {
        event.stopPropagation(); // Prevent zoom when clicking nodes
        await handleNodeClick(d);
      })
      .on('mouseover', function(event, d: any) {
        d3.select(this).attr('r', (d: any) => d.node_type === 'Event' ? 16 : 12);
        
        // Create tooltip with light background and dark text
        const tooltip = d3.select('body').append('div')
          .attr('class', 'absolute bg-white border border-gray-200 shadow-lg rounded-lg px-3 py-2 text-sm z-50')
          .style('pointer-events', 'none')
          .style('max-width', '250px');
        
        const expansionStatus = expandedNodes.has(d.id) ? '✓ Expanded' : 'Click to expand';
        
        tooltip.html(`
          <div class="font-semibold text-gray-900 mb-1">${d.title}</div>
          <div class="text-gray-700 mb-1">Type: ${d.node_type}</div>
          <div class="text-gray-700 mb-1">Degree: ${d.degree}</div>
          <div class="text-gray-600 text-xs">${expansionStatus}</div>
          ${d.description ? `<div class="text-gray-600 text-xs mt-1">${d.description.substring(0, 100)}${d.description.length > 100 ? '...' : ''}</div>` : ''}
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function(event, d: any) {
        d3.select(this).attr('r', (d: any) => d.node_type === 'Event' ? 12 : 8);
        d3.selectAll('div').filter(function() {
          return d3.select(this).classed('absolute') && d3.select(this).style('background-color') === 'rgb(255, 255, 255)';
        }).remove();
      });

    // Add labels
    const labels = g.append('g')
      .selectAll('text')
      .data(networkData.nodes)
      .enter()
      .append('text')
      .text((d) => d.title.length > 15 ? d.title.substring(0, 15) + '...' : d.title)
      .attr('x', 0)
      .attr('y', 0)
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .style('font-size', '10px')
      .style('pointer-events', 'none');

    // Update positions on simulation tick
    simulation.on('tick', () => {
      links
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      nodes
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      labels
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    // Cleanup function
    return () => {
      simulation.stop();
    };
  }, [networkData, expandedNodes]);

  const handleSessionChange = (sessionId: number) => {
    setSelectedSession(sessionId);
  };

  const handleNodeClick = async (node: NetworkNode) => {
    if (expandedNodes.has(node.id)) {
      // Node already expanded, collapse it
      const newExpandedNodes = new Set(expandedNodes);
      newExpandedNodes.delete(node.id);
      setExpandedNodes(newExpandedNodes);
    } else {
      // Expand node by loading related nodes
      try {
        setLoading(true);
        const expandedData = await apiService.expandNode(selectedSession!, node.id);
        
        // Merge new nodes and links with existing data
        const newNodes = [...networkData!.nodes];
        const newLinks = [...networkData!.links];
        
        // Add new nodes that aren't already present
        expandedData.nodes.forEach((newNode: NetworkNode) => {
          if (!newNodes.find(n => n.id === newNode.id)) {
            newNodes.push(newNode);
          }
        });
        
        // Add new links
        expandedData.links.forEach((newLink: any) => {
          if (!newLinks.find(l => l.source === newLink.source && l.target === newLink.target)) {
            newLinks.push(newLink);
          }
        });
        
        setNetworkData({
          nodes: newNodes,
          links: newLinks
        });
        
        // Mark node as expanded
        setExpandedNodes(new Set([...expandedNodes, node.id]));
        
      } catch (error) {
        console.error('Failed to expand node:', error);
        setError('Failed to expand node. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const renderEmptyState = () => (
    <div className="flex flex-col items-center justify-center h-96 text-center">
      <Database className="h-16 w-16 text-gray-400 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">No Network Data Available</h3>
      <p className="text-gray-600 mb-4 max-w-md">
        {sessions.length === 0 
          ? "No extraction sessions found. Start a new extraction to see network data."
          : "The selected session has no network data. Try selecting a different session or start a new extraction."
        }
      </p>
      <div className="space-x-4">
        <button
          onClick={() => window.location.href = '/extract'}
          className="btn-primary"
        >
          Start New Extraction
        </button>
        <button
          onClick={() => window.location.href = '/sessions'}
          className="btn-secondary"
        >
          View Sessions
        </button>
      </div>
    </div>
  );

  const renderErrorState = () => (
    <div className="flex flex-col items-center justify-center h-96 text-center">
      <div className="text-red-500 mb-4">
        <svg className="h-16 w-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">Connection Error</h3>
      <p className="text-gray-600 mb-4 max-w-md">
        {error}
      </p>
      <button
        onClick={() => window.location.reload()}
        className="btn-primary"
      >
        Retry
      </button>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Network Visualization</h2>
          <p className="text-gray-600">Interactive view of events and people relationships</p>
        </div>
        
        {/* Session Selector */}
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Session:</label>
          <select
            value={selectedSession || ''}
            onChange={(e) => handleSessionChange(Number(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            {sessions.map((session, index) => (
              <option key={`session-${session.id}-${index}`} value={session.id}>
                {session.session_name} ({session.total_nodes} nodes)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Network Stats */}
      {networkData && networkData.nodes.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <div className="flex items-center">
              <Network className="h-5 w-5 text-primary-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Nodes</p>
                <p className="text-2xl font-bold text-gray-900">{networkData.nodes.length}</p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <Users className="h-5 w-5 text-person-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-gray-600">People</p>
                <p className="text-2xl font-bold text-gray-900">
                  {networkData.nodes.filter(n => n.node_type === 'Person').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <Calendar className="h-5 w-5 text-event-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-gray-600">Events</p>
                <p className="text-2xl font-bold text-gray-900">
                  {networkData.nodes.filter(n => n.node_type === 'Event').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <Info className="h-5 w-5 text-gray-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-gray-600">Connections</p>
                <p className="text-2xl font-bold text-gray-900">{networkData.links.length}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Network Visualization */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Network Graph</h3>
          <div className="flex space-x-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-event-500"></div>
              <span className="text-sm text-gray-600">Events</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-person-500"></div>
              <span className="text-sm text-gray-600">People</span>
            </div>
          </div>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : error ? (
          renderErrorState()
        ) : !networkData || networkData.nodes.length === 0 ? (
          renderEmptyState()
        ) : (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
              <p className="text-sm text-gray-600">
                💡 <strong>Tip:</strong> Drag to pan • Scroll to zoom • Click nodes to expand/collapse
              </p>
            </div>
            <svg
              ref={svgRef}
              width="100%"
              height="600"
              className="bg-white cursor-grab active:cursor-grabbing"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default NetworkView; 