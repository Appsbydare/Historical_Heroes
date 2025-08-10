import { useState } from 'react';
import { Play, Square, Database, FileText, Settings } from 'lucide-react';
import type { ExtractionConfig } from '../types';
import apiService from '../services/api';

const ExtractionManager = () => {
  const [config, setConfig] = useState<ExtractionConfig>({
    output_type: 'sql',
    seed_url: 'https://en.wikipedia.org/wiki/Korean_War',
    max_degree: 3,
  });
  
  const [isExtracting, setIsExtracting] = useState(false);
  const [currentSession, setCurrentSession] = useState<number | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);

  const handleStartExtraction = async () => {
    setIsExtracting(true);
    setLogs([]);
    setProgress(0);
    
    try {
      const result = await apiService.startExtraction(config);
      setCurrentSession(result.session_id);
      setLogs(prev => [...prev, `Started extraction session ${result.session_id}`]);
      
      // Poll for status updates
      const pollInterval = setInterval(async () => {
        try {
          const status = await apiService.getExtractionStatus(result.session_id);
          setProgress(status.progress);
          setLogs(prev => [...prev, `Progress: ${status.progress}% - ${status.status}`]);
          
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(pollInterval);
            setIsExtracting(false);
            setLogs(prev => [...prev, `Extraction ${status.status}`]);
          }
        } catch (error) {
          console.error('Failed to get status:', error);
        }
      }, 2000);
      
    } catch (error) {
      console.error('Failed to start extraction:', error);
      setLogs(prev => [...prev, `Error: ${error}`]);
      setIsExtracting(false);
    }
  };

  const handleStopExtraction = async () => {
    if (currentSession) {
      try {
        await apiService.stopExtraction(currentSession);
        setLogs(prev => [...prev, 'Extraction stopped by user']);
        setIsExtracting(false);
      } catch (error) {
        console.error('Failed to stop extraction:', error);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Extraction Manager</h2>
        <p className="text-gray-600">Start new Wikipedia data extractions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Settings className="h-5 w-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Configuration</h3>
          </div>

          <div className="space-y-4">
            {/* Output Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Output Type
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="sql"
                    checked={config.output_type === 'sql'}
                    onChange={(e) => setConfig(prev => ({ ...prev, output_type: e.target.value as 'sql' | 'csv' }))}
                    className="mr-2"
                  />
                  <Database className="h-4 w-4 mr-1" />
                  SQL Database
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="csv"
                    checked={config.output_type === 'csv'}
                    onChange={(e) => setConfig(prev => ({ ...prev, output_type: e.target.value as 'sql' | 'csv' }))}
                    className="mr-2"
                  />
                  <FileText className="h-4 w-4 mr-1" />
                  CSV File
                </label>
              </div>
            </div>

            {/* Seed URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Seed URL
              </label>
              <input
                type="url"
                value={config.seed_url}
                onChange={(e) => setConfig(prev => ({ ...prev, seed_url: e.target.value }))}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                placeholder="https://en.wikipedia.org/wiki/..."
              />
            </div>

            {/* Max Degree */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Degree
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={config.max_degree}
                onChange={(e) => setConfig(prev => ({ ...prev, max_degree: parseInt(e.target.value) }))}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">
                Number of "hops" from the seed event (higher = more data, longer time)
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4 pt-4">
              <button
                onClick={handleStartExtraction}
                disabled={isExtracting}
                className="btn-primary flex items-center"
              >
                <Play className="h-4 w-4 mr-2" />
                Start Extraction
              </button>
              
              {isExtracting && (
                <button
                  onClick={handleStopExtraction}
                  className="btn-secondary flex items-center"
                >
                  <Square className="h-4 w-4 mr-2" />
                  Stop
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Progress Panel */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Database className="h-5 w-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Progress</h3>
          </div>

          {isExtracting && (
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Logs */}
          <div className="bg-gray-50 rounded-lg p-4 h-64 overflow-y-auto">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Logs</h4>
            {logs.length === 0 ? (
              <p className="text-gray-500 text-sm">No logs yet. Start an extraction to see progress.</p>
            ) : (
              <div className="space-y-1">
                {logs.map((log, index) => (
                  <div key={index} className="text-xs text-gray-600 font-mono">
                    {log}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">How it works</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">1. Seed Event</h4>
            <p>Start with a Wikipedia event page (e.g., Korean War)</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">2. Traversal</h4>
            <p>Extract people from events, then events from people, up to max degree</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">3. Network</h4>
            <p>Build a network of connected events and people for visualization</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExtractionManager; 