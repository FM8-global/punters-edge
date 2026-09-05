import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export default function Dashboard() {
  const [bets, setBets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [minScore, setMinScore] = useState(50);

  useEffect(() => {
    fetchBets();
  }, [minScore]);

  const fetchBets = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE}/bets?min_score=${minScore}`);
      setBets(response.data);
    } catch (err) {
      setError(`Failed to fetch bets: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">PunterEdge Dashboard</h1>
          <p className="text-gray-400">Australian Racing Betting Opportunities</p>
        </div>

        {/* Controls */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-4">
            <label className="text-sm font-semibold">Minimum Score:</label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={minScore}
              onChange={(e) => setMinScore(parseFloat(e.target.value))}
              className="w-48"
            />
            <span className="text-lg font-bold">{minScore}/100</span>
            <button
              onClick={fetchBets}
              className="ml-auto bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Status */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-400">Loading races...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-6">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Bets Table */}
        {!loading && !error && bets.length === 0 && (
          <div className="bg-gray-800 rounded-lg p-8 text-center">
            <p className="text-gray-400">No bets found with score ≥ {minScore}</p>
          </div>
        )}

        {!loading && bets.length > 0 && (
          <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold">Race</th>
                    <th className="px-6 py-4 text-left font-semibold">Runner</th>
                    <th className="px-6 py-4 text-right font-semibold">Best Price</th>
                    <th className="px-6 py-4 text-right font-semibold">Overlay %</th>
                    <th className="px-6 py-4 text-right font-semibold">Score</th>
                    <th className="px-6 py-4 text-left font-semibold">Start Time</th>
                    <th className="px-6 py-4 text-left font-semibold">Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {bets.map((bet, idx) => (
                    <tr
                      key={idx}
                      className="border-t border-gray-700 hover:bg-gray-700 transition"
                    >
                      <td className="px-6 py-4 font-semibold">
                        {bet.race_venue} R{bet.race_number}
                      </td>
                      <td className="px-6 py-4">
                        #{bet.runner_number} {bet.runner_name}
                      </td>
                      <td className="px-6 py-4 text-right font-semibold">
                        ${bet.best_price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="bg-yellow-600 px-2 py-1 rounded text-sm font-semibold">
                          {bet.overlay_pct.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span
                          className={`px-3 py-1 rounded font-bold text-sm ${
                            bet.score >= 70
                              ? 'bg-green-600'
                              : bet.score >= 50
                              ? 'bg-yellow-600'
                              : 'bg-red-600'
                          }`}
                        >
                          {bet.score.toFixed(0)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {new Date(bet.start_time).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-400">
                        {bet.reasoning}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Summary */}
            <div className="bg-gray-700 px-6 py-4 border-t border-gray-600">
              <div className="flex justify-between">
                <span className="font-semibold">Total Selections: {bets.length}</span>
                <span className="font-semibold">
                  Avg Score:{' '}
                  {(bets.reduce((sum, b) => sum + b.score, 0) / bets.length).toFixed(
                    1
                  )}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
