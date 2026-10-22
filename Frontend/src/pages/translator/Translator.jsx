import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import DragDropFiles from "../../components/dragdrop/DragDropFiles";
import GeneratedOutput from "../../components/generatedoutput/GeneratedOutput";
import Toast from "../../components/toast/Toast";
import "./Translator.css";

export default function Translator() {
    const navigate = useNavigate();
    const [file, setFile] = useState(null);
    const [outputText, setOutputText] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [toast, setToast] = useState(null);

    //soon added logging in
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const showToast = (message, type = "info") => {
        setToast({ message, type });
    };

    const handleTranslate = () => {
        // Sending file to API
        console.log("sending file:", file);
        
        if (!file) return;
        setIsLoading(true);

        //TEST OUTPUT
        setTimeout(() => {
            setOutputText("Rząd 1: 6 sc w magic ring\nRząd 2: 6 inc (12)");
            setIsLoading(false);
        }, 1500);
    };

    const handleReset = () => {
        console.log("Resetting translator state");

        setFile(null);
        setOutputText("");
        setIsLoading(false);
    }

    const handleSave = () => {
        try {
            console.log("Saving instruction:", outputText);

            // Test success or failure:
            const isSuccess = true;

            if (isSuccess) {
                showToast("Instruction saved!", "success");
            } else {
                throw new Error("Error while saving");
            }
        } catch (error) {
            showToast("Failed to save instruction.", "error");
        }
    };

    return (
        <div className="translator-container">
            <h1 className="translator-title">Translator</h1>

            <div className="translator-grid">
                <div className="workspace-col">
                    <DragDropFiles
                        file={file}
                        setFile={setFile}
                        accepts="image/png,image/jpeg,image/jpg,image/webp,image/svg+xml,image/bmp"
                    />
                </div>
                <div className="workspace-col"></div>
                    {/* Display generated output */}
                    <GeneratedOutput outputText={outputText} isLoading={isLoading} />
                </div>

            {/* Show translate button */}
            {(file && !outputText && !isLoading) && (
                <button type="button" className="btn btn-primary" onClick={handleTranslate}>
                    Translate chart
                </button>
            )}

            {(!isLoading && outputText) && (
                isLoggedIn ? (
                    <button type ="button" className="btn btn-primary" onClick={handleSave}>
                        Save instruction
                    </button>
                ) : (
                    <div className="save-info">
                        If you want to save this information, please{" "}
                        <Link to="/register" className="info-btn">
                            Register
                        </Link>
                        {" "}or{" "}
                        <Link to="/log-in" className="info-btn">
                            Log in
                        </Link>
                        {" "}first.
                    </div>
                )
            )}

            {(isLoading || outputText) && (
                <button type ="button" className="btn btn-primary" onClick={handleReset}>
                    New translation
                </button>
            )}

            {/* Toast */}
            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}
        </div>
    );
}