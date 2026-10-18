# Element 8 is 0: the setting is a foundation, not a company

Checked 2026-10-19 against the pinned rust-lang/team tree and the snapshot.

- Team files that mention "manager": 4. They are `cargo.toml` (the Cargo package
  manager, in a description), `program.toml` and `leadership-council.toml` (both
  referencing the program-managers team), and `program-managers.toml` itself.
- Team files that mention the Foundation, hired roles or employees: 13 of 224,
  including `foundation-staff`, `foundation-board`, `foundation-smt`,
  `foundation-board-project-directors`, `funding-advisors`,
  `maintainers-in-residence`, `program-managers` and `crates-io-on-call`. The
  project itself describes some of these as funded roles, in the files' own words:

      teams/program-managers.toml:
      # This team includes the program managers hired by the Project
      # (via the Foundation) in support of program management.

      teams/crates-io-on-call.toml:
      # Note: This team is composed of employees of the Rust Foundation.

- Company-structure fields in data/snapshot.json (manager, revenue, customer,
  contract, salary): 0.

What is NOT in the data, and what element 8 is about: no revenue, no customer, no
contract, no salary, no reporting line. The teams are not an org chart; team leads
hold peer authority in a foundation project. That is why element 8 scores 0, by
nature rather than by omission.
