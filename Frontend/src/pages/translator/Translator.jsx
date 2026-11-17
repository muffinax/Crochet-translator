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

    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const showToast = (message, type = "info") => {
        setToast({ message, type });
    };

    const handleTranslate = async () => {
        if (!file) {
            showToast("Wybierz plik przed tłumaczeniem!", "error");
            return;
        }
        
        setIsLoading(true);
        setOutputText("");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://localhost:8000/api/translate", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Błąd podczas tłumaczenia.");
            }

            const data = await response.json();
            
            if (data.status === "success") {
                setOutputText(data.text);
                showToast("Tłumaczenie zakończone sukcesem!", "success");
            } else {
                throw new Error("Nieznany błąd formatu odpowiedzi serwera.");
            }

        } catch (error) {
            console.error("API error:", error);
            showToast(error.message, "error");
        } finally {
            setIsLoading(false);
        }
    };

    const handleReset = () => {
        setFile(null);
        setOutputText("");
        setIsLoading(false);
    }

    const handleSave = () => {
        try {
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
                {/* LEFT */}
                <div className="workspace-col">
                    <DragDropFiles
                        file={file}
                        setFile={setFile}
                        accepts="image/png,image/jpeg,image/jpg,image/webp,image/svg+xml,image/bmp"
                        isLocked={isLoading || Boolean(outputText)} 
                    />
                </div>

                {/* RIGHT */}
                <div className="workspace-col">
                    <GeneratedOutput outputText={outputText} isLoading={isLoading} />
                </div>
            </div>

            {/* Lower section */}
                    
            <div className="bottom-actions">

                {(file && !outputText && !isLoading) && (
                    <button type="button" className="btn btn-primary" onClick={handleTranslate}>
                        Translate chart
                    </button>
                )}

                {(!isLoading && outputText) && (
                    isLoggedIn ? (
                        <button type="button" className="btn btn-success" onClick={handleSave}>
                            Save instruction
                        </button>
                    ) : (
                        <div className="save-info">
                            If you want to save this information, please{" "}
                            <Link to="/register" className="info-btn">Register</Link>
                            {" "}or{" "}
                            <Link to="/log-in" className="info-btn">Log in</Link>
                            {" "}first.
                        </div>
                    )
                )}

                {(isLoading || outputText) && (
                    <button type="button" className="btn btn-secondary" onClick={handleReset}>
                        New translation
                    </button>
                )}
            </div>

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