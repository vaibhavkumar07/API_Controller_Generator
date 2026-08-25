"use client";

import { useRef, useState } from "react";

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

const defaultXml = `<catalog>
  <book id="1">The Hobbit</book>
</catalog>`;

type AppMode = "generate" | "xmlToHtml";

export default function Home() {
  const [mode, setMode] = useState<AppMode>("generate");
  const [inputText, setInputText] = useState(defaultInput);
  const [language, setLanguage] = useState("csharp");
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState("Ready to generate.");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [classesLang, setClassesLang] = useState("javascript");
  const [classesOutput, setClassesOutput] = useState("");

  const [xmlText, setXmlText] = useState(defaultXml);
  const [xmlFile, setXmlFile] = useState<File | null>(null);
  const [htmlOutput, setHtmlOutput] = useState("");
  const [xmlStatus, setXmlStatus] = useState("Ready to convert XML.");
  const [xmlLoading, setXmlLoading] = useState(false);
  const xmlFileInputRef = useRef<HTMLInputElement>(null);

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
        response = await fetch("http://localhost:5002/api/generate", {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch("http://localhost:5002/api/generate", {
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

  function handleGenerate() {
    generateWith(inputText, language, classesLang);
  }

  function handleControllerLangChange(val: string) {
    setLanguage(val);
    if (!isLoading && (output || classesOutput)) generateWith(inputText, val, classesLang);
  }

  function handleClassesLangChange(val: string) {
    setClassesLang(val);
    if (!isLoading && (output || classesOutput)) generateWith(inputText, language, val);
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

  function handleCopyClasses() {
    navigator.clipboard.writeText(classesOutput);
    setStatus("Copied classes to clipboard.");
  }

  function handleDownloadClasses() {
    const filename = `classes-${classesLang}.txt`;
    const blob = new Blob([classesOutput], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
    setStatus("Download started.");
  }

  function handleClearClasses() {
    setClassesOutput("");
    setStatus("Classes output cleared.");
  }

  async function handleXmlConvert() {
    if (!xmlText.trim() && !xmlFile) return;
    setXmlStatus("Converting XML to HTML...");
    setXmlLoading(true);
    try {
      let response: Response;
      if (xmlFile) {
        const formData = new FormData();
        formData.append("file", xmlFile);
        if (xmlText.trim()) formData.append("xmlText", xmlText);
        response = await fetch("http://localhost:5002/api/xml-to-html", {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch("http://localhost:5002/api/xml-to-html", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ xmlText }),
        });
      }
      const json = await response.json();
      if (!response.ok) {
        setXmlStatus(json.error || "Conversion failed.");
        setHtmlOutput("");
      } else {
        setHtmlOutput(json.html || "");
        setXmlStatus("HTML generated successfully.");
      }
    } catch {
      setXmlStatus("Server request failed. Is the backend running?");
      setHtmlOutput("");
    } finally {
      setXmlLoading(false);
    }
  }

  function handleHtmlDownload() {
    const blob = new Blob([htmlOutput], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "converted.html";
    a.click();
    URL.revokeObjectURL(url);
    setXmlStatus("Downloaded converted.html.");
  }

  function handleHtmlCopy() {
    navigator.clipboard.writeText(htmlOutput);
    setXmlStatus("Copied HTML to clipboard.");
  }

  function handleXmlClear() {
    setXmlText("");
    setXmlFile(null);
    setHtmlOutput("");
    setXmlStatus("Cleared.");
    if (xmlFileInputRef.current) xmlFileInputRef.current.value = "";
  }

  function handleTabKeyDown(event: React.KeyboardEvent) {
    if (event.key === "ArrowRight") setMode("xmlToHtml");
    else if (event.key === "ArrowLeft") setMode("generate");
  }

  const activeStatus = mode === "generate" ? status : xmlStatus;
  const activeLoading = mode === "generate" ? isLoading : xmlLoading;

  return (
    <main className="page-shell">
      <div
        className="mode-tabs"
        role="tablist"
        aria-label="App mode"
        onKeyDown={handleTabKeyDown}
      >
        <button
          type="button"
          id="tab-generate"
          role="tab"
          className={mode === "generate" ? "mode-tab active" : "mode-tab"}
          aria-selected={mode === "generate"}
          aria-controls="panel-generate"
          onClick={() => setMode("generate")}
        >
          API Generate
        </button>
        <button
          type="button"
          id="tab-xml"
          role="tab"
          className={mode === "xmlToHtml" ? "mode-tab active" : "mode-tab"}
          aria-selected={mode === "xmlToHtml"}
          aria-controls="panel-xml"
          onClick={() => setMode("xmlToHtml")}
        >
          XML → HTML
        </button>
      </div>

      <section className="hero-panel">
        <div>
          <p className="eyebrow">
            {mode === "generate" ? "API Controller Generator" : "XML to HTML"}
          </p>
          <h1>
            {mode === "generate"
              ? "Generate controller code from endpoint definitions"
              : "Convert XML into browsable HTML"}
          </h1>
          <p className="description">
            {mode === "generate"
              ? "Paste API endpoint definitions, upload a PDF, choose a language, and generate controller boilerplate instantly."
              : "Paste XML or upload an .xml file, convert it to a standalone HTML document, then preview, copy, or download."}
          </p>
        </div>
        <div className="status-card">
          <p>{activeStatus}</p>
          {activeLoading && <div className="spinner" />}
        </div>
      </section>

      {mode === "generate" ? (
        <div
          id="panel-generate"
          role="tabpanel"
          aria-labelledby="tab-generate"
        >
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
                    onChange={(event) => {
                      const file = event.target.files?.[0] ?? null;
                      setUploadedFile(file);
                    }}
                  />
                </label>
                {uploadedFile && <span className="file-meta">Selected: {uploadedFile.name}</span>}
              </div>
              <div className="controls-row">
                <button className="primary-button" onClick={handleGenerate} disabled={isLoading}>
                  Generate
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
                <button onClick={handleCopy} disabled={!output}>Copy</button>
                <button onClick={handleDownload} disabled={!output}>Download</button>
                <button className="secondary-button" onClick={handleClear} disabled={!output}>Clear</button>
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
                  <select
                    value={classesLang}
                    onChange={(event) => handleClassesLangChange(event.target.value)}
                  >
                    {classesLanguages.map((item) => (
                      <option key={item.value} value={item.value}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <div className="output-actions">
                <button onClick={handleCopyClasses} disabled={!classesOutput}>
                  Copy
                </button>
                <button onClick={handleDownloadClasses} disabled={!classesOutput}>
                  Download
                </button>
                <button className="secondary-button" onClick={handleClearClasses} disabled={!classesOutput}>
                  Clear
                </button>
              </div>
              <pre className="output-block">
                {classesOutput || "Classes code will appear here."}
              </pre>
            </div>
          </div>
        </div>
      ) : (
        <div
          id="panel-xml"
          role="tabpanel"
          aria-labelledby="tab-xml"
          className="xml-panel"
        >
          <div className="input-section">
            <div className="card">
              <div className="card-header">
                <h2>XML input</h2>
                <span>Paste XML or upload a file</span>
              </div>
              <textarea
                value={xmlText}
                onChange={(event) => setXmlText(event.target.value)}
                rows={12}
                spellCheck={false}
                aria-label="XML input"
              />
              <div className="file-upload-row">
                <label className="file-label">
                  Upload XML
                  <input
                    ref={xmlFileInputRef}
                    type="file"
                    accept=".xml,text/xml,application/xml"
                    onChange={(event) => {
                      setXmlFile(event.target.files?.[0] ?? null);
                    }}
                  />
                </label>
                {xmlFile && <span className="file-meta">Selected: {xmlFile.name}</span>}
              </div>
              <div className="controls-row">
                <div className="output-actions">
                  <button
                    type="button"
                    className="primary-button"
                    onClick={handleXmlConvert}
                    disabled={xmlLoading || (!xmlText.trim() && !xmlFile)}
                  >
                    {xmlLoading ? "Converting…" : "Convert"}
                  </button>
                  <button type="button" onClick={handleHtmlDownload} disabled={!htmlOutput}>
                    Download
                  </button>
                  <button type="button" onClick={handleHtmlCopy} disabled={!htmlOutput}>
                    Copy
                  </button>
                  <button type="button" className="secondary-button" onClick={handleXmlClear}>
                    Clear
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="card output-card">
            <div className="card-header">
              <div>
                <h2>HTML preview</h2>
                <span>Sandboxed render of converted document</span>
              </div>
            </div>
            {htmlOutput ? (
              <iframe
                className="html-preview"
                title="HTML preview"
                sandbox=""
                srcDoc={htmlOutput}
              />
            ) : (
              <pre className="output-block">Converted HTML will appear here.</pre>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
