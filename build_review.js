const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType, ExternalHyperlink,
  PageNumber, Footer } = require("docx");

const ACCENT = "1F4E79";
const HEAD_FILL = "1F4E79";
const SUB_FILL = "D6E4F0";
const EXTRAP_FILL = "FCEFD9";

const border = { style: BorderStyle.SINGLE, size: 1, color: "BFBFBF" };
const borders = { top: border, bottom: border, left: border, right: border };
const COLS = [1900, 2550, 2150, 2760]; // sums 9360
const TW = 9360;

function P(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after ?? 120, before: opts.before ?? 0, line: 276 },
    alignment: opts.align,
    children: Array.isArray(text) ? text : [new TextRun({ text, bold: opts.bold, italics: opts.italics, size: opts.size, color: opts.color })],
    ...(opts.heading ? { heading: opts.heading } : {}),
    ...(opts.bullet ? { numbering: { reference: "bul", level: 0 } } : {}),
  });
}
function cellPara(runs) { return new Paragraph({ spacing: { after: 0, line: 248 }, children: runs }); }
function R(t, o = {}) { return new TextRun({ text: t, bold: o.bold, italics: o.italics, size: o.size ?? 18, color: o.color }); }

function headerRow(labels) {
  return new TableRow({ tableHeader: true, children: labels.map((l, i) => new TableCell({
    borders, width: { size: COLS[i], type: WidthType.DXA }, shading: { fill: HEAD_FILL, type: ShadingType.CLEAR },
    margins: { top: 70, bottom: 70, left: 110, right: 110 }, children: [cellPara([R(l, { bold: true, color: "FFFFFF", size: 18 })])] })) });
}
function sectionRow(label) {
  return new TableRow({ children: [new TableCell({ borders, columnSpan: 4, width: { size: TW, type: WidthType.DXA },
    shading: { fill: SUB_FILL, type: ShadingType.CLEAR }, margins: { top: 60, bottom: 60, left: 110, right: 110 },
    children: [cellPara([R(label, { bold: true, color: ACCENT, size: 18 })])] })] });
}
function dataRow(cells, opts = {}) {
  const fill = opts.extrap ? EXTRAP_FILL : "FFFFFF";
  return new TableRow({ children: cells.map((c, i) => new TableCell({ borders, width: { size: COLS[i], type: WidthType.DXA },
    shading: { fill, type: ShadingType.CLEAR }, margins: { top: 60, bottom: 60, left: 110, right: 110 },
    children: [cellPara(Array.isArray(c) ? c : [R(c)])] })) });
}

const rows = [];
rows.push(headerRow(["Data point", "Value / finding", "Epoch source (year)", "Methodology / notes"]));
rows.push(sectionRow("A.  Compute coming online"));
rows.push(dataRow(["Growth rate of global AI compute",
  [R("≈"), R("3.3× per year", { bold: true }), R(" since 2022 (90% CI 2.7–4.1×); doubling every ~7 months.")],
  "“Global AI computing capacity is doubling every 7 months” (Jan 2026)",
  "Log-linear regression on quarterly H100-equivalent chip sales (AI Chip Sales datahub; financial filings + analyst reports)."]));
rows.push(dataRow(["Current installed stock",
  [R(">15 million H100-equivalents", { bold: true }), R(" cumulative (~16.5M on 8-bit peak basis) as of Q4 2025; drawing >10 GW.")],
  "AI Chip Sales datahub (Jan 8 2026)",
  "Chip-by-chip sales estimated from revenue & disclosures across Nvidia, Google, Amazon, AMD, Huawei."]));
rows.push(dataRow(["Ownership concentration",
  [R("5 hyperscalers hold ~71%", { bold: true }), R(" of global compute (Q4 2025); Google largest, driven by TPUs.")],
  "“Five hyperscalers now own over two-thirds of global AI compute” (2025–26)",
  "Per-owner allocation of estimated chip stock (H100-equivalents)."]));
rows.push(dataRow(["Frontier scaling head-room to 2030",
  [R("Training runs up to ~2×10²⁹ FLOP feasible; individual frontier runs ~4–16 GW; global AI power ~"), R("100 GW (~50 GW US) by 2030", { bold: true }), R("; inference compute overtakes training by 2030.")],
  "“Can AI scaling continue through 2030?” (2024–25)",
  "Constraint analysis across power, chip supply, data and latency."]));
rows.push(dataRow(["Projected 2031 stock (extrapolation)",
  [R("Applying 3–3.3×/yr to the ~15M Q4-2025 base ⇒ "), R("≈3.6–5.9 billion H100-equivalents", { bold: true }), R(" by 2030–31 (brief uses ~4.8B).")],
  "Brief extrapolation from Epoch growth rate — not an Epoch-published figure",
  "Compound growth on Epoch base. Epoch cautions actual growth likely slows (lead times, power)."], { extrap: true }));
rows.push(sectionRow("B.  What that corresponds to in AI models"));
rows.push(dataRow(["OpenAI compute stock",
  [R("~1.1M H100-e total; "), R("~480k H100-e for inference", { bold: true }), R(" (~44% of stock).")],
  "“How many digital workers could OpenAI deploy?” (Oct 2025)",
  "Estimated from The Information reporting on OpenAI compute spend."]));
rows.push(dataRow(["Concurrent frontier-model copies (extrapolation)",
  [R("Today ~0.83M copies (20M H100-e ÷ 24/copy of a 1.6T model); "), R("2031 ~24M copies", { bold: true }), R(" if a frontier copy needs ~200 H100-e (8×).")],
  "Brief back-of-envelope on Epoch stock + growth — not Epoch",
  "Stock ÷ per-copy GPU requirement; assumes model size growth."], { extrap: true }));
rows.push(sectionRow("C.  What that corresponds to in tokens"));
rows.push(dataRow(["Current inference supply",
  [R("World’s GB200+GB300 chips (~40% of supply) could serve "), R("500M–20B output tokens/sec", { bold: true }), R(" from a Kimi K2.6-class model (Q4 2025).")],
  "“Is a compute crunch coming?” (May 2026)",
  "Prefill/decode runtime model with chunked prefill + speculative decoding, calibrated to SemiAnalysis InferenceX."]));
rows.push(dataRow(["Inference capacity growth",
  [R(">3× per year", { bold: true }), R(" (more compute + efficiency gains).")],
  "“Is a compute crunch coming?” (May 2026)", "Same inference-supply model applied over time."]));
rows.push(dataRow(["Token demand",
  [R("200M–4B tokens/sec, "), R("growing ~10×/yr", { bold: true }), R(" — demand likely outpacing supply.")],
  "“Is a compute crunch coming?” (May 2026)",
  "Proxies: Google token volumes; usage at large firms extrapolated to all SWEs."]));
rows.push(dataRow(["Today’s token volumes",
  [R("OpenAI ~19 trillion tokens/day; "), R("Google ~35 trillion/day", { bold: true }), R(" (980T/month, Jul 2025).")],
  "“How many digital workers could OpenAI deploy?” (Oct 2025)",
  "Inference-budget approach + reported message/usage counts."]));
rows.push(dataRow(["Projected 2031 throughput (extrapolation)",
  [R("~1 trillion tokens/sec", { bold: true }), R(" under heavy workloads (~100B/s at 10% utilisation ⇒ ~6 trillion tokens/min).")],
  "Brief extrapolation (tripling current supply ~5 yrs) — not Epoch",
  "Consistent with 500M–20B/s tripling for ~5 years (→0.1–5T/s)."], { extrap: true }));
rows.push(sectionRow("D.  AI labour vs human labour supply"));
rows.push(dataRow(["Digital workers today",
  [R("~7 million", { bold: true }), R(" human-equivalent digital workers OpenAI could deploy (90% CI 0.4M–300M), on tasks AI can already do.")],
  "“How many digital workers could OpenAI deploy?” (Oct 2025)",
  "Tokens/day ÷ human token-throughput; cross-checked with METR task-time approach."]));
rows.push(dataRow(["Human token-processing benchmark",
  [R("~240k tokens/worker/day", { bold: true }), R(" (≈380 words/min thinking, 8h day).")],
  "“How many digital workers could OpenAI deploy?” (Oct 2025)",
  "Anchored to human thinking speed; brief uses ~1,000 tokens/min instead."]));
rows.push(dataRow(["Cost differential per task",
  [R("Hour-long SWE task: "), R("$1–10 for GPT-5 vs $50–100 for a human.", { bold: true })],
  "“How many digital workers could OpenAI deploy?” (Oct 2025)",
  "METR task token counts × API token prices vs human wage."]));
rows.push(dataRow(["2031 AI-vs-human cognitive output (extrapolation)",
  [R("1.5B white-collar workers × ~1,000 tokens/min ≈ 1.5T human-token-equivalents/min; projected ~6T LLM tokens/min ⇒ "), R("AI ~4× human output.", { bold: true })],
  "Brief calculation — not Epoch",
  "Combines brief’s 2031 token throughput with a human-token baseline."], { extrap: true }));

const table = new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: COLS, rows });

function link(text, url) { return new ExternalHyperlink({ children: [new TextRun({ text, style: "Hyperlink", size: 20 })], link: url }); }

const children = [];
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 80 }, children: [new TextRun("AI Labour Supply Is Increasing Exponentially")] }));
children.push(P("Systematic review of the evidence on compute coming online (Epoch AI)", { italics: true, color: "595959", size: 22, after: 60 }));
children.push(new Paragraph({ spacing: { after: 240 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 2 } }, children: [new TextRun({ text: "Evidence base: Epoch AI publications, data insights and datahubs, accessed June 2026.", size: 18, color: "808080" })] }));
children.push(P("Headline answer", { heading: HeadingLevel.HEADING_2 }));
children.push(P([R("Epoch AI does "), R("not", { bold: true }), R(" publish a single “compute online in 2031” number. What it publishes is a measured growth rate and a current stock, plus a 2030 power-capacity projection:")]));
children.push(P([R("Current global stock: "), R(">15 million H100-equivalents", { bold: true }), R(" (Q4 2025), growing "), R("≈3.3× per year", { bold: true }), R(" (doubling every ~7 months).")], { bullet: true }));
children.push(P([R("By 2030 Epoch projects "), R("~100 GW", { bold: true }), R(" of global AI power capacity (~50 GW in the US), and expects inference compute to overtake training compute.")], { bullet: true }));
children.push(P([R("Extrapolating the 3–3.3×/yr rate to 2031 gives "), R("≈3.6–5.9 billion H100-equivalents", { bold: true }), R(" (the brief’s ~4.8B sits inside this). This is a downstream extrapolation, not an Epoch figure — and Epoch itself cautions that growth will likely slow as power and lead-time constraints bind.")], { bullet: true, after: 200 }));
children.push(P("Scope and method", { heading: HeadingLevel.HEADING_2 }));
children.push(P("This note reviews Epoch AI’s evidence relevant to four claims in the section: (A) lots of compute is coming online; (B) what that corresponds to in AI models; (C) what that corresponds to in tokens; and (D) how AI labour supply compares to human labour. Each quantitative claim is traced to its Epoch source and methodology in the table below. To keep the evidence honest, the table separates figures Epoch has actually measured or projected from extrapolations made in the brief (shaded rows); the latter are derived by compounding Epoch’s growth rates and should be presented as the brief’s own estimates, not as Epoch’s.", { after: 200 }));
children.push(P("Evidence table", { heading: HeadingLevel.HEADING_2 }));
children.push(table);
children.push(P([R("Shaded rows = extrapolations made in the brief, not published by Epoch.", { italics: true, color: "808080", size: 18 })], { before: 100, after: 220 }));
children.push(P("Synthesis", { heading: HeadingLevel.HEADING_2 }));
children.push(P("Lots of compute is coming online.", { bold: true, after: 60 }));
children.push(P("Epoch’s most robust finding is the trend: global AI computing capacity has grown ~3.3× per year since 2022 (90% CI 2.7–4.1×), a doubling roughly every seven months, estimated by fitting a log-linear trend to quarterly H100-equivalent chip sales. The installed base passed 15 million H100-equivalents in Q4 2025, concentrated in five hyperscalers (~71%). Epoch’s scaling analysis finds the physical head-room (power, chips, data) to continue to ~100 GW of global AI power and ~2×10²⁹ FLOP training runs by 2030, while noting growth in chip stock is more likely to decelerate than accelerate.", { after: 160 }));
children.push(P("What that corresponds to in AI models.", { bold: true, after: 60 }));
children.push(P("Epoch estimates OpenAI alone runs inference on ~480k H100-equivalents (of ~1.1M total). At the back-of-envelope level used in the brief, today’s ~20M-chip stock could host on the order of ~0.83M concurrent copies of a frontier open model, rising to tens of millions of copies by 2031 under the compounded-growth assumption. These copy counts are the brief’s, built on Epoch’s stock and growth figures.", { after: 160 }));
children.push(P("What that corresponds to in tokens.", { bold: true, after: 60 }));
children.push(P("Epoch’s inference-supply model (“Is a compute crunch coming?”, May 2026) finds the world’s GB200/GB300 chips could already serve 500M–20B output tokens/sec from a frontier-class open model, with capacity tripling each year, against demand of 200M–4B tokens/sec growing ~10×/yr. For scale, OpenAI generates ~19 trillion tokens/day and Google ~35 trillion/day today. Tripling current supply for ~5 years lands around the brief’s ~1 trillion tokens/sec “heavy workload” figure (≈6 trillion tokens/min at 10% utilisation) — again, a brief extrapolation rather than an Epoch projection.", { after: 160 }));
children.push(P("AI labour vs human labour supply.", { bold: true, after: 60 }));
children.push(P("Epoch translates compute into labour directly: on tasks AI can already do, OpenAI has the inference compute to field ~7 million human-equivalent digital workers (90% CI 0.4M–300M), benchmarking against ~240k tokens a human worker “processes” per day, and noting AI performs hour-long software tasks for $1–10 versus $50–100 for a human. The brief’s 2031 comparison — ~6 trillion LLM tokens/min against ~1.5 trillion “human-token-equivalents”/min from 1.5B white-collar workers, i.e. AI output ~4× human — follows the same logic and lands the section’s core claim: within ~5 years, compute capacity alone is on track to rival human cognitive labour in the economy.", { after: 200 }));
children.push(P("Caveats", { heading: HeadingLevel.HEADING_2 }));
children.push(P("Epoch publishes growth rates and current stocks, not a 2031 capacity figure; multi-year extrapolations are the brief’s and carry wide uncertainty.", { bullet: true }));
children.push(P("Epoch’s own work flags that compute growth will likely slow (power, lead times) and that token demand may outpace supply — so a smooth 3×/yr line to 2031 is an upper-ish case.", { bullet: true }));
children.push(P("“Digital worker” and token-to-human conversions are explicitly speculative (90% CIs span 2–3 orders of magnitude) and measure capacity, not actual automation — today’s 7M figure applies only to tasks AI can already perform.", { bullet: true }));
children.push(P("The brief’s ~20M chip base is slightly above Epoch’s ~15–16.5M (Q4 2025); worth aligning for consistency.", { bullet: true, after: 200 }));
children.push(P("Sources", { heading: HeadingLevel.HEADING_2 }));
const src = [
  ["Global AI computing capacity is doubling every 7 months (Jan 2026)", "https://epoch.ai/data-insights/ai-chip-production"],
  ["AI Chip Sales datahub / “Global AI compute hits 15M H100-e” (Jan 2026)", "https://epoch.ai/data/ai-chip-sales"],
  ["Five hyperscalers now own over two-thirds of global AI compute", "https://epoch.ai/data-insights/hyperscalers-control-most-compute"],
  ["Can AI scaling continue through 2030?", "https://epoch.ai/blog/can-ai-scaling-continue-through-2030"],
  ["Is a compute crunch coming? (May 2026)", "https://epoch.ai/gradient-updates/is-a-compute-crunch-coming"],
  ["How many digital workers could OpenAI deploy? (Oct 2025)", "https://epoch.ai/gradient-updates/how-many-digital-workers-could-openai-deploy"],
];
src.forEach(([t, u]) => children.push(new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bul", level: 0 }, children: [link(t, u)] })));

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, font: "Arial", color: ACCENT }, paragraph: { spacing: { before: 120, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: ACCENT }, paragraph: { spacing: { before: 220, after: 120 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [ { reference: "bul", levels: [ { level: 0, format: "bullet", text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } } } } ] } ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1300, right: 1440, bottom: 1300, left: 1440 } } },
    footers: { default: new Footer({ children: [ new Paragraph({ alignment: AlignmentType.CENTER, children: [ new TextRun({ text: "Epoch AI compute evidence — systematic review  ·  page ", size: 16, color: "909090" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "909090" }) ] }) ] }) },
    children,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log("written", b.length); });
