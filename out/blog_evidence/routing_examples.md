# Routing examples, saved command outputs

Run 2026-10-19 against the loaded graph. Handles only, no names, no email addresses.

## $ python3 cmd/route.py 1892

RFC PR 1892: an RFC labelled T-lang and T-libs-api

```
========================================================================
T-lang  (RFC #1892: Deprecate uninitialized in favor of a new MaybeUninit type)
  route: lang (active), no successor hop needed   [tier ACTIVE]
  5 current members, sorted by latest authored RFC:
    handle                 role     authored   latest
    nikomatsakis           member   51         2026-03-25
    joshtriplett           member   16         2026-02-23
    scottmcm               member   3          2024-10-30
    traviscross            member   3          2024-04-24
    tmandry                lead     3          2023-04-27
========================================================================
T-libs-api  (RFC #1892: Deprecate uninitialized in favor of a new MaybeUninit type)
  route: libs-api (archived) --SUCCEEDED_BY--> libs   [tier SUCCESSOR, 1 hop(s)]
  37 current members, sorted by latest authored RFC:
    handle                 role     authored   latest
    nia-e                  lead     1          2026-07-15
    folkertdev             member   1          2026-07-01
    joshtriplett           member   16         2026-02-23
    davidtwco              member   4          2025-10-31
    Darksonn               member   3          2025-08-10
    m-ou-se                member   9          2024-10-30
    Amanieu                lead     13         2024-05-03
    tgross35               member   2          2023-09-09
    jhpratt                member   4          2023-07-13
    thomcc                 member   1          2022-08-30
    JohnTitor              member   1          2022-05-25
    ibraheemdev            member   1          2021-06-03
    sunfishcode            member   1          2021-05-25
    Mark-Simulacrum        member   1          2020-12-17
    KodrAus                member   3          2020-08-28
    yaahc                  member   1          2020-07-23
    SimonSapin             member   14         2018-10-27
    kennytm                member   3          2018-07-14
    hanna-kruppe           member   1          2017-12-29
    cuviper                member   1          2017-09-14
    cramertj               member   3          2017-08-28
    clarfonthey            member   1          2017-05-25
    BurntSushi             member   2          2016-05-18
    Byron                  member   0          -
    ChrisDenton            member   0          -
    LawnGnome              member   0          -
    NobodyXu               member   0          -
    aapoalas               member   0          -
    adamgemmell            member   0          -
    bushrat011899          member   0          -
    calebzulawski          member   0          -
    dtolnay                member   0          -
    joboet                 member   0          -
    programmerjake         member   0          -
    sayantn                member   0          -
    the8472                member   0          -
    workingjubilee         member   0          -
```

## $ python3 cmd/route.py T-libs-api

label T-libs-api: archived team, successor hop

```
========================================================================
T-libs-api
  merged RFCs carrying this label: 138
  route: libs-api (archived) --SUCCEEDED_BY--> libs   [tier SUCCESSOR, 1 hop(s)]
  37 current members, sorted by latest authored RFC:
    handle                 role     authored   latest
    nia-e                  lead     1          2026-07-15
    folkertdev             member   1          2026-07-01
    joshtriplett           member   16         2026-02-23
    davidtwco              member   4          2025-10-31
    Darksonn               member   3          2025-08-10
    m-ou-se                member   9          2024-10-30
    Amanieu                lead     13         2024-05-03
    tgross35               member   2          2023-09-09
    jhpratt                member   4          2023-07-13
    thomcc                 member   1          2022-08-30
    JohnTitor              member   1          2022-05-25
    ibraheemdev            member   1          2021-06-03
    sunfishcode            member   1          2021-05-25
    Mark-Simulacrum        member   1          2020-12-17
    KodrAus                member   3          2020-08-28
    yaahc                  member   1          2020-07-23
    SimonSapin             member   14         2018-10-27
    kennytm                member   3          2018-07-14
    hanna-kruppe           member   1          2017-12-29
    cuviper                member   1          2017-09-14
    cramertj               member   3          2017-08-28
    clarfonthey            member   1          2017-05-25
    BurntSushi             member   2          2016-05-18
    Byron                  member   0          -
    ChrisDenton            member   0          -
    LawnGnome              member   0          -
    NobodyXu               member   0          -
    aapoalas               member   0          -
    adamgemmell            member   0          -
    bushrat011899          member   0          -
    calebzulawski          member   0          -
    dtolnay                member   0          -
    joboet                 member   0          -
    programmerjake         member   0          -
    sayantn                member   0          -
    the8472                member   0          -
    workingjubilee         member   0          -
```

## $ python3 cmd/route.py T-dev-tools

label T-dev-tools: true gap

```
========================================================================
T-dev-tools
  merged RFCs carrying this label: 20
  ROUTING GAP: TRUE_GAP.
  There is no active team for this label, so there is nobody to route to.
```

## $ python3 cmd/route.py T-cargo

label T-cargo: ordinary active team

```
========================================================================
T-cargo
  merged RFCs carrying this label: 42
  route: cargo (active), no successor hop needed   [tier ACTIVE]
  8 current members, sorted by latest authored RFC:
    handle                 role     authored   latest
    epage                  member   13         2026-04-06
    joshtriplett           member   16         2026-02-23
    arlosi                 member   2          2022-07-05
    Eh2406                 lead     1          2022-02-15
    0xPoe                  member   0          -
    Muscraft               member   0          -
    ranger-ross            member   0          -
    weihanglo              lead     0          -
```
