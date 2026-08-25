"use client";

import { useState } from "react";
import { GENERATE_URL } from "../lib/api";

const languages = [
  { value: "csharp", label: "C# (.NET)" },
  { value: "java", label: "Java (Spring Boot)" },
  { value: "python", label: "Python (Flask)" },
];

const classesLanguages = [
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "python", label: "Python" },
  { value: "csharp", label: "C#" },
  { value: "java", label: "Java" },
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

type GeneratePanelProps = {
  status: string;
  setStatus: (value: string) => void;
  isLoading: boolean;
  setIsLoading: (value: boolean) => void;
};

export default function GeneratePanel({
  status,
  setStatus,
  isLoading,
  setIsLoading,
}: GeneratePanelProps) {
  const [inputText, setInputText] = useState(defaultInput);
  const [language, setLanguage] = useState("csharp");
  const [output, setOutput] = useState("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [classesLang, setClassesLang] = useState("javascript");
  const [classesOutput, setClassesOutput] = useState("");

  async function generateWith(text: string, ctrlLang: string, clsLang: string) {
    if (!text.trim()) return;
    setStatus("Generating controller and classes...");
    setIsLoading(true);

    try {
      let response: Response;
      if (uploadedFile) {
        const formData = new FormData();
        formData.append("language", ctrlLang);
        formData.append("classesLang", clsLang);
        formData.append("file", uploadedFile);
        if (text.trim()) formData.append("inputText", text);
        response = await fetch(GENERATE_URL, { method: "POST", body: formData });
      } else {
        response = await fetch(GENERATE_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ inputText: text, language: ctrlLang, classesLang: clsLang }),
        });
      }

      const json = await response.json();
      if (!response.ok) {
        setStatus(json.error || "Generation failed.");
        setOutput("");
        setClassesOutput("");
      } else {
        setOutput(json.controllerCode || "");
        setClassesOutput(json.classesCode || "");
        setStatus("Controller and classes generated successfully.");
      }
    } catch {
      setStatus("Server request failed. Is the backend running?");
      setOutput("");
      setClassesOutput("");
    } finally {
      setIsLoading(false);
    }
  }

  function handleControllerLangChange(val: string) {
    setLanguage(val);
    if (!isLoading && (output || classesOutput)) generateWith(inputText, val, classesLang);
  }

  function handleClassesLangChange(val: string) {
    setClassesLang(val);
    if (!isLoading && (output || classesOutput)) generateWith(inputText, language, val);
  }

  function handleDownload(content: string, filename: string) {
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
    setStatus("Download started.");
  }

  return (
    <div id="panel-generate" role="tabpanel" aria-labelledby="tab-generate">
      <p className="sr-only">{status}</p>
      <div className="input-section">
        <div className="card">
          <div className="card-header">
            <h2>Input</h2>
            <span>Text, JSON, or PDF upload</span>
          </div>
          <textarea
            value={inputText}
            onChange={(event) => setInputText(event.target.value)}
            rows={8}
            aria-label="API endpoint input"
          />
          <div className="file-upload-row">
            <label className="file-label">
              Upload PDF
              <input
                type="file"
                accept="application/pdf"
                onChange={(event) => setUploadedFile(event.target.files?.[0] ?? null)}
              />
            </label>
            {uploadedFile && <span className="file-meta">Selected: {uploadedFile.name}</span>}
          </div>
          <div className="controls-row">
            <button
              className="primary-button"
              onClick={() => generateWith(inputText, language, classesLang)}
              disabled={isLoading}
            >
              {isLoading ? "Generating…" : "Generate"}
            </button>
          </div>
        </div>
      </div>

      <div className="outputs-row">
        <div className="card output-card">
          <div className="card-header">
            <div>
              <h2>Controller</h2>
              <span>Server-side controller code</span>
            </div>
            <label>
              Language
              <select value={language} onChange={(event) => handleControllerLangChange(event.target.value)}>
                {languages.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="output-actions">
            <button
              onClick={() => {
                navigator.clipboard.writeText(output);
                setStatus("Copied output to clipboard.");
              }}
              disabled={!output}
            >
              Copy
            </button>
            <button onClick={() => handleDownload(output, `controller-${language}.txt`)} disabled={!output}>
              Download
            </button>
            <button
              className="secondary-button"
              onClick={() => {
                setOutput("");
                setStatus("Output cleared.");
              }}
              disabled={!output}
            >
              Clear
            </button>
          </div>
          <pre className="output-block">{output || "Controller code will appear here."}</pre>
        </div>

        <div className="card output-card">
          <div className="card-header">
            <div>
              <h2>Classes</h2>
              <span>Client-side caller code</span>
            </div>
            <label>
              Language
              <select value={classesLang} onChange={(event) => handleClassesLangChange(event.target.value)}>
                {classesLanguages.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="output-actions">
            <button
              onClick={() => {
                navigator.clipboard.writeText(classesOutput);
                setStatus("Copied classes to clipboard.");
              }}
              disabled={!classesOutput}
            >
              Copy
            </button>
            <button
              onClick={() => handleDownload(classesOutput, `classes-${classesLang}.txt`)}
              disabled={!classesOutput}
            >
              Download
            </button>
            <button
              className="secondary-button"
              onClick={() => {
                setClassesOutput("");
                setStatus("Classes output cleared.");
              }}
              disabled={!classesOutput}
            >
              Clear
            </button>
          </div>
          <pre className="output-block">{classesOutput || "Classes code will appear here."}</pre>
        </div>
      </div>
    </div>
  );
}
