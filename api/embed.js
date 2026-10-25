/*! Hot Quesadillas embed: a question of the day for any website.
 *  <div data-hq-embed></div>
 *  <script src="https://jimmy-grafton.github.io/quiz-night-console/api/embed.js" async></script>
 *  Options on the div: data-theme="light|dark", data-type="geography" (a type slug)
 */
(function () {
  var BASE = "https://jimmy-grafton.github.io/quiz-night-console/";
  var css = ".hq-card{all:initial;display:block;box-sizing:border-box;max-width:420px;padding:22px 22px 18px;border:1px solid #0b0b0b;background:#fff;color:#0b0b0b;font:15px/1.5 -apple-system,'Helvetica Neue',Arial,sans-serif}" +
    ".hq-card[data-theme=dark]{background:#0b0b0b;color:#f4f4f4;border-color:#f4f4f4}" +
    ".hq-card *{box-sizing:border-box}" +
    ".hq-top{display:flex;justify-content:space-between;gap:10px;font:11px/1 ui-monospace,Menlo,monospace;letter-spacing:.14em;text-transform:uppercase;opacity:.65}" +
    ".hq-q{display:block;margin:14px 0 16px;font:22px/1.25 Georgia,'Iowan Old Style',serif}" +
    ".hq-row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}" +
    ".hq-btn{all:unset;cursor:pointer;padding:9px 14px;border:1px solid currentColor;font:600 13px/1 -apple-system,'Helvetica Neue',Arial,sans-serif}" +
    ".hq-btn:hover{background:#0b0b0b;color:#fff}.hq-card[data-theme=dark] .hq-btn:hover{background:#f4f4f4;color:#0b0b0b}" +
    ".hq-clue{font:14px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.08em;margin:2px 0 12px;display:block}" +
    ".hq-a{display:block;margin:6px 0 12px;padding-left:12px;border-left:2px solid currentColor}" +
    ".hq-heat{color:#e8461e;letter-spacing:2px}" +
    ".hq-foot{display:block;margin-top:14px;font:12px/1.3 -apple-system,'Helvetica Neue',Arial,sans-serif;opacity:.65}.hq-foot a{color:inherit}";

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  function render(host, q, date) {
    var heat = 3, card = el("div", "hq-card");
    card.setAttribute("data-theme", host.getAttribute("data-theme") || "light");
    var top = el("div", "hq-top"), heatEl = el("span", "hq-heat");
    top.appendChild(el("span", null, q.type + " · " + date));
    top.appendChild(heatEl);
    var qEl = el("span", "hq-q", q.question), clue = el("span", "hq-clue"), ans = el("span", "hq-a", q.answer);
    clue.hidden = true; ans.hidden = true;
    var row = el("div", "hq-row"), cool = el("button", "hq-btn", "Turn down the heat"), show = el("button", "hq-btn", "Show answer");
    function paint() { heatEl.textContent = "●●●".slice(0, heat) + "○○○".slice(0, 3 - heat); }
    cool.onclick = function () {
      if (heat > 1) { heat--; clue.hidden = false; clue.textContent = heat === 2 ? q.clues.shape : q.clues.initials; paint(); }
      if (heat === 1) cool.hidden = true;
    };
    show.onclick = function () { ans.hidden = false; show.hidden = true; cool.hidden = true; };
    row.appendChild(cool); row.appendChild(show);
    var foot = el("span", "hq-foot"), a = el("a", null, "Hot Quesadillas");
    a.href = BASE; a.target = "_blank"; a.rel = "noopener";
    foot.appendChild(document.createTextNode("A fresh batch of 25 every Friday · ")); foot.appendChild(a);
    [top, qEl, clue, ans, row, foot].forEach(function (n) { card.appendChild(n); });
    paint();
    host.innerHTML = ""; host.appendChild(card);
  }

  function boot() {
    if (!document.getElementById("hq-embed-css")) { var s = el("style"); s.id = "hq-embed-css"; s.textContent = css; document.head.appendChild(s); }
    var hosts = document.querySelectorAll("[data-hq-embed]:not([data-hq-ready])");
    if (!hosts.length) return;
    fetch(BASE + "api/daily.json").then(function (r) { return r.json(); }).then(function (daily) {
      var today = new Date().toISOString().slice(0, 10);
      Array.prototype.forEach.call(hosts, function (host) {
        host.setAttribute("data-hq-ready", "");
        var want = host.getAttribute("data-type"), pick = null;
        daily.data.forEach(function (d) { if (!pick && d.date >= today && (!want || d.question.type_slug === want)) pick = d; });
        pick = pick || daily.data[0];
        if (pick) render(host, pick.question, pick.date);
      });
    }).catch(function () {});
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
