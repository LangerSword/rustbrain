(() => {
  // motion/debug.js
  (function() {
    "use strict";
    var frame = document.getElementById("stage");
    var panel = document.getElementById("controls");
    var status = document.getElementById("status");
    function buildControls(rb) {
      while (panel.firstChild) panel.removeChild(panel.firstChild);
      rb.triggers().forEach(function(st, i) {
        if (frame.contentWindow.ScrollTrigger && typeof frame.contentWindow.ScrollTrigger.getAll === "function" && !frame.contentWindow.ScrollTrigger.getAll().includes(st)) return;
        var row = document.createElement("div");
        row.className = "row";
        var name = st.trigger ? st.trigger.id || String(st.trigger.className) || "?" : "?";
        var lab = document.createElement("span");
        lab.className = "lab";
        lab.textContent = "st" + i + " " + name + " [" + Math.round(st.start) + ".." + Math.round(st.end) + "]";
        var range = document.createElement("input");
        range.type = "range";
        range.min = 0;
        range.max = 1e3;
        range.value = 0;
        range.addEventListener("input", function() {
          var y = st.start + (st.end - st.start) * (range.value / 1e3);
          frame.contentWindow.scrollTo(0, y);
        });
        row.appendChild(lab);
        row.appendChild(range);
        panel.appendChild(row);
      });
      Object.keys(rb.scenes).forEach(function(name) {
        var tl = rb.scenes[name];
        var row = document.createElement("div");
        row.className = "row";
        var lab = document.createElement("span");
        lab.className = "lab";
        lab.textContent = name + " timeline";
        var range = document.createElement("input");
        range.type = "range";
        range.min = 0;
        range.max = 1e3;
        range.value = 0;
        range.addEventListener("input", function() {
          tl.pause();
          tl.progress(range.value / 1e3);
        });
        row.appendChild(lab);
        row.appendChild(range);
        panel.appendChild(row);
      });
    }
    function connect() {
      var rb = null;
      try {
        rb = frame.contentWindow.rbDebug;
      } catch (e) {
        rb = null;
      }
      if (!rb) {
        status.textContent = "waiting for the site bundle...";
        setTimeout(connect, 600);
        return;
      }
      status.textContent = "connected: " + Object.keys(rb.scenes).length + " scene timelines, " + rb.triggers().length + " scroll triggers";
      buildControls(rb);
    }
    frame.addEventListener("load", function() {
      setTimeout(connect, 300);
    });
  })();
})();
