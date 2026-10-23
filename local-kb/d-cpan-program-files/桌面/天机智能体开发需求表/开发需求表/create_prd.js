const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak, TabStopType, TabStopPosition,
  PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader
} = require("docx");

// ─── Color palette ───
const C = {
  primary: "1A56DB",    // 深蓝
  accent: "7C3AED",     // 紫色
  dark: "1F2937",       // 深灰
  mid: "6B7280",        // 中灰
  light: "F3F4F6",      // 浅灰背景
  white: "FFFFFF",
  headerBg: "EEF2FF",   // 浅紫背景
  tableBorder: "D1D5DB",
  success: "059669",
  warning: "D97706",
};

const border = { style: BorderStyle.SINGLE, size: 1, color: C.tableBorder };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

// ─── Helper functions ───
function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, size: 36, font: "Arial", color: C.primary })],
    spacing: { before: 480, after: 240 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: C.primary, space: 8 } },
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, size: 30, font: "Arial", color: C.dark })],
    spacing: { before: 360, after: 180 },
  });
}

function heading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial", color: C.accent })],
    spacing: { before: 240, after: 120 },
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, size: 22, font: "Arial", color: C.dark, ...opts })],
    spacing: { after: 120, line: 360 },
  });
}

function boldPara(label, text) {
  return new Paragraph({
    children: [
      new TextRun({ text: label, bold: true, size: 22, font: "Arial", color: C.dark }),
      new TextRun({ text, size: 22, font: "Arial", color: C.mid }),
    ],
    spacing: { after: 100, line: 360 },
  });
}

function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: C.primary, type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, size: 20, font: "Arial", color: C.white })],
    })],
  });
}

function dataCell(text, width, opts = {}) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({ text, size: 20, font: "Arial", color: C.dark, bold: !!opts.bold })],
    })],
  });
}

function simpleTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({ children: headers.map((h, i) => headerCell(h, colWidths[i])) }),
      ...rows.map((row, ri) => new TableRow({
        children: row.map((cell, ci) => dataCell(cell, colWidths[ci], {
          shading: ri % 2 === 1 ? C.light : undefined,
          bold: ci === 0,
        })),
      })),
    ],
  });
}

function spacer() {
  return new Paragraph({ spacing: { after: 60 }, children: [] });
}

// ─── Build Document ───
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: C.primary },
        paragraph: { spacing: { before: 480, after: 240 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, font: "Arial", color: C.dark },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: C.accent },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "bullets2",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u25CB", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
        }],
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  sections: [
    // ═══════════ COVER PAGE ═══════════
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      children: [
        new Paragraph({ spacing: { before: 3600 }, children: [] }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          children: [new TextRun({ text: "\u5929\u673A\u667A\u80FD\u4F53", size: 64, bold: true, font: "Arial", color: C.primary })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          children: [new TextRun({ text: "TianJi AI Agent", size: 36, font: "Arial", color: C.accent })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 600 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.primary, space: 20 } },
          children: [new TextRun({ text: "\u8DE8\u5883\u7535\u5546 AI \u667A\u80FD\u4F53\u5E73\u53F0", size: 28, font: "Arial", color: C.mid })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          children: [new TextRun({ text: "\u4EA7\u54C1\u9700\u6C42\u6587\u6863 (PRD)", size: 32, bold: true, font: "Arial", color: C.dark })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 60 },
          children: [new TextRun({ text: "Product Requirements Document", size: 24, font: "Arial", color: C.mid })],
        }),
        new Paragraph({ spacing: { before: 1200 }, children: [] }),
        // Doc info table
        new Table({
          width: { size: 5400, type: WidthType.DXA },
          columnWidths: [2200, 3200],
          alignment: AlignmentType.CENTER,
          rows: [
            ["文档版本", "V1.0"],
            ["创建日期", "2026年5月24日"],
            ["文档状态", "初稿"],
            ["保密级别", "内部机密"],
            ["对标产品", "StoreClaw.ai"],
          ].map(([k, v]) => new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 2200, type: WidthType.DXA },
                shading: { fill: C.headerBg, type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: k, bold: true, size: 20, font: "Arial", color: C.primary })] })],
              }),
              new TableCell({
                borders, width: { size: 3200, type: WidthType.DXA }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: v, size: 20, font: "Arial", color: C.dark })] })],
              }),
            ],
          })),
        }),
        new PageBreak(),
      ],
    },
    // ═══════════ TOC + MAIN CONTENT ═══════════
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: C.tableBorder, space: 4 } },
            children: [
              new TextRun({ text: "\u5929\u673A\u667A\u80FD\u4F53 \u00B7 PRD V1.0", size: 16, font: "Arial", color: C.mid }),
              new PositionalTab({ alignment: PositionalTabAlignment.RIGHT, relativeTo: PositionalTabRelativeTo.MARGIN, leader: PositionalTabLeader.NONE }),
              new TextRun({ text: "\u5185\u90E8\u673A\u5BC6", size: 16, font: "Arial", color: C.mid }),
            ],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "\u7B2C ", size: 16, font: "Arial", color: C.mid }),
              new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Arial", color: C.mid }),
              new TextRun({ text: " \u9875", size: 16, font: "Arial", color: C.mid }),
            ],
          })],
        }),
      },
      children: [
        // ── TOC ──
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun({ text: "\u76EE\u5F55", bold: true, size: 36, font: "Arial", color: C.primary })],
          spacing: { after: 300 },
        }),
        new TableOfContents("Table of Contents", {
          hyperlink: true,
          headingStyleRange: "1-3",
        }),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════ 1. 产品概述 ═══════════
        heading1("1. \u4EA7\u54C1\u6982\u8FF0"),

        heading2("1.1 \u4EA7\u54C1\u80CC\u666F"),
        para("\u8DE8\u5883\u7535\u5546\u884C\u4E1A\u6B63\u5904\u4E8E\u9AD8\u901F\u53D1\u5C55\u671F\uFF0C\u5356\u5BB6\u9762\u4E34\u591A\u5E73\u53F0\u8FD0\u8425\u3001\u591A\u8BED\u8A00\u5185\u5BB9\u3001\u5E7F\u544A\u6295\u653E\u3001\u5E93\u5B58\u7BA1\u7406\u3001\u7ADE\u54C1\u5206\u6790\u7B49\u590D\u6742\u4EFB\u52A1\u3002\u4F20\u7EDF\u5DE5\u5177\u5404\u81EA\u4E3A\u6218\uFF0C\u6570\u636E\u5B64\u5C9B\u4E25\u91CD\uFF0C\u5356\u5BB6\u9700\u8981\u5728\u591A\u4E2A\u5E73\u53F0\u95F4\u9891\u7E41\u5207\u6362\uFF0C\u6548\u7387\u4F4E\u4E0B\u3002AI \u6280\u672F\u7684\u6210\u719F\u4E3A\u8DE8\u5883\u7535\u5546\u5356\u5BB6\u63D0\u4F9B\u4E86\u5168\u65B0\u7684\u89E3\u51B3\u65B9\u6848\uFF0C\u901A\u8FC7\u667A\u80FD\u4F53\u5E73\u53F0\u5C06\u5404\u9879\u8FD0\u8425\u4EFB\u52A1\u81EA\u52A8\u5316\u3001\u667A\u80FD\u5316\u3002"),
        para("\u5929\u673A\u667A\u80FD\u4F53\u5B9A\u4F4D\u4E3A\u8DE8\u5883\u7535\u5546\u9886\u57DF\u7684 AI Agent \u5E73\u53F0\uFF0C\u5BF9\u6807 StoreClaw.ai\uFF0C\u5E76\u5728\u5176\u57FA\u7840\u4E0A\u8FDB\u884C\u5DEE\u5F02\u5316\u521B\u65B0\uFF0C\u63D0\u4F9B\u77E5\u8BC6\u5E93\u3001\u6280\u80FD\u5171\u4EAB\u79EF\u5206\u4F53\u7CFB\u3001\u81EA\u5B9A\u4E49\u6570\u636E\u5E93\u5BF9\u63A5\u3001\u591A\u6A21\u578B API \u96C6\u6210\u7B49\u589E\u5F3A\u529F\u80FD\u3002"),

        heading2("1.2 \u4EA7\u54C1\u5B9A\u4F4D"),
        boldPara("\u4EA7\u54C1\u540D\u79F0\uFF1A", "\u5929\u673A\u667A\u80FD\u4F53 (TianJi AI Agent)"),
        boldPara("\u4EA7\u54C1\u7C7B\u578B\uFF1A", "SaaS \u5E73\u53F0 (Web + \u79FB\u52A8\u7AEF)"),
        boldPara("\u6838\u5FC3\u5B9A\u4F4D\uFF1A", "\u8DE8\u5883\u7535\u5546\u5168\u94FE\u8DEF AI \u667A\u80FD\u4F53\u5E73\u53F0"),
        boldPara("\u76EE\u6807\u7528\u6237\uFF1A", "\u8DE8\u5883\u7535\u5546\u5356\u5BB6\u3001\u54C1\u724C\u65B9\u3001\u670D\u52A1\u5546\u3001\u8FD0\u8425\u56E2\u961F"),
        boldPara("Slogan\uFF1A", "\u201C\u5929\u673A\u6D1E\u5BDF\uFF0C\u667A\u80FD\u51B3\u7B56\u2014\u2014\u60A8\u768424\u5C0F\u65F6\u8DE8\u5883\u7535\u5546\u667A\u80FD\u5408\u4F19\u4EBA\u201D"),

        heading2("1.3 \u5BF9\u6807\u5206\u6790\u4E0E\u5DEE\u5F02\u5316"),
        simpleTable(
          ["\u529F\u80FD\u7EF4\u5EA6", "StoreClaw", "\u5929\u673A\u667A\u80FD\u4F53 (\u672C\u4EA7\u54C1)"],
          [
            ["\u667A\u80FD\u5BF9\u8BDD", "\u2705 LLM Chat", "\u2705 \u591A\u6A21\u578B\u5207\u6362 + \u4E0A\u4E0B\u6587\u8BB0\u5FC6"],
            ["\u6280\u80FD\u5E02\u573A", "\u2705 \u5B98\u65B9 Skill Hub", "\u2705 \u5171\u4EAB\u5E02\u573A + \u79EF\u5206\u6536\u76CA\u4F53\u7CFB"],
            ["\u8FDE\u63A5\u5668", "\u2705 20+ \u5E73\u53F0", "\u2705 30+ \u5E73\u53F0 + \u81EA\u5B9A\u4E49 MCP/API"],
            ["\u5B9A\u65F6\u4EFB\u52A1", "\u2705 \u6A21\u677F\u5E93", "\u2705 \u53EF\u89C6\u5316\u7F16\u6392 + \u6A21\u677F\u5E02\u573A"],
            ["\u77E5\u8BC6\u5E93", "\u2716 \u65E0", "\u2705 \u5411\u91CF\u68C0\u7D22 + RAG"],
            ["\u81EA\u5B9A\u4E49\u6570\u636E\u5E93", "\u2716 \u65E0", "\u2705 MySQL/PostgreSQL/MongoDB"],
            ["\u591A\u6A21\u578B\u652F\u6301", "\u2716 \u5355\u6A21\u578B", "\u2705 GPT/Claude/\u6587\u5FC3/\u901A\u4E49\u5343\u95EE/DeepSeek"],
            ["\u79EF\u5206\u4F53\u7CFB", "\u2716 \u65E0", "\u2705 \u5206\u4EAB\u6280\u80FD\u83B7\u5F97\u79EF\u5206\u6536\u76CA"],
            ["\u8D44\u4EA7\u5E93", "\u2705 \u57FA\u7840\u7248", "\u2705 \u589E\u5F3A\u7248\u652F\u6301\u591A\u683C\u5F0F"],
            ["\u6E20\u9053\u7BA1\u7406", "\u2705 \u591A\u6E20\u9053", "\u2705 \u591A\u6E20\u9053 + \u667A\u80FD\u5206\u53D1"],
          ],
          [2400, 3480, 3480],
        ),
        spacer(),

        // ═══════════ 2. 核心功能模块 ═══════════
        new Paragraph({ children: [new PageBreak()] }),
        heading1("2. \u6838\u5FC3\u529F\u80FD\u6A21\u5757"),

        // ── 2.1 智能对话 ──
        heading2("2.1 \u667A\u80FD\u5BF9\u8BDD\u4E2D\u5FC3 (Chat)"),
        para("\u5BF9\u6807 StoreClaw /app/chat\uFF0C\u4F5C\u4E3A\u5E73\u53F0\u7684\u6838\u5FC3\u4EA4\u4E92\u5165\u53E3\uFF0C\u7528\u6237\u901A\u8FC7\u81EA\u7136\u8BED\u8A00\u4E0E AI \u667A\u80FD\u4F53\u8FDB\u884C\u4EA4\u4E92\uFF0C\u6267\u884C\u5404\u7C7B\u8DE8\u5883\u7535\u5546\u4EFB\u52A1\u3002"),

        heading3("2.1.1 \u65B0\u5EFA\u4EFB\u52A1"),
        ...bulletList([
          "\u667A\u80FD\u5BF9\u8BDD\u7A97\u53E3\uFF1A\u652F\u6301\u6587\u672C\u3001\u8BED\u97F3\u3001\u56FE\u7247\u591A\u6A21\u6001\u8F93\u5165",
          "\u5B9A\u5236\u6A21\u578B\uFF1A\u7528\u6237\u53EF\u9009\u62E9\u4E0D\u540C AI \u5927\u6A21\u578B (GPT-4o/Claude/\u6587\u5FC3\u4E00\u8A00/\u901A\u4E49\u5343\u95EE/DeepSeek)",
          "\u4E0A\u4F20\u6587\u4EF6\uFF1A\u652F\u6301 PDF\u3001Excel\u3001CSV\u3001\u56FE\u7247\u3001Word \u7B49\u683C\u5F0F\uFF0CAI \u81EA\u52A8\u89E3\u6790\u5185\u5BB9",
          "\u6302\u8F7D\u6280\u80FD\uFF1A\u5BF9\u8BDD\u4E2D\u53EF\u6302\u8F7D\u4E00\u4E2A\u6216\u591A\u4E2A Skill\uFF0C\u8BA9 AI \u5177\u5907\u4E13\u4E1A\u80FD\u529B",
          "\u5173\u8054\u9879\u76EE\uFF1A\u4EFB\u52A1\u53EF\u5F52\u5C5E\u5230\u7279\u5B9A\u9879\u76EE\uFF0C\u4FBF\u4E8E\u56E2\u961F\u534F\u4F5C",
          "\u4E0A\u4E0B\u6587\u8BB0\u5FC6\uFF1A\u652F\u6301\u957F\u671F\u8BB0\u5FC6\u548C\u4F1A\u8BDD\u5386\u53F2",
        ]),

        heading3("2.1.2 \u5BF9\u8BDD\u589E\u5F3A\u529F\u80FD"),
        ...bulletList([
          "\u6D41\u5F0F\u8F93\u51FA\uFF1A\u5B9E\u65F6\u6D41\u5F0F\u663E\u793A AI \u56DE\u590D",
          "\u4EE3\u7801\u9AD8\u4EAE\uFF1A\u652F\u6301\u591A\u8BED\u8A00\u4EE3\u7801\u9AD8\u4EAE\u4E0E\u4E00\u952E\u590D\u5236",
          "\u56FE\u8868\u6E32\u67D3\uFF1A\u652F\u6301\u5728\u5BF9\u8BDD\u4E2D\u76F4\u63A5\u751F\u6210\u56FE\u8868\u53EF\u89C6\u5316",
          "Markdown \u6E32\u67D3\uFF1A\u652F\u6301\u5BCC\u6587\u672C\u683C\u5F0F\u5316\u8F93\u51FA",
          "\u5BFC\u51FA\u529F\u80FD\uFF1A\u5BF9\u8BDD\u7ED3\u679C\u53EF\u5BFC\u51FA\u4E3A PDF/Word/Markdown",
        ]),

        // ── 2.2 定时任务 ──
        heading2("2.2 \u5B9A\u65F6\u4EFB\u52A1 (Schedule)"),
        para("\u5BF9\u6807 StoreClaw \u7684 Schedule \u6A21\u5757\uFF0C\u652F\u6301\u7528\u6237\u521B\u5EFA\u81EA\u52A8\u5316\u5B9A\u65F6\u4EFB\u52A1\uFF0C\u5B9E\u73B0 24/7 \u65E0\u4EBA\u503C\u5B88\u8FD0\u8425\u3002"),

        heading3("2.2.1 \u521B\u5EFA\u5B9A\u65F6\u4EFB\u52A1"),
        ...bulletList([
          "\u53EF\u89C6\u5316\u4EFB\u52A1\u7F16\u6392\u5668\uFF1A\u62D6\u62FD\u5F0F\u914D\u7F6E\u4EFB\u52A1\u6D41\u7A0B",
          "\u89E6\u53D1\u6761\u4EF6\uFF1ACron \u8868\u8FBE\u5F0F / \u56FA\u5B9A\u65F6\u95F4 / \u4E8B\u4EF6\u89E6\u53D1 / \u6570\u636E\u53D8\u5316\u89E6\u53D1",
          "\u4EFB\u52A1\u94FE\uFF1A\u591A\u4EFB\u52A1\u4E32\u8054\u6267\u884C\uFF0C\u524D\u4E00\u4E2A\u4EFB\u52A1\u7684\u8F93\u51FA\u4F5C\u4E3A\u4E0B\u4E00\u4E2A\u7684\u8F93\u5165",
          "\u6267\u884C\u65E5\u5FD7\uFF1A\u8BE6\u7EC6\u8BB0\u5F55\u6BCF\u6B21\u6267\u884C\u7684\u72B6\u6001\u3001\u8017\u65F6\u3001\u7ED3\u679C",
          "\u5F02\u5E38\u544A\u8B66\uFF1A\u4EFB\u52A1\u5931\u8D25\u81EA\u52A8\u901A\u77E5\uFF08\u90AE\u4EF6/\u5FAE\u4FE1/\u9489\u9489\uFF09",
        ]),

        heading3("2.2.2 \u6A21\u677F\u5E93"),
        ...bulletList([
          "\u5B98\u65B9\u6A21\u677F\uFF1A\u9884\u7F6E\u5E38\u7528\u5B9A\u65F6\u4EFB\u52A1\u6A21\u677F\uFF08\u6BCF\u65E5\u5E97\u94FA\u5065\u5EB7\u68C0\u67E5\u3001\u6BCF\u5468\u7ADE\u54C1\u76D1\u63A7\u3001\u6BCF\u6708\u62A5\u544A\u7B49\uFF09",
          "\u793E\u533A\u6A21\u677F\uFF1A\u7528\u6237\u53EF\u5206\u4EAB\u81EA\u5EFA\u6A21\u677F\u5230\u793E\u533A",
          "\u4E00\u952E\u5B89\u88C5\uFF1A\u6A21\u677F\u652F\u6301\u4E00\u952E\u5B89\u88C5\u5E76\u81EA\u5B9A\u4E49\u53C2\u6570",
        ]),

        // ── 2.3 技能中心 ──
        heading2("2.3 \u6280\u80FD\u4E2D\u5FC3 (Skills)"),
        para("\u5BF9\u6807 StoreClaw /app/skills\uFF0C\u8FD9\u662F\u5929\u673A\u667A\u80FD\u4F53\u7684\u6838\u5FC3\u5DEE\u5F02\u5316\u7ADE\u4E89\u529B\u6A21\u5757\u3002"),

        heading3("2.3.1 \u5B98\u65B9 Skill \u5E93"),
        para("\u6309\u7C7B\u522B\u7EC4\u7EC7\u7684\u9884\u7F6E\u4E13\u4E1A\u6280\u80FD\uFF1A"),
        simpleTable(
          ["\u6280\u80FD\u5206\u7C7B", "\u5305\u542B\u6280\u80FD", "\u8BF4\u660E"],
          [
            ["\u9009\u54C1\u4E0E\u91C7\u8D2D", "AliExpress\u91C7\u8D2D\u5458\u30011688\u5BFC\u8D2D\u3001\u7206\u6B3E\u4EA7\u54C1\u53D1\u73B0\u3001\u4EA7\u54C1\u57FA\u51C6\u5206\u6790", "\u667A\u80FD\u9009\u54C1\u4E0E\u4F9B\u5E94\u94FE\u5206\u6790"],
            ["\u8425\u9500\u4E0E\u5185\u5BB9", "SEO/GEO\u987E\u95EE\u3001\u5E7F\u544A\u89C4\u5212\u5E08\u3001\u793E\u5A92\u5185\u5BB9\u4E13\u5BB6\u3001\u90AE\u4EF6\u8425\u9500", "\u5168\u6E20\u9053\u8425\u9500\u81EA\u52A8\u5316"],
            ["\u5E97\u94FA\u7BA1\u7406", "Shopify\u7BA1\u7406\u3001Amazon\u7BA1\u7406\u3001TikTok Shop\u7BA1\u7406", "\u591A\u5E73\u53F0\u5E97\u94FA\u7EDF\u4E00\u7BA1\u7406"],
            ["\u8FD0\u8425\u5206\u6790", "\u5E97\u94FA\u8BCA\u65AD\u3001\u5E93\u5B58\u9884\u8B66\u3001\u5BA2\u6237\u6D1E\u5BDF\u3001GA\u8FFD\u8E2A", "\u6570\u636E\u9A71\u52A8\u7684\u8FD0\u8425\u51B3\u7B56"],
            ["\u5E02\u573A\u60C5\u62A5", "\u5E02\u573A\u60C5\u62A5\u5458\u3001\u7ADE\u54C1\u96F7\u8FBE\u3001\u884C\u4E1A\u5206\u6790", "\u5B9E\u65F6\u5E02\u573A\u52A8\u6001\u76D1\u63A7"],
            ["\u8DE8\u5883\u4E13\u5C5E", "Listing\u4F18\u5316\u3001\u5173\u952E\u8BCD\u7814\u7A76\u3001\u4E94\u70B9\u63CF\u8FF0\u751F\u6210\u3001A+\u9875\u9762\u8BBE\u8BA1", "\u8DE8\u5883\u7535\u5546\u6DF1\u5EA6\u4F18\u5316"],
          ],
          [1800, 4560, 3000],
        ),
        spacer(),

        heading3("2.3.2 \u6211\u7684 Skill"),
        ...bulletList([
          "\u81EA\u5EFA Skill\uFF1A\u7528\u6237\u53EF\u901A\u8FC7\u53EF\u89C6\u5316\u7F16\u8F91\u5668\u6216\u4EE3\u7801\u65B9\u5F0F\u521B\u5EFA\u81EA\u5B9A\u4E49 Skill",
          "Skill \u7248\u672C\u7BA1\u7406\uFF1A\u652F\u6301\u591A\u7248\u672C\u3001\u56DE\u6EDA\u3001\u53D1\u5E03\u7BA1\u7406",
          "Skill \u6D4B\u8BD5\u6C99\u7BB1\uFF1A\u63D0\u4F9B\u6D4B\u8BD5\u73AF\u5883\u9A8C\u8BC1 Skill \u6548\u679C",
          "\u5BFC\u5165/\u5BFC\u51FA\uFF1A\u652F\u6301\u4ECE GitHub\u3001\u672C\u5730\u6587\u4EF6\u5BFC\u5165",
        ]),

        heading3("2.3.3 \u2B50 \u6280\u80FD\u5171\u4EAB\u5E02\u573A\uFF08\u65B0\u589E\u4EAE\u70B9\uFF09"),
        para("\u8FD9\u662F\u5929\u673A\u667A\u80FD\u4F53\u7684\u6838\u5FC3\u5DEE\u5F02\u5316\u529F\u80FD\uFF0C\u6784\u5EFA\u4E00\u4E2A\u53BB\u4E2D\u5FC3\u5316\u7684\u6280\u80FD\u751F\u6001\u5E02\u573A\uFF1A"),
        ...bulletList([
          "\u53D1\u5E03\u4E0E\u5206\u4EAB\uFF1A\u7528\u6237\u53EF\u5C06\u81EA\u5EFA Skill \u53D1\u5E03\u5230\u5E02\u573A\u4F9B\u4ED6\u4EBA\u4F7F\u7528",
          "\u79EF\u5206\u6536\u76CA\u4F53\u7CFB\uFF1A\u6BCF\u6B21\u5176\u4ED6\u7528\u6237\u5B89\u88C5/\u8C03\u7528\u4F60\u7684 Skill\uFF0C\u4F5C\u8005\u83B7\u5F97\u79EF\u5206\u6536\u76CA",
          "\u8BC4\u5206\u4E0E\u8BC4\u4EF7\uFF1A\u793E\u533A\u8BC4\u5206\u3001\u4F7F\u7528\u91CF\u6392\u884C\u3001\u7528\u6237\u8BC4\u4EF7",
          "\u8BA4\u8BC1\u4F53\u7CFB\uFF1A\u5B98\u65B9\u8BA4\u8BC1 / \u793E\u533A\u4F18\u79C0 / \u65B0\u9510\u4F5C\u8005\u7B49\u7B49\u7EA7",
          "Skill \u5546\u5E97\uFF1A\u9AD8\u7EA7 Skill \u53EF\u8BBE\u7F6E\u4ED8\u8D39\u4F7F\u7528\uFF0C\u4F5C\u8005\u83B7\u5F97\u5206\u6210\u6536\u5165",
        ]),

        heading3("2.3.4 \u670D\u52A1\u5361\u4E0E Profile"),
        ...bulletList([
          "\u4E2A\u4EBA Profile\uFF1A\u5C55\u793A\u4F5C\u8005\u4FE1\u606F\u3001\u53D1\u5E03\u7684 Skill\u3001\u83B7\u5F97\u7684\u8BC4\u4EF7",
          "\u670D\u52A1\u5361\uFF1A\u4E13\u4E1A\u670D\u52A1\u5546\u53EF\u521B\u5EFA\u670D\u52A1\u5361\u7247\uFF0C\u63D0\u4F9B\u4ED8\u8D39\u54A8\u8BE2\u670D\u52A1",
        ]),

        // ── 2.4 连接器 ──
        new Paragraph({ children: [new PageBreak()] }),
        heading2("2.4 \u8FDE\u63A5\u5668 (Connectors)"),
        para("\u5BF9\u6807 StoreClaw /app/connectors\uFF0C\u652F\u6301\u4E0E\u5404\u7C7B\u5916\u90E8\u5E73\u53F0\u548C\u670D\u52A1\u7684\u5BF9\u63A5\u3002"),

        heading3("2.4.1 \u5E73\u53F0\u8FDE\u63A5\u5668"),
        simpleTable(
          ["\u7C7B\u522B", "\u652F\u6301\u5E73\u53F0"],
          [
            ["\u7535\u5546\u5E73\u53F0", "Amazon, Shopify, TikTok Shop, Wix, WooCommerce, eBay, Etsy, Temu, SHEIN"],
            ["\u793E\u4EA4\u5A92\u4F53", "TikTok, Instagram, Facebook, Twitter/X, YouTube, LinkedIn, Reddit, \u5C0F\u7EA2\u4E66"],
            ["\u529E\u516C\u534F\u4F5C", "Gmail, Slack, Discord, \u98DE\u4E66, \u9489\u9489, \u4F01\u4E1A\u5FAE\u4FE1"],
            ["\u5E7F\u544A\u5E73\u53F0", "Google Ads, Facebook Ads, Amazon Ads, TikTok Ads"],
            ["\u6570\u636E\u5206\u6790", "Google Analytics, \u5356\u5BB6\u7CBE\u7075, Jungle Scout, Helium 10"],
            ["\u7269\u6D41\u5E73\u53F0", "4PX, \u4E91\u9014, \u71D5\u6587, ShipBob"],
          ],
          [2400, 6960],
        ),
        spacer(),

        heading3("2.4.2 \u2B50 \u591A\u6A21\u578B API \u96C6\u6210\uFF08\u65B0\u589E\u4EAE\u70B9\uFF09"),
        para("\u533A\u522B\u4E8E StoreClaw \u7684\u5355\u6A21\u578B\u67B6\u6784\uFF0C\u5929\u673A\u667A\u80FD\u4F53\u652F\u6301\u591A\u6A21\u578B\u63A5\u5165\uFF1A"),
        ...bulletList([
          "\u5185\u7F6E\u6A21\u578B\uFF1AOpenAI GPT-4o\u3001Anthropic Claude\u3001Google Gemini",
          "\u56FD\u4EA7\u6A21\u578B\uFF1A\u6587\u5FC3\u4E00\u8A00\u3001\u901A\u4E49\u5343\u95EE\u3001DeepSeek\u3001\u6668\u661F\u3001\u667A\u8C31\u6E05\u8A00",
          "\u81EA\u5B9A\u4E49 API\uFF1A\u7528\u6237\u53EF\u63A5\u5165\u81EA\u5DF1\u7684 LLM API Key\uFF0C\u4F7F\u7528\u81EA\u6709\u6A21\u578B",
          "\u6A21\u578B\u8DEF\u7531\uFF1A\u6839\u636E\u4EFB\u52A1\u7C7B\u578B\u81EA\u52A8\u9009\u62E9\u6700\u4F18\u6A21\u578B\uFF08\u5982\u5199\u4F5C\u7528 Claude\u3001\u5206\u6790\u7528 GPT-4o\uFF09",
          "MCP \u534F\u8BAE\u652F\u6301\uFF1A\u5B8C\u6574\u652F\u6301 Model Context Protocol\uFF0C\u53EF\u63A5\u5165\u4EFB\u4F55 MCP Server",
        ]),

        heading3("2.4.3 \u2B50 \u81EA\u5B9A\u4E49\u6570\u636E\u5E93\u5BF9\u63A5\uFF08\u65B0\u589E\u4EAE\u70B9\uFF09"),
        ...bulletList([
          "\u652F\u6301\u6570\u636E\u5E93\uFF1AMySQL, PostgreSQL, MongoDB, Redis, ClickHouse",
          "\u5B89\u5168\u8FDE\u63A5\uFF1A\u901A\u8FC7 SSH \u96A7\u9053\u6216 VPN \u5B89\u5168\u8FDE\u63A5\u7528\u6237\u6570\u636E\u5E93",
          "SQL \u67E5\u8BE2\u52A9\u624B\uFF1AAI \u81EA\u52A8\u751F\u6210 SQL \u67E5\u8BE2\u5E76\u53EF\u89C6\u5316\u5C55\u793A\u7ED3\u679C",
          "\u6570\u636E\u540C\u6B65\uFF1A\u5B9A\u65F6\u540C\u6B65\u5916\u90E8\u6570\u636E\u5E93\u6570\u636E\u5230\u5E73\u53F0",
          "\u6570\u636E\u8131\u654F\uFF1A\u652F\u6301\u654F\u611F\u6570\u636E\u81EA\u52A8\u8131\u654F\u5904\u7406",
        ]),

        // ── 2.5 渠道 ──
        heading2("2.5 \u6E20\u9053\u7BA1\u7406 (Channels)"),
        para("\u5BF9\u6807 StoreClaw /app/channels\uFF0C\u7EDF\u4E00\u7BA1\u7406\u591A\u5E73\u53F0\u5185\u5BB9\u53D1\u5E03\u4E0E\u4E92\u52A8\u3002"),
        ...bulletList([
          "\u591A\u5E73\u53F0\u7EDF\u4E00\u53D1\u5E03\uFF1A\u4E00\u7BC7\u5185\u5BB9\u540C\u65F6\u53D1\u5E03\u5230\u591A\u4E2A\u793E\u4EA4\u5A92\u4F53\u5E73\u53F0",
          "\u667A\u80FD\u5206\u53D1\uFF1A\u6839\u636E\u5E73\u53F0\u7279\u6027\u81EA\u52A8\u8C03\u6574\u5185\u5BB9\u683C\u5F0F\u548C\u5C3A\u5BF8",
          "\u4E92\u52A8\u7BA1\u7406\uFF1A\u7EDF\u4E00\u67E5\u770B\u5404\u5E73\u53F0\u8BC4\u8BBA\u3001\u6D88\u606F\u5E76\u667A\u80FD\u56DE\u590D",
          "\u6548\u679C\u8FFD\u8E2A\uFF1A\u8DE8\u5E73\u53F0\u6570\u636E\u7EDF\u4E00\u770B\u677F\uFF0C\u5BF9\u6BD4\u5404\u6E20\u9053\u6548\u679C",
          "\u5185\u5BB9\u65E5\u5386\uFF1A\u53EF\u89C6\u5316\u5185\u5BB9\u53D1\u5E03\u8BA1\u5212\u65E5\u5386",
        ]),

        // ── 2.6 资产库 ──
        heading2("2.6 \u8D44\u4EA7\u5E93 (Library)"),
        para("\u5BF9\u6807 StoreClaw /app/library\uFF0C\u7EDF\u4E00\u7BA1\u7406\u6240\u6709\u6570\u5B57\u8D44\u4EA7\u3002"),
        ...bulletList([
          "\u6587\u4EF6\u7BA1\u7406\uFF1A\u652F\u6301\u56FE\u7247\u3001\u89C6\u9891\u3001\u6587\u6863\u3001\u8868\u683C\u7B49\u591A\u683C\u5F0F\u6587\u4EF6\u5B58\u50A8",
          "\u667A\u80FD\u5206\u7C7B\uFF1AAI \u81EA\u52A8\u6807\u7B7E\u3001\u5206\u7C7B\u3001\u641C\u7D22",
          "\u7248\u672C\u7BA1\u7406\uFF1A\u6587\u4EF6\u5386\u53F2\u7248\u672C\u8BB0\u5F55\u4E0E\u56DE\u6EDA",
          "\u7D20\u6750\u751F\u6210\uFF1AAI \u4E00\u952E\u751F\u6210\u4EA7\u54C1\u56FE\u3001\u5E7F\u544A\u56FE\u3001\u793E\u5A92\u7D20\u6750",
          "\u56E2\u961F\u5171\u4EAB\uFF1A\u652F\u6301\u56E2\u961F\u6210\u5458\u95F4\u5171\u4EAB\u8D44\u4EA7\u4E0E\u6743\u9650\u7BA1\u7406",
          "\u4E91\u5B58\u50A8\u5BF9\u63A5\uFF1A\u652F\u6301 AWS S3\u3001\u963F\u91CC\u4E91 OSS\u3001\u817E\u8BAF\u4E91 COS",
        ]),

        // ── 2.7 知识库 ──
        heading2("2.7 \u2B50 \u77E5\u8BC6\u5E93 (Knowledge Base)\uFF08\u65B0\u589E\u4EAE\u70B9\uFF09"),
        para("\u8FD9\u662F StoreClaw \u4E0D\u5177\u5907\u7684\u91CD\u8981\u529F\u80FD\uFF0C\u4E3A\u7528\u6237\u63D0\u4F9B\u4E13\u5C5E\u77E5\u8BC6\u7BA1\u7406\u4E0E\u667A\u80FD\u68C0\u7D22\u80FD\u529B\uFF1A"),
        ...bulletList([
          "\u6587\u6863\u4E0A\u4F20\uFF1A\u652F\u6301 PDF\u3001Word\u3001Excel\u3001\u7F51\u9875\u94FE\u63A5\u3001\u7EAF\u6587\u672C\u7B49\u591A\u79CD\u683C\u5F0F",
          "\u5411\u91CF\u5316\u5B58\u50A8\uFF1A\u81EA\u52A8\u5C06\u6587\u6863\u5207\u5206\u3001\u5411\u91CF\u5316\u5B58\u50A8\uFF0C\u652F\u6301\u8BED\u4E49\u68C0\u7D22",
          "RAG \u589E\u5F3A\u751F\u6210\uFF1A\u5BF9\u8BDD\u65F6\u81EA\u52A8\u68C0\u7D22\u76F8\u5173\u77E5\u8BC6\uFF0C\u63D0\u5347\u56DE\u7B54\u51C6\u786E\u6027",
          "\u591A\u77E5\u8BC6\u5E93\u7BA1\u7406\uFF1A\u6309\u9879\u76EE/\u4E1A\u52A1\u7EBF\u521B\u5EFA\u591A\u4E2A\u72EC\u7ACB\u77E5\u8BC6\u5E93",
          "\u6743\u9650\u63A7\u5236\uFF1A\u77E5\u8BC6\u5E93\u7EA7\u522B\u7684\u8BBF\u95EE\u6743\u9650\u7BA1\u7406",
          "\u81EA\u52A8\u66F4\u65B0\uFF1A\u5B9A\u65F6\u722C\u53D6\u6307\u5B9A\u7F51\u9875\u66F4\u65B0\u77E5\u8BC6\u5E93\u5185\u5BB9",
          "\u5BFC\u5165\u6E90\uFF1A\u652F\u6301\u4ECE Notion\u3001\u8BED\u96C0\u3001\u98DE\u4E66\u6587\u6863\u7B49\u4E09\u65B9\u5E73\u53F0\u5BFC\u5165",
        ]),

        // ── 2.8 项目 ──
        heading2("2.8 \u9879\u76EE\u7BA1\u7406 (Projects)"),
        para("\u5BF9\u6807 StoreClaw /app/projects\uFF0C\u63D0\u4F9B\u56E2\u961F\u534F\u4F5C\u4E0E\u9879\u76EE\u7EC4\u7EC7\u80FD\u529B\u3002"),
        ...bulletList([
          "\u9879\u76EE\u7A7A\u95F4\uFF1A\u6BCF\u4E2A\u9879\u76EE\u72EC\u7ACB\u7684\u5DE5\u4F5C\u7A7A\u95F4\uFF0C\u5305\u542B\u4EFB\u52A1\u3001\u6587\u4EF6\u3001\u77E5\u8BC6\u5E93",
          "\u56E2\u961F\u534F\u4F5C\uFF1A\u90AE\u8BF7\u56E2\u961F\u6210\u5458\u3001\u89D2\u8272\u5206\u914D\u3001\u6743\u9650\u7BA1\u7406",
          "\u4EFB\u52A1\u770B\u677F\uFF1A\u770B\u677F\u89C6\u56FE\u8FFD\u8E2A\u4EFB\u52A1\u8FDB\u5EA6",
          "\u9879\u76EE\u62A5\u544A\uFF1AAI \u81EA\u52A8\u751F\u6210\u9879\u76EE\u8FDB\u5EA6\u62A5\u544A\u4E0E\u6570\u636E\u5206\u6790",
          "\u6A21\u677F\u5316\u9879\u76EE\uFF1A\u9884\u7F6E\u65B0\u54C1\u4E0A\u67B6\u3001\u65FA\u5B63\u51C6\u5907\u3001\u54C1\u724C\u51FA\u6D77\u7B49\u9879\u76EE\u6A21\u677F",
        ]),

        // ═══════════ 3. 积分与商业体系 ═══════════
        new Paragraph({ children: [new PageBreak()] }),
        heading1("3. \u2B50 \u79EF\u5206\u4E0E\u5546\u4E1A\u4F53\u7CFB\uFF08\u65B0\u589E\u4EAE\u70B9\uFF09"),

        heading2("3.1 \u79EF\u5206\u4F53\u7CFB\u8BBE\u8BA1"),
        para("\u5929\u673A\u667A\u80FD\u4F53\u5EFA\u7ACB\u5B8C\u6574\u7684\u79EF\u5206\u7ECF\u6D4E\u4F53\u7CFB\uFF0C\u6FC0\u52B1\u7528\u6237\u521B\u4F5C\u4E0E\u5206\u4EAB\u4F18\u8D28\u5185\u5BB9\uFF1A"),

        heading3("3.1.1 \u79EF\u5206\u83B7\u53D6\u65B9\u5F0F"),
        simpleTable(
          ["\u884C\u4E3A", "\u79EF\u5206\u5956\u52B1", "\u8BF4\u660E"],
          [
            ["\u53D1\u5E03 Skill", "+100 \u79EF\u5206", "\u6BCF\u53D1\u5E03\u4E00\u4E2A\u901A\u8FC7\u5BA1\u6838\u7684 Skill"],
            ["Skill \u88AB\u5B89\u88C5", "+5 \u79EF\u5206/\u6B21", "\u6BCF\u6B21\u5176\u4ED6\u7528\u6237\u5B89\u88C5\u4F60\u7684 Skill"],
            ["Skill \u88AB\u8C03\u7528", "+1 \u79EF\u5206/\u6B21", "\u6BCF\u6B21\u5176\u4ED6\u7528\u6237\u5728\u4EFB\u52A1\u4E2D\u8C03\u7528\u4F60\u7684 Skill"],
            ["\u5206\u4EAB\u6A21\u677F", "+50 \u79EF\u5206", "\u5206\u4EAB\u5B9A\u65F6\u4EFB\u52A1\u6A21\u677F\u5230\u793E\u533A"],
            ["\u9080\u8BF7\u65B0\u7528\u6237", "+200 \u79EF\u5206", "\u6BCF\u6210\u529F\u9080\u8BF7\u4E00\u4F4D\u65B0\u7528\u6237\u6CE8\u518C"],
            ["\u53C2\u4E0E\u8BC4\u4EF7", "+2 \u79EF\u5206", "\u5BF9 Skill \u53D1\u8868\u6709\u4EF7\u503C\u7684\u8BC4\u4EF7"],
            ["\u6BCF\u65E5\u767B\u5F55", "+10 \u79EF\u5206", "\u8FDE\u7EED\u767B\u5F55\u989D\u5916\u52A0\u500D"],
          ],
          [2400, 2400, 4560],
        ),
        spacer(),

        heading3("3.1.2 \u79EF\u5206\u6D88\u8D39\u65B9\u5F0F"),
        ...bulletList([
          "\u5151\u6362\u5E73\u53F0 Credits\uFF1A\u79EF\u5206\u53EF\u5151\u6362\u5E73\u53F0\u4F7F\u7528\u989D\u5EA6",
          "\u89E3\u9501\u9AD8\u7EA7\u529F\u80FD\uFF1A\u67D0\u4E9B\u9AD8\u7EA7\u529F\u80FD\u9700\u79EF\u5206\u89E3\u9501",
          "\u5151\u6362\u5468\u8FB9\uFF1A\u5B9A\u5236\u5468\u8FB9\u5546\u54C1\u5151\u6362",
          "\u63D0\u73B0\u6536\u76CA\uFF1A\u8FBE\u5230\u4E00\u5B9A\u989D\u5EA6\u53EF\u7533\u8BF7\u63D0\u73B0\uFF08\u9488\u5BF9\u4ED8\u8D39 Skill \u4F5C\u8005\uFF09",
        ]),

        heading2("3.2 \u4F1A\u5458\u5957\u9910\u8BBE\u8BA1"),
        para("\u53C2\u8003 StoreClaw \u7684\u8BA1\u8D39\u4F53\u7CFB\uFF0C\u7ED3\u5408\u5929\u673A\u7279\u8272\u8FDB\u884C\u4F18\u5316\uFF1A"),
        simpleTable(
          ["\u5957\u9910", "\u4EF7\u683C", "\u65E5\u5237\u65B0 Credits", "\u6708\u989D\u5EA6 Credits", "\u5E76\u53D1\u4EFB\u52A1", "\u7279\u8272\u529F\u80FD"],
          [
            ["\u514D\u8D39\u7248", "\u00A50", "50", "0", "1", "\u57FA\u7840\u529F\u80FD\u4F53\u9A8C"],
            ["\u4E13\u4E1A\u7248", "\u00A5128/\u6708", "100", "6,000", "10", "\u77E5\u8BC6\u5E93 + \u5168\u6280\u80FD"],
            ["\u65D7\u8230\u7248", "\u00A5258/\u6708", "100", "12,000", "10", "\u591A\u6A21\u578B + \u6570\u636E\u5E93\u5BF9\u63A5"],
            ["\u4F01\u4E1A\u7248", "\u00A51,288/\u6708", "200", "60,000", "20", "\u56E2\u961F\u534F\u4F5C + API + \u4E13\u5C5E\u652F\u6301"],
          ],
          [1500, 1500, 1500, 1560, 1200, 2100],
        ),
        spacer(),

        // ═══════════ 4. 系统设置 ═══════════
        heading1("4. \u7CFB\u7EDF\u8BBE\u7F6E\u4E0E\u7528\u6237\u4F53\u7CFB"),

        heading2("4.1 \u7528\u6237\u8D26\u6237\u4F53\u7CFB"),
        ...bulletList([
          "\u6CE8\u518C/\u767B\u5F55\uFF1A\u652F\u6301\u90AE\u7BB1\u3001\u624B\u673A\u53F7\u3001\u5FAE\u4FE1\u3001Google \u7B49\u591A\u79CD\u767B\u5F55\u65B9\u5F0F",
          "\u767B\u51FA\uFF1A\u5B89\u5168\u767B\u51FA\u4E0E\u591A\u8BBE\u5907\u7BA1\u7406",
          "\u4E2A\u4EBA\u8D44\u6599\uFF1A\u5934\u50CF\u3001\u6635\u79F0\u3001\u516C\u53F8\u4FE1\u606F\u3001\u8054\u7CFB\u65B9\u5F0F",
          "\u5B89\u5168\u8BBE\u7F6E\uFF1A\u5BC6\u7801\u4FEE\u6539\u3001\u4E8C\u6B21\u9A8C\u8BC1\u3001\u767B\u5F55\u65E5\u5FD7",
        ]),

        heading2("4.2 \u7CFB\u7EDF\u8BBE\u7F6E"),
        ...bulletList([
          "\u8BED\u8A00\u8BBE\u7F6E\uFF1A\u652F\u6301\u4E2D\u6587\u7B80\u4F53\u3001\u4E2D\u6587\u7E41\u4F53\u3001\u82F1\u6587\u3001\u65E5\u6587\u7B49\u591A\u8BED\u8A00",
          "\u4E3B\u9898\u8BBE\u7F6E\uFF1A\u4EAE\u8272/\u6697\u8272\u4E3B\u9898\u5207\u6362",
          "\u901A\u77E5\u8BBE\u7F6E\uFF1A\u90AE\u4EF6/\u6D88\u606F\u63A8\u9001/\u6D4F\u89C8\u5668\u901A\u77E5\u7BA1\u7406",
          "API Key \u7BA1\u7406\uFF1A\u7BA1\u7406\u5404\u5E73\u53F0\u63A5\u5165\u7684 API \u5BC6\u94A5",
          "\u7528\u91CF\u7EDF\u8BA1\uFF1A Credits \u6D88\u8017\u660E\u7EC6\u3001\u7528\u91CF\u8D8B\u52BF\u56FE",
        ]),

        heading2("4.3 \u5E2E\u52A9\u4E0E\u652F\u6301"),
        ...bulletList([
          "\u4E3B\u9875\u5F15\u5BFC\uFF1A\u65B0\u7528\u6237\u5F15\u5BFC\u6D41\u7A0B\uFF0C\u5FEB\u901F\u4E0A\u624B",
          "\u5E2E\u52A9\u4E2D\u5FC3\uFF1A\u5E38\u89C1\u95EE\u9898\u3001\u4F7F\u7528\u6559\u7A0B\u3001\u89C6\u9891\u6559\u7A0B",
          "\u5728\u7EBF\u5BA2\u670D\uFF1A\u5B9E\u65F6\u5BA2\u670D\u804A\u5929\u652F\u6301",
          "\u53CD\u9988\u5EFA\u8BAE\uFF1A\u7528\u6237\u53CD\u9988\u4E0E\u529F\u80FD\u5EFA\u8BAE\u6536\u96C6",
          "\u793E\u533A\u8BBA\u575B\uFF1A\u7528\u6237\u4EA4\u6D41\u793E\u533A",
        ]),

        // ═══════════ 5. 技术架构 ═══════════
        new Paragraph({ children: [new PageBreak()] }),
        heading1("5. \u6280\u672F\u67B6\u6784\u8BBE\u8BA1"),

        heading2("5.1 \u6574\u4F53\u67B6\u6784"),
        para("\u91C7\u7528\u5FAE\u670D\u52A1\u67B6\u6784\uFF0C\u524D\u540E\u7AEF\u5206\u79BB\uFF0C\u652F\u6301\u6C34\u5E73\u6269\u5C55\uFF1A"),
        simpleTable(
          ["\u5C42\u7EA7", "\u6280\u672F\u9009\u578B", "\u8BF4\u660E"],
          [
            ["\u524D\u7AEF", "React/Next.js + TypeScript + TailwindCSS", "Web \u7AEF + \u79FB\u52A8\u7AEF\u81EA\u9002\u5E94"],
            ["\u540E\u7AEF", "Node.js/Go + gRPC + REST API", "\u5FAE\u670D\u52A1\u67B6\u6784"],
            ["AI \u5F15\u64CE", "LangChain + LlamaIndex + \u81EA\u7814\u8DEF\u7531", "\u591A\u6A21\u578B\u8C03\u5EA6\u5F15\u64CE"],
            ["\u6570\u636E\u5C42", "PostgreSQL + Redis + Milvus/Pinecone", "\u5173\u7CFB\u578B + \u7F13\u5B58 + \u5411\u91CF\u6570\u636E\u5E93"],
            ["\u6D88\u606F\u961F\u5217", "RabbitMQ / Kafka", "\u5F02\u6B65\u4EFB\u52A1\u5904\u7406"],
            ["\u5BF9\u8C61\u5B58\u50A8", "AWS S3 / \u963F\u91CC\u4E91 OSS", "\u6587\u4EF6\u3001\u56FE\u7247\u5B58\u50A8"],
            ["\u90E8\u7F72", "Kubernetes + Docker + CI/CD", "\u5BB9\u5668\u5316\u90E8\u7F72"],
            ["\u76D1\u63A7", "Prometheus + Grafana + ELK", "\u5168\u94FE\u8DEF\u76D1\u63A7"],
          ],
          [2200, 4160, 3000],
        ),
        spacer(),

        heading2("5.2 \u5B89\u5168\u67B6\u6784"),
        ...bulletList([
          "\u6570\u636E\u52A0\u5BC6\uFF1A\u4F20\u8F93\u5C42 TLS 1.3\uFF0C\u5B58\u50A8\u5C42 AES-256 \u52A0\u5BC6",
          "OAuth 2.0\uFF1A\u7B2C\u4E09\u65B9\u5E73\u53F0\u6388\u6743\u5747\u91C7\u7528 OAuth 2.0 \u6807\u51C6\u534F\u8BAE",
          "\u6743\u9650\u6A21\u578B\uFF1ARBAC \u57FA\u4E8E\u89D2\u8272\u7684\u8BBF\u95EE\u63A7\u5236",
          "\u6570\u636E\u9694\u79BB\uFF1A\u591A\u79DF\u6237\u67B6\u6784\uFF0C\u6570\u636E\u4E25\u683C\u9694\u79BB",
          "\u5BA1\u8BA1\u65E5\u5FD7\uFF1A\u5173\u952E\u64CD\u4F5C\u5168\u94FE\u8DEF\u5BA1\u8BA1\u8BB0\u5F55",
          "\u5408\u89C4\u6027\uFF1A\u7B26\u5408 GDPR\u3001\u4E2A\u4FDD\u6CD5\u7B49\u6570\u636E\u4FDD\u62A4\u6CD5\u89C4",
        ]),

        // ═══════════ 6. 信息架构 ═══════════
        heading1("6. \u4FE1\u606F\u67B6\u6784\u4E0E\u5BFC\u822A\u8BBE\u8BA1"),

        heading2("6.1 \u4E3B\u5BFC\u822A\u7ED3\u6784"),
        para("\u5E73\u53F0\u91C7\u7528\u5DE6\u4FA7\u5BFC\u822A\u680F + \u53F3\u4FA7\u5185\u5BB9\u533A\u7684\u5E03\u5C40\uFF0C\u4E3B\u5BFC\u822A\u7ED3\u6784\u5982\u4E0B\uFF1A"),
        simpleTable(
          ["\u5BFC\u822A\u9879", "\u8DEF\u5F84", "\u8BF4\u660E"],
          [
            ["\u4E3B\u9875", "/home", "\u6570\u636E\u770B\u677F + \u5FEB\u6377\u5165\u53E3"],
            ["\u5BF9\u8BDD", "/chat", "\u667A\u80FD\u5BF9\u8BDD\u4E2D\u5FC3"],
            ["\u5B9A\u65F6\u4EFB\u52A1", "/schedule", "\u81EA\u52A8\u5316\u4EFB\u52A1\u7BA1\u7406"],
            ["\u6280\u80FD", "/skills", "\u6280\u80FD\u4E2D\u5FC3\u4E0E\u5E02\u573A"],
            ["\u8FDE\u63A5\u5668", "/connectors", "\u5E73\u53F0\u4E0E API \u8FDE\u63A5"],
            ["\u6E20\u9053", "/channels", "\u591A\u6E20\u9053\u5185\u5BB9\u7BA1\u7406"],
            ["\u8D44\u4EA7\u5E93", "/library", "\u6570\u5B57\u8D44\u4EA7\u7BA1\u7406"],
            ["\u77E5\u8BC6\u5E93", "/knowledge", "\u77E5\u8BC6\u5E93\u7BA1\u7406"],
            ["\u9879\u76EE", "/projects", "\u9879\u76EE\u7BA1\u7406"],
            ["\u8BBE\u7F6E", "/settings", "\u7CFB\u7EDF\u8BBE\u7F6E"],
          ],
          [2200, 2600, 4560],
        ),
        spacer(),

        // ═══════════ 7. 开发路线图 ═══════════
        new Paragraph({ children: [new PageBreak()] }),
        heading1("7. \u5F00\u53D1\u8DEF\u7EBF\u56FE"),

        heading2("7.1 \u7248\u672C\u89C4\u5212"),
        simpleTable(
          ["\u7248\u672C", "\u65F6\u95F4\u8282\u70B9", "\u6838\u5FC3\u4EA4\u4ED8\u7269", "\u72B6\u6001"],
          [
            ["V0.1 MVP", "2026 Q3", "\u667A\u80FD\u5BF9\u8BDD + \u57FA\u7840\u6280\u80FD + \u8FDE\u63A5\u5668 (Amazon/Shopify)", "\u89C4\u5212\u4E2D"],
            ["V0.5 Beta", "2026 Q4", "\u5B9A\u65F6\u4EFB\u52A1 + \u77E5\u8BC6\u5E93 + \u8D44\u4EA7\u5E93 + \u591A\u6A21\u578B", "\u89C4\u5212\u4E2D"],
            ["V1.0 \u6B63\u5F0F\u7248", "2027 Q1", "\u6280\u80FD\u5E02\u573A + \u79EF\u5206\u4F53\u7CFB + \u6E20\u9053\u7BA1\u7406 + \u9879\u76EE", "\u89C4\u5212\u4E2D"],
            ["V1.5 \u589E\u5F3A", "2027 Q2", "\u81EA\u5B9A\u4E49\u6570\u636E\u5E93 + \u4F01\u4E1A\u7248 + \u79FB\u52A8\u7AEF App", "\u89C4\u5212\u4E2D"],
            ["V2.0 \u751F\u6001", "2027 H2", "\u5F00\u653E\u5E73\u53F0 + \u5F00\u53D1\u8005 SDK + \u5168\u7403\u5316\u90E8\u7F72", "\u89C4\u5212\u4E2D"],
          ],
          [1800, 1800, 4200, 1560],
        ),
        spacer(),

        heading2("7.2 V0.1 MVP \u4EA4\u4ED8\u8303\u56F4"),
        para("MVP \u7248\u672C\u805A\u7126\u6838\u5FC3\u4EF7\u503C\u9A8C\u8BC1\uFF0C\u4EA4\u4ED8\u4EE5\u4E0B\u6838\u5FC3\u529F\u80FD\uFF1A"),
        ...bulletList([
          "\u667A\u80FD\u5BF9\u8BDD\uFF1A\u652F\u6301 GPT-4o \u548C Claude \u53CC\u6A21\u578B\u5207\u6362",
          "\u57FA\u7840\u6280\u80FD\uFF1A10\u4E2A\u6838\u5FC3\u8DE8\u5883\u7535\u5546 Skill\uFF08Listing\u4F18\u5316\u3001\u5173\u952E\u8BCD\u7814\u7A76\u3001\u7ADE\u54C1\u5206\u6790\u7B49\uFF09",
          "\u8FDE\u63A5\u5668\uFF1AAmazon SP-API + Shopify API \u5BF9\u63A5",
          "\u7528\u6237\u4F53\u7CFB\uFF1A\u6CE8\u518C/\u767B\u5F55 + \u57FA\u7840\u8BBE\u7F6E",
          "\u8BA1\u8D39\u4F53\u7CFB\uFF1A\u514D\u8D39\u7248 + \u4E13\u4E1A\u7248",
        ]),

        // ═══════════ 8. 竞品分析补充 ═══════════
        heading1("8. \u7ADE\u54C1\u5206\u6790\u8865\u5145"),

        heading2("8.1 StoreClaw \u4EA7\u54C1\u5206\u6790"),
        para("StoreClaw \u5B9A\u4F4D\u4E3A\u7535\u5546\u9886\u57DF\u7684 AI Agent\uFF0C\u4E3B\u6253\u56DB\u5927\u6838\u5FC3\u6A21\u5757\uFF1ALLM Chat\u3001Skills\u3001Connectors\u3001Schedule\u3002\u5176\u4EA7\u54C1\u4EF7\u683C\u4ECE\u514D\u8D39\u7248\u5230 $199.9/\u6708\u7684 Ultra \u7248\uFF0C\u5DF2\u8FDE\u63A5 20+ \u5E73\u53F0\u5305\u62EC Shopify\u3001Amazon\u3001TikTok \u7B49\u3002"),

        heading2("8.2 \u5929\u673A\u667A\u80FD\u4F53\u7ADE\u4E89\u4F18\u52BF"),
        ...bulletList([
          "\u77E5\u8BC6\u5E93\u80FD\u529B\uFF1AStoreClaw \u7F3A\u5C11\u77E5\u8BC6\u5E93\u529F\u80FD\uFF0C\u5929\u673A\u63D0\u4F9B\u5B8C\u6574\u7684 RAG \u77E5\u8BC6\u68C0\u7D22\u4F53\u7CFB",
          "\u591A\u6A21\u578B\u652F\u6301\uFF1AStoreClaw \u4EC5\u652F\u6301\u5355\u6A21\u578B\uFF0C\u5929\u673A\u652F\u6301 6+ \u5927\u6A21\u578B\u81EA\u7531\u5207\u6362",
          "\u79EF\u5206\u751F\u6001\uFF1A\u6784\u5EFA\u521B\u4F5C\u8005\u7ECF\u6D4E\u4F53\u7CFB\uFF0C\u6FC0\u52B1\u9AD8\u8D28\u91CF Skill \u521B\u4F5C",
          "\u6570\u636E\u5E93\u5BF9\u63A5\uFF1A\u652F\u6301\u7528\u6237\u81EA\u6709\u6570\u636E\u5E93\u8FDE\u63A5\uFF0C\u6253\u901A\u6570\u636E\u5B64\u5C9B",
          "\u672C\u571F\u5316\u4F18\u52BF\uFF1A\u66F4\u6DF1\u5165\u7684\u4E2D\u6587\u670D\u52A1\u3001\u672C\u571F\u5316\u652F\u4ED8\u3001\u56FD\u4EA7\u6A21\u578B\u652F\u6301",
        ]),

        // ═══════════ 9. 非功能性需求 ═══════════
        heading1("9. \u975E\u529F\u80FD\u6027\u9700\u6C42"),
        simpleTable(
          ["\u7EF4\u5EA6", "\u6307\u6807", "\u76EE\u6807\u503C"],
          [
            ["\u6027\u80FD", "API \u54CD\u5E94\u65F6\u95F4", "P95 < 500ms\uFF08\u975E AI \u63A5\u53E3\uFF09"],
            ["\u6027\u80FD", "AI \u9996\u5B57\u8F93\u51FA\u5EF6\u8FDF", "< 2s"],
            ["\u53EF\u7528\u6027", "\u7CFB\u7EDF\u53EF\u7528\u7387", "99.9% SLA"],
            ["\u5E76\u53D1", "\u5355\u8282\u70B9\u5E76\u53D1\u7528\u6237", "> 1,000"],
            ["\u5B89\u5168", "\u6570\u636E\u52A0\u5BC6", "TLS 1.3 + AES-256"],
            ["\u5408\u89C4", "\u6570\u636E\u4FDD\u62A4", "GDPR + \u4E2A\u4FDD\u6CD5"],
            ["\u56FD\u9645\u5316", "\u8BED\u8A00\u652F\u6301", "\u4E2D/\u82F1/\u65E5 + \u66F4\u591A"],
            ["\u53EF\u6269\u5C55", "\u5FAE\u670D\u52A1\u67B6\u6784", "\u652F\u6301\u6C34\u5E73\u81EA\u52A8\u6269\u5C55"],
          ],
          [2200, 3580, 3580],
        ),
        spacer(),

        // ═══════════ 10. 风险与应对 ═══════════
        heading1("10. \u98CE\u9669\u4E0E\u5E94\u5BF9\u7B56\u7565"),
        simpleTable(
          ["\u98CE\u9669\u7C7B\u522B", "\u98CE\u9669\u63CF\u8FF0", "\u5E94\u5BF9\u7B56\u7565"],
          [
            ["\u6280\u672F\u98CE\u9669", "\u591A\u6A21\u578B\u96C6\u6210\u590D\u6742\u5EA6\u9AD8", "\u91C7\u7528\u7EDF\u4E00\u7684\u6A21\u578B\u62BD\u8C61\u5C42\uFF0C\u6807\u51C6\u5316\u63A5\u5165\u534F\u8BAE"],
            ["\u5B89\u5168\u98CE\u9669", "\u7528\u6237\u6570\u636E\u5E93\u8FDE\u63A5\u5B89\u5168\u9690\u60A3", "\u5F3A\u5236 SSH \u96A7\u9053 + IP \u767D\u540D\u5355 + \u53EA\u8BFB\u6A21\u5F0F\u9ED8\u8BA4"],
            ["\u5546\u4E1A\u98CE\u9669", "\u79EF\u5206\u4F53\u7CFB\u5957\u5229\u4E0E\u4F5C\u5F0A", "\u667A\u80FD\u53CD\u4F5C\u5F0A\u7CFB\u7EDF + \u4EBA\u5DE5\u5BA1\u6838\u673A\u5236"],
            ["\u7ADE\u4E89\u98CE\u9669", "StoreClaw \u7B49\u7ADE\u54C1\u5FEB\u901F\u8FED\u4EE3", "\u4EE5\u77E5\u8BC6\u5E93+\u79EF\u5206\u751F\u6001\u6784\u5EFA\u62A4\u57CE\u6CB3"],
            ["\u8FD0\u8425\u98CE\u9669", "AI \u6210\u672C\u8FC7\u9AD8\u5F71\u54CD\u5229\u6DA6", "\u667A\u80FD\u6A21\u578B\u8DEF\u7531\u964D\u672C + \u7F13\u5B58\u7B56\u7565"],
          ],
          [1800, 3780, 3780],
        ),
        spacer(),

        // ═══════════ 11. AI Agent 核心架构设计 ═══════════
        new Paragraph({ children: [new PageBreak()] }),
        heading1("11. AI Agent \u6838\u5FC3\u67B6\u6784\u8BBE\u8BA1"),

        heading2("11.1 Agent \u8FD0\u884C\u8303\u5F0F"),
        para("\u5929\u673A\u667A\u80FD\u4F53\u91C7\u7528\u201C\u611F\u77E5 \u2192 \u89C4\u5212 \u2192 \u6267\u884C \u2192 \u53CD\u601D\u201D\u7684\u95ED\u73AF\u67B6\u6784\uFF0C\u652F\u6301\u5355\u667A\u80FD\u4F53\u4E0E\u591A\u667A\u80FD\u4F53\u534F\u540C\u4E24\u79CD\u6A21\u5F0F\uFF1A"),
        simpleTable(
          ["\u6A21\u5F0F", "\u9002\u7528\u573A\u666F", "\u6267\u884C\u6D41\u7A0B", "\u4EE3\u8868\u6280\u80FD"],
          [
            ["\u5355 Agent (ReAct)", "\u5BF9\u8BDD\u95EE\u7B54\u3001\u5355\u6B65\u5DE5\u5177\u8C03\u7528", "\u601D\u8003 \u2192 \u52A8\u4F5C \u2192 \u89C2\u5BDF \u2192 \u8FED\u4EE3\u76F4\u81F3\u5B8C\u6210", "Listing \u4F18\u5316\u3001\u5173\u952E\u8BCD\u7814\u7A76"],
            ["Plan-Execute", "\u590D\u6742\u591A\u6B65\u4EFB\u52A1\u3001\u5B9A\u65F6\u4EFB\u52A1\u94FE", "\u751F\u6210\u8BA1\u5212 \u2192 \u9010\u6B65\u6267\u884C \u2192 \u6C47\u603B\u9A8C\u8BC1", "\u5E97\u94FA\u8BCA\u65AD\u3001\u7ADE\u54C1\u76D1\u63A7\u62A5\u544A"],
            ["\u591A Agent \u534F\u540C", "\u8DE8\u9886\u57DF\u7EFC\u5408\u5206\u6790", "\u4E3B Agent \u5206\u89D2\u8272 \u2192 \u5B50 Agent \u5E76\u884C \u2192 \u7ED3\u679C\u805A\u5408", "\u5168\u94FE\u8DEF\u8FD0\u8425\u65B9\u6848\u751F\u6210"],
            ["Human-in-the-Loop", "\u9AD8\u98CE\u9669\u64CD\u4F5C\u9700\u4EBA\u5DE5\u786E\u8BA4", "\u6267\u884C\u524D\u9884\u89C8 \u2192 \u7528\u6237\u6279\u51C6 \u2192 \u6267\u884C", "\u5E7F\u544A\u6295\u653E\u3001\u4EF7\u683C\u8C03\u6574\u3001\u6279\u91CF\u4E0A\u67B6"],
          ],
          [1800, 2400, 3360, 2400],
        ),
        spacer(),

        heading2("11.2 \u591A\u667A\u80FD\u4F53\u7F16\u6392\u67B6\u6784"),
        para("\u5E73\u53F0\u5185\u7F6E Orchestrator \u8C03\u5EA6\u5C42\uFF0C\u8D1F\u8D23\u4EFB\u52A1\u5206\u89E3\u3001Agent \u9009\u62E9\u3001\u4E0A\u4E0B\u6587\u4F20\u9012\u4E0E\u7ED3\u679C\u805A\u5408\uFF1A"),
        ...bulletList([
          "\u4E3B Agent (Orchestrator)\uFF1A\u7406\u89E3\u7528\u6237\u610F\u56FE\uFF0C\u5206\u89E3\u5B50\u4EFB\u52A1\uFF0C\u5206\u914D\u4E13\u4E1A Skill \u4E0E\u5DE5\u5177",
          "\u4E13\u4E1A\u5B50 Agent\uFF1A\u6309\u9886\u57DF\u5212\u5206\uFF08\u9009\u54C1 Agent\u3001\u8425\u9500 Agent\u3001\u8FD0\u8425 Agent\u3001\u6570\u636E Agent\uFF09",
          "\u5DE5\u5177 Agent\uFF1A\u8D1F\u8D23\u8FDE\u63A5\u5668\u8C03\u7528\u3001SQL \u67E5\u8BE2\u3001API \u8BF7\u6C42\u7B49\u539F\u5B50\u64CD\u4F5C",
          "\u8BC4\u5BA1 Agent (Critic)\uFF1A\u5BF9\u8F93\u51FA\u7ED3\u679C\u8FDB\u884C\u8D28\u91CF\u68C0\u67E5\u3001\u4E8B\u5B9E\u6838\u5B9E\u4E0E\u683C\u5F0F\u6821\u9A8C",
          "\u6D88\u606F\u603B\u7EBF\uFF1A\u57FA\u4E8E\u4E8B\u4EF6\u9A71\u52A8\uFF0C\u5B50 Agent \u95F4\u901A\u8FC7\u6807\u51C6\u5316 Message Bus \u901A\u4FE1",
        ]),

        heading2("11.3 \u8BB0\u5FC6\u4F53\u7CFB"),
        simpleTable(
          ["\u8BB0\u5FC6\u7C7B\u578B", "\u5B58\u50A8\u65B9\u5F0F", "\u5B58\u7EED\u5468\u671F", "\u7528\u9014"],
          [
            ["\u5DE5\u4F5C\u8BB0\u5FC6", "Redis / \u4F1A\u8BDD\u7F13\u5B58", "\u5355\u6B21\u4EFB\u52A1", "\u5F53\u524D\u5BF9\u8BDD\u4E0A\u4E0B\u6587\u3001\u4E2D\u95F4\u7ED3\u679C"],
            ["\u77ED\u671F\u8BB0\u5FC6", "PostgreSQL", "7-30 \u5929", "\u7528\u6237\u504F\u597D\u3001\u6700\u8FD1\u4EFB\u52A1\u6458\u8981"],
            ["\u957F\u671F\u8BB0\u5FC6", "\u5411\u91CF\u6570\u636E\u5E93 (Milvus)", "\u6301\u4E45", "\u5386\u53F2\u51B3\u7B56\u3001\u4E1A\u52A1\u77E5\u8BC6\u3001\u54C1\u724C\u8BED\u8C03"],
            ["\u77E5\u8BC6\u5E93\u8BB0\u5FC6", "RAG \u5411\u91CF\u5E93", "\u6301\u4E45", "\u4F01\u4E1A\u6587\u6863\u3001SOP\u3001\u4EA7\u54C1\u8D44\u6599"],
            ["\u9879\u76EE\u8BB0\u5FC6", "\u9879\u76EE\u7A7A\u95F4\u9694\u79BB", "\u9879\u76EE\u751F\u547D\u5468\u671F", "\u56E2\u961F\u534F\u4F5C\u4E0A\u4E0B\u6587\u5171\u4EAB"],
          ],
          [2000, 2800, 2000, 3360],
        ),
        spacer(),

        heading2("11.4 Skill \u6267\u884C\u6D41\u7A0B"),
        para("Skill \u662F\u5929\u673A\u667A\u80FD\u4F53\u7684\u53EF\u590D\u7528\u80FD\u529B\u5355\u5143\uFF0C\u91C7\u7528\u6807\u51C6\u5316 Skill Schema \u5B9A\u4E49\uFF1A"),
        ...bulletList([
          "Skill Manifest\uFF1A\u540D\u79F0\u3001\u7248\u672C\u3001\u63CF\u8FF0\u3001\u8F93\u5165\u53C2\u6570 Schema\u3001\u6240\u9700\u8FDE\u63A5\u5668\u3001\u6240\u9700\u6743\u9650",
          "\u6267\u884C\u5F15\u64CE\uFF1A\u89E3\u6790 Manifest \u2192 \u52A0\u8F7D Prompt \u6A21\u677F \u2192 \u7ED1\u5B9A\u5DE5\u5177 \u2192 \u8C03\u7528 LLM \u2192 \u8FD4\u56DE\u7ED3\u6784\u5316\u7ED3\u679C",
          "\u5DE5\u5177\u94FE\uFF1ASkill \u53EF\u7EC4\u5408\u591A\u4E2A Connector \u5F62\u6210\u5DE5\u5177\u94FE\uFF08\u5982\u62C9\u53D6 Amazon \u6570\u636E \u2192 \u5206\u6790 \u2192 \u751F\u6210\u62A5\u544A\uFF09",
          "\u6C99\u7BB1\u9694\u79BB\uFF1A\u7528\u6237\u81EA\u5EFA Skill \u5728\u72EC\u7ACB\u6C99\u7BB1\u73AF\u5883\u8FD0\u884C\uFF0C\u9650\u5236 API \u8C03\u7528\u9891\u7387\u4E0E\u6570\u636E\u8BBF\u95EE\u8303\u56F4",
          "\u7248\u672C\u4E0E\u56DE\u6EDA\uFF1A\u6BCF\u6B21\u53D1\u5E03\u751F\u6210\u7248\u672C\u53F7\uFF0C\u652F\u6301\u4E00\u952E\u56DE\u6EDA\u81F3\u4EFB\u610F\u5386\u53F2\u7248\u672C",
        ]),

        heading3("11.4.1 Skill Schema \u793A\u4F8B"),
        para('{\n  "name": "amazon-listing-optimizer",\n  "version": "1.2.0",\n  "category": "cross-border",\n  "inputs": { "asin": "string", "target_market": "string" },\n  "connectors": ["amazon-sp-api"],\n  "knowledge_bases": ["brand-guidelines"],\n  "tools": ["fetch_listing", "keyword_research", "generate_bullets"],\n  "output_format": "markdown"\n}'),

        heading2("11.5 \u6A21\u578B\u8DEF\u7531\u4E0E Prompt \u5DE5\u7A0B"),
        simpleTable(
          ["\u4EFB\u52A1\u7C7B\u578B", "\u63A8\u8350\u6A21\u578B", "\u6E29\u5EA6", "\u8BF4\u660E"],
          [
            ["\u957F\u6587\u6848\u521B\u4F5C", "Claude 3.5 Sonnet", "0.7", "Listing\u3001A+\u9875\u9762\u3001\u90AE\u4EF6\u8425\u9500"],
            ["\u6570\u636E\u5206\u6790", "GPT-4o", "0.2", "SQL \u751F\u6210\u3001\u62A5\u8868\u89E3\u8BFB\u3001\u8D8B\u52BF\u9884\u6D4B"],
            ["\u4E2D\u6587\u5185\u5BB9", "\u901A\u4E49\u5343\u95EE / \u6587\u5FC3\u4E00\u8A00", "0.6", "\u672C\u571F\u5316\u8425\u9500\u6587\u6848"],
            ["\u4EE3\u7801/\u811A\u672C", "DeepSeek Coder", "0.1", "Skill \u5F00\u53D1\u3001\u6570\u636E\u5904\u7406\u811A\u672C"],
            ["\u5FEB\u901F\u95EE\u7B54", "GPT-4o-mini / DeepSeek", "0.5", "\u65E5\u5E38\u54A8\u8BE2\uFF0C\u964D\u4F4E\u6210\u672C"],
            ["\u591A\u6A21\u6001", "GPT-4o", "0.4", "\u56FE\u7247\u8BC6\u522B\u3001\u4EA7\u54C1\u56FE\u5206\u6790"],
          ],
          [2400, 2800, 1200, 3560],
        ),
        spacer(),
        para("Prompt \u5C42\u7EA7\u7ED3\u6784\uFF1A\u7CFB\u7EDF\u5C42 (Platform) \u2192 \u89D2\u8272\u5C42 (Skill) \u2192 \u4EFB\u52A1\u5C42 (Task) \u2192 \u4E0A\u4E0B\u6587\u5C42 (RAG/Memory) \u2192 \u7528\u6237\u5C42 (User Input)\u3002\u5404\u5C42\u53EF\u72EC\u7ACB\u7BA1\u7406\u4E0E A/B \u6D4B\u8BD5\u3002"),

        heading2("11.6 \u5DE5\u5177\u8C03\u7528\u4E0E MCP \u96C6\u6210"),
        ...bulletList([
          "\u7EDF\u4E00\u5DE5\u5177\u6CE8\u518C\u4E2D\u5FC3\uFF1A\u6240\u6709 Connector\u3001\u6570\u636E\u5E93\u3001\u81EA\u5B9A\u4E49 API \u5747\u6CE8\u518C\u4E3A Tool",
          "Function Calling\uFF1A\u652F\u6301 OpenAI / Anthropic \u539F\u751F\u5DE5\u5177\u8C03\u7528\u683C\u5F0F",
          "MCP Server\uFF1A\u7528\u6237\u53EF\u63A5\u5165\u81EA\u5B9A\u4E49 MCP Server\uFF0C\u6269\u5C55\u5DE5\u5177\u80FD\u529B",
          "\u6743\u9650\u7EA7\u522B\uFF1A\u5DE5\u5177\u8C03\u7528\u524D\u68C0\u67E5 RBAC \u6743\u9650\u4E0E OAuth Token \u6709\u6548\u6027",
          "\u8C03\u7528\u9650\u6D41\uFF1A\u6309\u5957\u9910\u9650\u5236\u5355\u7528\u6237\u5E76\u53D1\u5DE5\u5177\u8C03\u7528\u6570",
          "\u5BA1\u8BA1\u65E5\u5FD7\uFF1A\u6240\u6709\u5DE5\u5177\u8C03\u7528\u8BB0\u5F55\u53C2\u6570\u3001\u8017\u65F6\u3001\u7ED3\u679C\u72B6\u6001",
        ]),

        heading2("11.7 \u6570\u636E\u6D41\u4E0E\u9690\u79C1\u8BBE\u8BA1"),
        ...bulletList([
          "\u6570\u636E\u5206\u7C7B\uFF1A\u516C\u5F00\u6570\u636E / \u5185\u90E8\u6570\u636E / \u654F\u611F\u6570\u636E\u4E09\u7EA7\uFF0C\u654F\u611F\u6570\u636E\u81EA\u52A8\u8131\u654F\u540E\u9001\u6A21\u578B",
          "\u79DF\u6237\u9694\u79BB\uFF1A\u6BCF\u4E2A\u79DF\u6237\u72EC\u7ACB\u5411\u91CF\u5E93\u3001\u6570\u636E\u5E93\u547D\u540D\u7A7A\u95F4",
          "\u6570\u636E\u7559\u5B58\uFF1A\u7528\u6237\u53EF\u914D\u7F6E\u5BF9\u8BDD\u5386\u53F2\u4E0E\u77E5\u8BC6\u5E93\u4FDD\u7559\u5468\u671F",
          "\u6A21\u578B\u8C03\u7528\u4E0D\u843D\u76D8\uFF1A\u654F\u611F\u5B57\u6BB5\u5728\u9001\u6A21\u578B\u524D\u8131\u654F\uFF0C\u539F\u59CB\u6570\u636E\u4EC5\u5B58\u50A8\u4E8E\u7528\u6237\u6388\u6743\u533A\u57DF",
          "BYOK \u6A21\u5F0F\uFF1A\u7528\u6237\u81EA\u5E26 API Key \u65F6\uFF0C\u8BF7\u6C42\u76F4\u8FDE\u6A21\u578B\u5382\u5546\uFF0C\u5E73\u53F0\u4E0D\u7F13\u5B58\u54CD\u5E94\u5185\u5BB9",
        ]),

        heading2("11.8 \u5178\u578B\u4E1A\u52A1\u573A\u666F\u65F6\u5E8F"),
        heading3("\u573A\u666F\u4E00\uFF1A\u65B0\u54C1 Listing \u4F18\u5316"),
        ...numberedList([
          "\u7528\u6237\u4E0A\u4F20\u4EA7\u54C1\u4FE1\u606F\u6216\u5173\u8054 Amazon ASIN",
          "Orchestrator \u5206\u914D Listing \u4F18\u5316 Skill + \u5173\u952E\u8BCD\u7814\u7A76 Skill",
          "Skill \u8C03\u7528 Amazon SP-API \u83B7\u53D6\u7ADE\u54C1\u6570\u636E",
          "RAG \u68C0\u7D22\u54C1\u724C\u77E5\u8BC6\u5E93\u83B7\u53D6\u8BED\u8C03\u89C4\u8303",
          "Claude \u751F\u6210\u4E94\u70B9\u63CF\u8FF0 + A+ \u5185\u5BB9\u8349\u6848",
          "Critic Agent \u6821\u9A8C\u8FDD\u89C4\u8BCD\u4E0E\u5E73\u53F0\u653F\u7B56",
          "\u7528\u6237\u786E\u8BA4\u540E\u4E00\u952E\u540C\u6B65\u81F3 Amazon/Shopify",
        ]),
        heading3("\u573A\u666F\u4E8C\uFF1A\u6BCF\u65E5\u5E97\u94FA\u5065\u5EB7\u68C0\u67E5\uFF08\u5B9A\u65F6\u4EFB\u52A1\uFF09"),
        ...numberedList([
          "Cron \u89E6\u53D1\u6BCF\u65E5 08:00 \u6267\u884C",
          "\u4EFB\u52A1\u94FE\uFF1A\u62C9\u53D6\u5E97\u94FA\u6570\u636E \u2192 \u8BCA\u65AD\u5206\u6790 \u2192 \u751F\u6210\u62A5\u544A \u2192 \u63A8\u9001\u901A\u77E5",
          "\u5F02\u5E38\u6307\u6807\u81EA\u52A8\u544A\u8B66\uFF08\u5E93\u5B58\u3001\u8BC4\u5206\u3001\u8F6C\u5316\u7387\u4E0B\u964D\uFF09",
          "\u62A5\u544A\u63A8\u9001\u81F3\u90AE\u4EF6/\u9489\u9489/\u4F01\u4E1A\u5FAE\u4FE1",
        ]),

        // ═══════════ 附录 ═══════════
        heading1("\u9644\u5F55"),

        heading2("A. \u672F\u8BED\u8868"),
        simpleTable(
          ["\u672F\u8BED", "\u82F1\u6587", "\u8BF4\u660E"],
          [
            ["Skill", "Skill", "\u53EF\u590D\u7528\u7684 AI \u80FD\u529B\u6A21\u5757\uFF0C\u5C01\u88C5\u7279\u5B9A\u4E1A\u52A1\u903B\u8F91"],
            ["\u8FDE\u63A5\u5668", "Connector", "\u4E0E\u5916\u90E8\u5E73\u53F0/\u670D\u52A1\u7684\u96C6\u6210\u63A5\u53E3"],
            ["\u77E5\u8BC6\u5E93", "Knowledge Base", "\u7ED3\u6784\u5316\u5B58\u50A8\u7684\u4E1A\u52A1\u77E5\u8BC6\uFF0C\u652F\u6301\u5411\u91CF\u68C0\u7D22"],
            ["RAG", "Retrieval-Augmented Generation", "\u68C0\u7D22\u589E\u5F3A\u751F\u6210\uFF0C\u5229\u7528\u77E5\u8BC6\u5E93\u63D0\u5347\u56DE\u7B54\u8D28\u91CF"],
            ["MCP", "Model Context Protocol", "AI \u6A21\u578B\u4E0A\u4E0B\u6587\u534F\u8BAE\uFF0C\u7528\u4E8E\u5DE5\u5177\u96C6\u6210"],
            ["Credits", "Credits", "\u5E73\u53F0\u6D88\u8D39\u989D\u5EA6\u5355\u4F4D"],
          ],
          [2200, 3580, 3580],
        ),
        spacer(),

        heading2("B. \u53C2\u8003\u6587\u6863"),
        ...bulletList([
          "StoreClaw \u5B98\u7F51: https://www.storeclaw.ai/",
          "StoreClaw \u529F\u80FD\u9875: https://www.storeclaw.ai/features",
          "StoreClaw \u5B9A\u4EF7\u9875: https://www.storeclaw.ai/pricing",
          "Amazon SP-API \u6587\u6863: https://developer-docs.amazon.com/sp-api/",
          "Shopify API \u6587\u6863: https://shopify.dev/docs/api",
          "MCP \u534F\u8BAE\u89C4\u8303: https://modelcontextprotocol.io/",
        ]),
        spacer(),
        para("\u2014\u2014 \u6587\u6863\u7ED3\u675F \u2014\u2014", { italics: true, color: C.mid }),
      ],
    },
  ],
});

function bulletList(items) {
  return items.map(text => new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60, line: 340 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: C.dark })],
  }));
}

function numberedList(items) {
  return items.map(text => new Paragraph({
    numbering: { reference: "numbers", level: 0 },
    spacing: { after: 60, line: 340 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: C.dark })],
  }));
}

const outputPath = require("path").join(__dirname, "天机智能体_PRD_V1.0.docx");

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`PRD document created: ${outputPath}`);
}).catch(err => {
  console.error("Failed to generate PRD:", err);
  process.exit(1);
});
