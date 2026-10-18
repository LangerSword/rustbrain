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
// the flipped one returns zero. Assertions live in scripts/test_queries.py.
//
// TRAP, measured 2026-10-19 on module ver 42201: a pattern EXPRESSION inside a CASE
// always evaluates truthy, so `CASE WHEN (p)-[:LEAD]->(o) THEN 'lead' ...` labels
// EVERY member as a lead. The working form collects the relationship types and
// tests membership with IN.
//
// params: $slug (the team label slug, lowercased, T- prefix stripped)

// Start at the labelled team, follow up to 3 successor hops to the CURRENT team,
// then list its current members. SUCCEEDED_BY*0..3 allows zero hops, so an
// already-active label routes straight through.
MATCH (labelled:Team {slug: $slug})
MATCH (labelled)-[:SUCCEEDED_BY*0..3]->(owner:Team)
WHERE owner.status = 'active'
MATCH (owner)<-[r:LEAD|MEMBER]-(p:Person)
OPTIONAL MATCH (p)-[:AUTHORED]->(authored:RFC)
WITH owner, p, collect(DISTINCT type(r)) AS kinds,
     count(DISTINCT authored) AS authored_count, max(authored.created) AS latest
RETURN owner.slug AS owner,
       p.handle AS handle,
       CASE WHEN 'LEAD' IN kinds THEN 'lead' ELSE 'member' END AS role,
       authored_count AS authored,
       coalesce(latest, '') AS latest
ORDER BY latest DESC, authored DESC, handle
