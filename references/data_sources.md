# Data Sources and Processing

## Primary Data Sources

### Equity Return Data
- **Source**: S&P 500 constituent data
- **Period**: January 2020 - December 2025
- **Frequency**: Daily returns, aggregated to monthly
- **Adjustments**: Dividend-adjusted, split-adjusted returns
- **Currency**: USD (no currency conversion required)

### Risk Factor Data
- **Market Factor (MKT)**: S&P 500 index return minus risk-free rate
- **Size Factor (SMB)**: Custom mega-cap specific construction
- **Value Factor (HML)**: Book-to-market based factor
- **Risk-Free Rate**: 3-month Treasury bill rate

### Market Capitalization Data
- **Source**: End-of-month market values
- **Usage**: Portfolio formation and size quintile construction
- **Frequency**: Monthly rebalancing
- **Survivorship**: Focus on persistent large-cap companies

## Data Processing Steps

### 1. Sample Selection
```python
# Pseudo-code for sample selection
def select_sample(sp500_data, start_date, end_date):
    # Filter by date range
    sample = sp500_data[(sp500_data.date >= start_date) & 
                       (sp500_data.date <= end_date)]
    
    # Select top 200 by market cap
    monthly_samples = []
    for month in sample.date.unique():
        month_data = sample[sample.date == month]
        top_200 = month_data.nlargest(200, 'market_cap')
        monthly_samples.append(top_200)
    
    return pd.concat(monthly_samples)
```

### 2. Return Calculation
```python
# Calculate excess returns
def calculate_excess_returns(price_data, rf_rate):
    # Calculate simple returns
    returns = price_data.pct_change()
    
    # Convert to excess returns
    excess_returns = returns.sub(rf_rate, axis=0)
    
    return excess_returns
```

### 3. Factor Construction
```python
# SMB_mega factor construction
def construct_smb_mega(returns, market_caps):
    # Sort by market cap into quintiles
    quintiles = pd.qcut(market_caps, 5, labels=['Q1','Q2','Q3','Q4','Q5'])
    
    # Calculate quintile returns
    q5_returns = returns[quintiles == 'Q5'].mean()
    q1_returns = returns[quintiles == 'Q1'].mean()
    
    # SMB_mega = Small minus Big (Q1 - Q5 for mega-cap universe)
    smb_mega = q1_returns - q5_returns
    
    return smb_mega
```

## Data Quality Checks

### Missing Data Handling
- **Approach**: Forward-fill for up to 5 trading days
- **Threshold**: Exclude securities with >20% missing observations
- **Validation**: Cross-check with alternative data sources

### Outlier Detection
- **Method**: Winsorization at 1st and 99th percentiles
- **Application**: Applied to returns and factor loadings
- **Rationale**: Reduce impact of extreme observations on statistical inference

### Survivorship Bias
- **Consideration**: Intentionally focus on persistent large-cap companies
- **Justification**: Research question specifically about mega-cap dominance
- **Alternative**: Robustness check with full survivorship-bias-free sample

## File Descriptions

### enhanced_results_summary.csv
- **Content**: Main regression results and factor loadings
- **Columns**: 
  - `factor`: Factor name (MKT, SMB_mega, HML)
  - `coefficient`: Factor loading estimate
  - `t_statistic`: Statistical significance
  - `p_value`: Probability value
  - `confidence_interval`: 95% confidence bounds

### factor_loadings.csv
- **Content**: Time-series of factor loadings by portfolio
- **Columns**:
  - `date`: Monthly observation date
  - `portfolio`: Size quintile (Q1-Q5)
  - `mkt_beta`: Market factor loading
  - `smb_beta`: Size factor loading
  - `hml_beta`: Value factor loading

### portfolio_returns.csv
- **Content**: Monthly portfolio returns by size quintile
- **Columns**:
  - `date`: Monthly observation date
  - `q1_return`: Smallest quintile return
  - `q2_return`: Second quintile return
  - `q3_return`: Third quintile return
  - `q4_return`: Fourth quintile return
  - `q5_return`: Largest quintile return
  - `smb_mega`: Size factor return (Q1-Q5)

## Replication Instructions

### Data Requirements
1. S&P 500 constituent list with historical changes
2. Daily stock price and volume data
3. Market capitalization data (monthly)
4. Risk-free rate time series
5. Fama-French factor data (for comparison)

### Processing Pipeline
1. **Data Cleaning**: Handle missing values, outliers, corporate actions
2. **Sample Construction**: Select top 200 companies monthly
3. **Return Calculation**: Compute excess returns over risk-free rate
4. **Factor Construction**: Build custom SMB_mega and other factors
5. **Portfolio Formation**: Create size-sorted portfolios
6. **Statistical Analysis**: Run Fama-MacBeth regressions
7. **Robustness Testing**: Validate results across specifications

### Computational Requirements
- **Software**: Python 3.8+, pandas, numpy, scipy, statsmodels
- **Memory**: Minimum 8GB RAM for full sample processing
- **Storage**: Approximately 500MB for complete dataset
- **Runtime**: 15-30 minutes for full analysis pipeline