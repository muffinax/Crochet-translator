import React, { useState } from "react";
import "./generatedoutput.css";

export default function GeneratedOutput({ outputText, isLoading }) {
    const [copied, setCopied] = useState(false);
    
    const handleCopy = () => {
        navigator.clipboard.writeText(outputText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000); // Reset copied state after 2 seconds
    };

    if (isLoading) {
        return (
            <div className="output-loading">
                <p>Loading...</p>
            </div>
        );
    }

    if (!outputText) {
        return null; // Don't render anything if there's no output text
    }

    return (
        <div className="output-container">
            <div className="output-header">
                <h3>Wygenerowana instrukcja:</h3>
            </div>
            <div className="output-text">
                <pre>{outputText}</pre>
            </div>
        </div>
  );
}