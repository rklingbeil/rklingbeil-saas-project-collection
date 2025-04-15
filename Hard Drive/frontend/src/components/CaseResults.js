// File: /Users/rick/CaseProject/frontend/src/components/CaseResults.js
import React, { useState } from 'react';

const CaseResults = ({ prediction, similarCases }) => {
  const [showSimilarCases, setShowSimilarCases] = useState(false);

  // Function to format prediction output into paragraphs/blocks.
  const formatPrediction = (text) => {
    return text.split("\n\n").map((block, index) => (
      <div key={index} className="prediction-block">
        {block.split("\n").map((line, idx) => (
          <p key={idx} className="prediction-line">{line}</p>
        ))}
      </div>
    ));
  };

  // Function to format similar cases into a readable format.
  const formatSimilarCases = (cases) => {
    return cases.map((item, index) => (
      <div key={index} className="similar-case">
        <h3>Similar Case {index + 1}</h3>
        <p><strong>Court:</strong> {item.court}</p>
        <p><strong>Date:</strong> {item.date}</p>
        <p><strong>Claim Type:</strong> {item.claim_type}</p>
        <p><strong>Injury Type:</strong> {item.injury_type}</p>
        <p><strong>Facts:</strong> {item.facts}</p>
        <p><strong>Injuries:</strong> {item.injuries}</p>
        <p><strong>Economic Damages:</strong> {item.specials}</p>
        {item.result && <p><strong>Result:</strong> {item.result}</p>}
        <hr />
      </div>
    ));
  };

  // Function to download the similar cases as a text file.
  const downloadSimilarCases = () => {
    if (!similarCases || similarCases.length === 0) return;
    const text = JSON.stringify(similarCases, null, 2);
    const element = document.createElement("a");
    const file = new Blob([text], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = "SimilarCases.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Function to download the prediction results as a text file.
  const downloadResults = () => {
    if (!prediction) return;
    const element = document.createElement("a");
    const file = new Blob([prediction], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = "CaseAnalysisResults.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (!prediction && (!similarCases || similarCases.length === 0)) {
    return null;
  }

  return (
    <div className="output-container">
      <h2>Prediction</h2>
      <div className="prediction-card">
        {formatPrediction(prediction)}
      </div>
      <div className="similar-cases-container">
        <button 
          onClick={() => setShowSimilarCases(!showSimilarCases)} 
          className="toggle-button"
        >
          {showSimilarCases ? "Hide Similar Cases" : "View Similar Cases"}
        </button>
        {showSimilarCases && (
          <div className="similar-cases">
            <h3>Similar Cases</h3>
            {formatSimilarCases(similarCases)}
            <button onClick={downloadSimilarCases} className="download-button">
              Download Similar Cases
            </button>
          </div>
        )}
      </div>
      <div className="download-container">
        <button type="button" onClick={downloadResults} className="download-button">
          Download Results
        </button>
      </div>
    </div>
  );
};

export default CaseResults;
