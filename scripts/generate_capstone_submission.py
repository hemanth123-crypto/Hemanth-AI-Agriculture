"""Generate submission PDFs and an editable, text-based PowerPoint from source facts."""
from __future__ import annotations

import json
import zipfile
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF

ROOT = Path(__file__).resolve().parents[1]
GREEN = colors.HexColor("#08794d")
DARK = colors.HexColor("#143a2a")
PALE = colors.HexColor("#e8f5ed")
MUTED = colors.HexColor("#53665c")
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle(name="DocTitle", parent=STYLES["Title"], textColor=DARK,
                          fontSize=23, leading=28, alignment=TA_CENTER, spaceAfter=8))
STYLES.add(ParagraphStyle(name="SubTitle", parent=STYLES["Normal"], textColor=MUTED,
                          fontSize=9, leading=13, alignment=TA_CENTER, spaceAfter=14))
STYLES.add(ParagraphStyle(name="H1g", parent=STYLES["Heading1"], textColor=GREEN,
                          fontSize=15, leading=19, spaceBefore=10, spaceAfter=6))
STYLES.add(ParagraphStyle(name="H2g", parent=STYLES["Heading2"], textColor=DARK,
                          fontSize=11, leading=14, spaceBefore=7, spaceAfter=4))
STYLES.add(ParagraphStyle(name="Bodyg", parent=STYLES["BodyText"], fontSize=9,
                          leading=13, spaceAfter=5))
STYLES.add(ParagraphStyle(name="Smallg", parent=STYLES["BodyText"], fontSize=7.5,
                          leading=10, textColor=MUTED))


def footer(canvas, doc):
    canvas.saveState()
    w, _ = doc.pagesize
    canvas.setStrokeColor(colors.HexColor("#c8ded1"))
    canvas.line(18 * mm, 14 * mm, w - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "CropShield AI | Capstone Submission")
    canvas.drawRightString(w - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def para(text, style="Bodyg"):
    return Paragraph(text, STYLES[style])


def bullet(text):
    return para("&#8226;&nbsp; " + text)


def make_doc(path: Path, title: str, subtitle: str, story, pagesize=A4):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=pagesize, rightMargin=18*mm,
                            leftMargin=18*mm, topMargin=17*mm, bottomMargin=20*mm,
                            title=title, author="CropShield AI Project Team")
    doc.build([para(title, "DocTitle"), para(subtitle, "SubTitle"), *story],
              onFirstPage=footer, onLaterPages=footer)


def grid(rows, widths=None, font=8):
    cooked = [[para(str(cell), "Smallg" if i else "Bodyg") for cell in row]
              for i, row in enumerate(rows)]
    t = Table(cooked, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), GREEN), ("TEXTCOLOR", (0,0),(-1,0), colors.white),
        ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"), ("BACKGROUND", (0,1),(-1,-1), PALE),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.white, PALE]),
        ("GRID", (0,0),(-1,-1), .35, colors.HexColor("#bfd8c9")),
        ("VALIGN", (0,0),(-1,-1), "TOP"), ("LEFTPADDING", (0,0),(-1,-1), 6),
        ("RIGHTPADDING", (0,0),(-1,-1), 6), ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5), ("FONTSIZE", (0,0),(-1,-1), font),
    ]))
    return t


def architecture_diagram():
    d = Drawing(740, 390)
    d.add(Rect(0, 0, 760, 390, fillColor=colors.HexColor("#f7fbf8"),
              strokeColor=colors.HexColor("#c8ded1"), rx=9, ry=9))
    rows = [
        ("DATA", ["Synthetic 1,500-row\nCSV", "Preprocessing\n& features", "Structured cases\n(row records)"]),
        ("RETRIEVAL", ["Local dense\nHashingVectorizer\n+ projection", "FAISS inner-product\nindex", "Keyword index\n+ metadata filters", "Hybrid merge\n+ reranker"]),
        ("ADVISORY", ["Input validation\n& guardrails", "Query classifier\n+ agent orchestrator", "Recommendation / risk /\nyield / impact agents", "Optional LLM\nprovider judge"]),
        ("SERVING", ["FastAPI routes\n+ Pydantic", "HTML / CSS / JS\nSPA", "Optional Streamlit\nclient", "SQLite auth\n+ JSON feedback"]),
    ]
    y = 318
    palette = [colors.HexColor("#d9efe2"), colors.HexColor("#dceeea"),
               colors.HexColor("#e8f1dc"), colors.HexColor("#e0eaf1")]
    for idx, (label, boxes) in enumerate(rows):
        d.add(String(18, y+23, label, fontName="Helvetica-Bold", fontSize=10, fillColor=DARK))
        x, box_w = 120, (620 - 12*(len(boxes)-1))/len(boxes)
        for j, text in enumerate(boxes):
            bx = x+j*(box_w+12)
            d.add(Rect(bx, y, box_w, 51, fillColor=palette[idx],
                       strokeColor=GREEN, strokeWidth=.8, rx=5, ry=5))
            lines = text.split("\n")
            for line_i, line in enumerate(lines):
                d.add(String(bx+box_w/2, y+31-line_i*11, line,
                             textAnchor="middle", fontName="Helvetica", fontSize=8,
                             fillColor=DARK))
            if j:
                d.add(Line(bx-10, y+25, bx-2, y+25, strokeColor=GREEN, strokeWidth=1.2))
                d.add(String(bx-7, y+28, ">", fontName="Helvetica-Bold", fontSize=8, fillColor=GREEN))
        if idx < len(rows)-1:
            d.add(Line(430, y-8, 430, y-22, strokeColor=GREEN, strokeWidth=1.1))
            d.add(String(427, y-20, "v", fontName="Helvetica-Bold", fontSize=8, fillColor=GREEN))
        y -= 78
    d.add(String(18, 20, "Local artifact paths: data/ | models/ | indexes/ | evaluation/reports/",
                 fontName="Helvetica", fontSize=8, fillColor=MUTED))
    return d


def generate_architecture():
    story = [para("System overview", "H1g"), para(
        "The application keeps its implementation in the existing <b>app/</b> package. "
        "This diagram reflects the code and configured local artifacts: structured case rows, "
        "a local dense projection and FAISS index, a keyword index, hybrid retrieval, the "
        "agent workflow, API and UI clients."), Spacer(1, 5), architecture_diagram(),
        Spacer(1, 8), para("Data and execution path", "H1g"),
        bullet("CSV records are loaded and normalized by the existing preprocessing and document-processing utilities; this is row-based case indexing, not a separate chunked document corpus."),
        bullet("A deterministic local dense representation is built using scikit-learn HashingVectorizer features and a seeded projection, then searched through FAISS. Keyword and metadata retrieval provide complementary signals."),
        bullet("The FastAPI query route sends validated agricultural requests through query classification, retrieval, recommendation, risk, yield and impact components. Optional LLM calls depend on configured provider access."),
        bullet("The browser SPA is served by FastAPI. A separate Streamlit client is present under frontend/ and calls the API. Authentication state is stored in SQLite; feedback is stored locally."),
        para("Storage and boundaries", "H1g"),
        para("Model files are in models/, FAISS and keyword artifacts in indexes/, and reports in evaluation/reports/. The checked-in .env.example contains placeholders only. No ChromaDB service is implemented in the inspected source."),
    ]
    make_doc(ROOT/"architecture"/"Architecture_Diagram.pdf", "CropShield AI Architecture",
             "Implementation-based architecture diagram | generated 10 October 2026", story,
             pagesize=landscape(A4))


def generate_design():
    story = [para("Problem statement", "H1g"), para(
        "Agricultural decisions depend on interacting crop, season, location, soil, weather and input conditions. "
        "CropShield AI provides a single interface to search historical crop cases, summarize relevant evidence, "
        "recommend crops, estimate yield and surface agronomic risks."),
        para("Business objective", "H1g"), para(
        "Support agronomists, extension officers and agricultural users with faster, evidence-linked decision support. "
        "Predictions are advisory estimates and should be reviewed with local agronomic expertise."),
        para("Architecture and technology choices", "H1g"), grid([
            ["Layer", "Implementation", "Reason / trade-off"],
            ["API", "Python, FastAPI, Pydantic, Uvicorn", "Typed HTTP endpoints and generated OpenAPI docs."],
            ["Retrieval", "FAISS CPU, local hashed dense features, keyword/metadata search, hybrid ranking", "Local operation and reproducibility; hashed vectors are not a pretrained semantic embedding model."],
            ["Generation", "Optional OpenAI-compatible chat/judge provider", "External key, credits, endpoint access, latency and structured output can limit runtime evaluation."],
            ["ML", "scikit-learn RandomForest classifier and regressor", "Fits tabular features; quality reflects synthetic training data and should not be generalized to field outcomes."],
            ["UI", "FastAPI-served HTML/CSS/JS SPA; separate Streamlit client", "Main browser app uses no frontend build step; Streamlit requires its optional dependency."],
            ["Storage", "CSV, model files, FAISS/index artifacts, SQLite auth, JSON feedback", "Simple local persistence; not a distributed production data layer."],
        ], widths=[24*mm, 60*mm, 90*mm]),
        para("Retrieval strategy", "H1g"), para(
        "The project builds vector and keyword indexes over structured case rows. Retrieval can apply crop, state and season metadata filters, combine dense and lexical evidence, and rerank candidates. Labeled benchmark evaluation compares retrieved crop labels with the query's ground-truth labels using Precision@K, Recall@K, MRR and hit rate."),
        para("Agent workflow", "H1g"), para(
        "The orchestrator applies input/scope checks, classifies the query and extracts conditions, retrieves supporting cases, invokes recommendation, risk, yield and impact components where appropriate, validates output and formats the advisory. The implementation is a modular orchestrated pipeline; component boundaries do not imply independently hosted agents."),
        para("Evaluation strategy", "H1g"), para(
        "Local retrieval and ML reports are persisted under evaluation/reports/. RAGAS and DeepEval adapters exist for per-query LLM judging. Those judge evaluations are provider-dependent and can fail when the configured model endpoint is unreachable or its account has no credits. The report distinguishes saved benchmark evidence from pending live judge results."),
        para("Limitations and trade-offs", "H1g"),
        bullet("The principal 1,500-row dataset is synthetic local test data, not a verified field survey; measured performance is not evidence of real-world agronomic accuracy."),
        bullet("A saved retrieval benchmark can be biased by its 20 labeled queries and crop-level relevance labels; it does not measure all forms of answer quality."),
        bullet("LLM judge output is nondeterministic, costs credits and depends on valid endpoint configuration. RAGAS/DeepEval scores are therefore not always available."),
        bullet("FAISS and local files suit a single-node prototype; access controls, backup, monitoring and data governance need production hardening."),
        bullet("The Streamlit frontend is an additional client; the primary UI is the static frontend served by FastAPI."),
    ]
    make_doc(ROOT/"design"/"Design_Document.pdf", "CropShield AI Design Document",
             "Capstone submission | based on inspected source, configuration and saved reports", story)


def generate_api():
    story = [para("Overview", "H1g"), para(
        "FastAPI serves interactive OpenAPI documentation at <b>/docs</b> and ReDoc at <b>/redoc</b>. "
        "JSON request and response models are defined in app/models/schemas.py and individual route modules. "
        "Authentication uses bearer tokens for protected routes; the login response returns the token."),
        para("Primary application endpoints", "H1g"), grid([
            ["Method and path", "Purpose", "Request / response summary"],
            ["GET /health; GET /api/health", "Service, retrieval and model readiness", "JSON health state."],
            ["GET /api/crops; /api/states; /api/seasons", "UI option metadata", "JSON arrays of supported values."],
            ["POST /api/auth/login", "Authenticate", "{email, password} -> {success, token, user, message}."],
            ["POST /api/auth/signup", "Create account", "{name, email, password, role?} -> auth response; admin role cannot be self-assigned."],
            ["GET /api/auth/me", "Validate current token", "Authorization: Bearer <token> -> {email, name, role}."],
            ["POST /api/query", "Agricultural advisory", "AdvisoryRequest -> recommendations, similar cases, risk/yield/impact, formatted advisory and latency."],
            ["POST /api/search", "Hybrid case search", "{query, crop?, state?, season?, ph?, rainfall?, temperature?, top_k?} -> list of cases."],
            ["GET /api/cases", "Browse indexed cases", "Optional crop/state/season/limit query parameters -> case list."],
            ["POST /api/recommend; /api/recommendation", "Crop recommendation", "Existing recommendation request schema -> RecommendationResponse."],
            ["POST /api/alternatives", "Alternative crop recommendation", "Existing recommendation request schema -> RecommendationResponse."],
            ["POST /api/predict-yield; /api/prediction", "ML yield estimate", "Yield prediction feature object -> predicted yield, interval and related fields."],
            ["POST /api/suitability", "Crop suitability classification", "Existing suitability inputs -> class and scores."],
            ["POST /api/analyze-impact", "Agronomic impact analysis", "Existing analysis input schema -> impact result."],
            ["POST /api/feedback; GET /api/feedback/summary", "Feedback capture / aggregates", "FeedbackRequest -> status; summary -> aggregate JSON."],
            ["POST /api/evaluate; GET /api/evaluation/latest", "Evaluation run / saved result", "Evaluation request -> report; latest -> saved JSON report."],
            ["POST /api/evaluation/crop; GET /api/evaluation/crop", "Crop evaluation features", "See generated OpenAPI schema for required fields."],
            ["POST /api/advisory-report/pdf", "Generate advisory PDF", "Existing advisory report payload -> downloadable PDF response."],
            ["/api/admin/*", "Administrative overview, users, feedback, evaluation, ML, dataset and health", "Admin routes; require authorized admin session/token."],
        ], widths=[46*mm, 39*mm, 89*mm]),
        para("Example requests", "H1g"), para("Advisory query:<br/><font name='Courier'>{\"query\":\"Compare rice and maize for Kharif in Andhra Pradesh with 1000 mm rainfall and pH 6.5\",\"top_k\":5}</font>"),
        para("Search cases:<br/><font name='Courier'>{\"query\":\"Wheat in Punjab during Rabi\",\"crop\":\"Wheat\",\"state\":\"Punjab\",\"season\":\"Rabi\",\"top_k\":5}</font>"),
        para("Yield prediction:<br/><font name='Courier'>{\"crop\":\"Rice\",\"season\":\"Kharif\",\"state\":\"Andhra Pradesh\",\"area\":1000,\"fertilizer\":120,\"pesticide\":1,\"n\":80,\"p\":40,\"k\":40,\"ph\":6.5,\"temperature\":28,\"rainfall\":1100,\"humidity\":75}</font>"),
        para("Exact field constraints can evolve with the source schemas; run the server and consult <b>http://127.0.0.1:8000/docs</b> for the live contract. The endpoint list above reflects route decorators in app/api/.", "Smallg")]
    make_doc(ROOT/"docs"/"API_Documentation.pdf", "CropShield AI API Documentation",
             "FastAPI route inventory and representative JSON contracts", story)


def generate_dataset():
    sample_path = ROOT/"data"/"sample"/"sample_crop_data.csv"
    with sample_path.open(encoding="utf-8", newline="") as f:
        header = f.readline().strip().split(",")
    fields = [
        ["Crop", "Crop variety label used in advisory and model features."],
        ["Crop_Year", "Year field associated with the generated case."],
        ["Season", "Agricultural season category."],
        ["State", "Indian state/region category."],
        ["Area", "Cultivated area feature."], ["Production", "Production outcome feature."],
        ["Yield", "Yield outcome used as regression target."],
        ["Fertilizer, Pesticide", "Agricultural input quantities/features."],
        ["N, P, K", "Soil macronutrient values."],
        ["pH, Temperature, Rainfall, Humidity", "Soil and climate features."],
    ]
    story = [para("Dataset identity and provenance", "H1g"), para(
        "The operational sample is <b>data/sample/sample_crop_data.csv</b>; the application also uses "
        "<b>data/processed/processed_data.csv</b>. Source code marks the 1,500-row sample as synthetic test data. "
        "It is generated inside this project and has no external dataset link or verified field provenance. "
        "Do not present it as an official government or surveyed dataset."),
        grid([["Attribute", "Value"], ["Dataset name", "CropShield AI synthetic crop case dataset"],
              ["External source / URL", "None; locally generated synthetic test data."],
              ["Format", "CSV, comma-separated UTF-8 text"],
              ["Rows", "1,500 in the sample and processed dataset (verify locally if files are regenerated)."],
              ["Purpose", "Hybrid case retrieval, crop advisory context, model training and evaluation."],
              ["Crop labels", "12 crop categories"], ["Region labels", "15 states in saved model metadata"],
              ["Season labels", "Kharif, Rabi, Summer, Whole Year"],
              ["Raw-to-processed", "Processed data adds NPK_Total, NPK nutrient ratios, Rain_Temp_Ratio and Fertilizer_Per_Area."],
              ["Missing values", "The current processed file's saved admin inspection reports zero missing values; re-check after replacing inputs."],
              ["License / field consent", "No external license or field-consent claim applies; generated test data."],
             ], widths=[42*mm, 132*mm]), para("Core fields", "H1g"),
        grid([["Field", "Meaning"]] + fields, widths=[58*mm, 116*mm]),
        para("Preprocessing and use", "H1g"), para(
        "The preprocessing pipeline cleans and normalizes the CSV, handles feature conversions and records data quality. "
        "The processed file contains engineered ratios and per-area fertilizer values. Model training uses Crop, Season and State "
        "as categorical variables; N, P, K, pH, temperature, rainfall, humidity, fertilizer and pesticide as numeric variables. "
        "Dataset path settings and sample values are in app/config/settings.py and data/; the files were intentionally not moved."),
        para("Limitations", "H1g"), para(
        "Synthetic distributions do not encode real regional agronomic variation. The model's test metrics measure fit to a held-out "
        "split from generated data, not expected error in farmers' fields. Replace with appropriately licensed, quality-checked local data "
        "and retrain before operational decision-making.")]
    make_doc(ROOT/"docs"/"Dataset_Details.pdf", "CropShield AI Dataset Details",
             "Provenance, schema, preprocessing and responsible interpretation", story)


def generate_eval():
    retrieval = json.loads((ROOT/"evaluation/reports/retrieval_evaluation_report.json").read_text(encoding="utf-8"))
    ml = json.loads((ROOT/"evaluation/reports/ml_metrics.json").read_text(encoding="utf-8"))
    overall = json.loads((ROOT/"evaluation/reports/evaluation_report.json").read_text(encoding="utf-8"))
    r = retrieval["retrieval_metrics"]
    y = ml["yield_regressor"]
    c = ml["suitability_classifier"]
    live_report_present = any(ROOT.glob("evaluation/reports/*ragas*.json")) or any(ROOT.glob("evaluation/reports/*deepeval*.json"))
    story = [para("Evidence and scope", "H1g"), para(
        "This report summarizes existing local JSON artifacts inspected on 10 October 2026. It does not represent a new run "
        "unless explicitly stated. Saved RAGAS/DeepEval live judge score artifacts were not found; these provider-dependent metrics "
        "are pending successful execution with a reachable, funded compatible endpoint." if not live_report_present else
        "This report summarizes existing local JSON artifacts inspected on 10 October 2026."),
        para("Retrieval benchmark (saved run)", "H1g"), grid([
            ["Metric", "Saved value", "Interpretation"],
            ["Benchmark", f"{r['total_benchmark_queries']} labeled queries; timestamp {retrieval.get('evaluation_timestamp','not recorded')}", "Historical saved benchmark; not rerun for this document."],
            ["Precision@1 / @3 / @5", f"{r['precision_at_1']} / {r['precision_at_3']} / {r['precision_at_5']}", "Crop-label precision at each cutoff."],
            ["Recall@5", str(r["recall_at_5"]), "Fraction of expected relevant crop labels retrieved by rank 5."],
            ["MRR", str(r["mrr"]), "Mean reciprocal rank of first relevant result."],
            ["Hit rate@5", str(r["hit_rate_at_5"]), "Share of queries with at least one relevant result among top five."],
            ["Duration", f"{retrieval.get('evaluation_duration_seconds','not recorded')} seconds", "Recorded duration for the saved run."],
        ], widths=[38*mm, 50*mm, 92*mm]),
        para("Machine learning (saved held-out split)", "H1g"), grid([
            ["Model / measure", "Value", "Evaluation set"],
            ["RandomForestRegressor R²", str(y["r2_score"]), f"{y['test_samples']} held-out samples"],
            ["Yield MAE", str(y["mae"]), "Yield target units follow the dataset; synthetic data."],
            ["Yield RMSE", str(y["rmse"]), "Same held-out split."],
            ["RandomForestClassifier accuracy", str(c["accuracy"]), f"{c['test_samples']} held-out samples"],
            ["Suitability precision / recall / F1", f"{c['precision']} / {c['recall']} / {c['f1_score']}", "Macro/aggregate behavior depends on saved evaluation implementation."],
        ], widths=[59*mm, 43*mm, 78*mm]),
        para("LLM evaluation", "H1g"), para(
        "<b>RAGAS: pending.</b> <b>DeepEval: pending.</b> The saved evaluation UI/runtime reported judge provider connectivity/credit errors; "
        "per-query RAGAS and DeepEval scores must not be inferred from retrieval ranking metrics. Current saved report artifacts include "
        f"an older aggregate judge summary dated {overall.get('evaluation_timestamp','unknown')} with overall score "
        f"{overall.get('llm_judge_metrics',{}).get('average_overall_score','not recorded')} and groundedness "
        f"{overall.get('llm_judge_metrics',{}).get('average_groundedness','not recorded')}. This is retained as a historical artifact only; "
        "its provider configuration and run details were not independently revalidated here."),
        para("Tests", "H1g"), para("Verification run on 10 October 2026: 30 tests passed. Pytest emitted one non-blocking cache write warning because the sandbox denied access to its cache nodeids file. Re-run the command in README.md for a fresh result."),
        para("How to interpret", "H1g"), bullet("Retrieval labels measure crop-label matching, not expert-validated relevance or answer correctness."),
        bullet("The dataset is synthetic; its metrics are development signals, not evidence of field accuracy."),
        bullet("Run a fresh local retrieval benchmark and a funded/reachable LLM judge before presenting live RAGAS or DeepEval scores."),
    ]
    make_doc(ROOT/"docs"/"Evaluation_Report.pdf", "CropShield AI Evaluation Report",
             "Saved evaluation evidence and explicitly pending results", story)


def make_pptx():
    saved_retrieval = json.loads((ROOT/"evaluation/reports/retrieval_evaluation_report.json").read_text(encoding="utf-8"))["retrieval_metrics"]
    saved_ml = json.loads((ROOT/"evaluation/reports/ml_metrics.json").read_text(encoding="utf-8"))
    yield_r2 = saved_ml["yield_regressor"]["r2_score"]
    slides = [
        ("CropShield AI", ["AI-powered agriculture crop advisory assistant", "Capstone project review | October 2026"]),
        ("Problem and users", ["Farm decisions combine crop, soil, climate, season and input conditions.", "Historical cases are difficult to search consistently.", "Primary users: agronomists, extension officers and agricultural decision-makers."]),
        ("Business need", ["Find comparable crop cases quickly.", "Bring recommendations, yield estimates and risk context into one workflow.", "Show evidence and limitations so users can review advice responsibly."]),
        ("Solution overview", ["FastAPI backend with browser dashboard and optional Streamlit client.", "Hybrid case retrieval and modular advisory agents.", "Random Forest crop suitability and yield models.", "Authentication, admin tools, feedback and evaluation features."]),
        ("Architecture", ["CSV cases -> preprocessing -> local vectors and FAISS + keyword index.", "Query -> guardrails -> classifier -> hybrid retriever -> recommendation/risk/yield/impact.", "FastAPI -> HTML/CSS/JavaScript SPA; optional Streamlit client.", "SQLite account store; JSON feedback and evaluation artifacts."]),
        ("Data flow and retrieval", ["1,500-row sample is locally generated synthetic data.", "Row-based case indexing with crop/state/season metadata.", "Local HashingVectorizer + seeded projection; FAISS similarity plus lexical evidence.", "Labeled benchmark: Precision@K, Recall@5, MRR and Hit Rate@5."]),
        ("Technology stack", ["Python 3.12, FastAPI, Pydantic, Uvicorn.", "FAISS CPU, scikit-learn, NumPy, pandas.", "RandomForestRegressor and RandomForestClassifier.", "Optional OpenAI-compatible LLM judge; credentials from environment.", "No ChromaDB implementation was found in the inspected source."]),
        ("Agent workflow and demo", ["Validate/scope query -> classify and extract conditions.", "Retrieve cases -> recommend and analyze risk/yield/impact -> validate response.", "Demo: ask for crop options with state, season, rainfall and pH; inspect evidence and caveats.", "Yield page: update agronomic inputs and request model estimate."]),
        ("Evaluation results", [f"Saved 20-query retrieval run: P@1 {saved_retrieval['precision_at_1']:.2f}; P@5 {saved_retrieval['precision_at_5']:.2f}; Recall@5 {saved_retrieval['recall_at_5']:.4f}; MRR {saved_retrieval['mrr']:.3f}.", f"Saved RandomForest yield R2: {yield_r2:.4f} on 300 held-out synthetic rows.", "Live RAGAS/DeepEval runs depend on an accessible, funded judge endpoint.", "This deck avoids presenting unavailable judge scores as successful results."]),
        ("Challenges and limitations", ["Synthetic data limits real-world validity.", "LLM judge latency, endpoint errors and credits affect availability.", "Retrieval relevance labels cover a small benchmark and crop-label match only.", "Local file persistence and auth need production operations hardening."]),
        ("Learnings and next steps", ["Keep data provenance and evaluation status explicit.", "Validate models on licensed, representative, expert-reviewed field data.", "Expand labeled query sets and rerun retrieval evaluations.", "Configure judge provider, verify RAGAS/DeepEval runs, monitor and report reproducibly."]),
    ]
    # Small helper keeps slide content independent from credentials or .env.
    pptx = ROOT/"presentation"/"Project_Presentation.pptx"
    pptx.parent.mkdir(parents=True, exist_ok=True)
    def esc(x): return escape(str(x), {"'": "&apos;", '"': "&quot;"})
    # Use valid non-visual shape properties (spid/name/textbox) for each slide.
    def fixed_shape(sid, name, x, y, cx, cy, text, size, color, bold=False, fill=None):
        fillxml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
        runs = ''.join(f'<a:p><a:pPr/><a:r><a:rPr lang="en-US" sz="{size}" b="{1 if bold else 0}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Aptos"/></a:rPr><a:t>{esc(line)}</a:t></a:r></a:p>' for line in text.split("\n"))
        return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{esc(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fillxml}<a:ln><a:noFill/></a:ln></p:spPr>'
                f'<p:txBody><a:bodyPr wrap="square" lIns="140000" rIns="140000" tIns="100000" bIns="100000"/><a:lstStyle/>{runs}</p:txBody></p:sp>')
    def slide_xml(index, title, points):
        body = "\\n".join("- " + p for p in points)
        tree = ('<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                + fixed_shape(2,"Background",0,0,12192000,6858000,"",1800,"FFFFFF",fill="06190F")
                + fixed_shape(3,"Accent",0,0,260000,6858000,"",1800,"FFFFFF",fill="18B56A")
                + fixed_shape(4,"Title",520000,400000,11000000,900000,title,2900,"FFFFFF",True)
                + fixed_shape(5,"Body",650000,1550000,10800000,4450000,body,1850,"C9E7D5")
                + fixed_shape(6,"Footer",520000,6300000,10000000,350000,f"CropShield AI | Capstone review     {index:02d}",1000,"7FAB91"))
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
                f'<p:cSld><p:spTree>{tree}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')
    types = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
             '<Default Extension="xml" ContentType="application/xml"/>',
             '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>']
    rels = []
    ids = []
    for i, _ in enumerate(slides,1):
        types.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
        ids.append(f'<p:sldId id="{255+i}" r:id="rId{i}"/>')
    pres_rel_id = len(slides)+1
    rels.append(f'<Relationship Id="rId{pres_rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>')
    types.append('<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>')
    types.append('<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>')
    types.append('<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>')
    with zipfile.ZipFile(pptx,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'+''.join(types)+'</Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>')
        z.writestr("ppt/presentation.xml", '<?xml version="1.0" encoding="UTF-8"?><p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId'+str(pres_rel_id)+'"/></p:sldMasterIdLst><p:sldIdLst>'+''.join(ids)+'</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="wide"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>')
        z.writestr("ppt/_rels/presentation.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(rels)+'</Relationships>')
        z.writestr("ppt/slideMasters/slideMaster1.xml", '<?xml version="1.0" encoding="UTF-8"?><p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>')
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>')
        z.writestr("ppt/slideLayouts/slideLayout1.xml", '<?xml version="1.0" encoding="UTF-8"?><p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>')
        z.writestr("ppt/theme/theme1.xml", '<?xml version="1.0" encoding="UTF-8"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="CropShield"><a:themeElements><a:clrScheme name="CropShield"><a:dk1><a:srgbClr val="06190F"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="143A2A"/></a:dk2><a:lt2><a:srgbClr val="E8F5ED"/></a:lt2><a:accent1><a:srgbClr val="18B56A"/></a:accent1><a:accent2><a:srgbClr val="C9E7D5"/></a:accent2><a:accent3><a:srgbClr val="08794D"/></a:accent3><a:accent4><a:srgbClr val="F3C969"/></a:accent4><a:accent5><a:srgbClr val="4788B8"/></a:accent5><a:accent6><a:srgbClr val="53665C"/></a:accent6><a:hlink><a:srgbClr val="18B56A"/></a:hlink><a:folHlink><a:srgbClr val="08794D"/></a:folHlink></a:clrScheme><a:fontScheme name="CropShield"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme><a:fmtScheme name="CropShield"><a:fillStyleLst><a:solidFill><a:schemeClr val="accent1"/></a:solidFill></a:fillStyleLst><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>')
        for i, (title, points) in enumerate(slides,1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml(i,title,points))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>')
    with zipfile.ZipFile(pptx) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]) == len(slides)


if __name__ == "__main__":
    generate_architecture()
    generate_design()
    generate_api()
    generate_dataset()
    generate_eval()
    make_pptx()
    print("Generated four submission PDFs and the 11-slide presentation.")
