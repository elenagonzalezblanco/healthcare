(function (root) {
  "use strict";
  const supported = value => /^(es|en)(?:-|$)/i.exec(String(value || ""))?.[1].toLowerCase() || null;
  function choose(query, saved, languages) {
    return supported(query) || supported(saved) || (languages || []).map(supported).find(Boolean) || "es";
  }
  if (typeof module !== "undefined" && module.exports) module.exports = {supported, choose};
  if (!root.document) return;
  let saved;
  try { saved = root.localStorage.getItem("privia-language"); } catch (_) {}
  const language = choose(new URL(root.location.href).searchParams.get("lang"), saved, root.navigator.languages || [root.navigator.language]);
  root.PriviaLanguage = {language, locale: language === "en" ? "en-GB" : "es-ES"};
  root.document.cookie = `privia_language=${language}; Path=/; Max-Age=31536000; SameSite=Lax${root.location.protocol === "https:" ? "; Secure" : ""}`;
  try { root.localStorage.setItem("privia-language", language); } catch (_) {}
  const rendered = root.document.documentElement.lang;
  if (rendered && rendered !== language) {
    const destination = new URL(root.location.href);
    destination.searchParams.set("lang", language);
    if (root.document.documentElement.dataset.staticLanguage === "true") {
      if (destination.pathname.endsWith("/")) destination.pathname += "index.html";
      destination.pathname = destination.pathname.replace(/(?:\.en)?\.html$/, language === "en" ? ".en.html" : ".html");
    }
    root.location.replace(destination.href);
    return;
  }
  root.document.addEventListener("DOMContentLoaded", () => {
    const target = root.document.querySelector("[data-language-control]") || root.document.querySelector(".demo-band, .topbar") || root.document.querySelector("header.site .container") || root.document.querySelector("header") || root.document.body;
    if (target) {
      const label = root.document.createElement("label");
      label.className = "privia-language";
      label.title = language === "en" ? "Language" : "Idioma";
      const symbol = root.document.createElement("i");
      symbol.setAttribute("data-lucide", "languages");
      symbol.setAttribute("aria-hidden", "true");
      const select = root.document.createElement("select");
      select.setAttribute("aria-label", label.title);
      for (const [value, name] of [["es", "Español"], ["en", "English"]]) {
        const option = root.document.createElement("option");
        option.value = value; option.textContent = name; option.selected = value === language;
        select.append(option);
      }
      select.addEventListener("change", () => {
        const destination = new URL(root.location.href);
        destination.searchParams.set("lang", select.value);
        if (root.document.documentElement.dataset.staticLanguage === "true") {
          if (destination.pathname.endsWith("/")) destination.pathname += "index.html";
          destination.pathname = destination.pathname.replace(/(?:\.en)?\.html$/, select.value === "en" ? ".en.html" : ".html");
        }
        root.location.assign(destination.href);
      });
      label.append(symbol, select); target.append(label);
      root.lucide?.createIcons();
    }
    root.document.addEventListener("click", event => {
      const link = event.target.closest("a[href]");
      if (!link || link.hasAttribute("download")) return;
      const destination = new URL(link.href, root.location.href);
      const hosts = [root.location.host, "elenagonzalezblanco.github.io", "privia-demo-6camog4fqjoxo.swedencentral.cloudapp.azure.com", "medrag-prodgl3vc4-web.blackstone-b235e782.eastus2.azurecontainerapps.io", "patient-care.blackstone-b235e782.eastus2.azurecontainerapps.io"];
      if (!hosts.includes(destination.host) || !/^https?:$/.test(destination.protocol) || destination.pathname.startsWith("/api/")) return;
      if (destination.origin === root.location.origin && destination.pathname === root.location.pathname && link.getAttribute("href").startsWith("#")) return;
      destination.searchParams.set("lang", language); link.href = destination.href;
    });
  });
})(typeof window !== "undefined" ? window : globalThis);