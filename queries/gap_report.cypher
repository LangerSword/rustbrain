// GAP REPORT: every T-* label actually used by merged RFCs, with its tier and load.
//
// EDGE DIRECTIONS:
//   (Team)-[:GOVERNED]->(RFC)      team points AT rfc
//   (Team)-[:SUCCEEDED_BY]->(Team) archived points AT active successor
//
// The label list comes from RFC.team_labels (stored on the node), so a label with
// NO team file at all still appears here. That is the point: a label with no file
// is exactly the routing gap the product exists to surface.
MATCH (r:RFC)
UNWIND r.team_labels AS label
WITH label, count(DISTINCT r) AS rfcs
OPTIONAL MATCH (t:Team {slug: label})
OPTIONAL MATCH (t)-[:SUCCEEDED_BY]->(succ:Team)
RETURN label,
       rfcs,
       coalesce(t.status, 'NO_TEAM_FILE') AS status,
       CASE
         WHEN t IS NULL THEN 'TRUE_GAP'
         WHEN t.status = 'active' THEN 'ACTIVE'
         WHEN succ IS NOT NULL THEN 'SUCCESSOR'
         ELSE 'TRUE_GAP'
       END AS tier,
       succ.slug AS successor
ORDER BY tier, rfcs DESC
