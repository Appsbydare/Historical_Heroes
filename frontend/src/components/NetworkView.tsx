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

    // Create force simulation with better positioning
    const simulation = d3.forceSimulation(networkData.nodes)
      .force('link', d3.forceLink(networkData.links).id((d: any) => d.id).distance(120)) // Increased distance for bigger nodes
      .force('charge', d3.forceManyBody().strength(-400)) // Stronger repulsion
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: any) => d.node_type === 'Event' ? 45 : 20)); // Much bigger collision radius for Events

    // Create links with better styling
    const links = g.append('g')
      .selectAll('line')
      .data(networkData.links)
      .enter()
      .append('line')
      .attr('class', 'link')
      .attr('stroke', '#666')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6);

    // Create nodes with proper colors
    const nodes = g.append('g')
      .selectAll('circle')
      .data(networkData.nodes)
      .enter()
      .append('circle')
      .attr('r', (d) => d.node_type === 'Event' ? 35 : 12) // Much bigger for Events
      .attr('fill', (d) => d.node_type === 'Event' ? '#000000' : '#90EE90') // Black for Events, Light Green for People
      .attr('stroke', (d) => d.node_type === 'Event' ? '#333' : '#228B22')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', async (event, d) => {
        event.stopPropagation(); // Prevent zoom when clicking nodes
        
        // Get click position relative to the SVG
        const clickX = event.clientX;
        const clickY = event.clientY;
        
        console.log('Node clicked at position:', clickX, clickY);
        await handleNodeClick(d);
      })
      .on('mouseover', function(event, d: any) {
        // Increase size on hover
        d3.select(this).attr('r', (d: any) => d.node_type === 'Event' ? 40 : 15);
        
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
        // Reset size
        d3.select(this).attr('r', (d: any) => d.node_type === 'Event' ? 35 : 12);
        d3.selectAll('div').filter(function() {
          return d3.select(this).classed('absolute') && d3.select(this).style('background-color') === 'rgb(255, 255, 255)';
        }).remove();
      });

    // Add labels with wrapped text for Events
    const labels = g.append('g')
      .selectAll('text')
      .data(networkData.nodes)
      .enter()
      .append('text')
      .attr('x', (d: any) => d.x || 0)
      .attr('y', (d: any) => d.y || 0)
      .attr('text-anchor', 'middle')
      .style('font-size', (d) => d.node_type === 'Event' ? '12px' : '10px') // Bigger font for Events
      .style('fill', (d) => d.node_type === 'Event' ? '#ffffff' : '#000000') // White text for black nodes, black text for green nodes
      .style('pointer-events', 'none')
      .style('font-weight', (d) => d.node_type === 'Event' ? 'bold' : 'normal') // Bold for Events
      .style('opacity', 0) // Start invisible
      .each(function(d: any) {
        const text = d3.select(this);
        const words: string[] = d.title.split(' ');
        const maxWidth = d.node_type === 'Event' ? 60 : 60; // Bigger width for Events
        
        if (d.node_type === 'Event') {
          // For Events, wrap text inside the circle
          let line = '';
          let lines: string[] = [];
          
          words.forEach((word: string) => {
            const testLine = line + word + ' ';
            if (testLine.length * 6 > maxWidth) { // Approximate character width
              lines.push(line);
              line = word + ' ';
            } else {
              line = testLine;
            }
          });
          lines.push(line);
          
          // Clear existing text and add wrapped lines
          text.text('');
          text.style('font-weight', 'bold'); // Bold for Events
          text.attr('dy', '0.35em'); // Center vertically in circle
          text.style('text-anchor', 'middle'); // Ensure horizontal centering
          text.style('fill', '#ffffff'); // Ensure white color for the main text element
          lines.forEach((line: string, i: number) => {
            text.append('tspan')
              .attr('x', 0)
              .attr('dy', i === 0 ? '-0.3em' : '1.2em')
              .style('fill', '#ffffff') // Ensure white color
              .style('font-weight', 'bold')
              .style('text-anchor', 'middle') // Ensure each line is centered
              .style('font-size', '12px') // Larger font size for better visibility
              .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)') // Add text shadow for better contrast
              .text(line.trim());
          });
        } else {
          // For People, position text above the node
          text.text(d.title.length > 12 ? d.title.substring(0, 12) + '...' : d.title);
          text.style('font-weight', 'normal'); // Not bold for People
          text.attr('dy', '-1.2em'); // Position above the node
          text.style('text-anchor', 'middle'); // Ensure horizontal centering
          text.style('font-size', '10px'); // Ensure consistent font size
          text.style('fill', '#000000'); // Ensure black color for visibility
          text.style('text-shadow', '1px 1px 2px rgba(255,255,255,0.8)'); // Add white shadow for better contrast
        }
      });

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
        .attr('y', (d: any) => d.y)
        .style('opacity', 1); // Make visible once positioned
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
    console.log('Node clicked:', node); // Debug log
    
    if (expandedNodes.has(node.id)) {
      console.log('Node already expanded, collapsing:', node.id); // Debug log
      // Node already expanded, collapse it
      const newExpandedNodes = new Set(expandedNodes);
      newExpandedNodes.delete(node.id);
      setExpandedNodes(newExpandedNodes);
    } else {
      console.log('Expanding node:', node.id, 'Session:', selectedSession); // Debug log
      // Expand node by loading related nodes
      try {
        setLoading(true);
        console.log('Calling API to expand node...'); // Debug log
        const expandedData = await apiService.expandNode(selectedSession!, node.id);
        console.log('API response:', expandedData); // Debug log
        
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
          const linkExists = newLinks.find(l => 
            (l.source === newLink.source && l.target === newLink.target) ||
            (l.source === newLink.target && l.target === newLink.source)
          );
          if (!linkExists) {
            newLinks.push(newLink);
          }
        });
        
        console.log('Updated network data - Nodes:', newNodes.length, 'Links:', newLinks.length); // Debug log
        
        // Update the network data to trigger re-render
        setNetworkData({
          nodes: newNodes,
          links: newLinks
        });
        
        // Mark node as expanded
        setExpandedNodes(new Set([...expandedNodes, node.id]));
        
        // Force a small delay to ensure state updates
        setTimeout(() => {
          console.log('Network updated with new links!');
        }, 100);
        
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
          <label htmlFor="session-select" className="text-sm font-medium text-gray-700">Session:</label>
          <select
            id="session-select"
            value={selectedSession || ''}
            onChange={(e) => handleSessionChange(Number(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            aria-label="Select a session to view network data"
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