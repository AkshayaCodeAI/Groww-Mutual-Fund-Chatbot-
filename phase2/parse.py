"""
Phase 2.2: Parse — Extract all important fields from Groww scheme page HTML.
Maps to: Type, Expense ratio, Exit load, Min SIP, Min lump sum, Lock-in, Benchmark, Risk,
Fund Manager, Launch date, Category, Scheme type, Asset allocation, Top holdings,
1Y/3Y/5Y returns, ELSS tax benefit, LTCG/STCG tax rule, Tax implication, Stamp duty,
Fund House, About Scheme, One Time SIP, Holding Analysis, Advanced Ratios,
Minimum investments, Annualised/Absolute returns defs, Exit load def, FAQ, etc.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PHASE1_DIR = ROOT / "phase1"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw_pages"
PARSED_DIR = DATA_DIR / "parsed"
SOURCES_PATH = PHASE1_DIR / "sources.json"

LAST_UPDATED = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_sources() -> dict:
    with open(SOURCES_PATH, encoding="utf-8") as f:
        return json.load(f)


def text_clean(s: str) -> str:
    if not s:
        return ""
    return " ".join(s.split()).strip()


def parse_scheme_page(html: str, scheme_id: str, scheme_name: str, source_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    body_text = soup.get_text(separator=" ", strip=True)

    out = {
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "source_url": source_url,
        "last_updated": LAST_UPDATED,
        "type": "Direct" if "direct" in source_url.lower() else "Regular",
        "expense_ratio": None,
        "exit_load": None,
        "min_sip": None,
        "min_lumpsum": None,
        "lock_in_period": None,
        "benchmark": None,
        "risk": None,
        "fund_manager": None,
        "launch_date": None,
        "category": None,
        "scheme_type": None,
        "asset_allocation": None,
        "top_holdings": [],
        "return_1y": None,
        "return_3y": None,
        "return_5y": None,
        "elss_tax_benefit": None,
        "ltcg_tax_rule": None,
        "stcg_tax_rule": None,
        "tax_implication": None,
        "stamp_duty": None,
        "fund_house": None,
        "fund_house_url": None,
        "about_scheme": None,
        "investment_objective": None,
        "min_1st_investment": None,
        "min_2nd_investment": None,
        "one_time_sip": None,
        "holding_analysis": None,
        "advanced_ratios": None,
        "annualised_returns_definition": None,
        "absolute_returns_definition": None,
        "expense_ratio_definition": None,
        "exit_load_definition": None,
        "stamp_duty_definition": None,
        "tax_definition": None,
        "faqs": [],
    }

    # ---- 1. Type (already set), 2. Expense ratio ----
    if not scheme_name and soup.find("title"):
        title = soup.find("title").get_text()
        out["scheme_name"] = text_clean(title.split(" - ")[0]) if " - " in title else text_clean(title)

    er = re.search(r"Expense\s+ratio\s*[\s\n]*([\d.]+%?)", body_text, re.I)
    if er:
        out["expense_ratio"] = er.group(1).strip()

    # ---- 4. Min SIP, 5. Min lump sum, 31. Minimum investments ----
    sip = re.search(r"Min\.?\s*for\s*SIP\s*[\s\n]*₹\s*([\d,]+)", body_text, re.I)
    if sip:
        out["min_sip"] = "₹" + sip.group(1).replace(",", "")
    min1 = re.search(r"Min\.?\s*for\s*1st\s*investment\s*[\s\n]*₹\s*([\d,]+)", body_text, re.I)
    min2 = re.search(r"Min\.?\s*for\s*2nd\s*investment\s*[\s\n]*₹\s*([\d,]+)", body_text, re.I)
    if min1:
        out["min_1st_investment"] = "₹" + min1.group(1).replace(",", "")
    if min2:
        out["min_2nd_investment"] = "₹" + min2.group(1).replace(",", "")
    if out["min_1st_investment"] and not out["min_lumpsum"]:
        out["min_lumpsum"] = out["min_1st_investment"]

    # ---- 3. Exit load, 34. Exit load (same) ----
    el_match = re.search(r"Exit\s+load\s+of\s+([^.\n]+?)(?:\.|$)", body_text, re.I)
    if el_match:
        out["exit_load"] = text_clean(el_match.group(0))[:200]
    if not out["exit_load"]:
        el2 = re.search(r"Exit\s+load[^.]*?(\d+%[^.]{5,150})", body_text, re.I | re.DOTALL)
        if el2:
            out["exit_load"] = text_clean(el2.group(0)[:200])

    # ---- 36. Tax implication, 19. LTCG, 20. STCG ----
    tax = re.search(r"Tax\s+implication\s*[\s\n]+([^\n]+(?:\n[^\n]+){0,2})", body_text, re.I)
    if tax:
        out["tax_implication"] = text_clean(tax.group(1))[:500]
        ti = out["tax_implication"].lower()
        stcg_m = re.search(r"[^.]+(?:within one year|within 1 year|redeem within)[^.]+\.?", out["tax_implication"], re.I | re.DOTALL)
        if stcg_m:
            out["stcg_tax_rule"] = text_clean(stcg_m.group(0))[:200]
        if "after one year" in ti or "after 1 year" in ti or "exceeding" in ti or "12.5%" in ti or "20%" in ti:
            out["ltcg_tax_rule"] = out["tax_implication"][:300]

    # ---- 35. Stamp duty ----
    stamp = re.search(r"Stamp\s+duty[^.]*?([\d.]+%[^.]*?(?:from|July|Jan|Feb|Mar|Apr|May|Jun|Aug|Sep|Oct|Nov|Dec)[^.]*?\d{4})", body_text, re.I)
    if stamp:
        out["stamp_duty"] = text_clean(stamp.group(0)[:150])

    # ---- 27. Fund House ----
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "/mutual-funds/amc/" in href:
            out["fund_house"] = text_clean(a.get_text())
            out["fund_house_url"] = ("https://groww.in" + href.split("?")[0]) if href.startswith("/") else href.split("?")[0]
            break

    # ---- 10. Launch date ----
    launch = re.search(r"(?:Launch\s+Date|made\s+available\s+to\s+investors\s+on)\s*[\s\n]*(\d{1,2}\s+\w+\s+\d{4})", body_text, re.I)
    if launch:
        out["launch_date"] = text_clean(launch.group(1))

    # ---- 8. Risk ----
    risk = re.search(r"rated\s+([^.]*?risk)", body_text, re.I)
    if risk:
        out["risk"] = text_clean(risk.group(1))

    # ---- 7. Benchmark ----
    bench = re.search(r"Fund\s+benchmark\s*([^\n]+)", body_text, re.I)
    if bench:
        out["benchmark"] = text_clean(bench.group(1))[:200]
    if not out["benchmark"]:
        bench2 = re.search(r"benchmark\s*[\s\n]*([^\n]+?)(?:\n|Scheme\s|Investment)", body_text, re.I)
        if bench2:
            out["benchmark"] = text_clean(bench2.group(1))[:200]

    # ---- 11. Category (from "Category average (Equity Mid Cap)" or "Rank (...)" ) ----
    cat = re.search(r"Category\s+average\s*\(([^)]+)\)", body_text, re.I)
    if cat:
        out["category"] = text_clean(cat.group(1))
    if not out["category"]:
        rank_cat = re.search(r"Rank\s*\(([^)]+)\)", body_text)
        if rank_cat:
            out["category"] = text_clean(rank_cat.group(1))

    # ---- 28. About Scheme, 12. Scheme type ----
    about_heading = soup.find(string=re.compile(r"About\s+\w+"))
    if about_heading:
        parent = about_heading.find_parent()
        if parent:
            parts = []
            for sib in parent.find_next_siblings():
                t = sib.get_text() if hasattr(sib, "get_text") else str(sib)
                parts.append(t)
                if len(" ".join(parts)) > 1500:
                    break
            out["about_scheme"] = text_clean(" ".join(parts)[:2000])
            # Scheme type: "is a Equity Mutual Fund Scheme" or similar
            if " is a " in out["about_scheme"]:
                st = re.search(r"is a\s+([^.]+?)\s+Scheme", out["about_scheme"], re.I)
                if st:
                    out["scheme_type"] = text_clean(st.group(1))

    obj = re.search(r"Investment\s+Objective\s*[\s\n]+([^\n]+)", body_text, re.I)
    if obj:
        out["investment_objective"] = text_clean(obj.group(1))[:500]

    # ---- 9. Fund Manager ----
    fm_names = re.findall(r"([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:Feb|Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*-\s*Present", body_text)
    if fm_names:
        out["fund_manager"] = list(dict.fromkeys(fm_names))

    # ---- 15–17. 1Y, 3Y, 5Y returns (Fund returns row: columns vary) ----
    fund_ret = re.search(r"Fund\s+returns\s+[^|]*\|[^|]*\|\s*([+\d.-]+%)\s+([+\d.-]+%)?\s+([+\d.-]+%)?\s+([+\d.-]+%)?", body_text)
    if fund_ret:
        g = [x for x in fund_ret.groups() if x]
        if len(g) >= 3:
            out["return_3y"], out["return_5y"] = g[0], g[1]
            if len(g) >= 4:
                out["return_5y"] = g[2]
        if len(g) >= 1 and not out["return_1y"]:
            out["return_1y"] = g[0]
    # Alternative: table with 1Y 3Y 5Y columns
    ret_1y = re.search(r"\b1Y\b[^|]*\|[^|]*\|\s*([+\d.-]+%)", body_text)
    if ret_1y and not out["return_1y"]:
        out["return_1y"] = ret_1y.group(1)

    # ---- 14. Top holdings, 13. Asset allocation (summary from holdings) ----
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            texts = [c.get_text(strip=True) for c in cells]
            if any("%" in t for t in texts) and any(t for t in texts if len(t) > 2 and t not in ("Name", "Sector", "Assets")):
                name = texts[0] if texts else ""
                assets = next((t for t in texts if "%" in t), "")
                sector = texts[1] if len(texts) > 2 else ""
                if name and "Name" not in name:
                    out["top_holdings"].append({"name": name[:200], "assets": assets[:20], "sector": sector[:50]})
    if out["top_holdings"]:
        out["asset_allocation"] = "Equity/Debt/Others as per holdings table. Top holdings: " + "; ".join(
            f"{h.get('name', '')} {h.get('assets', '')}" for h in out["top_holdings"][:5]
        )[:500]

    # ---- 6. Lock-in, 18. ELSS tax benefit ----
    if "ELSS" in body_text or "elss" in scheme_id or "tax saver" in body_text.lower():
        out["lock_in_period"] = "3 years (ELSS lock-in)"
        out["elss_tax_benefit"] = "ELSS schemes qualify for deduction under Section 80C up to ₹1.5 lakh and have a 3-year lock-in."
    if re.search(r"lock[- ]?in\s*(?:of\s*)?(\d+\s*year)", body_text, re.I):
        m = re.search(r"lock[- ]?in\s*(?:of\s*)?(\d+\s*year[^.]*)", body_text, re.I)
        if m and not out["lock_in_period"]:
            out["lock_in_period"] = text_clean(m.group(0))[:100]

    # ---- 29. One Time SIP ----
    if "One time" in body_text or "One-time" in body_text:
        one_time = re.search(r"(?:One\s*[- ]?time|one\s*time)[^.]*?(?:₹\s*[\d,]+|minimum[^.]*)?", body_text, re.I)
        if one_time:
            out["one_time_sip"] = text_clean(one_time.group(0))[:150]

    # ---- 30. Holding Analysis (summary) ----
    if out["top_holdings"]:
        out["holding_analysis"] = f"Holdings: {len(out['top_holdings'])} positions. " + "; ".join(
            f"{h.get('name', '')} {h.get('assets', '')}" for h in out["top_holdings"][:10]
        )[:800]

    # ---- 30. Advanced Ratios (Sharpe, etc.) ----
    if "Sharpe" in body_text or "Alpha" in body_text or "Beta" in body_text:
        ar = re.search(r"(?:Sharpe|Alpha|Beta)[^.]*[\d.]+", body_text)
        if ar:
            out["advanced_ratios"] = text_clean(ar.group(0))[:200]

    # ---- 32–33, 24–25: Glossary (Understand terms) ----
    if "Annualised returns" in body_text and "yearly returns" in body_text.lower():
        out["annualised_returns_definition"] = "Average of the yearly returns of a mutual fund over a given period."
    if "Absolute returns" in body_text and "total return" in body_text.lower():
        out["absolute_returns_definition"] = "The total return of a mutual fund over a given period."
    if "Expense ratio" in body_text and "fee payable" in body_text.lower():
        out["expense_ratio_definition"] = "A fee payable to a mutual fund house for managing your mutual fund investments."
    if "Exit load" in body_text and "fee payable" in body_text.lower():
        out["exit_load_definition"] = "A fee payable to a mutual fund house for exiting a fund before the completion of a specified period."
    if "Stamp duty" in body_text:
        out["stamp_duty_definition"] = "A form of tax payable for the purchase or sale of an asset or security."
    if "LTCG" in body_text or "STCG" in body_text or "capital gains" in body_text.lower():
        out["tax_definition"] = "Tax on capital gains (LTCG/STCG) depending on holding period and fund type."

    # ---- 26. FAQs (accordion or Q/A blocks) ----
    for tag in soup.find_all(["div", "section"], class_=re.compile(r"faq|accordion|question", re.I)):
        q = tag.find(string=re.compile(r"\?|what|how|can", re.I))
        if q:
            qtext = q.strip() if isinstance(q, str) else q.get_text(strip=True)
            parent = q.find_parent() if hasattr(q, "find_parent") else tag
            if parent:
                next_el = parent.find_next_sibling()
                if next_el:
                    a = next_el.get_text(separator=" ", strip=True)[:500]
                    if qtext and a and len(qtext) > 10:
                        out["faqs"].append({"question": qtext[:300], "answer": a})
    if not out["faqs"]:
        for h in soup.find_all(["h3", "h4", "h5"]):
            ht = h.get_text(strip=True)
            if "?" in ht and len(ht) > 15:
                n = h.find_next_sibling()
                if n:
                    at = n.get_text(separator=" ", strip=True)[:400]
                    if at:
                        out["faqs"].append({"question": ht[:300], "answer": at})

    return out


def run_parse() -> None:
    sources = load_sources()
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    for scheme in sources["scheme_pages"]:
        scheme_id = scheme["scheme_id"]
        scheme_name = scheme.get("scheme_name", scheme_id)
        url = scheme["url"]
        raw_file = RAW_DIR / f"{scheme_id}.html"
        if not raw_file.exists():
            print(f"Skip {scheme_id}: no raw file at {raw_file}")
            continue
        html = raw_file.read_text(encoding="utf-8")
        data = parse_scheme_page(html, scheme_id, scheme_name, url)
        out_path = PARSED_DIR / f"{scheme_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Parsed {scheme_id} -> {out_path.name}")


if __name__ == "__main__":
    run_parse()
    print("Done.")
