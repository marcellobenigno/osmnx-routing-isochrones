// Copy buttons, active section in the top menu, remembered language.
(function () {
  document.querySelectorAll("pre").forEach(function (pre) {
    var b = document.createElement("button");
    b.className = "copy";
    b.type = "button";
    b.textContent = document.documentElement.dataset.copy || "Copy";
    b.addEventListener("click", function () {
      var text = pre.querySelector("code").innerText;
      navigator.clipboard.writeText(text).then(function () {
        var old = b.textContent;
        b.textContent = "✓";
        setTimeout(function () { b.textContent = old; }, 1400);
      });
    });
    pre.appendChild(b);
  });

  document.querySelectorAll(".lang a").forEach(function (a) {
    a.addEventListener("click", function () {
      try { localStorage.setItem("osmnx-doc-lang", a.dataset.lang); } catch (e) { /* private mode */ }
    });
  });

  var links = Array.prototype.slice.call(document.querySelectorAll(".topnav a"));
  if (!("IntersectionObserver" in window) || !links.length) return;
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting && byId[e.target.id]) {
        links.forEach(function (a) { a.classList.remove("active"); });
        byId[e.target.id].classList.add("active");
      }
    });
  }, { rootMargin: "-40% 0px -55% 0px" });
  document.querySelectorAll("section[id]").forEach(function (s) { observer.observe(s); });
})();
