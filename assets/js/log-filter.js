// Filtering for the book and album logs (layouts "books" and "albums").
// The page renders every entry twice, by date and by person; this shows one
// view, hides entries below the minimum rating or off the chosen shelf (tag),
// hides headings left empty, and keeps the choice in the URL
// (?by=person&min=4&tag=mathematics).
(function () {
  var root = document.querySelector("[data-log]");
  if (!root) return;

  var status = root.querySelector(".log-status");
  var none = root.querySelector(".log-none");
  var byButtons = root.querySelectorAll(".log-by");
  var stars = root.querySelectorAll(".log-stars button");
  var views = root.querySelectorAll(".log-view");
  var shelf = root.querySelectorAll(".log-shelf-tag");
  var tagLinks = root.querySelectorAll(".log-tag");
  var known = Array.prototype.map.call(shelf, function (b) { return b.dataset.tag; });
  var noun = status.dataset.noun;

  var params = new URLSearchParams(location.search);
  var state = {
    by: params.get("by") === "person" ? "person" : "date",
    min: Math.min(5, Math.max(0, parseInt(params.get("min"), 10) || 0)),
    tag: params.get("tag") || "",
  };
  if (known.indexOf(state.tag) < 0) state.tag = "";

  function apply() {
    var shown = 0, total = 0;
    views.forEach(function (view) {
      var active = view.dataset.view === state.by;
      view.hidden = !active;
      view.querySelectorAll(".log-item").forEach(function (item) {
        var ok = parseFloat(item.dataset.rating) >= state.min &&
          (!state.tag || item.dataset.tags.split("|").indexOf(state.tag) >= 0);
        item.hidden = !ok;
        if (active) { total++; if (ok) shown++; }
      });
      view.querySelectorAll(".log-group").forEach(function (group) {
        group.hidden = !group.querySelector(".log-item:not([hidden])");
      });
    });

    byButtons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.by === state.by)); });
    stars.forEach(function (s) {
      var n = parseInt(s.dataset.min, 10);
      s.classList.toggle("on", n <= state.min);
      s.setAttribute("aria-pressed", String(n === state.min));
    });

    shelf.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.tag === state.tag)); });
    tagLinks.forEach(function (a) { a.classList.toggle("on", a.dataset.tag === state.tag); });

    status.textContent = state.min > 0 || state.tag ? "Showing " + shown + " of " + total + " " + noun + "." : "";
    none.hidden = shown > 0;

    var query = new URLSearchParams();
    if (state.by !== "date") query.set("by", state.by);
    if (state.min) query.set("min", state.min);
    if (state.tag) query.set("tag", state.tag);
    var search = query.toString();
    history.replaceState(null, "", location.pathname + (search ? "?" + search : "") + location.hash);
  }

  byButtons.forEach(function (b) {
    b.addEventListener("click", function () { state.by = b.dataset.by; apply(); });
  });
  stars.forEach(function (s) {
    s.addEventListener("click", function () {
      var n = parseInt(s.dataset.min, 10);
      state.min = state.min === n ? 0 : n; // clicking the chosen star clears it
      apply();
    });
  });
  shelf.forEach(function (b) {
    b.addEventListener("click", function () { state.tag = b.dataset.tag; apply(); });
  });
  tagLinks.forEach(function (a) {
    a.addEventListener("click", function () {
      state.tag = state.tag === a.dataset.tag ? "" : a.dataset.tag; // clicking the chosen tag clears it
      apply();
    });
  });
  root.querySelector(".log-clear").addEventListener("click", function () {
    state.min = 0; state.tag = ""; apply();
  });

  apply();
})();
