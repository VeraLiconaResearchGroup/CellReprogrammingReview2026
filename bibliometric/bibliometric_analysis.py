#!/usr/bin/env python3
"""
Bibliometric Analysis: Computational Approaches in Cell Reprogramming

This script queries NCBI PubMed and PMC to assess the adoption of computational 
approaches for target identification in cell reprogramming literature.

Usage:
    python bibliometric_analysis.py [--email YOUR_EMAIL] [--start-year 2014] [--end-year 2024]

Requirements:
    pip install biopython pandas matplotlib seaborn

Author: Vera-Licona Lab
Purpose: Supplementary analysis for cell reprogramming computational methods review
"""

import argparse
import time
import sys
from datetime import datetime

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from Bio import Entrez
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install biopython pandas matplotlib seaborn")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_EMAIL = "your.email@institution.edu"
DEFAULT_START_YEAR = 2014
DEFAULT_END_YEAR = 2026  # bumped from 2024 in the 51 -> 57 extension (2026-05-27)
                          # so PubMed/PMC counts capture the 2025-2026 publications
                          # of REVIVE, CANDiT, SwitchTFI, Atlas-guided, REPROcode, TRAPT.
SLEEP_TIME = 0.4  # Seconds between queries (NCBI rate limit)


# =============================================================================
# Query Definitions
# =============================================================================

QUERIES = {
    "baseline": {
        "Total cell reprogramming": "cell reprogramming",
    },
    "tier1_broad": {
        "Any computational/bioinformatics": "(cell reprogramming) AND (computational OR bioinformatics OR in silico OR algorithm)",
        "Gene regulatory network + reprogramming": "(cell reprogramming OR cell fate) AND (gene regulatory network OR GRN) AND (analysis OR model)",
        "Boolean/logical models": "(Boolean network OR logical model) AND (cell fate OR reprogramming OR differentiation)",
    },
    "tier2_target_id": {
        "Computational + prediction + reprogramming": "computational AND prediction AND reprogramming",
        "Computational + identify + reprogramming": "computational AND identify AND reprogramming",
        "Computational + prediction + TF": "(cell reprogramming OR transdifferentiation OR direct conversion) AND (computational prediction OR in silico prediction OR network model) AND (transcription factor OR reprogramming factor OR target gene)",
        "Network-based target prediction": "(network model OR network analysis) AND (identify target OR predict target) AND (reprogramming OR cell fate conversion)",
        "Bioinformatics-guided factor selection": "(bioinformatics analysis OR computational screening) AND (reprogramming factor OR conversion factor OR transcription factor) AND (cell reprogramming OR cell conversion)",
    },
    "tier2_phrases": {
        "Guided by computational analysis": "(guided by computational OR based on computational analysis OR computationally guided) AND reprogramming",
        "Computational screen/screening": "(computational screen OR computational screening OR in silico screen) AND reprogramming",
        "Predicted transcription factors": "(predicted transcription factor OR computationally predicted TF) AND reprogramming",
        "Algorithm + identify + reprog factor": "algorithm AND (identify OR predict) AND (reprogramming factor OR conversion factor)",
    },
    "tier3_tools": {
        "CellNet": "CellNet AND (reprogramming OR iPSC OR differentiation)",
        "Mogrify": "Mogrify AND reprogramming",
        "CellOracle": "CellOracle",
        "ANANSE": "ANANSE AND (reprogramming OR transcription factor)",
        "SCENIC": "SCENIC AND (cell fate OR differentiation OR reprogramming)",
        "OncoTreat/VIPER": "(OncoTreat OR VIPER master regulator)",
        "Boolean network control": "Boolean network AND control AND (cell fate OR reprogramming)",
        # ---- 6 methods added in the 51 -> 57 corpus extension (2026-05-27) ----
        # Each query disambiguates the tool name from generic English usage so
        # the count reflects citations of the method, not unrelated papers.
        # REVIVE is a common English word and a brand name for many things
        # (clinical trials, supplements, devices), so the query co-requires
        # one of three distinctive markers from the paper's title/abstract:
        # "rejuvenating perturbations" (the paper's central phrase), "aging
        # clock" (its core mathematical object), or "fibroblast aging" (its
        # primary biological context). Tightened in two rounds on 2026-05-21
        # after a one-off probe (35 -> 44 -> 4 with progressively tighter
        # variants); "OR reprogramming" was dropped because it caused a
        # ~10x over-match against unrelated clinical-trial REVIVE papers.
        "REVIVE": "REVIVE AND (rejuvenating perturbations OR aging clock OR fibroblast aging)",
        "CANDiT": "CANDiT AND (differentiation OR colorectal OR CRC OR BoNE OR CDX2)",
        "SwitchTFI": "SwitchTFI",
        "Atlas-guided/Taiji2": "(Taiji2 OR \"Taiji v2\" OR \"atlas-guided\") AND (T cell OR transcription factor OR reprogramming)",
        "REPROcode": "REPROcode AND (reprogramming OR transcription factor OR dendritic OR immune)",
        "TRAPT": "TRAPT AND (transcriptional regulator OR transcription regulator OR ChIP OR epigenomic OR Cistrome)",
    },
}

PMC_QUERIES = {
    "Total cell reprogramming": "cell reprogramming",
    "Computational + prediction + reprogramming": "computational AND prediction AND reprogramming",
    "Computational + identify + reprogramming": "computational AND identify AND reprogramming",
    "Guided by computational + reprogramming": "(guided by computational OR based on computational analysis OR computationally guided) AND reprogramming",
    "In silico + identify/predict + TF + reprog": "(in silico) AND (identify OR predict) AND (transcription factor) AND reprogramming",
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_count(query, db="pubmed", mindate=None, maxdate=None):
    """Query NCBI database and return count of matching articles."""
    try:
        handle = Entrez.esearch(
            db=db,
            term=query,
            mindate=mindate,
            maxdate=maxdate,
            datetype="pdat",
            rettype="count"
        )
        record = Entrez.read(handle)
        handle.close()
        time.sleep(SLEEP_TIME)
        return int(record["Count"])
    except Exception as e:
        print(f"Error querying {db}: {e}")
        return None


def query_year_range(query, db="pubmed", start_year=DEFAULT_START_YEAR, end_year=DEFAULT_END_YEAR):
    """Run a query for each year and return results as DataFrame."""
    results = []
    for year in range(start_year, end_year + 1):
        count = get_count(query, db=db, mindate=str(year), maxdate=str(year))
        results.append({"Year": year, "Count": count})
        print(f"  {year}: {count}")
    return pd.DataFrame(results)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# =============================================================================
# Main Analysis
# =============================================================================

def run_analysis(email, start_year, end_year, output_dir="."):
    """Run the complete bibliometric analysis."""
    
    # Set up Entrez
    Entrez.email = email
    
    print_section("BIBLIOMETRIC ANALYSIS: COMPUTATIONAL APPROACHES IN CELL REPROGRAMMING")
    print(f"\nAnalysis Period: {start_year}-{end_year}")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Email: {email}")
    
    # =========================================================================
    # Part 1: PubMed Analysis
    # =========================================================================
    print_section("PART 1: PUBMED ANALYSIS (Title/Abstract)")
    
    pubmed_results = {}
    for category, queries in QUERIES.items():
        print(f"\n--- {category.upper()} ---")
        pubmed_results[category] = {}
        for name, query in queries.items():
            count = get_count(query, db="pubmed", mindate=str(start_year), maxdate=str(end_year))
            pubmed_results[category][name] = count
            print(f"{name}: {count:,}")
    
    baseline_pubmed = pubmed_results["baseline"]["Total cell reprogramming"]
    
    # =========================================================================
    # Part 2: PubMed Year-by-Year
    # =========================================================================
    print_section("PART 2: PUBMED YEAR-BY-YEAR TRENDS")
    
    print("\nTotal cell reprogramming:")
    total_by_year = query_year_range("cell reprogramming", db="pubmed", start_year=start_year, end_year=end_year)
    total_by_year.columns = ["Year", "Total"]
    
    print("\nComputational + prediction + reprogramming:")
    pred_by_year = query_year_range("computational AND prediction AND reprogramming", db="pubmed", start_year=start_year, end_year=end_year)
    pred_by_year.columns = ["Year", "Comp_Predict"]
    
    print("\nComputational + identify + reprogramming:")
    ident_by_year = query_year_range("computational AND identify AND reprogramming", db="pubmed", start_year=start_year, end_year=end_year)
    ident_by_year.columns = ["Year", "Comp_Identify"]
    
    pubmed_trend_df = total_by_year.merge(pred_by_year, on="Year").merge(ident_by_year, on="Year")
    pubmed_trend_df["Pct_Predict"] = (pubmed_trend_df["Comp_Predict"] / pubmed_trend_df["Total"] * 100).round(2)
    pubmed_trend_df["Pct_Identify"] = (pubmed_trend_df["Comp_Identify"] / pubmed_trend_df["Total"] * 100).round(2)
    
    print("\nPubMed Year-by-Year Summary:")
    print(pubmed_trend_df.to_string(index=False))
    
    # =========================================================================
    # Part 3: PMC Analysis
    # =========================================================================
    print_section("PART 3: PMC ANALYSIS (Full-Text)")
    
    pmc_results = {}
    for name, query in PMC_QUERIES.items():
        count = get_count(query, db="pmc", mindate=str(start_year), maxdate=str(end_year))
        pmc_results[name] = count
        print(f"{name}: {count:,}")
    
    baseline_pmc = pmc_results["Total cell reprogramming"]
    
    # =========================================================================
    # Part 4: PMC Year-by-Year
    # =========================================================================
    print_section("PART 4: PMC YEAR-BY-YEAR TRENDS")
    
    print("\nTotal cell reprogramming (PMC):")
    pmc_total_by_year = query_year_range("cell reprogramming", db="pmc", start_year=start_year, end_year=end_year)
    pmc_total_by_year.columns = ["Year", "Total"]
    
    print("\nComputational + prediction + reprogramming (PMC):")
    pmc_pred_by_year = query_year_range("computational AND prediction AND reprogramming", db="pmc", start_year=start_year, end_year=end_year)
    pmc_pred_by_year.columns = ["Year", "Comp_Predict"]
    
    print("\nComputational + identify + reprogramming (PMC):")
    pmc_ident_by_year = query_year_range("computational AND identify AND reprogramming", db="pmc", start_year=start_year, end_year=end_year)
    pmc_ident_by_year.columns = ["Year", "Comp_Identify"]
    
    pmc_trend_df = pmc_total_by_year.merge(pmc_pred_by_year, on="Year").merge(pmc_ident_by_year, on="Year")
    pmc_trend_df["Pct_Predict"] = (pmc_trend_df["Comp_Predict"] / pmc_trend_df["Total"] * 100).round(1)
    pmc_trend_df["Pct_Identify"] = (pmc_trend_df["Comp_Identify"] / pmc_trend_df["Total"] * 100).round(1)
    
    print("\nPMC Year-by-Year Summary:")
    print(pmc_trend_df.to_string(index=False))
    
    # =========================================================================
    # Part 5: Save Results
    # =========================================================================
    print_section("PART 5: SAVING RESULTS")
    
    # Save CSVs
    pubmed_trend_df.to_csv(f"{output_dir}/pubmed_trend_{start_year}_{end_year}.csv", index=False)
    pmc_trend_df.to_csv(f"{output_dir}/pmc_trend_{start_year}_{end_year}.csv", index=False)
    print(f"Saved: pubmed_trend_{start_year}_{end_year}.csv")
    print(f"Saved: pmc_trend_{start_year}_{end_year}.csv")
    
    # =========================================================================
    # Part 6: Generate Plots
    # =========================================================================
    print_section("PART 6: GENERATING PLOTS")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Computational Approaches in Cell Reprogramming ({start_year}-{end_year})", 
                 fontsize=14, fontweight='bold')
    colors = sns.color_palette("Set2")
    
    # Plot 1: PubMed total
    ax1 = axes[0, 0]
    ax1.plot(pubmed_trend_df["Year"], pubmed_trend_df["Total"], 'o-', color=colors[0], linewidth=2)
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Number of Papers")
    ax1.set_title("PubMed: Total Cell Reprogramming Papers")
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: PubMed percentages
    ax2 = axes[0, 1]
    ax2.plot(pubmed_trend_df["Year"], pubmed_trend_df["Pct_Predict"], 's-', 
             label="Comp+Predict", color=colors[1], linewidth=2)
    ax2.plot(pubmed_trend_df["Year"], pubmed_trend_df["Pct_Identify"], '^-', 
             label="Comp+Identify", color=colors[2], linewidth=2)
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Percentage (%)")
    ax2.set_title("PubMed: Computational Target ID (% of total)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 5)
    
    # Plot 3: PMC counts
    ax3 = axes[1, 0]
    ax3.plot(pmc_trend_df["Year"], pmc_trend_df["Total"], 'o-', label="Total", color=colors[0], linewidth=2)
    ax3.plot(pmc_trend_df["Year"], pmc_trend_df["Comp_Predict"], 's-', 
             label="Comp+Predict", color=colors[1], linewidth=2)
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Number of Papers")
    ax3.set_title("PMC Full-Text: Absolute Counts")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: PMC percentages
    ax4 = axes[1, 1]
    ax4.plot(pmc_trend_df["Year"], pmc_trend_df["Pct_Predict"], 's-', 
             label="Comp+Predict", color=colors[1], linewidth=2)
    ax4.plot(pmc_trend_df["Year"], pmc_trend_df["Pct_Identify"], '^-', 
             label="Comp+Identify", color=colors[2], linewidth=2)
    ax4.set_xlabel("Year")
    ax4.set_ylabel("Percentage (%)")
    ax4.set_title("PMC Full-Text: Computational Mentions (% of total)")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = f"{output_dir}/bibliometric_analysis_{start_year}_{end_year}.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_path}")
    plt.close()
    
    # =========================================================================
    # Part 7: Final Summary
    # =========================================================================
    print_section("FINAL SUMMARY")
    
    print(f"\nBaseline Counts:")
    print(f"  PubMed: {baseline_pubmed:,} cell reprogramming papers")
    print(f"  PMC:    {baseline_pmc:,} cell reprogramming papers")
    
    pred_pubmed = pubmed_results["tier2_target_id"]["Computational + prediction + reprogramming"]
    ident_pubmed = pubmed_results["tier2_target_id"]["Computational + identify + reprogramming"]
    pred_pmc = pmc_results["Computational + prediction + reprogramming"]
    ident_pmc = pmc_results["Computational + identify + reprogramming"]
    
    print(f"\nKey Metrics:")
    print(f"  Comp+Predict (PubMed): {pred_pubmed:,} ({pred_pubmed/baseline_pubmed*100:.1f}%)")
    print(f"  Comp+Predict (PMC):    {pred_pmc:,} ({pred_pmc/baseline_pmc*100:.1f}%)")
    print(f"  Comp+Identify (PubMed): {ident_pubmed:,} ({ident_pubmed/baseline_pubmed*100:.1f}%)")
    print(f"  Comp+Identify (PMC):    {ident_pmc:,} ({ident_pmc/baseline_pmc*100:.1f}%)")
    
    print(f"\nInterpretation:")
    print(f"  • PubMed (~1-3%): Papers where computational target ID is PRIMARY FOCUS")
    print(f"  • PMC (~30-40%): Papers that MENTION computational approaches in full text")
    print(f"  • The gap suggests awareness is high but primary adoption is low")
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    
    return {
        "pubmed_results": pubmed_results,
        "pmc_results": pmc_results,
        "pubmed_trend": pubmed_trend_df,
        "pmc_trend": pmc_trend_df,
    }


# =============================================================================
# Command Line Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Bibliometric analysis of computational approaches in cell reprogramming literature"
    )
    parser.add_argument(
        "--email", 
        type=str, 
        default=DEFAULT_EMAIL,
        help="Your email for NCBI queries (required by NCBI)"
    )
    parser.add_argument(
        "--start-year", 
        type=int, 
        default=DEFAULT_START_YEAR,
        help=f"Start year for analysis (default: {DEFAULT_START_YEAR})"
    )
    parser.add_argument(
        "--end-year", 
        type=int, 
        default=DEFAULT_END_YEAR,
        help=f"End year for analysis (default: {DEFAULT_END_YEAR})"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default=".",
        help="Output directory for results (default: current directory)"
    )
    
    args = parser.parse_args()
    
    if args.email == DEFAULT_EMAIL:
        print("WARNING: Please set your email with --email YOUR_EMAIL")
        print("         NCBI requires a valid email for E-utilities queries")
        print()
    
    run_analysis(
        email=args.email,
        start_year=args.start_year,
        end_year=args.end_year,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
