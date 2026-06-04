-- SQL examples for consumer and market research interviews.
-- Demo tables: demo_consumer_survey, segmented_survey, feedback_topics.

-- 1. Brand funnel by acquisition channel.
SELECT
    primary_channel,
    COUNT(*) AS respondents,
    AVG(awareness) AS awareness_rate,
    AVG(consideration) AS consideration_rate,
    AVG(trial) AS trial_rate,
    AVG(repeat_purchase) AS repeat_rate
FROM demo_consumer_survey
GROUP BY 1
ORDER BY repeat_rate DESC;

-- 2. NPS by segment.
SELECT
    segment,
    COUNT(*) AS respondents,
    AVG(nps) AS avg_nps,
    100.0 * AVG(CASE WHEN nps >= 9 THEN 1 ELSE 0 END)
      - 100.0 * AVG(CASE WHEN nps <= 6 THEN 1 ELSE 0 END) AS nps_score
FROM segmented_survey
GROUP BY 1
ORDER BY nps_score DESC;

-- 3. Topic pain points by segment.
SELECT
    s.segment,
    t.topic_id,
    COUNT(*) AS responses,
    AVG(s.nps) AS avg_nps,
    AVG(s.monthly_purchase_frequency) AS purchase_frequency
FROM segmented_survey s
JOIN feedback_topics t ON s.respondent_id = t.respondent_id
GROUP BY 1, 2
ORDER BY responses DESC;

