// Filtering for the book and album logs (layouts "books" and "albums").
// The page renders every entry twice, by date and by person; this shows one
// view, hides entries below the minimum rating, hides headings left empty, and
// keeps the choice in the URL (?by=person&min=4).
(function () {
  var root = document.querySelector("[data-log]");
  if (!root) return;

  var controls = root.querySelector(".log-controls");
  var status = root.querySelector(".log-status");
  var none = root.querySelector(".log-none");
  var byButtons = root.querySelectorAll(".log-by");
  var stars = root.querySelectorAll(".log-stars button");
  var views = root.querySelectorAll(".log-view");
  var noun = status.dataset.noun;

  var params = new URLSearchParams(location.search);
  var state = {
    by: params.get("by") === "person" ? "person" : "date",
    min: Math.min(5, Math.max(0, parseInt(params.get("min"), 10) || 0)),
  };

  function apply() {
    var shown = 0, total = 0;
    views.forEach(function (view) {
      var active = view.dataset.view === state.by;
      view.hidden = !active;
      view.querySelectorAll(".log-item").forEach(function (item) {
        var ok = parseFloat(item.dataset.rating) >= state.min;
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

    status.textContent = state.min > 0 ? "Showing " + shown + " of " + total + " " + noun + "." : "";
    none.hidden = shown > 0;

    var query = new URLSearchParams();
    if (state.by !== "date") query.set("by", state.by);
    if (state.min) query.set("min", state.min);
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
  root.querySelector(".log-clear").addEventListener("click", function () {
    state.min = 0; apply();
  });

  controls.hidden = false;
  apply();
})();
