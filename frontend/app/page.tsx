"use client";

import { useState } from "react";
import GeneratePanel from "./components/GeneratePanel";
import ToolSwitcher, { type AppMode } from "./components/ToolSwitcher";
import XmlToHtmlPanel from "./components/XmlToHtmlPanel";
import { DOCS_URL } from "./lib/api";

export default function Home() {
  const [mode, setMode] = useState<AppMode>("generate");
  const [genStatus, setGenStatus] = useState("Ready to generate.");
  const [genLoading, setGenLoading] = useState(false);
  const [xmlStatus, setXmlStatus] = useState("Ready to convert XML.");
  const [xmlLoading, setXmlLoading] = useState(false);

  const activeStatus = mode === "generate" ? genStatus : xmlStatus;
  const activeLoading = mode === "generate" ? genLoading : xmlLoading;

  return (
    <main className="page-shell">
      <header className="brand-header">
        <p className="brand-mark">API Framework</p>
        <ToolSwitcher mode={mode} onModeChange={setMode} docsUrl={DOCS_URL} />
      </header>

      <section className="hero-panel">
        <div>
          <p className="eyebrow">
            {mode === "generate" ? "Code generation" : "Transform"}
          </p>
          <h1>
            {mode === "generate"
              ? "Generate controller code from endpoint definitions"
              : "Convert XML into working HTML"}
          </h1>
          <p className="description">
            {mode === "generate"
              ? "Paste API endpoint definitions, upload a PDF, choose a language, and generate controller and client boilerplate."
              : "Paste XML or upload an .xml file, convert it to a standalone HTML document, then preview, copy, or download."}
          </p>
        </div>
        <div className="status-card" aria-live="polite">
          <p>{activeStatus}</p>
          {activeLoading && <div className="spinner" aria-hidden="true" />}
        </div>
      </section>

      {mode === "generate" ? (
        <GeneratePanel
          status={genStatus}
          setStatus={setGenStatus}
          isLoading={genLoading}
          setIsLoading={setGenLoading}
        />
      ) : (
        <XmlToHtmlPanel
          status={xmlStatus}
          setStatus={setXmlStatus}
          isLoading={xmlLoading}
          setIsLoading={setXmlLoading}
        />
      )}
    </main>
  );
}
