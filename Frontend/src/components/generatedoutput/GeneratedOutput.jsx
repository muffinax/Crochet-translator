import React, { useState } from "react";
import "./generatedoutput.css";

export default function GeneratedOutput({ outputText, isLoading }) {
    const [copied, setCopied] = useState(false);
    
    const handleCopy = () => {
        navigator.clipboard.writeText(outputText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (isLoading) {
        return (
            <div className="output-loading">
                <p>Loading...</p>
            </div>
        );
    }

    if (!outputText) {
        return null;
    }

    return (
        <div className="output-container">
            {isLoading ? (
                <div className="output-state">
                <div className="spinner" />
                <p>Translating pattern...</p>
            </div>
        ) : outputText ? (
            <div className="output-content">
                <div className="output-header">
                    <h3>Instruction</h3>
                    <button type="button" className="btn btn-secondary btn-sm" onClick={handleCopy}
                    >{copied ? "Copied!" : "Copy"}
                    </button>
                </div>
                <div className="output-body">
                    <pre>{outputText}</pre>
                </div>
            </div>
        ) : (
            <div className="output-state">
                <h4>Instruction will appear here</h4>
                <p>Upload a pattern image and click "Translate Pattern"</p>
            </div>
            )}
        </div>
    );
}