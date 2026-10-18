// GAP TIERS: classify every team label into one of three tiers.
//
// EDGE DIRECTIONS:
//   (Team)-[:GOVERNED]->(RFC)     team points AT rfc
//   (Team)-[:SUCCEEDED_BY]->(Team) archived points AT active successor
//
// tier 1 = ACTIVE      : the labelled team exists and is active
// tier 2 = SUCCESSOR   : archived, with a curated SUCCEEDED_BY edge to an active team
// tier 3 = TRUE_GAP    : archived with no successor, or no team file at all
MATCH (t:Team)
OPTIONAL MATCH (t)-[:SUCCEEDED_BY]->(succ:Team)
RETURN t.slug AS label,
       t.status AS status,
       CASE
         WHEN t.status = 'active' THEN 'ACTIVE'
         WHEN succ IS NOT NULL THEN 'SUCCESSOR'
         ELSE 'TRUE_GAP'
       END AS tier,
       succ.slug AS successor
ORDER BY tier, label
