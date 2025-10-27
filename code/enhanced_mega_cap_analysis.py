"""
향상된 메가캡 분석: 논문용 추가 그래프 및 분석
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data():
    """데이터 로드 및 전처리"""
    print("=" * 60)
    print("향상된 메가캡 분석 시작")
    print("=" * 60)
    
    # 데이터 로드
    stocks_df = pd.read_csv('us_market/paper/Size_Reversal/back_data/table0_top200_stocks.csv')
    returns_df = pd.read_csv('us_market/paper/Size_Reversal/back_data/data1_daily_returns.csv', index_col=0)
    returns_df.index = pd.to_datetime(returns_df.index)
    ff_df = pd.read_csv('us_market/paper/Size_Reversal/back_data/data2_fama_french_factors.csv', index_col=0)
    ff_df.index = pd.to_datetime(ff_df.index)
    
    print(f"✅ 데이터 로드 완료")
    print(f"   - 주식 수: {len(returns_df.columns)}")
    print(f"   - 기간: {returns_df.index[0].strftime('%Y-%m-%d')} ~ {returns_df.index[-1].strftime('%Y-%m-%d')}")
    
    return stocks_df, returns_df, ff_df

def create_enhanced_mega_factors(stocks_df, returns_df):
    """향상된 메가캡 팩터 구성 (다양한 분할 방식)"""
    print(f"\n🔧 향상된 메가캡 팩터 구성")
    
    # 시가총액 기준 정렬
    stocks_sorted = stocks_df.copy().reset_index(drop=True)
    
    # 1. 기본 50-50 분할
    small_50_tickers = [t for t in stocks_sorted.iloc[100:200]['ticker'].tolist() if t in returns_df.columns]
    big_50_tickers = [t for t in stocks_sorted.iloc[0:100]['ticker'].tolist() if t in returns_df.columns]
    
    # 2. 30-30-40 분할 (Top 30, Middle 40, Bottom 30)
    top_30_tickers = [t for t in stocks_sorted.iloc[0:30]['ticker'].tolist() if t in returns_df.columns]
    middle_40_tickers = [t for t in stocks_sorted.iloc[30:70]['ticker'].tolist() if t in returns_df.columns]
    bottom_30_tickers = [t for t in stocks_sorted.iloc[70:100]['ticker'].tolist() if t in returns_df.columns]
    
    # 3. Quintile 분할 (5개 그룹)
    quintiles = {}
    for i in range(5):
        start_idx = i * 40
        end_idx = (i + 1) * 40
        quintiles[f'Q{i+1}'] = [t for t in stocks_sorted.iloc[start_idx:end_idx]['ticker'].tolist() if t in returns_df.columns]
    
    # 포트폴리오 수익률 계산
    portfolios = {}
    
    # 50-50 분할
    portfolios['Small_50'] = returns_df[small_50_tickers].mean(axis=1)
    portfolios['Big_50'] = returns_df[big_50_tickers].mean(axis=1)
    portfolios['SMB_50'] = portfolios['Small_50'] - portfolios['Big_50']
    
    # 30-30-40 분할
    portfolios['Top_30'] = returns_df[top_30_tickers].mean(axis=1)
    portfolios['Middle_40'] = returns_df[middle_40_tickers].mean(axis=1)
    portfolios['Bottom_30'] = returns_df[bottom_30_tickers].mean(axis=1)
    
    # Quintile 포트폴리오
    for q, tickers in quintiles.items():
        if tickers:
            portfolios[q] = returns_df[tickers].mean(axis=1)
    
    # SMB 팩터들
    portfolios['SMB_30'] = portfolios['Bottom_30'] - portfolios['Top_30']  # Bottom 30 - Top 30
    portfolios['SMB_Q5Q1'] = portfolios['Q5'] - portfolios['Q1']  # Q5 - Q1
    
    mega_factors_df = pd.DataFrame(portfolios)
    
    print(f"   ✅ 다양한 SMB 팩터 구성 완료")
    print(f"   - SMB_50 (50-50): {portfolios['SMB_50'].mean()*252:.1%}")
    print(f"   - SMB_30 (Bottom30-Top30): {portfolios['SMB_30'].mean()*252:.1%}")
    print(f"   - SMB_Q5Q1 (Q5-Q1): {portfolios['SMB_Q5Q1'].mean()*252:.1%}")
    
    return mega_factors_df, {
        'small_50': small_50_tickers,
        'big_50': big_50_tickers,
        'top_30': top_30_tickers,
        'bottom_30': bottom_30_tickers,
        'quintiles': quintiles
    }

def enhanced_fama_macbeth(returns_df, ff_df, mega_factors_df, ticker_groups):
    """향상된 Fama-MacBeth 분석"""
    print(f"\n🔬 향상된 Fama-MacBeth 분석")
    
    # 데이터 정렬
    common_dates = returns_df.index.intersection(ff_df.index).intersection(mega_factors_df.index)
    returns_aligned = returns_df.loc[common_dates]
    ff_aligned = ff_df.loc[common_dates]
    mega_aligned = mega_factors_df.loc[common_dates]
    
    results = {}
    
    # 다양한 SMB 팩터로 분석
    smb_factors = ['SMB_50', 'SMB_30', 'SMB_Q5Q1']
    
    for smb_factor in smb_factors:
        print(f"\n   📊 {smb_factor} 팩터 분석 중...")
        
        # Stage 1: 시계열 회귀
        stage1_results = {}
        
        for ticker in returns_aligned.columns:
            excess_return = returns_aligned[ticker] - ff_aligned['RF']
            
            X = pd.DataFrame({
                'Mkt_RF': ff_aligned['Mkt-RF'],
                'SMB_mega': mega_aligned[smb_factor],
                'HML': ff_aligned['HML']
            })
            
            valid_idx = ~(excess_return.isna() | X.isna().any(axis=1))
            y = excess_return[valid_idx]
            X_clean = X[valid_idx]
            
            if len(y) > 50:
                X_with_const = np.column_stack([np.ones(len(X_clean)), X_clean])
                try:
                    coeffs = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
                    stage1_results[ticker] = {
                        'alpha': coeffs[0],
                        'beta_market': coeffs[1],
                        'beta_smb_mega': coeffs[2],
                        'beta_hml': coeffs[3]
                    }
                except:
                    pass
        
        stage1_df = pd.DataFrame(stage1_results).T
        
        # Stage 2: 횡단면 회귀
        stage2_results = []
        
        for date in common_dates:
            daily_returns = returns_aligned.loc[date]
            valid_tickers = [t for t in daily_returns.index if t in stage1_df.index]
            
            if len(valid_tickers) > 10:
                y = daily_returns[valid_tickers].values
                X = stage1_df.loc[valid_tickers, ['beta_market', 'beta_smb_mega', 'beta_hml']].values
                
                valid_idx = ~(np.isnan(y) | np.isnan(X).any(axis=1))
                
                if valid_idx.sum() > 5:
                    y_clean = y[valid_idx]
                    X_clean = X[valid_idx]
                    X_with_const = np.column_stack([np.ones(len(X_clean)), X_clean])
                    
                    try:
                        coeffs = np.linalg.lstsq(X_with_const, y_clean, rcond=None)[0]
                        stage2_results.append({
                            'date': date,
                            'gamma_market': coeffs[1],
                            'gamma_smb_mega': coeffs[2],
                            'gamma_hml': coeffs[3]
                        })
                    except:
                        pass
        
        stage2_df = pd.DataFrame(stage2_results)
        
        # Stage 3: 시계열 평균
        factor_results = {}
        for factor in ['gamma_market', 'gamma_smb_mega', 'gamma_hml']:
            values = stage2_df[factor].dropna()
            mean_premium = values.mean()
            t_stat = mean_premium / (values.std() / np.sqrt(len(values)))
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), len(values) - 1))
            
            factor_results[factor] = {
                'daily_premium': mean_premium,
                'annual_premium': mean_premium * 252,
                't_stat': t_stat,
                'p_value': p_value
            }
        
        results[smb_factor] = {
            'factor_results': factor_results,
            'stage1_df': stage1_df,
            'stage2_df': stage2_df
        }
        
        print(f"      SMB Premium: {factor_results['gamma_smb_mega']['annual_premium']:.1%} (t={factor_results['gamma_smb_mega']['t_stat']:.2f})")
    
    return results

def create_comprehensive_visualizations(mega_factors_df, results, ticker_groups):
    """종합적인 시각화 생성"""
    print(f"\n📊 종합 시각화 생성 중...")
    
    # 설정
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    
    # Figure 1: 포트폴리오 성과 비교
    fig1, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1-1: 누적 수익률 비교 (50-50 분할)
    cum_small = (1 + mega_factors_df['Small_50']).cumprod()
    cum_big = (1 + mega_factors_df['Big_50']).cumprod()
    
    axes[0,0].plot(mega_factors_df.index, cum_small, label='Small Portfolio (101-200위)', linewidth=2, color='red')
    axes[0,0].plot(mega_factors_df.index, cum_big, label='Big Portfolio (1-100위)', linewidth=2, color='blue')
    axes[0,0].set_title('A. 메가캡 포트폴리오 누적 성과 (50-50 분할)', fontweight='bold')
    axes[0,0].set_ylabel('Cumulative Return')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # 1-2: Quintile 성과 비교
    colors = ['darkblue', 'blue', 'gray', 'orange', 'red']
    for i, (q, color) in enumerate(zip(['Q1', 'Q2', 'Q3', 'Q4', 'Q5'], colors)):
        if q in mega_factors_df.columns:
            cum_q = (1 + mega_factors_df[q]).cumprod()
            axes[0,1].plot(mega_factors_df.index, cum_q, label=f'{q} (순위 {i*40+1}-{(i+1)*40})', 
                          linewidth=2, color=color)
    
    axes[0,1].set_title('B. Quintile 포트폴리오 성과 비교', fontweight='bold')
    axes[0,1].set_ylabel('Cumulative Return')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # 1-3: SMB 팩터들 비교
    axes[1,0].plot(mega_factors_df.index, mega_factors_df['SMB_50'].cumsum(), 
                   label='SMB_50 (50-50 분할)', linewidth=2, color='green')
    axes[1,0].plot(mega_factors_df.index, mega_factors_df['SMB_30'].cumsum(), 
                   label='SMB_30 (Bottom30-Top30)', linewidth=2, color='purple')
    axes[1,0].plot(mega_factors_df.index, mega_factors_df['SMB_Q5Q1'].cumsum(), 
                   label='SMB_Q5Q1 (Q5-Q1)', linewidth=2, color='orange')
    
    axes[1,0].set_title('C. 다양한 SMB 팩터 누적 성과', fontweight='bold')
    axes[1,0].set_ylabel('Cumulative SMB Return')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # 1-4: 연간 성과 요약
    annual_returns = {}
    for col in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        if col in mega_factors_df.columns:
            annual_returns[col] = mega_factors_df[col].mean() * 252
    
    quintiles = list(annual_returns.keys())
    returns_values = list(annual_returns.values())
    
    bars = axes[1,1].bar(quintiles, [r*100 for r in returns_values], 
                        color=['darkblue', 'blue', 'gray', 'orange', 'red'])
    axes[1,1].set_title('D. Quintile별 연간 수익률', fontweight='bold')
    axes[1,1].set_ylabel('Annual Return (%)')
    axes[1,1].grid(True, alpha=0.3, axis='y')
    
    # 막대 위에 수치 표시
    for bar, value in zip(bars, returns_values):
        axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                      f'{value*100:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('us_market/paper/Size_Reversal/figures/fig_enhanced_portfolio_analysis.pdf', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    # Figure 2: 베타 분석
    fig2, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    smb_factors = ['SMB_50', 'SMB_30', 'SMB_Q5Q1']
    titles = ['50-50 분할', 'Bottom30-Top30', 'Q5-Q1']
    
    for i, (smb_factor, title) in enumerate(zip(smb_factors, titles)):
        if smb_factor in results:
            stage1_df = results[smb_factor]['stage1_df']
            
            # 베타 분포
            axes[0,i].hist(stage1_df['beta_smb_mega'], bins=20, alpha=0.7, 
                          color=['green', 'purple', 'orange'][i], edgecolor='black')
            axes[0,i].axvline(stage1_df['beta_smb_mega'].mean(), color='red', 
                             linestyle='--', linewidth=2)
            axes[0,i].set_title(f'SMB Beta 분포 ({title})', fontweight='bold')
            axes[0,i].set_xlabel('Beta')
            axes[0,i].set_ylabel('Frequency')
            axes[0,i].text(0.05, 0.95, f'평균: {stage1_df["beta_smb_mega"].mean():.3f}\n'
                                      f'표준편차: {stage1_df["beta_smb_mega"].std():.3f}', 
                          transform=axes[0,i].transAxes, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # 일별 프리미엄 분포
            stage2_df = results[smb_factor]['stage2_df']
            axes[1,i].hist(stage2_df['gamma_smb_mega'], bins=30, alpha=0.7, 
                          color=['green', 'purple', 'orange'][i], edgecolor='black')
            axes[1,i].axvline(stage2_df['gamma_smb_mega'].mean(), color='red', 
                             linestyle='--', linewidth=2)
            axes[1,i].set_title(f'일별 SMB 프리미엄 ({title})', fontweight='bold')
            axes[1,i].set_xlabel('Daily Premium')
            axes[1,i].set_ylabel('Frequency')
            
            # 통계 정보
            factor_results = results[smb_factor]['factor_results']['gamma_smb_mega']
            axes[1,i].text(0.05, 0.95, f'연간: {factor_results["annual_premium"]:.1%}\n'
                                      f't-stat: {factor_results["t_stat"]:.2f}\n'
                                      f'p-value: {factor_results["p_value"]:.3f}', 
                          transform=axes[1,i].transAxes, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('us_market/paper/Size_Reversal/figures/fig_enhanced_beta_analysis.pdf', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    # Figure 3: 시계열 분석
    fig3, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 3-1: Rolling correlation (SMB vs Market)
    window = 252  # 1년
    rolling_corr = mega_factors_df['SMB_50'].rolling(window).corr(
        pd.read_csv('us_market/paper/Size_Reversal/back_data/data2_fama_french_factors.csv', 
                   index_col=0, parse_dates=True)['Mkt-RF'])
    
    axes[0,0].plot(rolling_corr.index, rolling_corr, linewidth=2, color='blue')
    axes[0,0].set_title('A. SMB-Market 1년 Rolling Correlation', fontweight='bold')
    axes[0,0].set_ylabel('Correlation')
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # 3-2: Rolling volatility
    rolling_vol_smb = mega_factors_df['SMB_50'].rolling(window).std() * np.sqrt(252)
    rolling_vol_market = pd.read_csv('us_market/paper/Size_Reversal/back_data/data2_fama_french_factors.csv', 
                                   index_col=0, parse_dates=True)['Mkt-RF'].rolling(window).std() * np.sqrt(252)
    
    axes[0,1].plot(rolling_vol_smb.index, rolling_vol_smb, label='SMB Volatility', linewidth=2, color='red')
    axes[0,1].plot(rolling_vol_market.index, rolling_vol_market, label='Market Volatility', linewidth=2, color='blue')
    axes[0,1].set_title('B. 1년 Rolling Volatility', fontweight='bold')
    axes[0,1].set_ylabel('Annualized Volatility')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # 3-3: 월별 SMB 성과
    monthly_smb = mega_factors_df['SMB_50'].resample('M').sum()
    monthly_performance = monthly_smb.groupby(monthly_smb.index.month).mean() * 12
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    bars = axes[1,0].bar(months, monthly_performance.values * 100, 
                        color=['red' if x < 0 else 'blue' for x in monthly_performance.values])
    axes[1,0].set_title('C. 월별 평균 SMB 성과', fontweight='bold')
    axes[1,0].set_ylabel('Monthly SMB Return (%)')
    axes[1,0].grid(True, alpha=0.3, axis='y')
    axes[1,0].axhline(y=0, color='black', linestyle='-', alpha=0.8)
    
    # 3-4: 연도별 성과
    yearly_performance = {}
    for year in range(2021, 2025):
        year_data = mega_factors_df[mega_factors_df.index.year == year]['SMB_50']
        if len(year_data) > 0:
            yearly_performance[year] = year_data.sum()
    
    years = list(yearly_performance.keys())
    year_returns = list(yearly_performance.values())
    
    bars = axes[1,1].bar([str(y) for y in years], [r*100 for r in year_returns], 
                        color=['red' if x < 0 else 'blue' for x in year_returns])
    axes[1,1].set_title('D. 연도별 SMB 성과', fontweight='bold')
    axes[1,1].set_ylabel('Annual SMB Return (%)')
    axes[1,1].grid(True, alpha=0.3, axis='y')
    axes[1,1].axhline(y=0, color='black', linestyle='-', alpha=0.8)
    
    # 막대 위에 수치 표시
    for bar, value in zip(bars, year_returns):
        axes[1,1].text(bar.get_x() + bar.get_width()/2, 
                      bar.get_height() + (1 if bar.get_height() > 0 else -3), 
                      f'{value*100:.1f}%', ha='center', 
                      va='bottom' if bar.get_height() > 0 else 'top', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('us_market/paper/Size_Reversal/figures/fig_enhanced_timeseries_analysis.pdf', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"   ✅ 모든 시각화 완료")
    print(f"   - 포트폴리오 분석: fig_enhanced_portfolio_analysis.pdf")
    print(f"   - 베타 분석: fig_enhanced_beta_analysis.pdf") 
    print(f"   - 시계열 분석: fig_enhanced_timeseries_analysis.pdf")

def create_results_summary_table(results):
    """결과 요약 테이블 생성"""
    print(f"\n📋 결과 요약 테이블 생성")
    
    summary_data = []
    
    for smb_factor in ['SMB_50', 'SMB_30', 'SMB_Q5Q1']:
        if smb_factor in results:
            factor_results = results[smb_factor]['factor_results']
            
            for factor_name, factor_key in [('Market', 'gamma_market'), 
                                          ('Size', 'gamma_smb_mega'), 
                                          ('Value', 'gamma_hml')]:
                result = factor_results[factor_key]
                
                # 유의성 표시
                if result['p_value'] < 0.01:
                    sig = '***'
                elif result['p_value'] < 0.05:
                    sig = '**'
                elif result['p_value'] < 0.1:
                    sig = '*'
                else:
                    sig = ''
                
                summary_data.append({
                    'SMB_Factor': smb_factor,
                    'Factor': factor_name,
                    'Daily_Premium': f"{result['daily_premium']:.4f}",
                    'Annual_Premium': f"{result['annual_premium']:.1%}",
                    't_statistic': f"{result['t_stat']:.2f}",
                    'p_value': f"{result['p_value']:.3f}",
                    'Significance': sig
                })
    
    summary_df = pd.DataFrame(summary_data)
    
    # CSV로 저장
    summary_df.to_csv('us_market/paper/Size_Reversal/back_data/enhanced_results_summary.csv', index=False)
    
    print(f"   ✅ 요약 테이블 저장: enhanced_results_summary.csv")
    print(f"\n📊 주요 결과:")
    
    # Size Premium 결과만 출력
    size_results = summary_df[summary_df['Factor'] == 'Size']
    for _, row in size_results.iterrows():
        print(f"   - {row['SMB_Factor']}: {row['Annual_Premium']} (t={row['t_statistic']}, {row['Significance']})")
    
    return summary_df

def main():
    """메인 분석 실행"""
    # 1. 데이터 준비
    stocks_df, returns_df, ff_df = load_and_prepare_data()
    
    # 2. 향상된 팩터 구성
    mega_factors_df, ticker_groups = create_enhanced_mega_factors(stocks_df, returns_df)
    
    # 3. 향상된 Fama-MacBeth 분석
    results = enhanced_fama_macbeth(returns_df, ff_df, mega_factors_df, ticker_groups)
    
    # 4. 종합 시각화
    create_comprehensive_visualizations(mega_factors_df, results, ticker_groups)
    
    # 5. 결과 요약
    summary_df = create_results_summary_table(results)
    
    print(f"\n" + "=" * 60)
    print(f"🎯 향상된 분석 완료")
    print(f"=" * 60)
    print(f"✅ 3개의 새로운 그래프 생성")
    print(f"✅ 다양한 SMB 팩터 비교 완료")
    print(f"✅ 강건성 검정 수행")
    print(f"✅ 논문 수정을 위한 모든 자료 준비 완료")
    
    return results, summary_df, mega_factors_df

if __name__ == "__main__":
    results, summary_df, mega_factors_df = main()