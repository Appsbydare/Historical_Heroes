export interface Node {
  id: number;
  node_id: string;
  title: string;
  url: string;
  node_type: 'Event' | 'Person';
  degree: number;
  parent_url?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Session {
  id: number;
  session_name: string;
  seed_url: string;
  max_degree: number;
  total_nodes: number;
  status: 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  created_at: string;
}

export interface SessionSummary {
  session: Session;
  degree_counts: Record<number, { Event: number; Person: number }>;
}

export interface NetworkNode {
  id: string;
  title: string;
  node_type: 'Event' | 'Person';
  degree: number;
  description?: string;
  start_date?: string;
  end_date?: string;
  metadata?: Record<string, any>;
  x?: number;
  y?: number;
  fx?: number;
  fy?: number;
}

export interface NetworkLink {
  source: string;
  target: string;
  degree: number;
}

export interface NetworkData {
  nodes: NetworkNode[];
  links: NetworkLink[];
}

export interface ExtractionConfig {
  output_type: 'sql' | 'csv';
  seed_url: string;
  max_degree: number;
} 