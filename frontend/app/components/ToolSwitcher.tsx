"use client";

export type AppMode = "generate" | "xmlToHtml";

type ToolSwitcherProps = {
  mode: AppMode;
  onModeChange: (mode: AppMode) => void;
  docsUrl: string;
};

export default function ToolSwitcher({ mode, onModeChange, docsUrl }: ToolSwitcherProps) {
  function handleKeyDown(event: React.KeyboardEvent) {
    if (event.key === "ArrowRight") onModeChange("xmlToHtml");
    else if (event.key === "ArrowLeft") onModeChange("generate");
  }

  return (
    <div className="tool-bar">
      <div
        className="mode-tabs"
        role="tablist"
        aria-label="App mode"
        onKeyDown={handleKeyDown}
      >
        <button
          type="button"
          id="tab-generate"
          role="tab"
          className={mode === "generate" ? "mode-tab active" : "mode-tab"}
          aria-selected={mode === "generate"}
          aria-controls="panel-generate"
          onClick={() => onModeChange("generate")}
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
          onClick={() => onModeChange("xmlToHtml")}
        >
          XML → HTML
        </button>
      </div>
      <a className="docs-link" href={docsUrl} target="_blank" rel="noreferrer">
        API Docs
      </a>
    </div>
  );
}
