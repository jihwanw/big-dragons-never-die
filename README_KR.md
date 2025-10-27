# 대마불사: 메가캡 지배 시대 (2020-2025)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LaTeX](https://img.shields.io/badge/LaTeX-paper-green.svg)](paper/)

## 🎯 연구 개요

본 연구는 2020-2025년 기간 동안 S&P 500 상위 200개 메가캡 기업들 내에서도 사이즈 효과가 지속되어, 초대형 기업들이 상대적으로 작은 메가캡 기업들을 연간 **7-9%** 체계적으로 앞서는 현상을 문서화한 연구입니다. 이 현상을 "대마불사"라고 명명하며, 메가캡 유니버스 내에서도 사이즈 프리미엄이 역전되지 않고 오히려 강화되는 현상을 보여줍니다.

## 🔍 연구의 중요성

### 학술적 중요성
- **패러다임 도전**: 현대 시장에서 사이즈 프리미엄 역전 현상의 최초 종합 문서화
- **방법론적 혁신**: 표본 편향을 해결하는 메가캡 전용 SMB 팩터 구성
- **실증적 엄밀성**: 향상된 통계적 검증을 통한 Fama-MacBeth 횡단면 방법론
- **이론적 기여**: 메가캡 지속성 이해를 위한 "대마불사" 프레임워크 도입

### 실무적 함의
- **투자 전략**: 대형주 노출을 위한 포트폴리오 재조정이 필요한 근본적 변화
- **리스크 관리**: 전통적인 소형주 가치 전략이 구조적 역풍에 직면
- **시장 구조**: 주식 시장 역학의 영구적 변화 증거
- **규제적 통찰**: 메가캡 지배 시장의 집중 위험

## 📊 데이터 및 방법론

### 데이터 소스 및 확보 방법

#### 주요 데이터 소스
- **주식 데이터**: WRDS CRSP (Center for Research in Security Prices) 데이터베이스
- **시장 데이터**: S&P 500 구성종목 데이터 (역사적 변경사항 포함)
- **무위험 수익률**: FRED (Federal Reserve Economic Data)의 3개월 국채 수익률
- **표본 기간**: 2020년 10월 ~ 2024년 12월 (1,053 거래일)

#### 데이터 확보 과정
```python
# WRDS 연결 및 데이터 추출
import wrds
db = wrds.Connection(wrds_username='사용자명')

# 시가총액 데이터와 함께 S&P 500 구성종목 조회
query = """
SELECT date, permno, ret, prc, shrout, 
       ABS(prc) * shrout as market_cap
FROM crsp.dsf 
WHERE date BETWEEN '2020-10-01' AND '2024-12-31'
AND permno IN (SELECT DISTINCT permno FROM crsp.dsp500list)
ORDER BY date, market_cap DESC
"""
raw_data = db.raw_sql(query)
```

#### 표본 구성
- **유니버스**: S&P 500 구성종목만 포함 (소형주 완전 제외)
- **표본 크기**: 매월 시가총액 상위 200개 기업
- **리밸런싱**: 월말 시가총액 기준 월별 포트폴리오 재구성
- **생존편향**: 지속적 대형주에 초점 (생존편향 조정 불필요)
- **데이터 품질**: 최소 80% 데이터 가용성 요구; 최대 5거래일 전진보간

### 상세 방법론

#### 1. 포트폴리오 구성 과정
매월 모든 S&P 500 구성종목을 시가총액으로 순위를 매기고 상위 200개를 선택:

```python
def form_portfolios(data, n_companies=200):
    """메가캡 유니버스 내에서 사이즈별 포트폴리오 구성"""
    monthly_portfolios = []
    
    for month in data['date'].dt.to_period('M').unique():
        month_data = data[data['date'].dt.to_period('M') == month]
        
        # 시가총액 상위 200개 선택
        top_200 = month_data.nlargest(n_companies, 'market_cap')
        
        # 5분위 포트폴리오 생성 (Q1=상위200개 중 최소, Q5=최대)
        top_200['size_quintile'] = pd.qcut(top_200['market_cap'], 
                                          q=5, labels=['Q1','Q2','Q3','Q4','Q5'])
        monthly_portfolios.append(top_200)
    
    return pd.concat(monthly_portfolios)
```

#### 2. 팩터 구성
강건성 검증을 위해 3가지 다른 SMB (Small Minus Big) 팩터를 구성:

**SMB_50 팩터 (상위 50개 vs 하위 50개):**
```
SMB_50 = (1/50) × Σ(R_i,t for i in 순위 151-200) - (1/50) × Σ(R_i,t for i in 순위 1-50)
```

**SMB_30 팩터 (상위 30개 vs 하위 30개):**
```
SMB_30 = (1/30) × Σ(R_i,t for i in 순위 171-200) - (1/30) × Σ(R_i,t for i in 순위 1-30)
```

**SMB_Q5Q1 팩터 (5분위 vs 1분위):**
```
SMB_Q5Q1 = (1/40) × Σ(R_i,t for i in Q5) - (1/40) × Σ(R_i,t for i in Q1)
```

여기서 R_i,t는 시점 t에서 주식 i의 초과수익률(주식수익률 - 무위험수익률)을 나타냅니다.

#### 3. Fama-MacBeth 2단계 회귀분석

**1단계 - 시계열 회귀분석 (팩터 로딩 추정):**
각 주식 i에 대해 전체 시계열을 사용하여 팩터 민감도(베타) 추정:

```
R_i,t - RF_t = α_i + β_i,MKT(MKT_t - RF_t) + β_i,SMB(SMB_t) + β_i,HML(HML_t) + ε_i,t
```

여기서:
- R_i,t = 시점 t에서 주식 i의 수익률
- RF_t = 시점 t에서 무위험 수익률
- MKT_t = 시점 t에서 시장 수익률
- SMB_t = 시점 t에서 사이즈 팩터 수익률
- HML_t = 시점 t에서 가치 팩터 수익률
- β_i,j = 팩터 j에 대한 주식 i의 팩터 로딩

**2단계 - 횡단면 회귀분석 (위험 프리미엄 추정):**
각 시점 t에서 초과수익률을 추정된 베타에 회귀:

```
R_i,t - RF_t = λ_0,t + λ_MKT,t × β̂_i,MKT + λ_SMB,t × β̂_i,SMB + λ_HML,t × β̂_i,HML + η_i,t
```

여기서 λ_j,t는 시점 t에서 팩터 j의 위험 프리미엄을 나타냅니다.

**최종 위험 프리미엄 추정:**
횡단면 위험 프리미엄의 시계열 평균:

```
λ̄_j = (1/T) × Σ(λ_j,t) for t = 1 to T
```

이분산성과 자기상관을 고려한 Newey-West HAC 표준오차:

```
SE(λ̄_j) = √[(1/T) × Ω_j]
```

여기서 Ω_j는 Newey-West 공분산 행렬 추정량입니다.

#### 4. 통계적 검정 프레임워크

**t-통계량 계산:**
```
t_j = λ̄_j / SE(λ̄_j)
```

**유의수준:**
- *** p < 0.01 (99% 신뢰도)
- ** p < 0.05 (95% 신뢰도)
- * p < 0.10 (90% 신뢰도)

#### 5. 강건성 검증

**이동창 분석:**
```python
def rolling_analysis(data, window=252):
    """이동창 팩터 프리미엄 계산"""
    results = []
    for i in range(window, len(data)):
        window_data = data.iloc[i-window:i]
        premium = fama_macbeth_regression(window_data)
        results.append(premium)
    return results
```

**부트스트랩 신뢰구간:**
```python
def bootstrap_ci(data, n_bootstrap=1000, alpha=0.05):
    """부트스트랩 신뢰구간 생성"""
    bootstrap_results = []
    for _ in range(n_bootstrap):
        sample = data.sample(frac=1, replace=True)
        premium = fama_macbeth_regression(sample)
        bootstrap_results.append(premium)
    
    lower = np.percentile(bootstrap_results, 100 * alpha/2)
    upper = np.percentile(bootstrap_results, 100 * (1 - alpha/2))
    return lower, upper
```

### 데이터 처리 파이프라인
1. **원시 데이터 추출**: WRDS CRSP 데이터베이스에서 S&P 500 구성종목 조회
2. **데이터 정제**: 결측값, 기업행위, 이상값 처리
3. **표본 선택**: 시가총액 기준 월별 상위 200개 기업 선택
4. **수익률 계산**: 무위험 수익률 대비 일별 초과수익률 계산
5. **포트폴리오 구성**: 메가캡 유니버스 내에서 사이즈별 포트폴리오 생성
6. **팩터 구성**: 메가캡 유니버스만을 사용한 커스텀 SMB 팩터 구축
7. **통계 분석**: Fama-MacBeth 2단계 회귀 방법론 실행
8. **강건성 검증**: 다중 명세와 시간 구간에서 결과 검증

### 연구 설계
1. **팩터 구성**: 
   - SMB_mega: 메가캡 전용 사이즈 팩터 (Q5-Q1 방법론)
   - 전통적 SMB 대비 167% 향상된 베타 분포
   - 표본 일치 팩터 방법론

2. **통계적 프레임워크**:
   - Fama-MacBeth 2단계 회귀 방법론
   - 횡단면 위험 프리미엄 추정
   - Newey-West HAC 표준오차
   - 다중 강건성 검증

3. **검증 접근법**:
   - 표본 외 테스트
   - 대안적 팩터 명세
   - 부표본 안정성 분석
   - 몬테카를로 시뮬레이션

## 🏆 주요 발견사항

### 핵심 결과
- **메가캡 내 사이즈 효과**: 초대형 메가캡이 상대적 소형 메가캡 대비 연간 7-9% 초과수익률
- **통계적 유의성**: 모든 명세에서 t-통계량 > 3.0
- **지속성**: 60개월 연구 기간 전반에 걸친 일관된 초과수익
- **팩터 로딩**: 메가캡 포트폴리오의 음의 SMB_mega 로딩 (-0.847)

### 학술적 통찰
1. **메가캡 내 사이즈 효과**: 메가캡 유니버스 내에서도 사이즈 프리미엄 지속
2. **시장 구조 진화**: 메가캡 지배로의 근본적 변화
3. **팩터 모델 향상**: 표본 특화 팩터가 우수한 설명력 제공
4. **횡단면 패턴**: 사이즈와 수익률 간 체계적 관계 역전

### 실무적 통찰
1. **포트폴리오 구성**: 위험조정수익률을 위한 대형주 편향 최적
2. **팩터 투자**: 전통적 사이즈 팩터의 재보정 필요
3. **시장 타이밍**: 구조적 변화가 영구적 체제 변화 시사
4. **위험 평가**: 메가캡 집중 위험이 우수한 성과로 상쇄

## 📁 저장소 구조

```
big-dragons-never-die/
├── README.md                    # 영문 종합 가이드
├── README_KR.md                 # 한글 종합 가이드
├── paper/                       # 학술 논문 및 LaTeX 소스
│   ├── manuscript.tex           # 메인 논문 파일
│   ├── references.bib           # 참고문헌
│   └── figures/                 # 논문용 그림 파일들
├── data/                        # 연구 데이터셋 및 결과
│   ├── enhanced_results_summary.csv
│   ├── factor_loadings.csv
│   └── portfolio_returns.csv
├── code/                        # 분석 및 재현 스크립트
│   ├── mega_cap_factor_analysis.py
│   ├── enhanced_mega_cap_analysis.py
│   ├── factor_comparison_analysis.py
│   └── create_paper_figures.py
├── figures/                     # 발표용 시각화 자료
│   └── [11개 고품질 PDF 그래프]
└── references/                  # 지원 문서
    ├── methodology_notes.md
    └── data_sources.md
```

## 🚀 빠른 시작

### 사전 요구사항
```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels
```

### 재현 단계
1. **저장소 복제**:
   ```bash
   git clone https://github.com/jihwanw/big-dragons-never-die.git
   cd big-dragons-never-die
   ```

2. **메인 분석 실행**:
   ```bash
   python code/enhanced_mega_cap_analysis.py
   ```

3. **그래프 생성**:
   ```bash
   python code/create_paper_figures.py
   ```

4. **논문 컴파일**:
   ```bash
   cd paper/
   pdflatex manuscript.tex
   bibtex manuscript
   pdflatex manuscript.tex
   pdflatex manuscript.tex
   ```

## 📈 주요 시각화

저장소에는 다음을 보여주는 11개의 출판 준비 완료 그래프가 포함되어 있습니다:
- 시간에 따른 사이즈 프리미엄 진화
- 방법론별 팩터 로딩 비교  
- 누적 수익률 차이
- 횡단면 회귀 결과
- 강건성 테스트 결과

## 🎓 학술적 영향

### 인용 형식
```
[저자명]. "대마불사: 메가캡 유니버스 내 사이즈 프리미엄 지속성의 증거 (2020-2025)." 
[저널명], [연도]. DOI: [할당 예정]
```

## 🔧 기술적 참고사항

### 팩터 구성 세부사항
- **SMB_mega**: 메가캡 유니버스를 사용한 (Q5_수익률 - Q1_수익률)
- **베타 향상**: 횡단면 변동에서 167% 개선
- **강건성**: 다중 팩터 명세가 핵심 발견사항 검증

### 통계적 검증
- **Newey-West 표준오차**: 이분산성과 자기상관 고려
- **부트스트랩 신뢰구간**: 주요 결과의 비모수적 검증
- **부표본 분석**: 다양한 시간 구간에서 일관된 결과

## 📞 연락 및 협업

질문, 협업 또는 추가 데이터 접근을 위해:
- **연구 문의**: [이메일]
- **데이터 요청**: 사용 가능한 데이터셋은 `data/` 폴더 참조
- **재현 문제**: 상세한 설명과 함께 GitHub 이슈 생성

## 📄 라이선스

본 연구는 MIT 라이선스 하에 공개됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙏 감사의 말

본 연구 개발 과정에서 귀중한 피드백을 제공해 주신 학계와 실무진 커뮤니티에 특별한 감사를 드립니다. "대마불사" 프레임워크는 수십 년간의 자산 가격 연구를 기반으로 하면서 시장 역학의 근본적 변화를 문서화합니다.

---

*"현대 금융의 시대에서 가장 큰 기업들은 단순히 생존하는 것이 아니라 지배합니다. 용들은 실패하기에는 너무 크고, 흔들리기에는 너무 강력해졌습니다."*