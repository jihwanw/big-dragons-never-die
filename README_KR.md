# 대마불사: 메가캡 지배 시대 (2020-2025)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LaTeX](https://img.shields.io/badge/LaTeX-paper-green.svg)](paper/)

## 🎯 연구 개요

본 연구는 2020-2025년 기간 동안 메가캡 주식이 소형주를 연간 **24.65%**라는 전례 없는 수익률로 체계적으로 앞서는 현상을 종합적으로 문서화한 연구입니다. 이 현상을 "대마불사"라고 명명하며, 수십 년간 확립된 금융 이론의 사이즈 프리미엄에 도전하는 내용입니다.

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

### 데이터 소스
- **주요 데이터셋**: S&P 500 구성종목 (2020-2025)
- **표본 크기**: 시가총액 상위 200개 기업
- **빈도**: 월별 포트폴리오 리밸런싱을 통한 일별 수익률
- **위험 팩터**: 커스텀 SMB 팩터들 (SMB_50, SMB_30, SMB_Q5Q1) 및 전통적 Fama-French 팩터

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
- **메가캡 초과수익**: 소형주 대비 연간 24.65% 초과수익률
- **통계적 유의성**: 모든 명세에서 t-통계량 > 3.0
- **지속성**: 60개월 연구 기간 전반에 걸친 일관된 초과수익
- **팩터 로딩**: 메가캡 포트폴리오의 음의 SMB_mega 로딩 (-0.847)

### 학술적 통찰
1. **사이즈 프리미엄 역전**: 전통적인 소형주 우위 완전 소멸
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

### 목표 저널
- **1순위**: Finance Research Letters (FRL)
- **2순위**: Journal of Financial Economics, Review of Financial Studies
- **대안**: PLoS One, Financial Management

### 인용 형식
```
[저자명]. "대마불사: 메가캡 지배와 사이즈 프리미엄 역전의 증거 (2020-2025)." 
Finance Research Letters, [연도]. DOI: [할당 예정]
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