import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import DragDropFiles from "../../components/dragdrop/DragDropFiles";
import GeneratedOutput from "../../components/generatedoutput/GeneratedOutput";
import Toast from "../../components/toast/Toast";
import "./Translator.css";

export default function Translator() {
    const navigate = useNavigate();

    const [file, setFile] = useState(null);
    const [outputText, setOutputText] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    //soon added logging in
    const [isLoggedIn, setIsLoggedIn] = useState(true);

    // Toast state
    const [toast, setToast] = useState(null);

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

    const handleSave = () => {
        try {
            console.log("Saving instruction:", outputText);

            // Test success or failure:
            const isSuccess = true;

            if (isSuccess) {
                showToast("Saved instruction!", "success");
            } else {
                throw new Error("Error while saving");
            }
        } catch (error) {
            showToast("Failed to save instruction.", "error");
        }
    };

    return (
        <div>
            <h1>Translator</h1>

            {/* Display generated output */}
            {(isLoading || outputText) && (
                <GeneratedOutput outputText={outputText} isLoading={isLoading} />
            )}

            {(isLoading || outputText) && (
                isLoggedIn ? (
                    <button type ="button" className="save-btn" onClick={handleSave}>
                        Save instruction
                    </button>
                ) : (
                    <div className="save-info">
                        If you want to save this information, please{" "}
                        <button type="button" className="info-btn" onClick={() => navigate("/register")}>
                            register
                        </button>
                        {" "}or{" "}
                        <button type="button" className="info-btn" onClick={() => navigate("/log-in")}>
                            login
                        </button>
                        {" "}first.
                    </div>
                )
            )}

            {/* Display file dropdown */}
            <DragDropFiles
                file={file}
                setFile={setFile}
                accepts="image/png,image/jpeg,image/jpg,image/webp,image/svg+xml,image/bmp"
            />

            {/* Show translate button */}
            {file && (
                <button type="button" className="translate-btn" onClick={handleTranslate}>
                    Translate chart
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