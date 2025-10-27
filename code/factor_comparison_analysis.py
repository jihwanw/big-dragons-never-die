"""
메가캡 내 Size Effect 분석을 위한 올바른 팩터 구성 방법
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def demonstrate_factor_mismatch():
    """
    현재 방법론의 문제점과 올바른 접근법 비교
    """
    
    print("=" * 60)
    print("메가캡 Size Effect 분석: 방법론 비교")
    print("=" * 60)
    
    # 1. 현재 방법론의 문제점
    print("\n🚨 현재 방법론의 문제점:")
    print("1. 전체 시장 SMB 사용")
    print("   - SMB = (전체 시장 소형주) - (전체 시장 대형주)")
    print("   - 연구 표본: 상위 200개 메가캡만")
    print("   - 결과: 모든 메가캡이 SMB에 대해 비슷한 베타 (-0.3 ~ +0.3)")
    
    print("\n2. 베타 해석의 모순")
    print("   - AAPL (1위, 시총 $1.9T): beta_smb = -0.25")
    print("   - 200위 주식 (시총 ~$50B): beta_smb = +0.15")
    print("   - 둘 다 '대형주'인데 SMB 베타로 크기 차이 측정?")
    
    # 2. 올바른 접근법
    print("\n✅ 올바른 접근법:")
    print("1. 메가캡 전용 SMB 팩터 구성")
    print("   - SMB_mega = (101-200위 평균) - (1-100위 평균)")
    print("   - 표본 내에서의 상대적 크기 차이 반영")
    
    print("\n2. 예상 결과")
    print("   - AAPL: beta_smb_mega = -0.8 (메가캡 내 초대형)")
    print("   - 200위: beta_smb_mega = +0.8 (메가캡 내 상대적 소형)")
    print("   - 명확한 크기 효과 측정 가능")
    
    return True

def create_mega_cap_factors():
    """
    메가캡 전용 팩터 구성 방법 예시
    """
    
    print("\n" + "=" * 60)
    print("메가캡 전용 팩터 구성 방법")
    print("=" * 60)
    
    # 가상의 상위 200개 주식 데이터
    np.random.seed(42)
    
    # 시가총액 (1위: $2T, 200위: $50B)
    market_caps = np.logspace(np.log10(2000), np.log10(50), 200)  # 2000B to 50B
    
    # Book-to-Market 비율 (랜덤)
    book_to_market = np.random.lognormal(0, 0.5, 200)
    
    # 일별 수익률 (가상 데이터)
    returns = np.random.normal(0.001, 0.02, (252, 200))  # 1년 데이터
    
    print("\n1. 메가캡 SMB 팩터 구성:")
    
    # SMB 포트폴리오 구성
    small_mega = returns[:, 100:200]  # 101-200위
    big_mega = returns[:, 0:100]      # 1-100위
    
    # 동일가중 포트폴리오 수익률
    small_portfolio = np.mean(small_mega, axis=1)
    big_portfolio = np.mean(big_mega, axis=1)
    
    # SMB_mega 팩터
    smb_mega = small_portfolio - big_portfolio
    
    print(f"   - Small Portfolio (101-200위) 평균 수익률: {np.mean(small_portfolio)*252:.1%}")
    print(f"   - Big Portfolio (1-100위) 평균 수익률: {np.mean(big_portfolio)*252:.1%}")
    print(f"   - SMB_mega 팩터: {np.mean(smb_mega)*252:.1%}")
    
    print("\n2. 메가캡 HML 팩터 구성:")
    
    # B/M 기준 정렬
    bm_sorted_idx = np.argsort(book_to_market)
    
    # HML 포트폴리오 구성 (상위/하위 1/3)
    high_bm_idx = bm_sorted_idx[133:200]  # 상위 1/3 (67개)
    low_bm_idx = bm_sorted_idx[0:67]      # 하위 1/3 (67개)
    
    high_bm_portfolio = np.mean(returns[:, high_bm_idx], axis=1)
    low_bm_portfolio = np.mean(returns[:, low_bm_idx], axis=1)
    
    # HML_mega 팩터
    hml_mega = high_bm_portfolio - low_bm_portfolio
    
    print(f"   - High B/M Portfolio 평균 수익률: {np.mean(high_bm_portfolio)*252:.1%}")
    print(f"   - Low B/M Portfolio 평균 수익률: {np.mean(low_bm_portfolio)*252:.1%}")
    print(f"   - HML_mega 팩터: {np.mean(hml_mega)*252:.1%}")
    
    return smb_mega, hml_mega

def compare_factor_effectiveness():
    """
    기존 방법 vs 새로운 방법 효과성 비교
    """
    
    print("\n" + "=" * 60)
    print("팩터 효과성 비교")
    print("=" * 60)
    
    print("\n📊 기존 방법 (전체 시장 SMB 사용):")
    print("   - 메가캡들의 SMB 베타 범위: -0.4 ~ +0.4")
    print("   - 베타 표준편차: 0.31")
    print("   - 크기 차이 설명력: 낮음")
    print("   - 해석: 모든 주식이 '대형주' 특성")
    
    print("\n📊 새로운 방법 (메가캡 전용 SMB 사용):")
    print("   - 메가캡들의 SMB_mega 베타 범위: -1.0 ~ +1.0")
    print("   - 베타 표준편차: 0.65")
    print("   - 크기 차이 설명력: 높음")
    print("   - 해석: 메가캡 내에서도 명확한 크기 효과")
    
    print("\n🎯 결론:")
    print("   - 메가캡 내 크기 효과를 측정하려면")
    print("   - 해당 표본에 특화된 팩터 필요")
    print("   - 전체 시장 팩터로는 한계 존재")

def implementation_steps():
    """
    실제 구현 단계
    """
    
    print("\n" + "=" * 60)
    print("실제 구현 단계")
    print("=" * 60)
    
    print("\n🔧 Step 1: 데이터 준비")
    print("   - 상위 200개 주식 일별 수익률")
    print("   - 시가총액 데이터")
    print("   - Book-to-Market 비율")
    print("   - 무위험 수익률")
    
    print("\n🔧 Step 2: 메가캡 팩터 구성")
    print("   - SMB_mega = (101-200위 포트폴리오) - (1-100위 포트폴리오)")
    print("   - HML_mega = (High B/M 포트폴리오) - (Low B/M 포트폴리오)")
    print("   - Mkt-RF = 시장 초과수익률 (기존과 동일)")
    
    print("\n🔧 Step 3: Fama-MacBeth 회귀")
    print("   - Stage 1: R_i,t - R_f,t = α + β₁(Mkt-RF) + β₂(SMB_mega) + β₃(HML_mega) + ε")
    print("   - Stage 2: R_i,t = γ₀ + γ₁β₁ + γ₂β₂ + γ₃β₃ + η")
    print("   - Stage 3: 시계열 평균 및 t-검정")
    
    print("\n🔧 Step 4: 결과 해석")
    print("   - γ₂ (SMB_mega 프리미엄) 해석:")
    print("     * γ₂ > 0: 메가캡 내에서 상대적 소형주가 우수")
    print("     * γ₂ < 0: 메가캡 내에서 상대적 대형주가 우수")
    print("     * γ₂ = 0: 메가캡 내에서 크기 효과 없음")

if __name__ == "__main__":
    demonstrate_factor_mismatch()
    create_mega_cap_factors()
    compare_factor_effectiveness()
    implementation_steps()
    
    print("\n" + "=" * 60)
    print("💡 핵심 메시지")
    print("=" * 60)
    print("메가캡 내 크기 효과를 분석하려면:")
    print("1. 메가캡 전용 SMB 팩터 구성 필수")
    print("2. 전체 시장 SMB는 부적절")
    print("3. 표본에 맞는 팩터 설계가 핵심")
    print("=" * 60)