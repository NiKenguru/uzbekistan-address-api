import json
from functools import lru_cache
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Uzbekistan Address API")
SOURCE = "https://raw.githubusercontent.com/MIMAXUZ/uzbekistan-regions-data/master/JSON/"
MAX_BYTES = 256_000


@lru_cache(maxsize=2)
def load_catalog(name: str):
    try:
        with urlopen(f"{SOURCE}{name}.json", timeout=6) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Catalog is too large")
        records = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(records, list) or not records:
            raise ValueError("Expected a nonempty catalog")
        localized = []
        for item in records:
            entry = {
                "id": int(item["id"]),
                "soato": str(item["soato_id"]),
                "name": {"uz": item["name_uz"], "uz-Cyrl": item["name_oz"], "ru": item["name_ru"]},
            }
            if name == "districts":
                entry["region_id"] = int(item["region_id"])
            localized.append(entry)
        return localized
    except (OSError, URLError, ValueError, TypeError, KeyError) as error:
        raise HTTPException(502, "Address catalog unavailable") from error


@app.get("/api/regions")
def regions():
    return load_catalog("regions")


@app.get("/api/regions/{region_id}/districts")
def districts(region_id: int):
    if not any(row["id"] == region_id for row in regions()):
        raise HTTPException(404, "Region not found")
    return [row for row in load_catalog("districts") if row["region_id"] == region_id]


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return """<!doctype html>
<html lang="uz"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Uzbekistan Address API</title>
<style>body{font:1rem/1.55 system-ui;max-width:36rem;margin:3rem auto;padding:0 1.2rem;background:#eff6f9;color:#102f43}label{display:block;margin:.8rem 0 .2rem}select{font:inherit;width:100%;padding:.55rem}output{display:block;margin:1rem 0}</style>
<main><h1>Manzil ma’lumotnomasi</h1>
<p>Viloyat va tumanni tanlang, SOATO kodi avtomatik chiqadi.</p>
<label for="language">Til</label><select id="language"><option value="uz">O‘zbekcha</option><option value="uz-Cyrl">Ўзбекча</option><option value="ru">Русский</option></select>
<label for="region">Hudud</label><select id="region" disabled></select>
<label for="district">Tuman yoki shahar</label><select id="district" disabled></select>
<output id="result" aria-live="polite"></output><a href="/docs">API hujjatlari</a></main>
<script>
const field = id => document.getElementById(id);
const language = field("language");
const region = field("region");
const district = field("district");
const result = field("result");
let regions = [];
let districts = [];
let requestId = 0;

function render(select, rows) {
  const selected = select.value;
  select.replaceChildren(...rows.map(row => new Option(row.name[language.value], row.id)));
  if (rows.some(row => String(row.id) === selected)) select.value = selected;
  select.disabled = rows.length === 0;
}

async function load(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error("Catalog request failed");
  return response.json();
}

function showCode() {
  const selected = districts.find(row => String(row.id) === district.value);
  result.textContent = selected ? "SOATO: " + selected.soato : "";
}

async function updateDistricts() {
  const current = ++requestId;
  districts = [];
  render(district, districts);
  result.textContent = "Yuklanmoqda…";
  try {
    const data = await load("/api/regions/" + encodeURIComponent(region.value) + "/districts");
    if (current !== requestId) return;
    districts = data;
    render(district, districts);
    showCode();
  } catch {
    if (current === requestId) result.textContent = "Tumanlar ro‘yxatini yuklab bo‘lmadi.";
  }
}

language.onchange = () => { render(region, regions); render(district, districts); if (districts.length) showCode(); };
region.onchange = updateDistricts;
district.onchange = showCode;
load("/api/regions").then(data => { regions = data; render(region, regions); return updateDistricts(); })
  .catch(() => { result.textContent = "Hududlar ro‘yxatini yuklab bo‘lmadi."; });
</script></html>"""
