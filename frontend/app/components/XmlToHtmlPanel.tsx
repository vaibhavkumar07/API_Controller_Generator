"use client";

import { useRef, useState } from "react";
import { XML_TO_HTML_URL } from "../lib/api";

const defaultXml = `<?xml version="1.0" encoding="UTF-8"?>
<datacenter branch="US-West-SiliconValley">
    <network_management ui-component="tabs">
        <hardware_inventory>
            <router_ledger>
                <device><model>Cisco Nexus 9K</model><status>Active</status><ip>10.0.0.1</ip></device>
                <device><model>Juniper PTX10K</model><status>Pending</status><ip>10.0.0.2</ip></device>
                <device><model>Arista 7060X</model><status>Offline</status><ip>10.0.0.3</ip></device>
            </router_ledger>
        </hardware_inventory>
        <provisioning_console>
            <automated_tasks ui-component="accordion">
                <firewall_policies>
                    <rule_name>Block External ICMP Pings</rule_name>
                    <rule_input type="text" placeholder="Enter target IP Subnet CIDR" />
                    <action_button method="deployFirewallRule">Apply Global Rule</action_button>
                </firewall_policies>
            </automated_tasks>
        </provisioning_console>
    </network_management>
</datacenter>`;

type XmlToHtmlPanelProps = {
  status: string;
  setStatus: (value: string) => void;
  isLoading: boolean;
  setIsLoading: (value: boolean) => void;
};

export default function XmlToHtmlPanel({
  status,
  setStatus,
  isLoading,
  setIsLoading,
}: XmlToHtmlPanelProps) {
  const [xmlText, setXmlText] = useState(defaultXml);
  const [xmlFile, setXmlFile] = useState<File | null>(null);
  const [htmlOutput, setHtmlOutput] = useState("");
  const xmlFileInputRef = useRef<HTMLInputElement>(null);

  async function handleXmlConvert() {
    if (!xmlText.trim() && !xmlFile) return;
    setStatus("Converting XML to HTML...");
    setIsLoading(true);
    try {
      let response: Response;
      if (xmlFile) {
        const formData = new FormData();
        formData.append("file", xmlFile);
        if (xmlText.trim()) formData.append("xmlText", xmlText);
        response = await fetch(XML_TO_HTML_URL, { method: "POST", body: formData });
      } else {
        response = await fetch(XML_TO_HTML_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ xmlText }),
        });
      }
      const json = await response.json();
      if (!response.ok) {
        setStatus(json.error || "Conversion failed.");
        setHtmlOutput("");
      } else {
        setHtmlOutput(json.html || "");
        setStatus("HTML generated successfully.");
      }
    } catch {
      setStatus("Server request failed. Is the backend running?");
      setHtmlOutput("");
    } finally {
      setIsLoading(false);
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
    setStatus("Downloaded converted.html.");
  }

  function handleXmlClear() {
    setXmlText("");
    setXmlFile(null);
    setHtmlOutput("");
    setStatus("Cleared.");
    if (xmlFileInputRef.current) xmlFileInputRef.current.value = "";
  }

  return (
    <div id="panel-xml" role="tabpanel" aria-labelledby="tab-xml" className="xml-panel">
      <p className="sr-only">{status}</p>
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
                onChange={(event) => setXmlFile(event.target.files?.[0] ?? null)}
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
                disabled={isLoading || (!xmlText.trim() && !xmlFile)}
              >
                {isLoading ? "Converting…" : "Convert"}
              </button>
              <button type="button" onClick={handleHtmlDownload} disabled={!htmlOutput}>
                Download
              </button>
              <button
                type="button"
                onClick={() => {
                  navigator.clipboard.writeText(htmlOutput);
                  setStatus("Copied HTML to clipboard.");
                }}
                disabled={!htmlOutput}
              >
                Copy
              </button>
              <button type="button" className="secondary-button" onClick={handleXmlClear}>
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="outputs-row xml-outputs">
        <div className="card output-card">
          <div className="card-header">
            <div>
              <h2>HTML code</h2>
              <span>Generated HTML source</span>
            </div>
          </div>
          <pre className="output-block" aria-label="HTML source code">
            {htmlOutput || "Converted HTML source will appear here."}
          </pre>
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
              sandbox="allow-scripts"
              srcDoc={htmlOutput}
            />
          ) : (
            <pre className="output-block">Converted HTML preview will appear here.</pre>
          )}
        </div>
      </div>
    </div>
  );
}
