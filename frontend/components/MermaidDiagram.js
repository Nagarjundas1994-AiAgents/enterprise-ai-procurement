"use client";

import { useEffect, useId, useState } from "react";
import mermaid from "mermaid";

let initializedTheme = null;

function currentTheme() {
  if (typeof document === "undefined") return "dark";
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

function ensureInit(theme) {
  if (initializedTheme === theme) return;
  const light = theme === "light";
  mermaid.initialize({
    startOnLoad: false,
    theme: light ? "base" : "dark",
    securityLevel: "loose",
    flowchart: { htmlLabels: true, curve: "basis" },
    themeVariables: light
      ? {
          darkMode: false,
          background: "#ffffff",
          primaryColor: "#e8eefb",
          primaryTextColor: "#16233a",
          primaryBorderColor: "#a97e2f",
          lineColor: "#0a6ed1",
          secondaryColor: "#f1f4fa",
          tertiaryColor: "#e3e9f4",
          edgeLabelBackground: "#ffffff",
          clusterBkg: "#f4f6fb",
          clusterBorder: "#a97e2f",
          titleColor: "#16233a"
        }
      : {
          darkMode: true,
          background: "#0a1122",
          primaryColor: "#1b2a4d",
          primaryTextColor: "#eef2fa",
          primaryBorderColor: "#d4af69",
          lineColor: "#7fb0ff",
          secondaryColor: "#13203c",
          tertiaryColor: "#0d1528"
        }
  });
  initializedTheme = theme;
}

/**
 * Renders a single mermaid diagram to SVG.
 * SSR-safe: shows <pre> until mounted, then swaps in the SVG.
 * On parse failure shows the source + error (never blank).
 */
export default function MermaidDiagram({ code }) {
  const rawId = useId().replace(/[^a-zA-Z0-9]/g, "");
  const [svg, setSvg] = useState("");
  const [error, setError] = useState("");
  // Bumps whenever the UI theme flips so the diagram re-renders in the new theme.
  const [themeTick, setThemeTick] = useState(0);

  useEffect(() => {
    const bump = () => setThemeTick((t) => t + 1);
    window.addEventListener("pc-theme-change", bump);
    const obs =
      typeof MutationObserver !== "undefined"
        ? new MutationObserver((mut) => {
            if (mut.some((m) => m.attributeName === "data-theme")) bump();
          })
        : null;
    if (obs && typeof document !== "undefined") {
      obs.observe(document.documentElement, { attributes: true });
    }
    return () => {
      window.removeEventListener("pc-theme-change", bump);
      if (obs) obs.disconnect();
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    ensureInit(currentTheme());
    setSvg("");
    setError("");
    const clean = String(code || "").trim();
    if (!clean) return;
    // mermaid.render requires a unique diagram id per call
    const diagramId = `mmd-${rawId}-${Math.random().toString(36).slice(2, 8)}`;
    (async () => {
      try {
        const result = await mermaid.render(diagramId, clean);
        const out = typeof result === "string" ? result : result.svg;
        if (!cancelled) setSvg(out || "");
      } catch (e) {
        if (!cancelled) setError(String((e && e.message) || e));
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, rawId, themeTick]);

  if (error) {
    return (
      <div className="mermaid-fallback">
        <pre className="md-pre">{String(code)}</pre>
        <div className="mermaid-error">Diagram could not be rendered: {error}</div>
      </div>
    );
  }
  if (!svg) {
    // Loading state: show source so layout does not jump
    return <pre className="md-pre">{String(code)}</pre>;
  }
  return (
    <div className="mermaid-diagram-wrap">
      <div className="mermaid-diagram" dangerouslySetInnerHTML={{ __html: svg }} />
      <details className="mermaid-source">
        <summary>View diagram source</summary>
        <pre className="md-pre">{String(code)}</pre>
      </details>
    </div>
  );
}
