"""Aplica solo la identidad editorial a briefs nuevos; conserva citas y enlaces."""
import html
from html.parser import HTMLParser
from pathlib import Path
import re

BRAND = re.compile(r"\b(?:PRIVIA|Privia)(?:[ ]+(?:HEALTH|Health))?\b")
PUBLIC_ORIGIN = "https://elevalos.com"
SITE_ORIGINS = {
    "https://elenagonzalezblanco.github.io/healthcare": PUBLIC_ORIGIN,
    "https://privia-demo-6camog4fqjoxo.swedencentral.cloudapp.azure.com": "https://portal.elevalos.com",
    "https://medrag-prodgl3vc4-web.blackstone-b235e782.eastus2.azurecontainerapps.io": "https://research.elevalos.com",
}


def configure_domain(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    def update_attribute(match):
        value = match[3]
        for previous, current in SITE_ORIGINS.items():
            if value == previous or value.startswith(previous + "/") or value.startswith(previous + "?"):
                value = current + value[len(previous):]
                break
        return match[1] + match[2] + value + match[2]
    page = re.sub(r'(\b(?:href|src|content)=)(["\'])(.*?)\2', update_attribute, raw)
    relative = path.resolve().relative_to(Path(__file__).resolve().parent).as_posix()
    canonical = PUBLIC_ORIGIN + "/" + ("" if relative == "index.html" else relative)
    page = re.sub(r'<link\b[^>]*rel=["\']canonical["\'][^>]*>\s*', "", page)
    page = re.sub(r'<meta\b[^>]*property=["\']og:url["\'][^>]*>\s*', "", page)
    page = page.replace("</head>", f'<link rel="canonical" href="{canonical}">\n'
                        f'<meta property="og:url" content="{canonical}">\n</head>')
    if page != raw:
        path.write_text(page, encoding="utf-8")


class EditorialBrand(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.protected = []

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        raw = re.sub(r'((?:alt|title|aria-label|content)=)(["\'])(.*?)(\2)',
                     lambda m: m[1] + m[2] + BRAND.sub("ELEVALOS", m[3]) + m[4], raw)
        self.output.append(raw)
        if tag in {"a", "blockquote", "script", "style"}:
            external = dict(attrs).get("href", "").startswith(("http://", "https://"))
            self.protected.append((tag, tag != "a" or external))

    def handle_startendtag(self, tag, attrs):
        raw = re.sub(r'((?:alt|title|aria-label|content)=)(["\'])(.*?)(\2)',
                     lambda m: m[1] + m[2] + BRAND.sub("ELEVALOS", m[3]) + m[4],
                     self.get_starttag_text())
        self.output.append(raw)

    def handle_endtag(self, tag):
        self.output.append(f"</{tag}>")
        if self.protected and self.protected[-1][0] == tag:
            self.protected.pop()

    def handle_data(self, data):
        self.output.append(data if any(flag for _, flag in self.protected)
                           else BRAND.sub("ELEVALOS", data))

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")

    def handle_comment(self, data):
        self.output.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.output.append(f"<!{decl}>")


def brand_brief(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    parser = EditorialBrand()
    parser.feed(raw)
    page = "".join(parser.output)
    if 'images/brand/favicon.ico' not in page:
        assets = "../images/brand/"
        title_match = re.search(r"<title>(.*?)</title>", page, re.S)
        title = html.escape(html.unescape(title_match[1]) if title_match else "ELEVALOS", quote=True)
        head = f"""
<link rel="icon" href="{assets}favicon.ico?v=elevalos-20260922">
<link rel="icon" type="image/png" sizes="32x32" href="{assets}elevalos-icon-32.png?v=elevalos-20260922">
<link rel="apple-touch-icon" sizes="180x180" href="{assets}elevalos-icon-180.png?v=elevalos-20260922">
<link rel="manifest" href="{assets}site.webmanifest?v=elevalos-20260922">
<link rel="stylesheet" href="{assets}elevalos-brand.css?v=elevalos-20260922">
<meta name="application-name" content="ELEVALOS">
<meta name="theme-color" content="#0b3829">
<meta property="og:site_name" content="ELEVALOS">
<meta property="og:title" content="{title}">
<meta property="og:image" content="https://elevalos.com/images/brand/elevalos-social.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:image" content="https://elevalos.com/images/brand/elevalos-social.png">
"""
        page = re.sub(r'<link[^>]+rel=["\'](?:icon|apple-touch-icon)["\'][^>]*>\n?', "", page)
        page = page.replace("</head>", head + "</head>")
    if 'class="elevalos-wordmark"' not in page:
        header = ('<a class="elevalos-brand-link" href="../index.html" style="margin:16px 24px">'
                  '<img class="elevalos-wordmark" src="../images/brand/elevalos-wordmark-320.webp" '
                  'srcset="../images/brand/elevalos-wordmark-320.webp 320w, ../images/brand/elevalos-wordmark-640.webp 640w" '
                  'sizes="(max-width: 480px) 150px, 176px" width="320" height="80" alt="ELEVALOS"></a>')
        page = re.sub(r"(<body\b[^>]*>)", r"\1" + header, page, count=1)
    if page != raw:
        path.write_text(page, encoding="utf-8")
