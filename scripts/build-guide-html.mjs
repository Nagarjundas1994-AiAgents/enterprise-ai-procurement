import fs from 'fs';
import path from 'path';

const sourceMdPath = 'C:/Users/nagar/.gemini/antigravity-ide/brain/67ea9316-4263-477c-9cf8-119764b8a3d1/enterprise_ai_procurement_complete_guide.md';
const outputHtmlPath1 = path.resolve('enterprise-ai-procurement-guide.html');
const outputHtmlPath2 = path.resolve('docs/enterprise-ai-procurement-guide.html');

console.log('Reading source markdown from:', sourceMdPath);
const md = fs.readFileSync(sourceMdPath, 'utf8');
console.log('Source loaded. Length:', md.length);

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/<[^>]+>/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// Parse markdown into tokens
const lines = md.split('\n');
let html = '';
let inCode = false;
let codeLang = '';
let codeBuffer = [];
let inTable = false;
let tableBuffer = [];
let inList = false;
let listType = ''; // 'ul' or 'ol'
let inBlockquote = false;
let bqBuffer = [];

function flushBlockquote() {
  if (!inBlockquote) return '';
  inBlockquote = false;
  const content = bqBuffer.join('\n').trim();
  bqBuffer = [];
  
  let alertType = 'note';
  let cleanContent = content;
  if (content.startsWith('[!NOTE]')) {
    alertType = 'note';
    cleanContent = content.substring(7).trim();
  } else if (content.startsWith('[!TIP]')) {
    alertType = 'tip';
    cleanContent = content.substring(6).trim();
  } else if (content.startsWith('[!IMPORTANT]')) {
    alertType = 'important';
    cleanContent = content.substring(12).trim();
  } else if (content.startsWith('[!WARNING]')) {
    alertType = 'warning';
    cleanContent = content.substring(10).trim();
  } else if (content.startsWith('[!CAUTION]')) {
    alertType = 'caution';
    cleanContent = content.substring(10).trim();
  } else {
    return `<blockquote class="styled-quote"><div class="quote-bar"></div><div class="quote-body">${inlineFormat(cleanContent)}</div></blockquote>\n`;
  }

  const icons = {
    note: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    tip: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8.5 14.5A2.5 2.5 0 0011 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 11-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 002.5 2.5z"/></svg>',
    important: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    caution: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
  };

  return `<div class="callout callout-${alertType}">
    <div class="callout-icon">${icons[alertType] || icons.note}</div>
    <div class="callout-content">
      <div class="callout-title">${alertType.toUpperCase()}</div>
      <div class="callout-text">${inlineFormat(cleanContent)}</div>
    </div>
  </div>\n`;
}

function flushTable() {
  if (!inTable) return '';
  inTable = false;
  if (tableBuffer.length === 0) return '';
  
  let headerRow = tableBuffer[0];
  let bodyRows = tableBuffer.slice(2);
  
  let tableHtml = '<div class="table-responsive"><table class="data-table"><thead><tr>';
  const headers = headerRow.split('|').map(s => s.trim()).filter((s, i, arr) => i > 0 && i < arr.length - 1);
  headers.forEach(h => {
    tableHtml += `<th>${inlineFormat(h)}</th>`;
  });
  tableHtml += '</tr></thead><tbody>';

  bodyRows.forEach(row => {
    const cells = row.split('|').map(s => s.trim()).filter((s, i, arr) => i > 0 && i < arr.length - 1);
    if (cells.length > 0) {
      tableHtml += '<tr>';
      cells.forEach(c => {
        tableHtml += `<td>${inlineFormat(c)}</td>`;
      });
      tableHtml += '</tr>';
    }
  });

  tableHtml += '</tbody></table></div>\n';
  tableBuffer = [];
  return tableHtml;
}

function flushList() {
  if (!inList) return '';
  const tag = listType;
  inList = false;
  listType = '';
  return `</${tag}>\n`;
}

function inlineFormat(text) {
  if (!text) return '';
  return text
    .replace(/`([^`]+)`/g, (m, code) => `<code class="inline-code">${escapeHtml(code)}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, label, url) => {
      if (url.startsWith('file:///')) {
        const basename = label || path.basename(url);
        return `<span class="file-ref" title="File: ${escapeHtml(url)}" onclick="navigator.clipboard.writeText('${escapeHtml(url)}')"><svg class="ref-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><code>${escapeHtml(basename)}</code></span>`;
      }
      return `<a href="${escapeHtml(url)}" class="doc-link" target="${url.startsWith('#') ? '_self' : '_blank'}" rel="noopener">${escapeHtml(label)}</a>`;
    });
}

function renderDiagramCard(rawCode, title = 'Interactive Architecture Diagram') {
  const diagramId = 'mermaid-' + Math.random().toString(36).substring(2, 9);
  return `<div class="diagram-card" id="${diagramId}-card">
    <div class="diagram-toolbar">
      <div class="diagram-tag">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="3"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/></svg>
        <span>${title}</span>
      </div>
      <div class="diagram-actions">
        <div class="btn-group-zoom">
          <button class="btn-zoom" onclick="zoomDiagram('${diagramId}', -0.15)" title="Zoom Out">&minus;</button>
          <button class="btn-zoom" onclick="resetDiagramZoom('${diagramId}')" title="Reset Zoom (100%)">100%</button>
          <button class="btn-zoom" onclick="zoomDiagram('${diagramId}', 0.15)" title="Zoom In">&plus;</button>
        </div>
        <button class="btn-sm" onclick="toggleDiagramFullscreen('${diagramId}')" title="Toggle Fullscreen">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
          <span>Fullscreen</span>
        </button>
        <button class="btn-sm" onclick="toggleDiagramSource('${diagramId}')">View Source</button>
        <button class="btn-sm btn-primary-sm" onclick="copyDiagramCode('${diagramId}')">Copy Code</button>
      </div>
    </div>
    <div class="mermaid-container" id="${diagramId}-view">
      <div class="mermaid-pan-wrapper" id="${diagramId}-pan">
        <pre class="mermaid">${rawCode}</pre>
      </div>
    </div>
    <div class="diagram-source-view" id="${diagramId}-src" style="display:none;">
      <pre><code class="language-mermaid">${escapeHtml(rawCode)}</code></pre>
    </div>
  </div>\n`;
}

const navSections = [];
let currentSecId = '';
let currentSecNum = '';
let currentSecTitle = '';
let inSection = false;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];

  // Code blocks
  if (line.startsWith('```')) {
    if (!inCode) {
      html += flushList();
      html += flushTable();
      html += flushBlockquote();
      inCode = true;
      codeLang = line.replace('```', '').trim();
      codeBuffer = [];
      continue;
    } else {
      inCode = false;
      const rawCode = codeBuffer.join('\n');
      if (codeLang === 'mermaid') {
        html += renderDiagramCard(rawCode, 'Mermaid Vector Diagram');
      } else {
        const codeId = 'code-' + Math.random().toString(36).substring(2, 9);
        let langLabel = codeLang ? codeLang.toUpperCase() : 'CODE';
        html += `<div class="code-panel">
          <div class="code-panel-header">
            <div class="code-lang-badge">${langLabel}</div>
            <button class="btn-copy" onclick="copyCodeBlock(this)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
              <span>Copy</span>
            </button>
          </div>
          <pre class="code-pre"><code class="language-${codeLang || 'text'}">${escapeHtml(rawCode)}</code></pre>
        </div>\n`;
      }
      codeBuffer = [];
      codeLang = '';
      continue;
    }
  }

  if (inCode) {
    codeBuffer.push(line);
    continue;
  }

  // Blockquote
  if (line.startsWith('>')) {
    html += flushList();
    html += flushTable();
    inBlockquote = true;
    bqBuffer.push(line.replace(/^>\s?/, ''));
    continue;
  } else if (inBlockquote) {
    html += flushBlockquote();
  }

  // Tables
  if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
    html += flushList();
    inTable = true;
    tableBuffer.push(line.trim());
    continue;
  } else if (inTable) {
    html += flushTable();
  }

  // Lists
  const ulMatch = line.match(/^(\s*)[-*+]\s+(.*)$/);
  const olMatch = line.match(/^(\s*)\d+\.\s+(.*)$/);

  if (ulMatch) {
    if (!inList || listType !== 'ul') {
      html += flushList();
      inList = true;
      listType = 'ul';
      html += '<ul class="guide-list">\n';
    }
    html += `<li>${inlineFormat(ulMatch[2])}</li>\n`;
    continue;
  } else if (olMatch) {
    if (!inList || listType !== 'ol') {
      html += flushList();
      inList = true;
      listType = 'ol';
      html += '<ol class="guide-ordered-list">\n';
    }
    html += `<li>${inlineFormat(olMatch[2])}</li>\n`;
    continue;
  } else if (inList) {
    html += flushList();
  }

  // Headings
  if (line.startsWith('# ')) {
    const titleText = line.substring(2).trim();
    html += `<div class="hero-header">
      <div class="hero-badge">SAP CAP + A2A + MCP CONTROL TOWER</div>
      <h1 class="hero-title">${escapeHtml(titleText)}</h1>
      <p class="hero-subtitle">Production-grade enterprise procurement platform with autonomous agent workflows, policy-governed authorization, and end-to-end auditability.</p>
      <div class="hero-stats">
        <div class="stat-pill"><span class="stat-val">18</span><span class="stat-lbl">Detailed Chapters</span></div>
        <div class="stat-pill"><span class="stat-val">18</span><span class="stat-lbl">Mermaid Diagrams</span></div>
        <div class="stat-pill"><span class="stat-val">15</span><span class="stat-lbl">MCP Business Tools</span></div>
        <div class="stat-pill"><span class="stat-val">7</span><span class="stat-lbl">A2A Autonomous Agents</span></div>
        <div class="stat-pill"><span class="stat-val">100%</span><span class="stat-lbl">Production Code Ready</span></div>
      </div>
    </div>\n`;
    continue;
  }

  if (line.startsWith('## Table of Contents')) {
    html += `<div class="toc-banner card">
      <div class="toc-banner-title">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
        <h3>Master Blueprint Navigator</h3>
      </div>
      <p class="text-muted">Explore all 18 chapters of the implementation architecture below. Track your completion progress or jump directly to any technical component.</p>
      <div class="chapter-matrix" id="toc-matrix">
        <!-- Rendered by JS -->
      </div>
    </div>\n`;
    while (i + 1 < lines.length && !lines[i + 1].startsWith('## 1. ')) {
      i++;
    }
    continue;
  }

  const h2Match = line.match(/^##\s+(\d+)\.\s+(.*)$/);
  if (h2Match) {
    if (inSection) {
      html += '</section>\n';
    }
    inSection = true;
    currentSecNum = h2Match[1];
    currentSecTitle = h2Match[2].trim();
    currentSecId = 'chapter-' + currentSecNum;
    navSections.push({
      id: currentSecId,
      num: currentSecNum,
      title: currentSecTitle
    });

    html += `<section class="guide-section" id="${currentSecId}" data-sec-num="${currentSecNum}">
      <div class="section-anchor-header">
        <div class="sec-num-badge">Chapter ${currentSecNum}</div>
        <h2 class="section-heading">${escapeHtml(currentSecTitle)}</h2>
        <button class="sec-check-btn" onclick="toggleChapterDone('${currentSecId}')" title="Mark as completed">
          <svg class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
          <span class="check-lbl">Mark Done</span>
        </button>
      </div>\n`;

    // Inject Additional Diagram for Chapter 17 (Local Dev Pipeline)
    if (currentSecNum === '17') {
      const localDevFlow = `flowchart TD
    START["1. Clone & Install<br/>npm install"] --> ENV["2. Configure Env<br/>cp .env.example .env"]
    ENV --> BOOT["3. Boot CAP Server<br/>npm start (port 4004)"]
    BOOT --> A2A["4. Boot Remote Agent<br/>npm run remote-agent (port 4007)"]
    A2A --> HEALTH["5. Verify Health<br/>curl /health &rarr; alive"]
    HEALTH --> TEST_WORKFLOW["6. Test Procurement Lifecycle<br/>Alice PR &rarr; Bob Approval &rarr; PO"]
    TEST_WORKFLOW --> TEST_MCP["7. Test MCP Tools<br/>callTool: search_procurement"]
    TEST_MCP --> VITEST["8. Run Vitest Security Tests<br/>npm test &rarr; 100% Passing"]
    
    style START fill:#0a84ff22,stroke:#0a84ff,stroke-width:2px
    style BOOT fill:#10b98122,stroke:#10b981,stroke-width:2px
    style VITEST fill:#8b5cf622,stroke:#8b5cf6,stroke-width:2px`;
      html += renderDiagramCard(localDevFlow, 'Local Execution & Verification Pipeline');
    }
    continue;
  }

  const h3Match = line.match(/^###\s+(.*)$/);
  if (h3Match) {
    const h3Text = h3Match[1].trim();
    const h3Id = slugify(h3Text);
    html += `<h3 class="guide-h3" id="${h3Id}"><a href="#${h3Id}" class="anchor-hash">#</a> ${inlineFormat(h3Text)}</h3>\n`;

    // Inject Additional Diagram for Chapter 8.1 (ProcurementService OData Actions)
    if (h3Text.includes('8.1 ProcurementService')) {
      const serviceFlow = `flowchart LR
    subgraph ClientLayer["Clients & AI Agents"]
        EMP["Employee / Manager"]
        LLM["AI Agent / MCP Client"]
    end

    subgraph ServiceLayer["ProcurementService (/odata/v4/procurement)"]
        direction TB
        ACTIONS["Bound Actions:<br/>• submitRequisition<br/>• approveRequisition<br/>• rejectRequisition<br/>• createPurchaseOrder<br/>• receiveGoods<br/>• matchInvoice"]
        ENTITIES["CRUD Entities:<br/>• PurchaseRequisitions<br/>• PurchaseOrders<br/>• GoodsReceipts<br/>• Invoices<br/>• Budgets"]
    end

    subgraph Governance["Governance & Persistence"]
        POL["Policy Engine<br/>(Rules & Risk Thresholds)"]
        AUD["Audit Logger<br/>(Tamper-evident logs)"]
        DB[("PostgreSQL / SQLite<br/>(Tenant-Isolated)")]
    end

    EMP --> ServiceLayer
    LLM --> ServiceLayer
    ServiceLayer --> POL
    POL --> AUD
    ServiceLayer --> DB
    
    style ServiceLayer fill:#1e293b,stroke:#0ea5e9,stroke-width:2px
    style Governance fill:#0f172a,stroke:#8b5cf6,stroke-width:2px`;
      html += renderDiagramCard(serviceFlow, 'ProcurementService Architecture & Governance Flow');
    }

    // Inject Additional Diagram for Chapter 9.6 (3-Way Invoice Matching)
    if (h3Text.includes('9.6 Three-Way Invoice Matching')) {
      const matchFlow = `flowchart TD
    INV["Supplier Invoice Received<br/>(Amount, Quantity, PO Ref)"] --> FETCH["Fetch Purchase Order &<br/>Goods Receipt from DB"]
    FETCH --> CHECK_PO{"PO exists &<br/>Approved?"}
    CHECK_PO -->|No| REJ_PO["REJECT: Invalid PO Reference"]
    CHECK_PO -->|Yes| CHECK_GR{"Goods Receipt<br/>Recorded?"}
    CHECK_GR -->|No| REJ_GR["HOLD: Goods Not Yet Received"]
    CHECK_GR -->|Yes| MATCH["Compare 3 Dimensions:<br/>1. Unit Price Tolerance (&le; 2%)<br/>2. Quantity Received vs Billed<br/>3. Tax & Line Item Surcharges"]
    MATCH --> TOL{"Within Tolerances?"}
    TOL -->|Yes| AUTO_MATCH["Status: MATCHED<br/>Auto-Schedule Payment"]
    TOL -->|No| DISC["Status: DISCREPANCY<br/>Route to AP Exception Queue"]
    
    style AUTO_MATCH fill:#10b98122,stroke:#10b981,stroke-width:2px
    style DISC fill:#f43f5e22,stroke:#f43f5e,stroke-width:2px`;
      html += renderDiagramCard(matchFlow, 'Three-Way Invoice Matching Algorithm');
    }

    // Inject Additional Diagram for Chapter 9.8 (Prompt Injection Defense)
    if (h3Text.includes('9.8 Prompt Injection Defense')) {
      const shieldFlow = `flowchart LR
    RAW["Raw User / Vendor Input<br/>e.g. PR Description, Notes"] --> SAN["sanitizeForLLM()"]
    SAN --> DELIM["Strip System Delimiters<br/>(---, \`\`\`, &lt;system&gt;)"]
    DELIM --> PATTERN["Neutralize Injection Patterns<br/>('ignore previous instructions', etc.)"]
    PATTERN --> SAFE["Encapsulate in XML Data Boundary<br/>&lt;untrusted_business_data&gt;"]
    SAFE --> LLM["LLM Agent Prompt Context"]
    
    style RAW fill:#f43f5e18,stroke:#f43f5e,stroke-width:2px
    style SAFE fill:#10b98118,stroke:#10b981,stroke-width:2px`;
      html += renderDiagramCard(shieldFlow, 'Prompt Injection & Sanitization Shield Flow');
    }
    continue;
  }

  const h4Match = line.match(/^####\s+(.*)$/);
  if (h4Match) {
    const h4Text = h4Match[1].trim();
    const h4Id = slugify(h4Text);
    html += `<h4 class="guide-h4" id="${h4Id}">${inlineFormat(h4Text)}</h4>\n`;
    continue;
  }

  if (line.trim() === '---') {
    html += '<hr class="section-divider"/>\n';
    continue;
  }

  if (line.trim().length === 0) {
    continue;
  }

  html += `<p class="guide-p">${inlineFormat(line)}</p>\n`;
}

if (inSection) {
  html += '</section>\n';
}

console.log('Markdown parsed successfully into HTML. Nav sections:', navSections.length);

const fullHtml = `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Enterprise AI Procurement — Complete End-to-End Build Guide</title>
  <meta name="description" content="A production-grade, multi-tenant procurement platform powered by SAP CAP, PostgreSQL, AI Agents (MCP + A2A), and enterprise-grade RBAC." />
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">

  <!-- Highlight.js for code syntax highlighting -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/tokyo-night-dark.min.css" id="hljs-theme">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/typescript.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/json.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/yaml.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/sql.min.js"></script>

  <!-- Mermaid.js for Interactive Native Vector Diagrams -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

  <style>
    :root {
      --bg: #0b101b;
      --bg-surface: #111827;
      --bg-card: #141f32;
      --bg-card-hover: #19273f;
      --bg-code: #090e17;
      --border: #1e2e47;
      --border-bright: #2d456a;
      
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --text-faint: #64748b;
      
      --sap-blue: #0a84ff;
      --sap-cyan: #00d2ff;
      --sap-indigo: #6366f1;
      --sap-purple: #8b5cf6;
      --sap-emerald: #10b981;
      --sap-amber: #f59e0b;
      --sap-rose: #f43f5e;
      
      --accent-gradient: linear-gradient(135deg, #0a84ff 0%, #00d2ff 50%, #8b5cf6 100%);
      --card-gradient: linear-gradient(180deg, rgba(20, 31, 50, 0.8) 0%, rgba(17, 24, 39, 0.95) 100%);
      --glow-blue: 0 0 25px rgba(10, 132, 255, 0.25);
      
      --sidebar-w: 320px;
      --header-h: 68px;
      --radius: 12px;
      --radius-sm: 8px;
      --font-body: 'Inter', system-ui, -apple-system, sans-serif;
      --font-title: 'Outfit', 'Inter', system-ui, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    [data-theme="light"] {
      --bg: #f8fafc;
      --bg-surface: #ffffff;
      --bg-card: #ffffff;
      --bg-card-hover: #f1f5f9;
      --bg-code: #0f172a;
      --border: #e2e8f0;
      --border-bright: #cbd5e1;
      
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-faint: #94a3b8;
      
      --sap-blue: #0284c7;
      --sap-cyan: #0891b2;
      --sap-indigo: #4f46e5;
      --sap-purple: #7c3aed;
      --sap-emerald: #059669;
      --sap-amber: #d97706;
      --sap-rose: #e11d48;
      
      --card-gradient: #ffffff;
      --glow-blue: 0 4px 20px rgba(2, 132, 199, 0.12);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; scroll-padding-top: calc(var(--header-h) + 24px); }
    body {
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.65;
      font-size: 15px;
      overflow-x: hidden;
    }

    /* Top Reading Progress Bar */
    #progress-bar {
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: var(--accent-gradient);
      z-index: 1000;
      width: 0%;
      transition: width 0.1s ease-out;
      box-shadow: 0 0 10px #0a84ff;
    }

    /* Header */
    header.main-header {
      position: sticky;
      top: 0;
      height: var(--header-h);
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 28px;
      z-index: 100;
    }
    [data-theme="light"] header.main-header {
      background: rgba(255, 255, 255, 0.9);
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 14px;
      text-decoration: none;
      color: inherit;
    }
    .brand-icon {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: var(--glow-blue);
    }
    .brand-text h1 {
      font-family: var(--font-title);
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      line-height: 1.2;
    }
    .brand-text span {
      font-size: 0.75rem;
      color: var(--sap-cyan);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .search-box-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }
    .search-box-wrapper svg {
      position: absolute;
      left: 12px;
      color: var(--text-faint);
      pointer-events: none;
    }
    .search-input {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 8px 14px 8px 36px;
      border-radius: var(--radius-sm);
      font-size: 0.85rem;
      width: 260px;
      transition: all 0.2s;
    }
    .search-input:focus {
      outline: none;
      border-color: var(--sap-blue);
      box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.2);
      width: 340px;
    }
    .search-kbd {
      position: absolute;
      right: 10px;
      background: var(--border);
      color: var(--text-muted);
      font-size: 0.7rem;
      padding: 2px 6px;
      border-radius: 4px;
      pointer-events: none;
    }

    .btn-header {
      background: var(--bg-surface);
      color: var(--text-main);
      border: 1px solid var(--border);
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .btn-header:hover {
      background: var(--border);
      border-color: var(--border-bright);
    }
    .btn-theme {
      padding: 8px;
    }

    /* Layout */
    .app-layout {
      display: flex;
      min-height: calc(100vh - var(--header-h));
    }

    /* Sidebar */
    aside.sidebar {
      width: var(--sidebar-w);
      min-width: var(--sidebar-w);
      background: var(--bg-surface);
      border-right: 1px solid var(--border);
      height: calc(100vh - var(--header-h));
      position: sticky;
      top: var(--header-h);
      overflow-y: auto;
      padding: 20px 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .sidebar-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }
    .sidebar-title {
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--text-faint);
    }
    .sidebar-progress {
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--sap-emerald);
      background: rgba(16, 185, 129, 0.1);
      padding: 2px 8px;
      border-radius: 999px;
    }

    .nav-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
      list-style: none;
    }
    .nav-item a {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      border-radius: var(--radius-sm);
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 500;
      transition: all 0.15s;
    }
    .nav-item a:hover {
      color: var(--text-main);
      background: var(--bg-card);
    }
    .nav-item.active a {
      color: #ffffff;
      background: var(--sap-blue);
      font-weight: 600;
      box-shadow: 0 4px 14px rgba(10, 132, 255, 0.35);
    }
    .nav-num {
      width: 22px;
      height: 22px;
      border-radius: 6px;
      background: var(--border);
      color: var(--text-muted);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 700;
      font-family: var(--font-mono);
      flex-shrink: 0;
    }
    .nav-item.active .nav-num {
      background: rgba(255, 255, 255, 0.25);
      color: #ffffff;
    }
    .nav-item.completed a {
      border-left: 3px solid var(--sap-emerald);
    }

    /* Main Content */
    main.content-area {
      flex: 1;
      padding: 40px 48px;
      max-width: 1220px;
      margin: 0 auto;
      overflow-x: hidden;
    }

    /* Hero */
    .hero-header {
      background: var(--card-gradient);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 36px 40px;
      margin-bottom: 36px;
      position: relative;
      overflow: hidden;
      box-shadow: var(--glow-blue);
    }
    .hero-header::before {
      content: '';
      position: absolute;
      top: -50%;
      right: -20%;
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, rgba(10, 132, 255, 0.18) 0%, transparent 70%);
      pointer-events: none;
    }
    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      color: var(--sap-cyan);
      background: rgba(0, 210, 255, 0.12);
      border: 1px solid rgba(0, 210, 255, 0.3);
      padding: 4px 12px;
      border-radius: 999px;
      margin-bottom: 14px;
    }
    .hero-title {
      font-family: var(--font-title);
      font-size: 2.25rem;
      font-weight: 800;
      line-height: 1.25;
      margin-bottom: 14px;
      letter-spacing: -0.02em;
    }
    .hero-subtitle {
      font-size: 1.05rem;
      color: var(--text-muted);
      max-width: 850px;
      margin-bottom: 24px;
      line-height: 1.6;
    }
    .hero-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 14px;
    }
    .stat-pill {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
    }
    .stat-val {
      font-size: 1.4rem;
      font-weight: 800;
      font-family: var(--font-mono);
      color: var(--sap-blue);
      line-height: 1;
      margin-bottom: 4px;
    }
    .stat-lbl {
      font-size: 0.75rem;
      color: var(--text-faint);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    /* TOC Banner */
    .toc-banner {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px;
      margin-bottom: 36px;
    }
    .toc-banner-title {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--sap-blue);
      margin-bottom: 6px;
    }
    .toc-banner-title h3 {
      font-family: var(--font-title);
      font-size: 1.2rem;
      color: var(--text-main);
    }
    .chapter-matrix {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 10px;
      margin-top: 18px;
    }
    .matrix-card {
      display: flex;
      align-items: center;
      gap: 12px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      text-decoration: none;
      color: var(--text-main);
      transition: all 0.2s;
    }
    .matrix-card:hover {
      background: var(--bg-card-hover);
      border-color: var(--sap-blue);
      transform: translateY(-2px);
    }
    .matrix-num {
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: var(--border);
      color: var(--sap-cyan);
      font-family: var(--font-mono);
      font-weight: 700;
      font-size: 0.85rem;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .matrix-title {
      font-size: 0.86rem;
      font-weight: 600;
      line-height: 1.3;
    }

    /* Guide Sections */
    .guide-section {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 36px;
      margin-bottom: 36px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    [data-theme="light"] .guide-section {
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }

    .section-anchor-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .sec-num-badge {
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      background: rgba(10, 132, 255, 0.12);
      color: var(--sap-blue);
      border: 1px solid rgba(10, 132, 255, 0.3);
      padding: 4px 10px;
      border-radius: 6px;
    }
    .section-heading {
      font-family: var(--font-title);
      font-size: 1.65rem;
      font-weight: 700;
      color: var(--text-main);
      flex: 1;
      margin-left: 12px;
      letter-spacing: -0.01em;
    }
    .sec-check-btn {
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .sec-check-btn:hover {
      background: var(--border);
      color: var(--text-main);
    }
    .sec-check-btn.checked {
      background: rgba(16, 185, 129, 0.15);
      border-color: var(--sap-emerald);
      color: var(--sap-emerald);
    }

    .guide-h3 {
      font-family: var(--font-title);
      font-size: 1.22rem;
      font-weight: 700;
      color: var(--text-main);
      margin: 28px 0 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .anchor-hash {
      color: var(--text-faint);
      text-decoration: none;
      opacity: 0.4;
      transition: opacity 0.2s;
    }
    .anchor-hash:hover {
      opacity: 1;
      color: var(--sap-blue);
    }
    .guide-h4 {
      font-family: var(--font-title);
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--sap-cyan);
      margin: 20px 0 10px;
    }
    .guide-p {
      margin-bottom: 16px;
      color: var(--text-muted);
      line-height: 1.7;
    }
    .guide-p strong {
      color: var(--text-main);
    }
    .section-divider {
      border: 0;
      height: 1px;
      background: var(--border);
      margin: 28px 0;
    }

    /* Lists */
    .guide-list, .guide-ordered-list {
      margin-left: 24px;
      margin-bottom: 18px;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .guide-list li, .guide-ordered-list li {
      line-height: 1.6;
    }
    .guide-list li strong, .guide-ordered-list li strong {
      color: var(--text-main);
    }

    /* Code Blocks */
    .code-panel {
      background: var(--bg-code);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      margin: 18px 0 24px;
      overflow: hidden;
      box-shadow: 0 4px 14px rgba(0,0,0,0.3);
    }
    .code-panel-header {
      background: rgba(255, 255, 255, 0.03);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 16px;
    }
    .code-lang-badge {
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--sap-blue);
      letter-spacing: 0.06em;
      font-family: var(--font-mono);
    }
    .btn-copy {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-faint);
      font-size: 0.75rem;
      padding: 4px 10px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s;
    }
    .btn-copy:hover {
      background: var(--border);
      color: var(--text-main);
    }
    .code-pre {
      padding: 16px 20px;
      overflow-x: auto;
      font-family: var(--font-mono);
      font-size: 0.88rem;
      line-height: 1.55;
    }
    .code-pre code {
      background: transparent !important;
      padding: 0 !important;
      border: 0 !important;
    }
    .inline-code {
      background: rgba(10, 132, 255, 0.1);
      color: var(--sap-cyan);
      border: 1px solid rgba(10, 132, 255, 0.2);
      font-family: var(--font-mono);
      font-size: 0.88em;
      padding: 1px 6px;
      border-radius: 4px;
    }

    /* Diagram Cards - Premium Sizing & Interactive Controls */
    .diagram-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      margin: 28px 0;
      overflow: hidden;
      box-shadow: 0 8px 30px rgba(0,0,0,0.3);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .diagram-card:hover {
      border-color: var(--border-bright);
    }
    .diagram-toolbar {
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 18px;
      flex-wrap: wrap;
      gap: 10px;
    }
    .diagram-tag {
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--sap-purple);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .diagram-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .btn-group-zoom {
      display: inline-flex;
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow: hidden;
      background: var(--bg-card);
    }
    .btn-zoom {
      background: transparent;
      border: 0;
      border-right: 1px solid var(--border);
      color: var(--text-muted);
      padding: 5px 10px;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-zoom:last-child {
      border-right: 0;
    }
    .btn-zoom:hover {
      background: var(--border);
      color: var(--text-main);
    }
    .btn-sm {
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 5px 10px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s;
    }
    .btn-sm:hover {
      background: var(--border);
      color: var(--text-main);
    }
    .btn-primary-sm {
      background: rgba(10, 132, 255, 0.15);
      border-color: rgba(10, 132, 255, 0.35);
      color: var(--sap-blue);
    }
    .btn-primary-sm:hover {
      background: var(--sap-blue);
      color: #ffffff;
    }

    /* Mermaid Container with Expanded Dimensions */
    .mermaid-container {
      padding: 40px 24px;
      overflow-x: auto;
      overflow-y: hidden;
      display: flex;
      justify-content: center;
      align-items: center;
      background: radial-gradient(circle at center, rgba(17, 24, 39, 0.4) 0%, rgba(9, 14, 23, 0.9) 100%);
      background-image: 
        radial-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px),
        radial-gradient(circle at center, rgba(17, 24, 39, 0.4) 0%, rgba(9, 14, 23, 0.9) 100%);
      background-size: 24px 24px, 100% 100%;
      min-height: 480px;
      position: relative;
    }
    [data-theme="light"] .mermaid-container {
      background: #f8fafc;
      background-image: 
        radial-gradient(#cbd5e1 1px, transparent 1px);
      background-size: 24px 24px;
    }
    .mermaid-pan-wrapper {
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      transform-origin: center center;
    }
    .mermaid-container svg {
      width: 100% !important;
      max-width: 100% !important;
      min-width: min(100%, 820px);
      height: auto !important;
      min-height: 420px;
      font-size: 15px !important;
      filter: drop-shadow(0 8px 24px rgba(0,0,0,0.35));
    }
    .mermaid-container svg .actor {
      stroke-width: 2px !important;
      font-weight: 700 !important;
    }
    .mermaid-container svg text {
      font-family: 'Inter', system-ui, sans-serif !important;
      font-size: 14.5px !important;
    }
    .mermaid-container svg .node rect,
    .mermaid-container svg .node circle,
    .mermaid-container svg .node polygon {
      stroke-width: 2px !important;
    }
    .mermaid-container svg .edgePath .path {
      stroke-width: 2px !important;
    }

    /* Diagram Fullscreen Mode */
    .diagram-card.is-fullscreen {
      position: fixed;
      inset: 24px;
      z-index: 2500;
      margin: 0;
      max-height: calc(100vh - 48px);
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 80px rgba(0,0,0,0.85);
      border: 1px solid var(--sap-blue);
      border-radius: var(--radius);
    }
    .diagram-card.is-fullscreen .mermaid-container {
      flex: 1;
      min-height: 0;
      overflow: auto;
    }
    .diagram-card.is-fullscreen .mermaid-container svg {
      min-width: 960px;
      min-height: 600px;
    }

    .diagram-source-view {
      padding: 16px;
      background: var(--bg-code);
      border-top: 1px solid var(--border);
    }

    /* Tables */
    .table-responsive {
      overflow-x: auto;
      margin: 20px 0;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
    }
    .data-table th {
      background: var(--bg-card);
      color: var(--text-main);
      font-weight: 700;
      text-align: left;
      padding: 12px 16px;
      border-bottom: 2px solid var(--border);
      font-family: var(--font-title);
    }
    .data-table td {
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      color: var(--text-muted);
    }
    .data-table tr:hover td {
      background: var(--bg-card-hover);
      color: var(--text-main);
    }

    /* Callouts */
    .callout {
      display: flex;
      gap: 14px;
      padding: 16px 20px;
      border-radius: var(--radius-sm);
      margin: 20px 0;
      border: 1px solid;
    }
    .callout-icon {
      flex-shrink: 0;
      margin-top: 2px;
    }
    .callout-title {
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      margin-bottom: 4px;
    }
    .callout-text {
      font-size: 0.9rem;
      line-height: 1.6;
    }
    .callout-note {
      background: rgba(10, 132, 255, 0.08);
      border-color: rgba(10, 132, 255, 0.25);
      color: var(--text-main);
    }
    .callout-note .callout-icon, .callout-note .callout-title { color: var(--sap-blue); }
    .callout-tip {
      background: rgba(16, 185, 129, 0.08);
      border-color: rgba(16, 185, 129, 0.25);
      color: var(--text-main);
    }
    .callout-tip .callout-icon, .callout-tip .callout-title { color: var(--sap-emerald); }
    .callout-important, .callout-warning {
      background: rgba(245, 158, 11, 0.08);
      border-color: rgba(245, 158, 11, 0.25);
      color: var(--text-main);
    }
    .callout-important .callout-icon, .callout-important .callout-title,
    .callout-warning .callout-icon, .callout-warning .callout-title { color: var(--sap-amber); }
    .callout-caution {
      background: rgba(244, 63, 94, 0.08);
      border-color: rgba(244, 63, 94, 0.25);
      color: var(--text-main);
    }
    .callout-caution .callout-icon, .callout-caution .callout-title { color: var(--sap-rose); }

    /* Quotes */
    .styled-quote {
      display: flex;
      gap: 14px;
      margin: 18px 0;
      background: var(--bg-card);
      padding: 14px 18px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
    }
    .quote-bar {
      width: 4px;
      border-radius: 4px;
      background: var(--accent-gradient);
      flex-shrink: 0;
    }
    .quote-body {
      color: var(--text-muted);
      font-style: italic;
      line-height: 1.6;
    }

    /* File References */
    .file-ref {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      padding: 2px 8px;
      border-radius: 6px;
      cursor: pointer;
      color: var(--sap-cyan);
      transition: all 0.15s;
    }
    .file-ref:hover {
      border-color: var(--sap-cyan);
      background: rgba(0, 210, 255, 0.1);
    }
    .file-ref code {
      font-family: var(--font-mono);
      font-size: 0.85em;
    }
    .ref-icon { color: var(--sap-cyan); }

    /* Toast Notification */
    #toast {
      position: fixed;
      bottom: 28px;
      right: 28px;
      background: #111827;
      color: #ffffff;
      border: 1px solid var(--sap-blue);
      box-shadow: 0 10px 30px rgba(0,0,0,0.5), var(--glow-blue);
      padding: 12px 20px;
      border-radius: var(--radius-sm);
      font-size: 0.85rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
      opacity: 0;
      transform: translateY(20px);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: none;
      z-index: 2000;
    }
    #toast.show {
      opacity: 1;
      transform: translateY(0);
    }

    /* Floating Back to Top Button */
    #back-to-top {
      position: fixed;
      bottom: 28px;
      left: 28px;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: var(--bg-surface);
      border: 1px solid var(--border);
      color: var(--text-main);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 6px 18px rgba(0,0,0,0.3);
      opacity: 0;
      pointer-events: none;
      transition: all 0.25s;
      z-index: 90;
    }
    #back-to-top.visible {
      opacity: 1;
      pointer-events: auto;
    }
    #back-to-top:hover {
      background: var(--sap-blue);
      color: #ffffff;
      transform: translateY(-3px);
    }

    /* Diagrams Modal */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      z-index: 3000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-backdrop.open {
      display: flex;
    }
    .modal-box {
      background: var(--bg-surface);
      border: 1px solid var(--border-bright);
      border-radius: var(--radius);
      width: 100%;
      max-width: 860px;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 60px rgba(0,0,0,0.6);
      overflow: hidden;
    }
    .modal-header {
      padding: 16px 22px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-card);
    }
    .modal-header h3 {
      font-family: var(--font-title);
      font-size: 1.15rem;
      color: var(--text-main);
    }
    .modal-close {
      background: transparent;
      border: 0;
      color: var(--text-muted);
      font-size: 1.5rem;
      cursor: pointer;
      line-height: 1;
    }
    .modal-close:hover { color: var(--sap-rose); }
    .modal-body {
      padding: 20px;
      overflow-y: auto;
    }
    .modal-hint {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 16px;
    }
    .modal-diag-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 12px;
    }
    .modal-diag-item {
      display: flex;
      align-items: center;
      gap: 12px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 12px 16px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .modal-diag-item:hover {
      background: var(--bg-card-hover);
      border-color: var(--sap-blue);
      transform: translateX(4px);
    }
    .modal-diag-num {
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--sap-purple);
      font-family: var(--font-mono);
      background: rgba(139, 92, 246, 0.12);
      padding: 3px 8px;
      border-radius: 4px;
      white-space: nowrap;
    }
    .modal-diag-title {
      font-size: 0.86rem;
      font-weight: 600;
      flex: 1;
      color: var(--text-main);
    }
    .modal-diag-jump {
      font-size: 0.82rem;
      color: var(--sap-blue);
      font-weight: 700;
    }

    /* Responsive */
    @media (max-width: 1080px) {
      aside.sidebar { display: none; }
      main.content-area { padding: 24px 20px; }
      .search-input { width: 180px; }
    }
  </style>
</head>
<body>
  <div id="progress-bar"></div>

  <header class="main-header">
    <a href="#top" class="brand-group">
      <div class="brand-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
      </div>
      <div class="brand-text">
        <h1>Enterprise AI Procurement</h1>
        <span>CAP + MCP + A2A ARCHITECTURE</span>
      </div>
    </a>

    <div class="header-actions">
      <div class="search-box-wrapper">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="search" id="quick-search" class="search-input" placeholder="Search architecture, code, APIs..." autocomplete="off"/>
        <span class="search-kbd">/</span>
      </div>

      <button class="btn-header" onclick="expandAllCode()">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
        <span>Diagrams</span>
      </button>

      <button class="btn-header btn-theme" id="theme-toggle" title="Toggle Light/Dark Theme">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
      </button>
    </div>
  </header>

  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="sidebar-title">Chapters &amp; Map</span>
        <span class="sidebar-progress" id="progress-lbl">0 / 18</span>
      </div>
      <ul class="nav-list" id="sidebar-nav">
        ${navSections.map(sec => `
          <li class="nav-item" id="nav-${sec.id}">
            <a href="#${sec.id}">
              <span class="nav-num">${sec.num}</span>
              <span class="nav-text">${escapeHtml(sec.title)}</span>
            </a>
          </li>
        `).join('')}
      </ul>
    </aside>

    <main class="content-area" id="top">
      ${html}
    </main>
  </div>

  <div id="toast">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
    <span id="toast-msg">Copied to clipboard!</span>
  </div>

  <button id="back-to-top" title="Scroll to Top" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"/></svg>
  </button>

  <script>
    // Initialize Mermaid with spacious configuration and clear typography
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      securityLevel: 'loose',
      fontFamily: 'Inter, system-ui, sans-serif',
      fontSize: 15,
      themeVariables: {
        fontSize: '15px',
        primaryColor: '#1e293b',
        primaryTextColor: '#f8fafc',
        primaryBorderColor: '#38bdf8',
        lineColor: '#60a5fa',
        secondaryColor: '#0f172a',
        tertiaryColor: '#1e1b4b'
      },
      flowchart: {
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis',
        padding: 24,
        nodeSpacing: 45,
        rankSpacing: 45
      },
      sequence: {
        useMaxWidth: false,
        actorMargin: 70,
        boxMargin: 14,
        boxTextMargin: 8,
        noteMargin: 12,
        messageMargin: 45,
        mirrorActors: false
      },
      er: {
        useMaxWidth: false,
        fontSize: 14
      },
      state: {
        useMaxWidth: false
      }
    });

    // Initialize Highlight.js
    hljs.highlightAll();

    // Populate Chapter Matrix in TOC Banner
    const tocMatrix = document.getElementById('toc-matrix');
    const sections = ${JSON.stringify(navSections)};
    if (tocMatrix) {
      tocMatrix.innerHTML = sections.map(s => \`
        <a href="#\${s.id}" class="matrix-card">
          <span class="matrix-num">\${s.num}</span>
          <span class="matrix-title">\${s.title}</span>
        </a>
      \`).join('');
    }

    // Diagram Zoom & Pan Engine
    const diagramScales = {};
    function zoomDiagram(id, delta) {
      diagramScales[id] = (diagramScales[id] || 1) + delta;
      if (diagramScales[id] < 0.35) diagramScales[id] = 0.35;
      if (diagramScales[id] > 2.8) diagramScales[id] = 2.8;
      const pan = document.getElementById(id + '-pan');
      if (pan) {
        pan.style.transform = 'scale(' + diagramScales[id].toFixed(2) + ')';
        showToast('Zoom: ' + Math.round(diagramScales[id] * 100) + '%');
      }
    }

    function resetDiagramZoom(id) {
      diagramScales[id] = 1;
      const pan = document.getElementById(id + '-pan');
      if (pan) {
        pan.style.transform = 'scale(1)';
        showToast('Zoom reset to 100%');
      }
    }

    function toggleDiagramFullscreen(id) {
      const card = document.getElementById(id + '-card');
      if (card) {
        card.classList.toggle('is-fullscreen');
        if (card.classList.contains('is-fullscreen')) {
          document.body.style.overflow = 'hidden';
          showToast('Fullscreen mode — Press ESC to exit');
        } else {
          document.body.style.overflow = '';
        }
      }
    }

    function copyDiagramCode(diagId) {
      const srcBlock = document.getElementById(diagId + '-src');
      if (srcBlock) {
        const code = srcBlock.querySelector('code')?.innerText || '';
        copyText(code);
      }
    }

    function toggleDiagramSource(diagId) {
      const src = document.getElementById(diagId + '-src');
      const view = document.getElementById(diagId + '-view');
      if (src.style.display === 'none') {
        src.style.display = 'block';
        view.style.display = 'none';
      } else {
        src.style.display = 'none';
        view.style.display = 'flex';
      }
    }

    // Diagrams Modal / Jump
    function expandAllCode() {
      openDiagramsModal();
    }

    function openDiagramsModal() {
      let modal = document.getElementById('diagrams-modal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'diagrams-modal';
        modal.className = 'modal-backdrop';
        const cards = document.querySelectorAll('.diagram-card');
        let linksHtml = '';
        cards.forEach((card, idx) => {
          const parentSec = card.closest('.guide-section');
          const secTitle = parentSec ? parentSec.querySelector('.section-heading')?.innerText || 'Architecture' : 'Diagram';
          const diagTag = card.querySelector('.diagram-tag span')?.innerText || ('Diagram ' + (idx + 1));
          linksHtml += '<div class="modal-diag-item" data-target-id="' + card.id + '">' +
            '<span class="modal-diag-num">Diagram ' + (idx + 1) + '</span>' +
            '<span class="modal-diag-title">' + diagTag + ' <small style="color:var(--text-faint);display:block;">' + secTitle + '</small></span>' +
            '<span class="modal-diag-jump">View &rarr;</span>' +
          '</div>';
        });

        modal.innerHTML = 
          '<div class="modal-box">' +
            '<div class="modal-header">' +
              '<h3>Architecture &amp; Flow Diagrams Index (' + cards.length + ' Diagrams)</h3>' +
              '<button class="modal-close" onclick="closeDiagramsModal()">&times;</button>' +
            '</div>' +
            '<div class="modal-body">' +
              '<p class="modal-hint">Click any diagram below to jump directly to its vector rendering with interactive zoom & fullscreen controls:</p>' +
              '<div class="modal-diag-grid">' +
                linksHtml +
              '</div>' +
            '</div>' +
          '</div>';
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
          const item = e.target.closest('.modal-diag-item');
          if (item) {
            const targetId = item.getAttribute('data-target-id');
            if (targetId) jumpToDiagram(targetId);
          }
          if (e.target === modal) closeDiagramsModal();
        });
      }
      modal.classList.add('open');
    }

    function closeDiagramsModal() {
      const modal = document.getElementById('diagrams-modal');
      if (modal) modal.classList.remove('open');
    }

    function jumpToDiagram(id) {
      closeDiagramsModal();
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.style.outline = '2px solid var(--sap-blue)';
        setTimeout(() => { el.style.outline = 'none'; }, 2000);
      }
    }

    // Reading Progress & Scrollspy
    const progressBar = document.getElementById('progress-bar');
    const backToTop = document.getElementById('back-to-top');
    const navItems = document.querySelectorAll('.nav-item');

    window.addEventListener('scroll', () => {
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = (window.scrollY / docHeight) * 100;
      progressBar.style.width = scrolled + '%';

      if (window.scrollY > 400) {
        backToTop.classList.add('visible');
      } else {
        backToTop.classList.remove('visible');
      }

      let currentActive = '';
      const sectionElements = document.querySelectorAll('.guide-section');
      sectionElements.forEach(sec => {
        const top = sec.offsetTop - 120;
        if (window.scrollY >= top) {
          currentActive = sec.id;
        }
      });

      if (currentActive) {
        navItems.forEach(item => {
          if (item.id === 'nav-' + currentActive) {
            item.classList.add('active');
          } else {
            item.classList.remove('active');
          }
        });
      }
    });

    // Dark / Light Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const target = current === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', target);
      localStorage.setItem('theme', target);
    });

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      document.documentElement.setAttribute('data-theme', savedTheme);
    }

    // Quick Search Filter
    const quickSearch = document.getElementById('quick-search');
    quickSearch.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const sections = document.querySelectorAll('.guide-section');
      sections.forEach(sec => {
        const text = sec.innerText.toLowerCase();
        if (!q || text.includes(q)) {
          sec.style.display = '';
        } else {
          sec.style.display = 'none';
        }
      });
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== quickSearch) {
        e.preventDefault();
        quickSearch.focus();
      }
      if (e.key === 'Escape') {
        const fsCard = document.querySelector('.diagram-card.is-fullscreen');
        if (fsCard) {
          fsCard.classList.remove('is-fullscreen');
          document.body.style.overflow = '';
        }
        closeDiagramsModal();
      }
    });

    // Copy Toast Helper
    function showToast(msg) {
      const toast = document.getElementById('toast');
      const toastMsg = document.getElementById('toast-msg');
      toastMsg.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => { toast.classList.remove('show'); }, 2200);
    }

    function copyText(text) {
      navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!');
      });
    }

    function copyCodeBlock(btn) {
      const code = btn.closest('.code-panel').querySelector('code').innerText;
      copyText(code);
    }

    // Chapter completion tracking
    function updateProgressLabel() {
      const completed = JSON.parse(localStorage.getItem('guide_completed_chapters') || '[]');
      const lbl = document.getElementById('progress-lbl');
      if (lbl) lbl.innerText = completed.length + ' / ' + sections.length;
      sections.forEach(s => {
        const navEl = document.getElementById('nav-' + s.id);
        const secEl = document.getElementById(s.id);
        if (completed.includes(s.id)) {
          if (navEl) navEl.classList.add('completed');
          if (secEl) {
            const btn = secEl.querySelector('.sec-check-btn');
            if (btn) btn.classList.add('checked');
          }
        } else {
          if (navEl) navEl.classList.remove('completed');
          if (secEl) {
            const btn = secEl.querySelector('.sec-check-btn');
            if (btn) btn.classList.remove('checked');
          }
        }
      });
    }

    function toggleChapterDone(secId) {
      let completed = JSON.parse(localStorage.getItem('guide_completed_chapters') || '[]');
      if (completed.includes(secId)) {
        completed = completed.filter(id => id !== secId);
      } else {
        completed.push(secId);
      }
      localStorage.setItem('guide_completed_chapters', JSON.stringify(completed));
      updateProgressLabel();
    }

    updateProgressLabel();
  </script>
</body>
</html>`;

fs.writeFileSync(outputHtmlPath1, fullHtml, 'utf8');
console.log('Written to:', outputHtmlPath1);

fs.writeFileSync(outputHtmlPath2, fullHtml, 'utf8');
console.log('Written to:', outputHtmlPath2);
