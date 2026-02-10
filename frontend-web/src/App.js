import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, 
         BarElement, Title, Tooltip, Legend, LineElement, PointElement } from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import axios from 'axios';
import './App.css';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, 
                LineElement, PointElement, Title, Tooltip, Legend);

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [selectedEquipment, setSelectedEquipment] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [viewMode, setViewMode] = useState('grid'); // grid or table

  useEffect(() => {
    if (authenticated) {
      loadHistory();
    }
  }, [authenticated]);

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/datasets/history/`, {
        auth: { username, password }
      });
      setHistory(response.data.datasets || []);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Please enter username and password');
      return;
    }

    try {
      await axios.get(`${API_URL}/datasets/`, {
        auth: { username, password }
      });
      setAuthenticated(true);
    } catch (error) {
      setError('Login failed! Check your credentials.');
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && !selectedFile.name.endsWith('.csv')) {
      setError('Please select a CSV file');
      setFile(null);
      return;
    }
    setFile(selectedFile);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `${API_URL}/datasets/upload_csv/`,
        formData,
        {
          auth: { username, password },
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      setData(response.data);
      setError('');
      loadHistory();
      alert('✅ File uploaded successfully!');
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message || 'Upload failed';
      const details = error.response?.data?.details;
      
      if (details && Array.isArray(details)) {
        setError(`❌ ${errorMsg}\n\nDetails:\n${details.join('\n')}`);
      } else {
        setError(`❌ ${errorMsg}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async (datasetId) => {
    try {
      setError('');
      const response = await axios.get(
        `${API_URL}/datasets/${datasetId}/generate_pdf/`,
        {
          auth: { username, password },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${datasetId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      alert('✅ PDF downloaded successfully!');
    } catch (error) {
      setError('❌ PDF generation failed');
    }
  };

  const handleLogout = () => {
    setAuthenticated(false);
    setUsername('');
    setPassword('');
    setData(null);
    setHistory([]);
    setFile(null);
    setError('');
    setSelectedEquipment(null);
  };

  const handleEquipmentClick = (equipment) => {
    setSelectedEquipment(equipment);
  };

  const closeModal = () => {
    setSelectedEquipment(null);
  };

  const getHealthColor = (score) => {
    if (score >= 80) return '#11998e';
    if (score >= 60) return '#f39c12';
    return '#e74c3c';
  };

  const getHealthStatus = (score) => {
    if (score >= 80) return '✅ Good';
    if (score >= 60) return '⚠️ Fair';
    return '🔴 Poor';
  };

  const getAlertIcon = (severity) => {
    if (severity === 'critical') return '🔴';
    if (severity === 'warning') return '🟡';
    return 'ℹ️';
  };

  const filterAndSortRows = () => {
    if (!data || !data.rows) return [];
    
    let filtered = data.rows;
    
    // Filter by type
    if (filterType !== 'all') {
      filtered = filtered.filter(row => row.Type === filterType);
    }
    
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(row => 
        row['Equipment Name'].toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'name') {
        return a['Equipment Name'].localeCompare(b['Equipment Name']);
      } else if (sortBy === 'pressure') {
        return b.Pressure - a.Pressure;
      } else if (sortBy === 'temperature') {
        return b.Temperature - a.Temperature;
      } else if (sortBy === 'health') {
        return (b.health_score || 0) - (a.health_score || 0);
      }
      return 0;
    });
    
    return filtered;
  };

  if (!authenticated) {
    return (
      <div className="App">
        <div className="login-container">
          <div className="login-header">
            <h2>🔐 Chemical Equipment Visualizer</h2>
            <p className="subtitle">Advanced Analytics & Safety Monitoring</p>
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">Login</button>
          </form>
          
          <div className="hint">
            <small>💡 Default: admin / admin123</small>
          </div>
        </div>
      </div>
    );
  }

  const filteredRows = filterAndSortRows();

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>⚗️ Chemical Equipment Analyzer</h1>
          <p className="header-subtitle">Advanced Safety & Analytics Platform</p>
        </div>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>

      {error && <div className="error-message" style={{whiteSpace: 'pre-line'}}>{error}</div>}

      <div className="upload-section">
        <div className="upload-box">
          <h3>📤 Upload Equipment Data</h3>
          <div className="upload-controls">
            <input 
              type="file" 
              accept=".csv" 
              onChange={handleFileChange}
              disabled={loading}
            />
            <button onClick={handleUpload} disabled={loading || !file}>
              {loading ? '⏳ Processing...' : '📤 Upload & Analyze'}
            </button>
          </div>
          <p className="upload-hint">
            Required columns: Equipment Name, Type, Flowrate (L/min), Pressure (bar), Temperature (°C)
          </p>
        </div>
      </div>

      {/* Upload History */}
      {history.length > 0 && (
        <div className="history-section">
          <h3>📋 Recent Uploads (Last 5)</h3>
          <div className="history-grid">
            {history.map((item) => (
              <div key={item.id} className="history-card">
                <h4>📄 {item.filename}</h4>
                <p><strong>📅 Uploaded:</strong> {new Date(item.upload_date).toLocaleString()}</p>
                <p><strong>🔢 Records:</strong> {item.total_count}</p>
                <p><strong>⚠️ Alerts:</strong> {item.alert_count || 0}</p>
                <button 
                  onClick={() => handleDownloadPDF(item.id)}
                  className="pdf-btn-small"
                >
                  📥 Download Report
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {data && (
        <div className="results-section">
          {/* Alert Summary */}
          {data.alerts && data.alerts.length > 0 && (
            <div className="alert-summary">
              <h3>⚠️ Safety Alerts Summary</h3>
              <div className="alert-counts">
                <div className="alert-count critical">
                  <span className="count">{data.alert_summary.critical}</span>
                  <span className="label">🔴 Critical</span>
                </div>
                <div className="alert-count warning">
                  <span className="count">{data.alert_summary.warning}</span>
                  <span className="label">🟡 Warning</span>
                </div>
                <div className="alert-count info">
                  <span className="count">{data.alert_summary.info}</span>
                  <span className="label">ℹ️ Info</span>
                </div>
              </div>
            </div>
          )}

          {/* Trend Comparison */}
          {data.comparison && (
            <div className="comparison-section">
              <h3>📈 Trend Comparison vs Previous Upload</h3>
              <div className="comparison-grid">
                <div className="comparison-card">
                  <h4>💧 Flowrate</h4>
                  <p className="current-value">{data.comparison.flowrate.current.toFixed(2)} L/min</p>
                  <p className={`change ${data.comparison.flowrate.change >= 0 ? 'positive' : 'negative'}`}>
                    {data.comparison.flowrate.change >= 0 ? '↑' : '↓'} {Math.abs(data.comparison.flowrate.change).toFixed(1)}%
                  </p>
                </div>
                <div className="comparison-card">
                  <h4>⚡ Pressure</h4>
                  <p className="current-value">{data.comparison.pressure.current.toFixed(2)} bar</p>
                  <p className={`change ${data.comparison.pressure.change >= 0 ? 'positive' : 'negative'}`}>
                    {data.comparison.pressure.change >= 0 ? '↑' : '↓'} {Math.abs(data.comparison.pressure.change).toFixed(1)}%
                  </p>
                </div>
                <div className="comparison-card">
                  <h4>🌡️ Temperature</h4>
                  <p className="current-value">{data.comparison.temperature.current.toFixed(2)} °C</p>
                  <p className={`change ${data.comparison.temperature.change >= 0 ? 'positive' : 'negative'}`}>
                    {data.comparison.temperature.change >= 0 ? '↑' : '↓'} {Math.abs(data.comparison.temperature.change).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          )}

          <h2>📊 Analysis Results</h2>
          
          {/* Statistics with Units */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">🔢</div>
              <h3>Total Equipment</h3>
              <p className="stat-value">{data.statistics.total_count}</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">💧</div>
              <h3>Avg Flowrate</h3>
              <p className="stat-value">{data.statistics.avg_flowrate.toFixed(2)}</p>
              <p className="stat-unit">L/min</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⚡</div>
              <h3>Avg Pressure</h3>
              <p className="stat-value">{data.statistics.avg_pressure.toFixed(2)}</p>
              <p className="stat-unit">bar</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🌡️</div>
              <h3>Avg Temperature</h3>
              <p className="stat-value">{data.statistics.avg_temperature.toFixed(2)}</p>
              <p className="stat-unit">°C</p>
            </div>
          </div>

          {/* Charts */}
          <div className="charts-container">
            <div className="chart">
              <h3>Equipment Distribution</h3>
              <Pie
                data={{
                  labels: Object.keys(data.statistics.equipment_distribution),
                  datasets: [{
                    data: Object.values(data.statistics.equipment_distribution),
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
                    borderWidth: 2,
                    borderColor: '#fff'
                  }]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  plugins: {
                    legend: { position: 'bottom' }
                  }
                }}
              />
            </div>

            <div className="chart">
              <h3>Average Parameters</h3>
              <Bar
                data={{
                  labels: ['Flowrate (L/min)', 'Pressure (bar)', 'Temperature (°C)'],
                  datasets: [{
                    label: 'Average Values',
                    data: [
                      data.statistics.avg_flowrate,
                      data.statistics.avg_pressure,
                      data.statistics.avg_temperature
                    ],
                    backgroundColor: ['rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)', 'rgba(255, 99, 132, 0.8)'],
                    borderColor: ['rgb(102, 126, 234)', 'rgb(118, 75, 162)', 'rgb(255, 99, 132)'],
                    borderWidth: 2
                  }]
                }}
                options={{
                  responsive: true,
                  plugins: { legend: { display: false } },
                  scales: { y: { beginAtZero: true } }
                }}
              />
            </div>
          </div>

          {/* Outliers Detection */}
          {data.outliers && (
            <div className="outliers-section">
              <h3>🔍 Outlier Detection</h3>
              <div className="outlier-grid">
                {Object.keys(data.outliers).map(key => {
                  const outliers = data.outliers[key];
                  if (outliers.length === 0) return null;
                  
                  return (
                    <div key={key} className="outlier-card">
                      <h4>{key.charAt(0).toUpperCase() + key.slice(1)} Outliers</h4>
                      <p className="outlier-count">{outliers.length} detected</p>
                      <ul className="outlier-list">
                        {outliers.slice(0, 3).map((o, i) => (
                          <li key={i}>{o.equipment}: {o.value.toFixed(1)}</li>
                        ))}
                      </ul>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Filters & Controls */}
          <div className="controls-section">
            <div className="control-group">
              <label>🔍 Search Equipment:</label>
              <input 
                type="text"
                placeholder="Search by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="control-group">
              <label>🏷️ Filter by Type:</label>
              <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                <option value="all">All Types</option>
                {Object.keys(data.statistics.equipment_distribution).map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div className="control-group">
              <label>📊 Sort by:</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="name">Name</option>
                <option value="pressure">Pressure (High to Low)</option>
                <option value="temperature">Temperature (High to Low)</option>
                <option value="health">Health Score (High to Low)</option>
              </select>
            </div>

            <div className="control-group">
              <label>👁️ View:</label>
              <div className="view-toggle">
                <button 
                  className={viewMode === 'grid' ? 'active' : ''}
                  onClick={() => setViewMode('grid')}
                >
                  📊 Grid
                </button>
                <button 
                  className={viewMode === 'table' ? 'active' : ''}
                  onClick={() => setViewMode('table')}
                >
                  📋 Table
                </button>
              </div>
            </div>
          </div>

          {/* Equipment Grid/Table View */}
          {viewMode === 'grid' ? (
            <div className="equipment-grid">
              <h3>💚 Equipment Health Dashboard</h3>
              <div className="equipment-cards">
                {filteredRows.map((row, idx) => {
                  const healthScore = row.health_score || 0;
                  const alerts = data.alerts?.filter(a => a.equipment === row['Equipment Name']) || [];
                  
                  return (
                    <div 
                      key={idx} 
                      className="equipment-card"
                      onClick={() => handleEquipmentClick(row)}
                      style={{borderLeft: `5px solid ${getHealthColor(healthScore)}`}}
                    >
                      <div className="equipment-header">
                        <h4>{row['Equipment Name']}</h4>
                        <span className="type-badge">{row.Type}</span>
                      </div>
                      
                      <div className="health-indicator">
                        <div className="health-score">
                          <span className="score">{healthScore.toFixed(0)}</span>
                          <span className="max">/100</span>
                        </div>
                        <div className="health-bar">
                          <div 
                            className="health-fill" 
                            style={{
                              width: `${healthScore}%`,
                              background: getHealthColor(healthScore)
                            }}
                          />
                        </div>
                        <p className="health-status">{getHealthStatus(healthScore)}</p>
                      </div>
                      
                      <div className="equipment-params">
                        <div className="param">
                          <span className="label">Flowrate:</span>
                          <span className="value">{row.Flowrate} L/min</span>
                        </div>
                        <div className="param">
                          <span className="label">Pressure:</span>
                          <span className="value">{row.Pressure} bar</span>
                        </div>
                        <div className="param">
                          <span className="label">Temp:</span>
                          <span className="value">{row.Temperature} °C</span>
                        </div>
                      </div>
                      
                      {alerts.length > 0 && (
                        <div className="alert-badge">
                          {getAlertIcon(alerts[0].severity)} {alerts.length} Alert{alerts.length > 1 ? 's' : ''}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="table-section">
              <h3>📋 Equipment Data Table</h3>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Equipment Name</th>
                      <th>Type</th>
                      <th>Flowrate (L/min)</th>
                      <th>Pressure (bar)</th>
                      <th>Temperature (°C)</th>
                      <th>Health Score</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRows.map((row, idx) => {
                      const healthScore = row.health_score || 0;
                      return (
                        <tr 
                          key={idx}
                          onClick={() => handleEquipmentClick(row)}
                          style={{cursor: 'pointer'}}
                        >
                          <td>{row['Equipment Name']}</td>
                          <td><span className="type-badge">{row.Type}</span></td>
                          <td>{row.Flowrate}</td>
                          <td>{row.Pressure}</td>
                          <td>{row.Temperature}</td>
                          <td>
                            <div className="health-mini">
                              <div 
                                className="health-mini-bar"
                                style={{
                                  width: `${healthScore}%`,
                                  background: getHealthColor(healthScore)
                                }}
                              />
                              <span>{healthScore.toFixed(0)}</span>
                            </div>
                          </td>
                          <td>{getHealthStatus(healthScore)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* PDF Download */}
          <div className="pdf-download-section">
            <button 
              onClick={() => handleDownloadPDF(data.data.id)}
              className="pdf-btn-large"
            >
              📥 Download Complete PDF Report
            </button>
          </div>

          {/* Alerts List */}
          {data.alerts && data.alerts.length > 0 && (
            <div className="alerts-list">
              <h3>⚠️ Detailed Alerts</h3>
              {data.alerts.map((alert, idx) => (
                <div key={idx} className={`alert-item ${alert.severity}`}>
                  <span className="alert-icon">{getAlertIcon(alert.severity)}</span>
                  <div className="alert-content">
                    <h4>{alert.equipment}</h4>
                    <p>{alert.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Equipment Detail Modal */}
      {selectedEquipment && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>×</button>
            <h2>{selectedEquipment['Equipment Name']}</h2>
            <p className="modal-type">Type: {selectedEquipment.Type}</p>
            
            <div className="modal-params">
              <div className="modal-param">
                <span className="param-label">💧 Flowrate</span>
                <span className="param-value">{selectedEquipment.Flowrate} L/min</span>
              </div>
              <div className="modal-param">
                <span className="param-label">⚡ Pressure</span>
                <span className="param-value">{selectedEquipment.Pressure} bar</span>
              </div>
              <div className="modal-param">
                <span className="param-label">🌡️ Temperature</span>
                <span className="param-value">{selectedEquipment.Temperature} °C</span>
              </div>
            </div>
            
            <div className="modal-health">
              <h3>Health Score</h3>
              <div className="health-score-large">
                <span style={{color: getHealthColor(selectedEquipment.health_score || 0)}}>
                  {(selectedEquipment.health_score || 0).toFixed(0)}
                </span>
                <span>/100</span>
              </div>
              <p>{getHealthStatus(selectedEquipment.health_score || 0)}</p>
            </div>
            
            {data.alerts?.filter(a => a.equipment === selectedEquipment['Equipment Name']).length > 0 && (
              <div className="modal-alerts">
                <h3>⚠️ Active Alerts</h3>
                {data.alerts.filter(a => a.equipment === selectedEquipment['Equipment Name']).map((alert, idx) => (
                  <div key={idx} className={`alert-item ${alert.severity}`}>
                    <span className="alert-icon">{getAlertIcon(alert.severity)}</span>
                    <p>{alert.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;