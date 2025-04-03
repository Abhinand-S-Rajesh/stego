import React, { useState } from "react";
import axios from "axios";
import "./App.css";

export default function SteganographyApp() {
    const [text, setText] = useState("");
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [encodedFile, setEncodedFile] = useState(null);
    const [decodedText, setDecodedText] = useState("");
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
        }
    };

    const handleEncode = async () => {
        if (!file || !text) {
            alert("⚠️ Please select an image and enter text to encode!");
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append("file", file);
        formData.append("text", text);

        try {
            const response = await axios.post("http://127.0.0.1:5000/api/encode", formData, {
                responseType: "blob",
            });
            setEncodedFile(URL.createObjectURL(response.data));
        } catch (error) {
            alert("❌ Encoding failed! Please check the file format and try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleDecode = async () => {
        if (!file) {
            alert("⚠️ Please select an image to decode!");
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("http://127.0.0.1:5000/api/decode", formData);
            setDecodedText(response.data.text);
        } catch (error) {
            alert("❌ Decoding failed! Make sure the image contains hidden text.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="card">
                <h2>Steganography Tool 🔐</h2>
                <input type="file" onChange={handleFileChange} className="input-file" />
                {preview && <img src={preview} alt="Selected" className="image-preview" />}
                <textarea
                    placeholder="Enter secret message..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    className="textarea"
                />
                <button onClick={handleEncode} className="button encode-button">Encode</button>
                <button onClick={handleDecode} className="button decode-button">Decode</button>

                {loading && <div className="loader"></div>}
            </div>

            {encodedFile && (
                <div className="card">
                    <h3>Download Encoded Image:</h3>
                    <a href={encodedFile} download="encoded.png" className="download-link">Download</a>
                </div>
            )}
            {decodedText && (
                <div className="card">
                    <h3>Decoded Message:</h3>
                    <p className="decoded-text">{decodedText}</p>
                </div>
            )}
        </div>
    );
}
