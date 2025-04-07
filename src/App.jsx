import React, { useState } from "react";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("encode");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [responseText, setResponseText] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");

  const handleEncode = async () => {
    if (!file || !message.trim()) {
      alert("Please select an image and enter a message.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("text", message);

    const res = await fetch("http://localhost:5000/api/encode", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (data.download_url) {
      setDownloadUrl("http://localhost:5000" + data.download_url);
    } else {
      setResponseText(data.error || "Encoding failed.");
    }
  };

  const handleDecode = async () => {
    if (!file) {
      alert("Please select an image to decode.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:5000/api/decode", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (data.text) {
      setResponseText(data.text);
    } else {
      setResponseText(data.warning || data.error || "No hidden message found.");
    }
  };

  return (
    <div className="container">
      <h2 className="title">Steganography Online</h2>
      <div className="tabs">
        <button onClick={() => setActiveTab("encode")} className={activeTab === "encode" ? "active" : ""}>Encode</button>
        <button onClick={() => setActiveTab("decode")} className={activeTab === "decode" ? "active" : ""}>Decode</button>
      </div>

      {activeTab === "encode" && (
        <div className="section">
          <p className="info-box">
            To encode a message into an image, choose the image you want to use, enter your text and hit the <strong>Encode</strong> button.
            The resulting image will contain your hidden message.
          </p>

          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
          <textarea placeholder="Enter your message here" rows="4" value={message} onChange={(e) => setMessage(e.target.value)} />

          <button onClick={handleEncode}>Encode</button>

          {downloadUrl && <p><a href={downloadUrl} download>Download Encoded Image</a></p>}
          {responseText && <p className="error">{responseText}</p>}
        </div>
      )}

      {activeTab === "decode" && (
        <div className="section">
          <p className="info-box">
            To decode a hidden message, upload an image that may contain steganographic content and click <strong>Decode</strong>.
          </p>

          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
          <button onClick={handleDecode}>Decode</button>

          {responseText && (
            <div className="output-box">
              <strong>Decoded Message:</strong>
              <p>{responseText}</p>
            </div>
          )}
        </div>
      )}

      <footer>© 2025 by you</footer>
    </div>
  );
}

export default App;
