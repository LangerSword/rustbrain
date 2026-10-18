# UI screenshots, captions

All three were captured from the clean-clone server (comments in clean_clone.md) at
1280 CSS px wide, device scale factor 2, so every image is 2560 px wide and the
15 px page font lands at 30 px of raster. Handles only, no names, no tokens.

(a) ui_rfc1892_successor_hop.png
    RFC PR 1892 routed by its labels: T-lang resolves to an active team with no hop,
    and T-libs-api is archived with 0 members, so the graph follows
    SUCCEEDED_BY to libs (RFC 3984, teams/archive/libs-api.toml:1) and lists the 37
    current libs reviewers sorted by latest authored RFC.

(b) ui_true_gap_dev_tools.png
    T-dev-tools is a true gap: 20 merged RFCs carry the label, no team file exists
    anywhere, and the UI says so instead of returning an empty result.

(c) ui_active_team_cargo.png
    T-cargo is an ordinary route: 42 merged RFCs, the team is active, no successor
    hop needed, reviewers sorted by latest activity with leads flagged.
