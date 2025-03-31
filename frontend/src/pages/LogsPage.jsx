import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { fetchLogs } from '../services/api';

const LogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const today = format(new Date(), 'yyyy-MM-dd');
  const [selectedDate, setSelectedDate] = useState(today);
  const [logTypes, setLogTypes] = useState(['api', 'llm', 'app']);
  const { logType } = useParams();
  const navigate = useNavigate();

  // Check if the user is authenticated
  useEffect(() => {
    const isAuth = localStorage.getItem('logs_authenticated') === 'true';
    setAuthenticated(isAuth);
    
    if (isAuth && !logType) {
      // If authenticated but no log type specified, default to 'api'
      navigate('/logs/api');
    }
  }, [logType, navigate]);

  // Handle authentication
  const handleLogin = (e) => {
    e.preventDefault();
    
    // Simple authentication check
    if (username === 'admin' && password === 'jd') {
      localStorage.setItem('logs_authenticated', 'true');
      setAuthenticated(true);
      
      // Navigate to a default log type if none specified
      if (!logType) {
        navigate('/logs/api');
      }
    } else {
      setError('Invalid username or password');
    }
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('logs_authenticated');
    setAuthenticated(false);
    setUsername('');
    setPassword('');
  };

  // Fetch logs when authenticated and log type changes
  useEffect(() => {
    if (!authenticated || !logType) return;

    const fetchLogsData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Create base64 encoded credentials for Basic Auth
        const credentials = btoa(`admin:jd`);
        
        // Use the API service to fetch logs
        const data = await fetchLogs(logType, selectedDate, credentials);
        console.log('Logs data received:', data);
        setLogs(data.logs || []);
      } catch (err) {
        console.error('Error fetching logs:', err);
        
        // Check if it's a 404 error
        if (err.message.includes('404')) {
          setError('Logs API endpoint not found. Make sure the backend server is running and the endpoint is correctly configured.');
        } else {
          setError(`Error fetching logs: ${err.message}`);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchLogsData();
  }, [authenticated, logType, selectedDate]);

  // Handle log type change
  const handleLogTypeChange = (type) => {
    navigate(`/logs/${type}`);
  };

  // Handle date change
  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    try {
      // Check if timestamp is a number (Unix timestamp)
      if (typeof timestamp === 'number') {
        const date = new Date(timestamp * 1000);
        return date.toLocaleString();
      }
      
      // Check if timestamp is a string (ISO format)
      if (typeof timestamp === 'string') {
        const date = new Date(timestamp);
        return date.toLocaleString();
      }
      
      // Default case
      return 'Invalid timestamp';
    } catch (e) {
      console.error('Error formatting timestamp:', e);
      return 'Invalid timestamp';
    }
  };

  // If not authenticated, show login form
  if (!authenticated) {
    return (
      <div className="min-h-screen bg-gray-100 py-12">
        <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">System Logs</h1>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}
          
          <form onSubmit={handleLogin}>
            <div className="mb-4">
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            
            <div className="mb-6">
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            
            <button
              type="submit"
              className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">System Logs</h1>
          
          <button
            onClick={handleLogout}
            className="py-2 px-4 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Logout
          </button>
        </div>
        
        <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
          <div className="p-4 border-b">
            <div className="flex flex-wrap items-center gap-4">
              <div>
                <label htmlFor="logType" className="block text-sm font-medium text-gray-700 mb-1">
                  Log Type
                </label>
                <div className="flex space-x-2">
                  {logTypes.map((type) => (
                    <button
                      key={type}
                      onClick={() => handleLogTypeChange(type)}
                      className={`py-1 px-3 rounded-md ${
                        logType === type
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {type.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <input
                  type="date"
                  id="date"
                  value={selectedDate}
                  onChange={handleDateChange}
                  className="px-3 py-1 border border-gray-300 rounded-md"
                />
              </div>
            </div>
          </div>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
        
        {loading ? (
          <div className="text-center py-12">
            <div className="spinner"></div>
            <p className="mt-4 text-gray-600">Loading logs...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="bg-white shadow-md rounded-lg p-6 text-center">
            <p className="text-gray-600">No logs found for the selected date and type.</p>
            <p className="mt-2 text-sm text-gray-500">
              Try selecting a different date or log type, or run the mock logs script to create test data.
            </p>
            <div className="mt-4 p-4 bg-gray-50 rounded-md text-left">
              <p className="text-sm font-medium text-gray-700">To create mock logs, run:</p>
              <pre className="mt-2 p-2 bg-gray-100 rounded text-sm overflow-x-auto">
                cd backend
                python create_test_log.py
              </pre>
            </div>
          </div>
        ) : (
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Level
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Message
                    </th>
                    {logType === 'api' && (
                      <>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Method
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Path
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Duration (ms)
                        </th>
                      </>
                    )}
                    {logType === 'llm' && (
                      <>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Operation
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Provider
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Duration (ms)
                        </th>
                      </>
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {logs.map((log, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatTimestamp(log.timestamp)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          log.level === 'ERROR' ? 'bg-red-100 text-red-800' :
                          log.level === 'WARNING' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {log.level}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">
                        {log.message}
                      </td>
                      {logType === 'api' && log.data && (
                        <>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.data.method || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.data.path || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            {log.data.status_code && (
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                log.data.status_code >= 400 ? 'bg-red-100 text-red-800' :
                                log.data.status_code >= 300 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-green-100 text-green-800'
                              }`}>
                                {log.data.status_code}
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.data.duration_ms ? log.data.duration_ms.toFixed(2) : '-'}
                          </td>
                        </>
                      )}
                      {logType === 'llm' && log.data && (
                        <>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.data.operation || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.data.provider || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.data.duration_ms ? log.data.duration_ms.toFixed(2) : '-'}
                          </td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LogsPage; 