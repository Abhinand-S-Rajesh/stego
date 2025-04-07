import React, { useState } from "react";
import "./App.css";

function App() {
  const [encodeText, setEncodeText] = useState("");
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState("");
  const [encodedDownload, setEncodedDownload] = useState(null);

  const [decodeFile, setDecodeFile] = useState(null);
  const [decodeUrl, setDecodeUrl] = useState("");
  const [decodedText, setDecodedText] = useState("");

  const handleEncode = async () => {
    const formData = new FormData();
    if (file) formData.append("file", file);
    else if (url) formData.append("url", url);
    else return alert("Please upload a file or provide an image URL.");

    formData.append("text", encodeText);

    const response = await fetch("http://127.0.0.1:5000/api/encode", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      setEncodedDownload(downloadUrl);
    } else {
      const err = await response.json();
      alert(err.error);
    }
  };

  const handleDecode = async () => {
    const formData = new FormData();
    if (decodeFile) formData.append("file", decodeFile);
    else if (decodeUrl) formData.append("url", decodeUrl);
    else return alert("Please upload a file or provide an image URL.");

    const response = await fetch("http://127.0.0.1:5000/api/decode", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    if (response.ok) {
      setDecodedText(result.text || result.warning);
    } else {
      alert(result.error);
    }
  };

  return (
    <div className="container">
      <h1>🕵️ Steganography Tool</h1>
      <div className="section">
        <h2>Encode Message</h2>
        <textarea
          placeholder="Enter message to hide..."
          value={encodeText}
          onChange={(e) => setEncodeText(e.target.value)}
        />
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <input
          type="text"
          placeholder="or paste image URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button onClick={handleEncode}>Encode</button>
        {encodedDownload && (
          <a href={encodedDownload} download="encoded.png" className="download-link">
            Download Encoded Image
          </a>
        )}
      </div>

      <div className="section">
        <h2>Decode Message</h2>
        <input type="file" onChange={(e) => setDecodeFile(e.target.files[0])} />
        <input
          type="text"
          placeholder="or paste image URL"
          value={decodeUrl}
          onChange={(e) => setDecodeUrl(e.target.value)}
        />
        <button onClick={handleDecode}>Decode</button>
        {decodedText && <p className="output">Decoded Text: <strong>{decodedText}</strong></p>}
      </div>
    </div>
  );
}

export default App;
