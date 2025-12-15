// Make any graphviz SVG clickable (opens raw SVG in new tab)
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".zoomable-graph svg").forEach(svg => {
    svg.style.cursor = "zoom-in";
    svg.addEventListener("click", () => {
      const src = svg.closest("img")?.src || svg.dataset?.src;
      if (src) window.open(src, "_blank");
    });
  });
});
