/* rustbrain site: the routing demo. Runs entirely from site/data.json, which is
   exported from the committed snapshot at build time (scripts/export_site_data.py)
   and asserted against it in CI (scripts/assert_site_numbers.py). No server. */

(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var resultBox = document.getElementById("demo");
  var tabs = document.querySelectorAll(".demo-tabs button[data-target]");
  if (!resultBox || !tabs.length) return;

  var cache = null;
  function load() {
    if (cache) return Promise.resolve(cache);
    return fetch("data.json").then(function (r) { return r.json(); }).then(function (d) {
      cache = d;
      return d;
    });
  }

  function rows(list, full) {
    var out = [];
    var n = full ? list.length : Math.min(5, list.length);
    for (var i = 0; i < n; i++) {
      var r = list[i];
      out.push("<tr><td>" + esc(r.handle) + "</td><td class=\"" + (r.role === "lead" ? "lead" : "") + "\">" +
        esc(r.role) + "</td><td class=\"num\">" + esc(r.authored) + "</td><td class=\"num\">" +
        esc(r.latest || "-") + "</td></tr>");
    }
    return out.join("");
  }

  function esc(v) {
    return String(v).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function labelRow(d, slug) {
    for (var t in d.gaps.tiers) {
      var ls = d.gaps.tiers[t];
      for (var i = 0; i < ls.length; i++) if (ls[i].label === slug) return { tier: t, row: ls[i] };
    }
    return null;
  }

  // The static result already holds the measured five rows; this adds the
  // "show all" expander on top, reading the same data.json. Created by JS so
  // a no-JS page never shows a control that cannot work.
  function enhanceAllReviewers() {
    var box = document.getElementById("demo");
    if (!box || box.querySelector("details.all-reviewers")) return;
    var det = document.createElement("details");
    det.className = "all-reviewers";
    var sum = document.createElement("summary");
    sum.textContent = "show all reviewers";
    det.appendChild(sum);
    var body = document.createElement("div");
    body.className = "all-reviewers-body";
    det.appendChild(body);
    load().then(function (d) {
      sum.textContent = "show all " + d.hero.reviewers.length + " reviewers";
    }).catch(function () {});
    det.addEventListener("toggle", function () {
      if (!det.open || body.getAttribute("data-filled")) return;
      body.setAttribute("data-filled", "1");
      load().then(function (d) {
        body.innerHTML = '<table class="reviewers"><thead><tr><th>handle</th><th>role</th>' +
          '<th class="num">authored</th><th class="num">latest</th></tr></thead><tbody>' +
          rows(d.hero.reviewers, true) + "</tbody></table>";
      }).catch(function () {});
    });
    box.appendChild(det);
  }

  function render(target) {
    return load().then(function (d) {
      // innerHTML is fed only this site's own precomputed data (site/data.json,
      // exported from the committed snapshot and asserted in CI); every field is
      // passed through esc() before it reaches the string. No user input exists.
      var html = "";
      if (target === "libs-api") {
        var e = d.hero.edge;
        html += "<h3>" + esc(d.hero.rfc_title) + "</h3>";
        html += "<div class=\"route\">RFC " + esc(d.hero.rfc) + " carries the label <b>T-libs-api</b>. " +
          "The team it names, <b>" + esc(e.from) + "</b>, is archived with 0 current members. " +
          "The graph follows <span class=\"hop\">SUCCEEDED_BY (RFC " + esc(e.rfc) + ", " + esc(e.source) + ")</span> " +
          "to <b>" + esc(e.to) + "</b>.</div>";
        html += "<table class=\"reviewers\"><thead><tr><th>handle</th><th>role</th>" +
          "<th class=\"num\">authored</th><th class=\"num\">latest</th></tr></thead><tbody>" +
          rows(d.hero.reviewers, false) + "</tbody></table>";
        html += "<div class=\"foot\">showing the first 5 of " + d.hero.reviewers.length +
          " reviewers, sorted by latest authored RFC. Tier: <span class=\"hop\">SUCCESSOR</span>.</div>";
      } else if (target === "T-cargo") {
        html += "<h3>label T-cargo</h3>";
        html += "<div class=\"route\"><b>cargo</b> is an active team; no successor hop needed.</div>";
        html += "<div class=\"foot\">42 merged RFCs carry this label. Full per-person rows are in " +
          "<a href=\"https://github.com/LangerSword/rustbrain/blob/main/out/blog_evidence/routing_examples.md\">routing_examples.md</a>.</div>";
      } else if (target === "T-dev-tools") {
        html += "<h3>label T-dev-tools</h3>";
        html += "<div class=\"gapbox\"><b class=\"gapflag\">true gap.</b> No team file exists for this label, " +
          "so there is nobody to route to. 20 merged RFCs carry it.</div>";
      }
      resultBox.innerHTML = html;
      if (target === "libs-api") enhanceAllReviewers();
      if (!reduce) {
        resultBox.style.opacity = "0";
        resultBox.style.transition = "opacity 200ms cubic-bezier(0.2,0.7,0.3,1)";
        requestAnimationFrame(function () { resultBox.style.opacity = "1"; });
      }
      for (var i = 0; i < tabs.length; i++) {
        tabs[i].setAttribute("aria-pressed", tabs[i].getAttribute("data-target") === target ? "true" : "false");
      }
    });
  }

  for (var i = 0; i < tabs.length; i++) {
    tabs[i].addEventListener("click", function (ev) { render(ev.currentTarget.getAttribute("data-target")); });
  }

  // Exposed for the motion layer: when GSAP is present, motion wraps render()
  // in a Flip transition and intercepts tab clicks; without it this file is
  // the whole demo, exactly as before.
  window.RB = { render: render, reduce: reduce };

  // the initial static result is the libs-api view: enhance it in place
  enhanceAllReviewers();
})();
