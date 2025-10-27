"""
메가캡 전용 팩터 구성 및 Fama-MacBeth 분석
올바른 방법론으로 메가캡 내 크기 효과 측정
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """
    기존 데이터 로드 및 전처리
    """
    print("=" * 60)
    print("메가캡 전용 팩터 분석 시작")
    print("=" * 60)
    
    # 1. 주식 리스트 로드
    stocks_df = pd.read_csv('us_market/paper/Size_Reversal/back_data/table0_top200_stocks.csv')
    print(f"\n📊 표본 정보:")
    print(f"   - 총 주식 수: {len(stocks_df)}")
    print(f"   - 1위 (최대): {stocks_df.iloc[0]['company_name']} (${stocks_df.iloc[0]['market_cap_billions']:.0f}B)")
    print(f"   - 200위 (최소): {stocks_df.iloc[-1]['company_name']} (${stocks_df.iloc[-1]['market_cap_billions']:.0f}B)")
    
    # 2. 수익률 데이터 로드
    returns_df = pd.read_csv('us_market/paper/Size_Reversal/back_data/data1_daily_returns.csv', index_col=0)
    returns_df.index = pd.to_datetime(returns_df.index)
    print(f"\n📈 수익률 데이터:")
    print(f"   - 기간: {returns_df.index[0].strftime('%Y-%m-%d')} ~ {returns_df.index[-1].strftime('%Y-%m-%d')}")
    print(f"   - 거래일 수: {len(returns_df)}")
    print(f"   - 주식 수: {len(returns_df.columns)}")
    
    # 3. Fama-French 팩터 로드
    ff_df = pd.read_csv('us_market/paper/Size_Reversal/back_data/data2_fama_french_factors.csv', index_col=0)
    ff_df.index = pd.to_datetime(ff_df.index)
    print(f"\n📊 Fama-French 팩터:")
    print(f"   - 팩터: {list(ff_df.columns)}")
    print(f"   - 기간: {ff_df.index[0].strftime('%Y-%m-%d')} ~ {ff_df.index[-1].strftime('%Y-%m-%d')}")
    
    return stocks_df, returns_df, ff_df

def create_mega_cap_factors(stocks_df, returns_df):
    """
    메가캡 전용 SMB 및 HML 팩터 구성
    """
    print("\n" + "=" * 60)
    print("메가캡 전용 팩터 구성")
    print("=" * 60)
    
    # 시가총액 기준 정렬 (이미 정렬되어 있지만 확인)
    stocks_sorted = stocks_df.copy().reset_index(drop=True)
    
    # 1. 메가캡 SMB 팩터 구성
    print("\n🔧 SMB_mega 팩터 구성:")
    
    # Small: 101-200위 (상대적 소형)
    small_tickers = stocks_sorted.iloc[100:200]['ticker'].tolist()
    # Big: 1-100위 (상대적 대형)  
    big_tickers = stocks_sorted.iloc[0:100]['ticker'].tolist()
    
    # 실제 데이터에 존재하는 티커만 필터링
    small_tickers = [t for t in small_tickers if t in returns_df.columns]
    big_tickers = [t for t in big_tickers if t in returns_df.columns]
    
    print(f"   - Small Portfolio (101-200위): {len(small_tickers)}개 주식")
    print(f"   - Big Portfolio (1-100위): {len(big_tickers)}개 주식")
    
    # 동일가중 포트폴리오 수익률 계산
    small_portfolio = returns_df[small_tickers].mean(axis=1)
    big_portfolio = returns_df[big_tickers].mean(axis=1)
    
    # SMB_mega 팩터
    smb_mega = small_portfolio - big_portfolio
    
    print(f"   - Small Portfolio 평균 수익률: {small_portfolio.mean()*252:.1%}")
    print(f"   - Big Portfolio 평균 수익률: {big_portfolio.mean()*252:.1%}")
    print(f"   - SMB_mega 팩터: {smb_mega.mean()*252:.1%}")
    
    # 2. 메가캡 HML 팩터 구성 (Book-to-Market 데이터가 없으므로 생략)
    print(f"\n🔧 HML_mega 팩터:")
    print("   - Book-to-Market 데이터 없음, 기존 HML 사용")
    
    # 팩터 데이터프레임 생성
    mega_factors = pd.DataFrame({
        'SMB_mega': smb_mega,
        'Small_Portfolio': small_portfolio,
        'Big_Portfolio': big_portfolio
    })
    
    return mega_factors, small_tickers, big_tickers

def fama_macbeth_with_mega_factors(returns_df, ff_df, mega_factors, small_tickers, big_tickers):
    """
    메가캡 전용 팩터를 사용한 Fama-MacBeth 회귀
    """
    print("\n" + "=" * 60)
    print("메가캡 팩터 Fama-MacBeth 분석")
    print("=" * 60)
    
    # 데이터 정렬
    common_dates = returns_df.index.intersection(ff_df.index).intersection(mega_factors.index)
    returns_aligned = returns_df.loc[common_dates]
    ff_aligned = ff_df.loc[common_dates]
    mega_aligned = mega_factors.loc[common_dates]
    
    print(f"\n📊 분석 데이터:")
    print(f"   - 공통 기간: {len(common_dates)}일")
    print(f"   - 분석 주식: {len(returns_aligned.columns)}개")
    
    # Stage 1: 시계열 회귀 (각 주식별)
    print(f"\n🔬 Stage 1: 시계열 회귀")
    
    stage1_results = {}
    
    for ticker in returns_aligned.columns:
        if ticker in small_tickers or ticker in big_tickers:
            # 초과수익률 계산
            excess_return = returns_aligned[ticker] - ff_aligned['RF']
            
            # 회귀 변수 준비
            X = pd.DataFrame({
                'Mkt_RF': ff_aligned['Mkt-RF'],
                'SMB_mega': mega_aligned['SMB_mega'],
                'HML': ff_aligned['HML']
            })
            
            # 결측치 제거
            valid_idx = ~(excess_return.isna() | X.isna().any(axis=1))
            y = excess_return[valid_idx]
            X_clean = X[valid_idx]
            
            if len(y) > 50:  # 충분한 관측치가 있는 경우만
                # 회귀 실행 (numpy 사용)
                X_with_const = np.column_stack([np.ones(len(X_clean)), X_clean])
                
                try:
                    coeffs = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
                    
                    # 결과 저장
                    stage1_results[ticker] = {
                        'alpha': coeffs[0],
                        'beta_market': coeffs[1],
                        'beta_smb_mega': coeffs[2],
                        'beta_hml': coeffs[3],
                        'observations': len(y)
                    }
                except:
                    pass
    
    print(f"   - 성공적으로 분석된 주식: {len(stage1_results)}개")
    
    # Stage 1 결과를 DataFrame으로 변환
    stage1_df = pd.DataFrame(stage1_results).T
    
    print(f"\n📈 Stage 1 베타 통계:")
    print(f"   - Market Beta 평균: {stage1_df['beta_market'].mean():.3f}")
    print(f"   - SMB_mega Beta 평균: {stage1_df['beta_smb_mega'].mean():.3f}")
    print(f"   - HML Beta 평균: {stage1_df['beta_hml'].mean():.3f}")
    
    # Stage 2: 횡단면 회귀 (각 시점별)
    print(f"\n🔬 Stage 2: 횡단면 회귀")
    
    stage2_results = []
    
    for date in common_dates:
        # 해당 날짜의 수익률
        daily_returns = returns_aligned.loc[date]
        
        # 베타가 있는 주식들만
        valid_tickers = [t for t in daily_returns.index if t in stage1_df.index]
        
        if len(valid_tickers) > 10:  # 충분한 주식이 있는 경우
            y = daily_returns[valid_tickers].values
            X = stage1_df.loc[valid_tickers, ['beta_market', 'beta_smb_mega', 'beta_hml']].values
            
            # 결측치 제거
            valid_idx = ~(np.isnan(y) | np.isnan(X).any(axis=1))
            
            if valid_idx.sum() > 5:
                y_clean = y[valid_idx]
                X_clean = X[valid_idx]
                
                # 상수항 추가
                X_with_const = np.column_stack([np.ones(len(X_clean)), X_clean])
                
                try:
                    # 회귀 실행
                    coeffs = np.linalg.lstsq(X_with_const, y_clean, rcond=None)[0]
                    
                    stage2_results.append({
                        'date': date,
                        'gamma_0': coeffs[0],
                        'gamma_market': coeffs[1],
                        'gamma_smb_mega': coeffs[2],
                        'gamma_hml': coeffs[3],
                        'n_stocks': len(y_clean)
                    })
                except:
                    pass
    
    stage2_df = pd.DataFrame(stage2_results)
    print(f"   - 성공적으로 분석된 날짜: {len(stage2_df)}일")
    
    # Stage 3: 시계열 평균 및 t-검정
    print(f"\n🔬 Stage 3: 시계열 평균 및 t-검정")
    
    results = {}
    for factor in ['gamma_market', 'gamma_smb_mega', 'gamma_hml']:
        values = stage2_df[factor].dropna()
        
        mean_premium = values.mean()
        std_premium = values.std()
        t_stat = mean_premium / (std_premium / np.sqrt(len(values)))
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), len(values) - 1))
        
        results[factor] = {
            'daily_premium': mean_premium,
            'annual_premium': mean_premium * 252,
            't_stat': t_stat,
            'p_value': p_value,
            'observations': len(values)
        }
    
    return results, stage1_df, stage2_df

def compare_methodologies(returns_df, ff_df, mega_factors, small_tickers, big_tickers):
    """
    기존 방법론 vs 새로운 방법론 비교
    """
    print("\n" + "=" * 60)
    print("방법론 비교: 기존 vs 메가캡 전용")
    print("=" * 60)
    
    # 1. 기존 방법론 (전체 시장 SMB 사용)
    print(f"\n📊 기존 방법론 (전체 시장 SMB):")
    
    # 기존 결과 로드
    old_results = pd.read_csv('us_market/paper/Size_Reversal/back_data/table3_final_results.csv')
    
    print(f"   - Market Premium: {old_results.loc[0, 'Annual_Premium']:.1f}% (t={old_results.loc[0, 't_statistic']:.2f})")
    print(f"   - Size Premium (SMB): {old_results.loc[1, 'Annual_Premium']:.1f}% (t={old_results.loc[1, 't_statistic']:.2f})")
    print(f"   - Value Premium (HML): {old_results.loc[2, 'Annual_Premium']:.1f}% (t={old_results.loc[2, 't_statistic']:.2f})")
    
    # 2. 새로운 방법론 실행
    print(f"\n📊 새로운 방법론 (메가캡 전용 SMB):")
    
    new_results, stage1_df, stage2_df = fama_macbeth_with_mega_factors(
        returns_df, ff_df, mega_factors, small_tickers, big_tickers
    )
    
    print(f"   - Market Premium: {new_results['gamma_market']['annual_premium']:.1f}% (t={new_results['gamma_market']['t_stat']:.2f})")
    print(f"   - Size Premium (SMB_mega): {new_results['gamma_smb_mega']['annual_premium']:.1f}% (t={new_results['gamma_smb_mega']['t_stat']:.2f})")
    print(f"   - Value Premium (HML): {new_results['gamma_hml']['annual_premium']:.1f}% (t={new_results['gamma_hml']['t_stat']:.2f})")
    
    # 3. 베타 분포 비교
    print(f"\n📈 베타 분포 비교:")
    
    # 기존 베타
    old_betas = pd.read_csv('us_market/paper/Size_Reversal/back_data/table1_stage1_betas.csv', index_col=0)
    
    print(f"\n   기존 SMB 베타:")
    print(f"   - 평균: {old_betas['beta_smb'].mean():.3f}")
    print(f"   - 표준편차: {old_betas['beta_smb'].std():.3f}")
    print(f"   - 범위: [{old_betas['beta_smb'].min():.3f}, {old_betas['beta_smb'].max():.3f}]")
    
    print(f"\n   새로운 SMB_mega 베타:")
    print(f"   - 평균: {stage1_df['beta_smb_mega'].mean():.3f}")
    print(f"   - 표준편차: {stage1_df['beta_smb_mega'].std():.3f}")
    print(f"   - 범위: [{stage1_df['beta_smb_mega'].min():.3f}, {stage1_df['beta_smb_mega'].max():.3f}]")
    
    return new_results, stage1_df, stage2_df, old_results, old_betas

def create_visualizations(stage1_df, stage2_df, mega_factors, old_betas):
    """
    결과 시각화
    """
    print(f"\n📊 결과 시각화 생성 중...")
    
    # 1. 베타 분포 비교
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 기존 SMB 베타
    axes[0,0].hist(old_betas['beta_smb'], bins=20, alpha=0.7, color='red', edgecolor='black')
    axes[0,0].axvline(old_betas['beta_smb'].mean(), color='red', linestyle='--', linewidth=2)
    axes[0,0].set_title('기존 SMB 베타 분포')
    axes[0,0].set_xlabel('Beta')
    axes[0,0].set_ylabel('Frequency')
    
    # 새로운 SMB_mega 베타
    axes[0,1].hist(stage1_df['beta_smb_mega'], bins=20, alpha=0.7, color='blue', edgecolor='black')
    axes[0,1].axvline(stage1_df['beta_smb_mega'].mean(), color='blue', linestyle='--', linewidth=2)
    axes[0,1].set_title('새로운 SMB_mega 베타 분포')
    axes[0,1].set_xlabel('Beta')
    axes[0,1].set_ylabel('Frequency')
    
    # SMB_mega 팩터 시계열
    axes[1,0].plot(mega_factors.index, mega_factors['SMB_mega'].cumsum(), color='green', linewidth=2)
    axes[1,0].set_title('SMB_mega 팩터 누적 수익률')
    axes[1,0].set_xlabel('Date')
    axes[1,0].set_ylabel('Cumulative Return')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # 일별 프리미엄 분포
    axes[1,1].hist(stage2_df['gamma_smb_mega'], bins=30, alpha=0.7, color='purple', edgecolor='black')
    axes[1,1].axvline(stage2_df['gamma_smb_mega'].mean(), color='purple', linestyle='--', linewidth=2)
    axes[1,1].set_title('SMB_mega 일별 프리미엄 분포')
    axes[1,1].set_xlabel('Daily Premium')
    axes[1,1].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('mega_cap_factor_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. 포트폴리오 수익률 비교
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    # 누적 수익률 계산
    small_cum = (1 + mega_factors['Small_Portfolio']).cumprod()
    big_cum = (1 + mega_factors['Big_Portfolio']).cumprod()
    
    ax.plot(mega_factors.index, small_cum, label='Small Portfolio (101-200위)', linewidth=2)
    ax.plot(mega_factors.index, big_cum, label='Big Portfolio (1-100위)', linewidth=2)
    
    ax.set_title('메가캡 내 포트폴리오 성과 비교', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Return')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('mega_cap_portfolio_performance.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """
    메인 분석 실행
    """
    # 1. 데이터 로드
    stocks_df, returns_df, ff_df = load_data()
    
    # 2. 메가캡 전용 팩터 구성
    mega_factors, small_tickers, big_tickers = create_mega_cap_factors(stocks_df, returns_df)
    
    # 3. 방법론 비교
    new_results, stage1_df, stage2_df, old_results, old_betas = compare_methodologies(
        returns_df, ff_df, mega_factors, small_tickers, big_tickers
    )
    
    # 4. 시각화
    create_visualizations(stage1_df, stage2_df, mega_factors, old_betas)
    
    # 5. 최종 결론
    print("\n" + "=" * 60)
    print("💡 핵심 결론")
    print("=" * 60)
    
    print(f"\n🔍 방법론적 개선:")
    print(f"   - 기존: 전체 시장 SMB 사용 (부적절)")
    print(f"   - 개선: 메가캡 전용 SMB_mega 사용 (적절)")
    
    print(f"\n📊 베타 분포 개선:")
    print(f"   - 기존 SMB 베타 표준편차: {old_betas['beta_smb'].std():.3f}")
    print(f"   - 새로운 SMB_mega 베타 표준편차: {stage1_df['beta_smb_mega'].std():.3f}")
    print(f"   - 개선도: {(stage1_df['beta_smb_mega'].std() / old_betas['beta_smb'].std() - 1) * 100:.1f}%")
    
    print(f"\n🎯 Size Premium 결과:")
    print(f"   - 기존 방법: {old_results.loc[1, 'Annual_Premium']:.1f}% (t={old_results.loc[1, 't_statistic']:.2f})")
    print(f"   - 새로운 방법: {new_results['gamma_smb_mega']['annual_premium']:.1f}% (t={new_results['gamma_smb_mega']['t_stat']:.2f})")
    
    print(f"\n✅ 학술적 기여:")
    print(f"   - 방법론적 일관성 확보")
    print(f"   - 해석의 명확성 향상")
    print(f"   - 이론적 타당성 강화")
    
    return new_results, stage1_df, stage2_df

if __name__ == "__main__":
    results = main()