# 消费者调研与市场洞察看板

这是一个面向快消品牌市场、市场研究、用户研究、消费者洞察和咨询岗位的市场研究项目。项目使用 Python 生成模拟消费者问卷数据，并整合品牌漏斗、NPS、人群聚类、开放题主题挖掘、价格敏感度和增长机会优先级排序。

数据为本地生成的模拟数据，代码为原创实现，未复制外部项目代码。

## 项目亮点

- 生成 5,200 份模拟消费者问卷样本。
- 覆盖人口属性、渠道、品类、品牌认知、考虑、试用、复购、NPS 和开放题反馈。
- 使用 KMeans 进行消费者分群。
- 使用 TF-IDF 和 NMF 对开放题反馈做主题挖掘。
- 计算品牌认知-考虑-试用-复购漏斗。
- 分析 NPS、满意度、支付意愿和价格敏感度。
- 输出细分人群画像、主题痛点、价格建议和机会地图。

## 项目结构

```text
.
|-- app.py                         # Streamlit 市场洞察看板
|-- data/                          # 模拟消费者问卷
|-- outputs/                       # 分群、主题、漏斗、价格和洞察报告
|-- scripts/
|   |-- generate_demo_data.py      # 生成模拟数据
|   `-- run_insights.py            # 运行洞察分析
|-- sql/
|   `-- market_research_queries.sql
|-- src/consumer_insights/
|   |-- analytics.py               # 分群、主题、漏斗、价格分析
|   `-- data.py                    # 数据生成与读取
`-- tests/
    `-- test_insights.py
```

## 快速开始

```bash
python -m pip install -r requirements.txt
python scripts/generate_demo_data.py
python scripts/run_insights.py
streamlit run app.py
python -m unittest discover -s tests
```

## 已生成样例结果

- 问卷样本：5,200
- 品牌认知率：64.69%
- 试用率：60.50%
- 复购率：64.31%
- NPS：24.87
- 平均支付意愿：26.28
- 样例最优演示价格点：20

## 输出文件

- `outputs/survey_kpis.json`：核心调研指标。
- `outputs/segment_profiles.csv`：消费者分群画像。
- `outputs/brand_funnel_overall.csv`：总体品牌漏斗。
- `outputs/brand_funnel_by_segment.csv`：分群品牌漏斗。
- `outputs/topic_terms.csv`：开放题主题词。
- `outputs/price_sensitivity.csv`：价格敏感度。
- `outputs/opportunity_map.csv`：机会优先级。
- `outputs/insights_report.md`：市场洞察摘要。
