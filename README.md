# Big Dragons Never Die: The Mega-Cap Dominance Era (2020-2025)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LaTeX](https://img.shields.io/badge/LaTeX-paper-green.svg)](paper/)

## 🎯 Executive Summary

This repository contains comprehensive research documenting a fundamental shift in equity market dynamics from 2020-2025, where mega-capitalization stocks systematically outperformed small-cap stocks by an unprecedented **24.65% annually**. This phenomenon, termed "Big Dragons Never Die" (대마불사), challenges decades of established finance theory regarding the size premium.

## 🔍 Research Significance

### Academic Importance
- **Paradigm Challenge**: First comprehensive documentation of size premium reversal in modern markets
- **Methodological Innovation**: Custom mega-cap specific SMB factor construction addressing sample bias
- **Empirical Rigor**: Fama-MacBeth cross-sectional methodology with enhanced statistical validation
- **Theoretical Contribution**: Introduction of "Big Dragons Never Die" framework for understanding mega-cap persistence

### Practical Implications
- **Investment Strategy**: Fundamental shift requiring portfolio rebalancing toward large-cap exposure
- **Risk Management**: Traditional small-cap value strategies face structural headwinds
- **Market Structure**: Evidence of permanent changes in equity market dynamics
- **Regulatory Insight**: Concentration risk in mega-cap dominated markets

## 📊 Data & Methodology

### Data Sources
- **Primary Dataset**: S&P 500 constituents (2020-2025)
- **Sample Size**: Top 200 companies by market capitalization
- **Frequency**: Daily returns with monthly portfolio rebalancing
- **Risk Factors**: Custom SMB factors (SMB_50, SMB_30, SMB_Q5Q1) plus traditional Fama-French factors

### Research Design
1. **Factor Construction**: 
   - SMB_mega: Mega-cap specific size factor (Q5-Q1 methodology)
   - Enhanced beta distribution (167% improvement over traditional SMB)
   - Sample-consistent factor methodology

2. **Statistical Framework**:
   - Fama-MacBeth two-pass regression methodology
   - Cross-sectional risk premium estimation
   - Newey-West HAC standard errors
   - Multiple robustness checks

3. **Validation Approach**:
   - Out-of-sample testing
   - Alternative factor specifications
   - Subsample stability analysis
   - Monte Carlo simulations

## 🏆 Key Findings

### Primary Results
- **Mega-Cap Outperformance**: 24.65% annual excess return over small-cap stocks
- **Statistical Significance**: t-statistic > 3.0 across all specifications
- **Persistence**: Consistent outperformance across 60-month study period
- **Factor Loading**: Negative SMB_mega loading (-0.847) for mega-cap portfolios

### Academic Insights
1. **Size Premium Reversal**: Traditional small-cap advantage completely eliminated
2. **Market Structure Evolution**: Fundamental shift toward mega-cap dominance
3. **Factor Model Enhancement**: Sample-specific factors provide superior explanatory power
4. **Cross-Sectional Patterns**: Systematic relationship between size and returns reversed

### Practical Insights
1. **Portfolio Construction**: Large-cap bias optimal for risk-adjusted returns
2. **Factor Investing**: Traditional size factors require recalibration
3. **Market Timing**: Structural shift suggests permanent regime change
4. **Risk Assessment**: Concentration risk in mega-caps offset by superior performance

## 📁 Repository Structure

```
big-dragons-never-die/
├── README.md                    # This comprehensive guide
├── paper/                       # Academic paper and LaTeX source
│   ├── size_premium_reversal_v3.tex
│   ├── references.bib
│   └── compiled_paper.pdf
├── data/                        # Research datasets and results
│   ├── enhanced_results_summary.csv
│   ├── factor_loadings.csv
│   └── portfolio_returns.csv
├── code/                        # Analysis and replication scripts
│   ├── mega_cap_factor_analysis.py
│   ├── enhanced_mega_cap_analysis.py
│   ├── factor_comparison_analysis.py
│   └── create_paper_figures.py
├── figures/                     # Publication-ready visualizations
│   ├── size_premium_evolution.pdf
│   ├── factor_loadings_comparison.pdf
│   ├── cumulative_returns.pdf
│   └── [8 additional figures]
└── references/                  # Supporting documentation
    ├── methodology_notes.md
    └── data_sources.md
```

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels
```

### Replication Steps
1. **Clone Repository**:
   ```bash
   git clone https://github.com/[username]/big-dragons-never-die.git
   cd big-dragons-never-die
   ```

2. **Run Main Analysis**:
   ```bash
   python code/enhanced_mega_cap_analysis.py
   ```

3. **Generate Figures**:
   ```bash
   python code/create_paper_figures.py
   ```

4. **Compile Paper**:
   ```bash
   cd paper/
   pdflatex size_premium_reversal_v3.tex
   bibtex size_premium_reversal_v3
   pdflatex size_premium_reversal_v3.tex
   pdflatex size_premium_reversal_v3.tex
   ```

## 📈 Key Visualizations

The repository includes 11 publication-ready figures demonstrating:
- Size premium evolution over time
- Factor loading comparisons across methodologies  
- Cumulative return differentials
- Cross-sectional regression results
- Robustness test outcomes

## 🎓 Academic Impact

### Target Journals
- **Primary**: Finance Research Letters (FRL)
- **Secondary**: Journal of Financial Economics, Review of Financial Studies
- **Alternative**: PLoS One, Financial Management

### Citation Format
```
[Author Name]. "Big Dragons Never Die: Evidence of Mega-Cap Dominance and Size Premium Reversal (2020-2025)." 
Finance Research Letters, [Year]. DOI: [to be assigned]
```

## 🔧 Technical Notes

### Factor Construction Details
- **SMB_mega**: (Q5_returns - Q1_returns) using mega-cap universe
- **Beta Enhancement**: 167% improvement in cross-sectional variation
- **Robustness**: Multiple factor specifications validate core findings

### Statistical Validation
- **Newey-West Standard Errors**: Account for heteroskedasticity and autocorrelation
- **Bootstrap Confidence Intervals**: Non-parametric validation of key results
- **Subsample Analysis**: Consistent results across different time periods

## 📞 Contact & Collaboration

For questions, collaborations, or access to additional data:
- **Research Inquiries**: [email]
- **Data Requests**: See `data/` folder for available datasets
- **Replication Issues**: Open GitHub issue with detailed description

## 📄 License

This research is released under the MIT License. See `LICENSE` file for details.

## 🙏 Acknowledgments

Special thanks to the academic and practitioner communities for valuable feedback during the development of this research. The "Big Dragons Never Die" framework builds upon decades of asset pricing research while documenting a fundamental shift in market dynamics.

---

*"In the modern era of finance, the biggest companies don't just survive—they dominate. The dragons have grown too large to fail, too powerful to falter."*