import React from "react";

function ResultList({ results, venues }) {
  if (!results || results.length === 0) {
    return <p>No results to display.</p>;
  }

  // Ensure results is an array
  const resultsArray = Array.isArray(results) ? results : Object.values(results);

  return (
    <div className="result-list-container">
      <h3 className="text-xl font-bold mb-4">Game Results</h3>
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2 border">Home Team</th>
            <th className="p-2 border">Away Team</th>
            <th className="p-2 border">Venue</th>
            <th className="p-2 border">Home Score</th>
            <th className="p-2 border">Away Score</th>
            <th className="p-2 border">Week</th>
            <th className="p-2 border">Date</th>
          </tr>
        </thead>
        <tbody>
          {resultsArray.map((result, index) => (
            <tr key={result.id || index} className="hover:bg-gray-50">
              <td className="p-2 border">{result.home_team_name || "N/A"}</td>
              <td className="p-2 border">{result.away_team_name || "N/A"}</td>
              <td className="p-2 border">{result.venue || "N/A"}</td>
              <td className="p-2 border text-center">{result.home_score ?? "N/A"}</td>
              <td className="p-2 border text-center">{result.away_score ?? "N/A"}</td>
              <td className="p-2 border text-center">{result.week || "N/A"}</td>
              <td className="p-2 border text-center">
                {result.game_date ? new Date(result.game_date).toLocaleDateString() : "N/A"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ResultList;