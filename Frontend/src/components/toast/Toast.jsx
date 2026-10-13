import React, { useEffect } from "react";
import "./Toast.css";

export default function Toast({ message, type, onClose }) {
    useEffect(() => {
        const timer = setTimeout(() => { onClose(); }, 3000); // Toast will disappear after 3 seconds

        return () => clearTimeout(timer);
    }, [onClose]);

    return (
    <div className={`toast-container toast-${type}`}>
        <span className="toast-message">{message}</span>
    </div>
    );
}