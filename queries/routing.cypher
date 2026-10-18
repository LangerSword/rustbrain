// ROUTING: given a team label slug, find who should review.
//
// EDGE DIRECTIONS, pinned to how the ingest creates them (scripts/load_graph.py):
//   (Person)-[:MEMBER]->(Team)          person points AT team
//   (Person)-[:LEAD]->(Team)            person points AT team, lead role
//   (Person)-[:AUTHORED]->(RFC)         person points AT rfc
//   (Team)-[:GOVERNED]->(RFC)           team points AT rfc
//   (Team)-[:SUCCEEDED_BY]->(Team)      archived team points AT its active successor
//
// A pattern that matches nothing returns ZERO ROWS with no error, so every
// direction below was verified by running both forms: the correct one returns rows,
// the flipped one returns zero. See tests in scripts/test_queries.py.
//
// params: $slug (the team label slug, lowercased, T- prefix stripped)

// Start at the labelled team, follow up to 3 successor hops to the CURRENT team,
// then list its current members. SUCCEEDED_BY*0..3 means the first hop may be zero
// when the labelled team is already active.
MATCH (labelled:Team {slug: $slug})
MATCH (labelled)-[:SUCCEEDED_BY*0..3]->(owner:Team)
WHERE owner.status = 'active'
MATCH (owner)<-[:LEAD|MEMBER]-(p:Person)
OPTIONAL MATCH (p)-[:AUTHORED]->(authored:RFC)
OPTIONAL MATCH (approved:RFC)-[:GOVERNED]->(owner)
WITH owner, p, count(DISTINCT authored) AS authored_count,
     max(authored.created) AS authored_latest
RETURN owner.slug AS owner_team,
       p.handle AS handle,
       CASE WHEN (p)-[:LEAD]->(owner) THEN 'lead' ELSE 'member' END AS role,
       authored_count,
       authored_latest
ORDER BY authored_latest DESC, authored_count DESC, handle
