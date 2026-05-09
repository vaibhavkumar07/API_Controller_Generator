"use client";

import { useMemo, useState } from "react";

const languages = [
  { value: "csharp", label: "C# (.NET)" },
  { value: "java", label: "Java (Spring Boot)" },
  { value: "python", label: "Python (Flask)" },
];

const defaultInput = `GET /api/quizzes
Response:
[
  {
    "id": 1,
    "title": "C# Basics",
    "description": "Beginner quiz"
  }
]`;

export default function Home() {
  const [inputText, setInputText] = useState(defaultInput);
  const [language, setLanguage] = useState("csharp");
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState("Ready to generate.");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  async function handleGenerate() {
    setStatus("Generating controller...");
    setIsLoading(true);

    try {
      let response;
      if (uploadedFile) {
        const formData = new FormData();
        formData.append("language", language);
        formData.append("file", uploadedFile);
        if (inputText.trim()) {
          formData.append("inputText", inputText);
        }

        response = await fetch("http://localhost:5000/api/generate", {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch("http://localhost:5000/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ inputText, language }),
        });
      }

      const json = await response.json();
      if (!response.ok) {
        setStatus(json.error || "Generation failed.");
        setOutput("");
      } else {
        setOutput(json.controllerCode || "");
        setStatus("Controller generated successfully.");
      }
    } catch (error) {
      setStatus("Server request failed. Is the backend running?");
      setOutput("");
    } finally {
      setIsLoading(false);
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(output);
    setStatus("Copied output to clipboard.");
  }

  function handleClear() {
    setOutput("");
    setStatus("Output cleared.");
  }

  function handleDownload() {
    const filename = `controller-${language}.txt`;
    const blob = new Blob([output], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
    setStatus("Download started.");
  }

  return (
    <main className="page-shell">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">API Controller Generator</p>
          <h1>Generate controller code from endpoint definitions</h1>
          <p className="description">
            Paste API endpoint definitions, upload a PDF, choose a language, and generate controller boilerplate instantly.
          </p>
        </div>
        <div className="status-card">
          <p>{status}</p>
          {isLoading && <div className="spinner" />}
        </div>
      </section>

      <section className="grid-panel">
        <div className="card input-card">
          <div className="card-header">
            <h2>Input</h2>
            <span>Text, JSON, or PDF upload</span>
          </div>
          <textarea
            value={inputText}
            onChange={(event) => setInputText(event.target.value)}
            rows={14}
            aria-label="API endpoint input"
          />
          <div className="file-upload-row">
            <label className="file-label">
              Upload PDF
              <input
                type="file"
                accept="application/pdf"
                onChange={(event) => {
                  const file = event.target.files?.[0] ?? null;
                  setUploadedFile(file);
                }}
              />
            </label>
            {uploadedFile && <span className="file-meta">Selected: {uploadedFile.name}</span>}
          </div>
          <div className="controls-row">
            <label>
              Language
              <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                {languages.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
            <button className="primary-button" onClick={handleGenerate} disabled={isLoading}>
              Generate
            </button>
          </div>
        </div>

        <div className="card output-card">
          <div className="card-header">
            <div>
              <h2>Generated Controller</h2>
              <span>Controller code output for the selected language.</span>
            </div>
          </div>
          <div className="output-actions">
            <button onClick={handleCopy} disabled={!output}>
              Copy
            </button>
            <button onClick={handleDownload} disabled={!output}>
              Download
            </button>
            <button className="secondary-button" onClick={handleClear} disabled={!output}>
              Clear
            </button>
          </div>
          <pre className="output-block">{output || "Your generated controller will appear here."}</pre>
        </div>
      </section>
    </main>
  );
}
