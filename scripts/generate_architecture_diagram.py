"""
Generate High-Resolution Architecture Diagram for AI-Powered Agriculture Crop Advisory Assistant.
Saves PNG and PDF in docs/
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_diagram():
    os.makedirs("docs", exist_ok=True)
    
    # Setup figure
    fig, ax = plt.subplots(figsize=(18, 12), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#0b0f19")

    # Title
    ax.text(50, 97, "AI-Powered Agriculture Crop Advisory Assistant", 
            ha="center", va="center", fontsize=20, fontweight="bold", color="#38bdf8")
    ax.text(50, 94, "Complete End-to-End System Architecture: Data -> RAG + ML -> Multi-Agent -> Guardrails -> Evaluation", 
            ha="center", va="center", fontsize=11, color="#94a3b8")

    def draw_box(x, y, w, h, title, subtitle, color, border_color="#38bdf8", text_color="#f8fafc"):
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.5,rounding_size=1.0",
            facecolor=color, edgecolor=border_color, linewidth=1.5, alpha=0.9
        )
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.62, title, ha="center", va="center", fontsize=9, fontweight="bold", color=text_color)
        ax.text(x + w/2, y + h*0.30, subtitle, ha="center", va="center", fontsize=7.5, color="#cbd5e1")

    def draw_arrow(x1, y1, x2, y2, color="#64748b", text=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.8, shrinkA=3, shrinkB=3))
        if text:
            ax.text((x1+x2)/2, (y1+y2)/2 + 1.2, text, ha="center", va="center", fontsize=7, color="#94a3b8")

    # Row 1: Ingestion & Storage (y: 80 - 88)
    ax.text(5, 89, "1. DATA INGESTION & FEATURE ENGINEERING", fontsize=9, fontweight="bold", color="#38bdf8")
    draw_box(4, 79, 16, 8, "Raw Dataset", "data/raw/agriculture.csv", "#1e293b", "#38bdf8")
    draw_box(24, 79, 16, 8, "Preprocessing", "Cleaning, Imputation, Norm", "#1e293b", "#38bdf8")
    draw_box(44, 79, 16, 8, "Case Construction", "Structured JSON Documents", "#1e293b", "#38bdf8")
    draw_box(64, 79, 15, 8, "FAISS Index", "Dense TF-IDF/SVD Vector", "#1e3a5f", "#60a5fa")
    draw_box(82, 79, 15, 8, "Keyword Index", "Sparse BM25-style Tokens", "#1e3a5f", "#60a5fa")

    draw_arrow(20, 83, 24, 83)
    draw_arrow(40, 83, 44, 83)
    draw_arrow(60, 83, 64, 83)
    draw_arrow(60, 83, 82, 83)

    # ML Training branch
    draw_box(24, 66, 16, 7.5, "ML Suitability", "RandomForestClassifier", "#2e1065", "#c084fc")
    draw_box(44, 66, 16, 7.5, "ML Yield Regressor", "RandomForestRegressor + CI", "#2e1065", "#c084fc")
    draw_arrow(32, 79, 32, 73.5)
    draw_arrow(32, 73.5, 44, 70)

    # User & API Layer (Left: x 4 to 20, y: 35 to 55)
    ax.text(5, 59, "2. CLIENT & API LAYER", fontsize=9, fontweight="bold", color="#fbbf24")
    draw_box(4, 49, 16, 8, "Web Dashboard", "SPA (HTML/CSS/JS)", "#78350f", "#fbbf24")
    draw_box(4, 37, 16, 8, "FastAPI Gateway", "REST Endpoints & Validation", "#78350f", "#fbbf24")
    draw_arrow(12, 49, 12, 45, "#fbbf24", "HTTP")
    draw_arrow(12, 45, 12, 49, "#fbbf24")

    # Guardrails
    ax.text(26, 59, "3. MULTI-STAGE GUARDRAILS", fontsize=9, fontweight="bold", color="#f87171")
    draw_box(24, 43, 16, 8, "Input Guardrail", "Injection, Scope & Range", "#7f1d1d", "#f87171")
    draw_arrow(20, 41, 24, 47, "#f87171", "Query")

    # Multi-Agent Pipeline (Middle: x 44 to 78, y: 15 to 55)
    ax.text(45, 59, "4. 8-STAGE DETERMINISTIC MULTI-AGENT PIPELINE", fontsize=9, fontweight="bold", color="#34d399")
    draw_box(44, 49, 16, 7, "Agent 1: Classifier", "Intent & Parameter Extraction", "#064e3b", "#34d399")
    draw_box(63, 49, 16, 7, "Agent 2: Hybrid RAG", "FAISS Dense + Sparse TF-IDF", "#064e3b", "#34d399")
    draw_box(82, 49, 15, 7, "Agent 3: Filter & Rerank", "RRF Fusion + Agro-Scoring", "#064e3b", "#34d399")

    draw_box(44, 38, 16, 7, "Agent 4: Recommender", "Grounded Crop Viability", "#064e3b", "#34d399")
    draw_box(63, 38, 16, 7, "Agent 5: Risk Agent", "Drought, Salinity & Extremes", "#064e3b", "#34d399")
    draw_box(82, 38, 15, 7, "Agent 6: Yield Agent", "ML Regressor + 80% CI Bounds", "#064e3b", "#34d399")

    draw_box(44, 27, 16, 7, "Agent 7: Impact Analysis", "Feature Importance & Sensitivity", "#064e3b", "#34d399")
    draw_box(63, 27, 16, 7, "Agent 8: LLM-as-Judge", "Groundedness Verification", "#064e3b", "#34d399")
    draw_box(82, 27, 15, 7, "Output Guardrails", "Disclaimer & Safety Check", "#7f1d1d", "#f87171")

    # Agent Flow Arrows
    draw_arrow(40, 47, 44, 52, "#34d399")
    draw_arrow(60, 52, 63, 52, "#34d399")
    draw_arrow(79, 52, 82, 52, "#34d399")
    
    draw_arrow(89, 49, 89, 45, "#34d399")
    draw_arrow(82, 41, 79, 41, "#34d399")
    draw_arrow(63, 41, 60, 41, "#34d399")
    
    draw_arrow(52, 38, 52, 34, "#34d399")
    draw_arrow(60, 30, 63, 30, "#34d399")
    draw_arrow(79, 30, 82, 30, "#34d399")

    # Connect Indexes & Models to Agents
    draw_arrow(71, 79, 71, 56, "#60a5fa", "RAG Evidence")
    draw_arrow(89, 79, 89, 56, "#60a5fa")
    draw_arrow(52, 66, 85, 45, "#c084fc", "ML Models")

    # Row 4: Final Response, Feedback, Evaluation (Bottom: y: 8 to 20)
    ax.text(5, 23, "5. ADVISORY RESPONSE, FEEDBACK & CONTINUOUS BENCHMARKING", fontsize=9, fontweight="bold", color="#e879f9")
    draw_box(4, 11, 20, 8, "Structured Advisory", "Section 45 Agronomic Response", "#1e293b", "#38bdf8")
    draw_box(28, 11, 18, 8, "Feedback Store", "data/feedback/feedback.json", "#3b0764", "#e879f9")
    draw_box(50, 11, 22, 8, "Evaluation Benchmark", "Precision@k, Recall@k, MRR, R^2", "#3b0764", "#e879f9")
    draw_box(76, 11, 21, 8, "Evaluation Reports", "reports/evaluation_report.md", "#3b0764", "#e879f9")

    draw_arrow(82, 27, 24, 15, "#38bdf8", "Advisory Payload")
    draw_arrow(24, 15, 28, 15, "#e879f9", "User Ratings")
    draw_arrow(46, 15, 50, 15, "#e879f9")
    draw_arrow(72, 15, 76, 15, "#e879f9")
    draw_arrow(14, 19, 12, 37, "#38bdf8", "Deliver to User")

    # Legend / Key in bottom strip
    ax.text(50, 3, "[Legend]  Light Blue: Data/RAG | Purple: ML Models | Green: Multi-Agents | Red: Guardrails | Amber: UI/API | Pink: Evaluation", 
            ha="center", va="center", fontsize=8, color="#64748b")

    plt.tight_layout()
    plt.savefig("docs/architecture.png", dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.savefig("docs/architecture.pdf", facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print("Architecture diagram generated at docs/architecture.png and docs/architecture.pdf")

if __name__ == "__main__":
    generate_diagram()
