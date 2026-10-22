"""PDF -> texto por pagina -> OCR se necessario -> Markdown e indice."""
import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus_md"
BEGIN = "<!-- extracoes:inicio -->"
END = "<!-- extracoes:fim -->"


def quality(text):
    compact = "".join(text.split())
    words = re.findall(r"[^\W\d_]{2,}", text, re.UNICODE)
    bad = sum(c == "\ufffd" or (ord(c) < 32 and not c.isspace()) for c in text)
    reasons = []
    if len(compact) < 40 or len(words) < 5:
        reasons.append("pouco texto")
    if bad / max(len(text), 1) > .02:
        reasons.append("caracteres suspeitos")
    return reasons


def image_coverage(page):
    """Union of raster rectangles, without double-counting overlaps."""
    bounds = page.rect * page.derotation_matrix
    rects = [pymupdf.Rect(info["bbox"]) & bounds for info in page.get_image_info()]
    rects = [r for r in rects if not r.is_empty]
    edges = sorted({x for r in rects for x in (r.x0, r.x1)})
    area = 0.0
    for left, right in zip(edges, edges[1:]):
        intervals = sorted((r.y0, r.y1) for r in rects if r.x0 < right and r.x1 > left)
        height, end = 0.0, float("-inf")
        for low, high in intervals:
            height += max(0, high - max(low, end))
            end = max(end, high)
        area += (right - left) * height
    return area / max(page.rect.get_area(), 1)


def image_text_suspect(page, text):
    return len("".join(text.split())) < 800 and image_coverage(page) >= .5


def ocr_page(page, folder, language, rotation=0):
    """One OCR pass at 300 dpi; orientation is an explicit agent decision."""
    initial_rotation = page.rotation
    try:
        page.set_rotation((initial_rotation + rotation) % 360)
        with pymupdf.open() as normalized:
            pix = page.get_pixmap(dpi=300, alpha=False)
            upright = normalized.new_page(width=page.rect.width, height=page.rect.height)
            upright.insert_image(upright.rect, stream=pix.tobytes("png"))
            tp = upright.get_textpage_ocr(language=language, dpi=300, full=True, tessdata=folder)
            return upright.get_text("text", textpage=tp, sort=True).strip()
    finally:
        page.set_rotation(initial_rotation)


def read_catalog(path):
    if not path.exists():
        return {}
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise ValueError(f"Catálogo inválido em {path.name}: {exc}") from exc
    if not isinstance(catalog, dict):
        raise ValueError("Catálogo inválido: a raiz deve ser um objeto JSON.")
    for key, entry in catalog.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Catálogo inválido em {key}: o item deve ser um objeto.")
        if entry.get("extracao") is not None and not isinstance(entry["extracao"], dict):
            raise ValueError(f"Catálogo inválido em {key}.extracao: use um objeto ou null.")
        extraction = entry.get("extracao") or {}
        for field in ("fonte", "sha256", "verificacao_tecnica", "status", "extrator"):
            if extraction.get(field) is not None and not isinstance(extraction[field], str):
                raise ValueError(f"Catálogo inválido em {key}.extracao.{field}: use texto ou null.")
            if field in extraction and extraction[field] is None:
                extraction[field] = ""
        if entry.get("palavras_chave") is None:
            entry["palavras_chave"] = []
        if not isinstance(entry["palavras_chave"], list) or not all(isinstance(w, str) for w in entry["palavras_chave"]):
            raise ValueError(f"Catálogo inválido em {key}.palavras_chave: use uma lista de textos.")
        for field in ("grupo", "tipo", "referencia", "resumo", "url", "fichamento", "uso_no_texto", "status_leitura", "status_metadados"):
            if entry.get(field) is not None and not isinstance(entry[field], str):
                raise ValueError(f"Catálogo inválido em {key}.{field}: use texto ou null.")
            if entry.get(field) is None:
                entry[field] = ""
    return catalog


def metadata(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    result = {}
    for line in text.split("---\n", 2)[1].splitlines():
        key, sep, value = line.partition(": ")
        if sep:
            try:
                result[key] = json.loads(value)
            except ValueError:
                result[key] = value
    return result


def tessdata(explicit, language):
    candidates = [explicit, str(ROOT / ".tools/tessdata"), os.environ.get("TESSDATA_PREFIX")]
    exe = shutil.which("tesseract")
    if exe:
        candidates.append(str(Path(exe).parent / "tessdata"))
    candidates += ["C:/Program Files/Tesseract-OCR/tessdata",
                   "/usr/share/tesseract-ocr/5/tessdata", "/usr/share/tessdata"]
    for value in candidates:
        if value and all((Path(value) / f"{lang}.traineddata").is_file() for lang in language.split("+")):
            return str(Path(value).resolve())
    raise RuntimeError(f"Dados OCR ausentes para {language}. Configure --tessdata ou TESSDATA_PREFIX.")


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def update_index():
    index = CORPUS / "INDEX.md"
    catalog_path = CORPUS / "catalogo.json"
    catalog = read_catalog(catalog_path)
    # Editorial fields live in a public catalog, independently of local full texts.
    for path in sorted(CORPUS.rglob("*.md")):
        if path == index:
            continue
        meta = metadata(path)
        if meta.get("tipo") != "texto_base" or "fonte" not in meta:
            continue
        key = path.relative_to(CORPUS).as_posix()
        entry = catalog.setdefault(key, {
            "grupo": "Geral", "tipo": "texto_base", "referencia": "",
            "resumo": "", "palavras_chave": [], "url": "", "fichamento": "",
            "uso_no_texto": "", "status_leitura": "nao_iniciada",
            "status_metadados": "pendente",
        })
        entry["extracao"] = {k: meta.get(k) for k in (
            "fonte", "sha256", "paginas", "extrator", "paginas_ocr",
            "paginas_pendentes", "paginas_ocr_alternativo", "rotacoes_ocr", "verificacao_tecnica", "status")}
    ordered = sorted(catalog.items(), key=lambda item: (
        item[1].get("grupo", "Geral"), item[1].get("tipo", "texto_base"),
        item[1].get("referencia") or item[0]))

    def cell(value):
        return str(value).replace("|", "&#124;").replace("\n", " ")

    def row(values):
        return "| " + " | ".join(map(cell, values)) + " |"

    def link(label, url):
        # Only relative project paths and HTTP(S) links are rendered as links.
        if not url or any(c in url for c in "\n\r"):
            return "Pendente"
        if ":" in url and not url.startswith(("http://", "https://")):
            return "Link inválido"
        safe = url.replace(" ", "%20").replace("(", "%28").replace(")", "%29").replace("<", "%3C").replace(">", "%3E")
        return f"[{label}](<{safe}>)"

    extracted = sum(bool(e.get("extracao")) for e in catalog.values())
    read = sum(e.get("status_leitura") == "concluida" for e in catalog.values())
    pending_meta = sum(e.get("status_metadados") != "conferido" for e in catalog.values())
    hashes = {}
    for key, entry in ordered:
        digest = (entry.get("extracao") or {}).get("sha256")
        if digest:
            hashes.setdefault(digest, []).append(key)
    duplicates = {key: keys for keys in hashes.values() if len(keys) > 1 for key in keys}
    rows = [BEGIN, "## Panorama", "",
            f"- Leituras catalogadas: **{len(catalog)}** · Com extração registrada: **{extracted}** · A incorporar: **{len(catalog) - extracted}**.",
            f"- Leitura concluída: **{read}** · Metadados a conferir: **{pending_meta}**.",
            f"- Conteúdos extraídos distintos (SHA-256): **{len(hashes)}** · Registros com conteúdo duplicado: **{len(duplicates)}**.", "",
            "## Mapa de leitura", "",
            "| Grupo | Tipo | Referência e acesso | Resumo | Palavras-chave | Leitura | Fichamento | Uso no texto |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for key, entry in ordered:
        ref = entry.get("referencia") or "Identificação pendente"
        if entry.get("url"):
            ref += " · " + link("Fonte", entry["url"])
        if entry.get("status_metadados") != "conferido":
            ref += " (metadados pendentes)"
        rows.append(row([entry.get("grupo", "Geral"), entry.get("tipo", "texto_base"), ref,
                         entry.get("resumo") or "Síntese pendente",
                         ", ".join(entry.get("palavras_chave", [])) or "A definir",
                         entry.get("status_leitura", "nao_iniciada"),
                         link("Fichamento", entry.get("fichamento", "")),
                         entry.get("uso_no_texto") or "A definir"]))
    rows += ["", "<details>", "<summary>Extração, OCR e conferência técnica</summary>", "",
             "Os links para Markdown são locais e podem não existir no GitHub. Metadados e sínteses permanecem no catálogo público.", "",
             "| Fonte | Markdown | Páginas | OCR tentado | Verificação técnica | Revisão |",
             "| --- | --- | --- | --- | --- | --- |"]
    alerts = []
    for key, entry in ordered:
        meta = entry.get("extracao")
        if not meta:
            rows.append(row([entry.get("referencia") or key, "A incorporar", "Pendente", "Pendente", "nao_extraido", "pendente_de_revisao"]))
            continue
        technical = meta.get("verificacao_tecnica", "não registrada")
        original = (ROOT / (meta.get("fonte") or "")).resolve()
        if not original.is_relative_to(ROOT) or not original.is_file():
            technical = "fonte_ausente"
        elif meta.get("sha256") != hashlib.sha256(original.read_bytes()).hexdigest():
            technical = "fonte_alterada_reextrair"
        if not (CORPUS / key).is_file():
            technical += "; markdown_local_ausente"
        if key in duplicates:
            technical += "; conteudo_duplicado"
            others = ", ".join(k for k in duplicates[key] if k != key)
            alerts.append(f"- {key}: conteúdo idêntico a {others}. Não conte como outra leitura; preserve notas antes de consolidar o catálogo.")
        if technical != "sem_alertas_automaticos":
            alerts.append(f"- {key}: {technical}.")
        rows.append(row([meta.get("fonte", ""), link("MD local", key), meta.get("paginas", "?"),
                         meta.get("paginas_ocr", []), technical, meta.get("status", "pendente_de_revisao")]))
    rows += ["", "</details>", "", "## Pendências", ""]
    if not catalog:
        rows.append("- Incorpore as primeiras fontes para começar o corpus.")
    else:
        if len(catalog) > extracted:
            rows.append(f"- Incorporar {len(catalog) - extracted} fonte(s) ainda sem extração registrada.")
        if pending_meta:
            rows.append(f"- Conferir metadados de {pending_meta} item(ns), sem preencher lacunas por suposição.")
        if len(catalog) > read:
            rows.append(f"- Finalizar a leitura e o fichamento dos itens ainda pendentes ({len(catalog) - read}).")
        rows.extend(alerts)
        if any((e.get("extracao") or {}).get("status") != "revisado" for e in catalog.values() if e.get("extracao")):
            rows.append("- Conferir as extrações com o original antes de marcar a revisão como concluída.")
        if not alerts and len(catalog) == extracted == read and not pending_meta:
            rows.append("- Confira o estado de revisão técnica indicado acima.")
    rows += ["", END]
    block = "\n".join(rows)
    current = index.read_text(encoding="utf-8") if index.exists() else "# Índice do corpus\n\n"
    if BEGIN in current and END in current:
        a = current.index(BEGIN)
        b = current.index(END, a) + len(END)
        current = current[:a] + block + current[b:]
    else:
        current = current.rstrip() + "\n\n" + block + "\n"
    atomic_write(catalog_path, json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    atomic_write(index, current)


def process(source, target, args):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    rotation = getattr(args, "rotacao_ocr", 0)
    signature = {"versao": 5, "idiomas": args.idiomas, "ocr_forcado": args.ocr, "rotacao_ocr": rotation}
    if target.exists() and not args.sobrescrever:
        old = metadata(target)
        if old.get("sha256") == digest and old.get("configuracao") == signature and old.get("verificacao_tecnica") == "sem_alertas_automaticos":
            print(f"Mantido: {target.relative_to(ROOT)}")
            return True
        print(f"Preservado: {target.relative_to(ROOT)}. Use --sobrescrever para reextrair; salve correções manuais antes.")
        return False
    pages, ocr_pages, pending, errors = [], [], [], []
    rotations = {}
    alternatives = {}
    try:
        with pymupdf.open(source) as doc:
            if doc.needs_pass:
                raise RuntimeError("PDF protegido por senha")
            if not len(doc):
                raise RuntimeError("PDF sem paginas")
            for number, page in enumerate(doc, 1):
                try:
                    native = page.get_text("text", sort=True).strip()
                except Exception as exc:
                    native = ""
                    errors.append(f"Página {number}: extração nativa falhou: {exc}")
                text, method = native, "pymupdf"
                invalid = sum(c == "\ufffd" or (ord(c) < 32 and not c.isspace()) for c in native)
                # Short text, formulas and abbreviations alone do not justify OCR.
                if args.ocr or not native.strip() or invalid / max(len(native), 1) > .02 or image_text_suspect(page, native):
                    ocr_pages.append(number)
                    try:
                        folder = tessdata(args.tessdata, args.idiomas)
                        candidate = ocr_page(page, folder, args.idiomas, rotation)
                        if rotation:
                            rotations[str(number)] = rotation
                        if native.strip():
                            if candidate:
                                alternatives[number] = candidate
                            errors.append(f"Página {number}: texto nativo preservado; comparar alternativa OCR com o PDF antes de escolher.")
                            pending.append(number)
                        else:
                            text, method = candidate, "tesseract"
                        if quality(candidate):
                            errors.append(f"Página {number}: OCR ainda apresenta " + ", ".join(quality(candidate)))
                            pending.append(number)
                    except Exception as exc:
                        errors.append(f"Página {number}: OCR indisponível ou falhou: {exc}")
                        pending.append(number)
                issues = quality(text)
                if issues:
                    pending.append(number)
                pages.append((number, text, method, issues))
    except Exception as exc:
        errors.append(f"Falha de leitura do PDF: {exc}")
    technical = "revisao_necessaria" if pending or errors or not pages else "sem_alertas_automaticos"
    meta = {"tipo": "texto_base", "fonte": source.relative_to(ROOT).as_posix(),
            "sha256": digest, "configuracao": signature, "paginas": len(pages),
            "extrator": "pymupdf+tesseract" if any(p[2] == "tesseract" for p in pages) else "pymupdf",
            "paginas_ocr": ocr_pages, "paginas_ocr_alternativo": sorted(alternatives), "rotacoes_ocr": rotations, "paginas_pendentes": sorted(set(pending)),
            "verificacao_tecnica": technical, "status": "pendente_de_revisao", "avisos": errors}
    lines = ["---"] + [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in meta.items()]
    lines += ["---", "", "# Texto extraído", "", "> Conferir com o PDF antes de citar. A verificação automática não valida conteúdo ou ordem de leitura.", ""]
    for number, text, method, issues in pages:
        lines += [f"<!-- page: {number} -->", f"## Página {number}", "", f"<!-- extrator: {method} -->", "",
                  text or "[Sem texto recuperado. Conferência manual necessária.]", ""]
        if number in alternatives:
            lines += ["### Alternativa OCR: não substitui o texto nativo acima", "",
                      "> Comparação pendente com o PDF. Não concatenar as duas versões como se fossem um único texto.", "",
                      alternatives[number], ""]
    atomic_write(target, "\n".join(lines))
    print(f"{source.name}: {len(pages)} páginas; OCR tentado em {ocr_pages}; {technical}.")
    for error in errors:
        print("  " + error)
    return technical == "sem_alertas_automaticos"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", type=Path, default=ROOT / "pdfs", help="PDF ou pasta; padrão: pdfs/")
    parser.add_argument("--saida", type=Path, help="Markdown de destino para um único PDF")
    parser.add_argument("--sobrescrever", action="store_true")
    parser.add_argument("--ocr", action="store_true", help="Gera OCR em todas as páginas, preservando texto nativo como principal")
    parser.add_argument("--rotacao-ocr", type=int, choices=(0, 90, 180, 270), default=0, help="Rotação adicional somente para OCR, após conferência do PDF")
    parser.add_argument("--idiomas", default="por+eng")
    parser.add_argument("--tessdata", help="Pasta com os arquivos .traineddata")
    parser.add_argument("--atualizar-indice", action="store_true", help="Reconstrói o índice sem extrair PDFs")
    args = parser.parse_args()
    if args.atualizar_indice:
        update_index()
        print("Índice atualizado a partir do catálogo e das extrações locais.")
        return 0
    source = args.pdf.resolve()
    if not source.is_relative_to(ROOT) or not source.exists():
        parser.error("A entrada deve existir dentro do projeto.")
    if args.saida and source.is_dir():
        parser.error("--saida só pode ser usado com um PDF.")
    files = sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf") if source.is_dir() else [source]
    jobs = []
    for pdf in files:
        if args.saida:
            target = args.saida.resolve()
        elif source.is_dir():
            target = CORPUS / pdf.relative_to(source).with_suffix(".md")
        elif pdf.is_relative_to(ROOT / "pdfs"):
            target = CORPUS / pdf.relative_to(ROOT / "pdfs").with_suffix(".md")
        else:
            target = CORPUS / (pdf.stem + ".md")
        if pdf.suffix.lower() != ".pdf" or not target.is_relative_to(CORPUS) or target.suffix.lower() != ".md" or target == CORPUS / "INDEX.md":
            parser.error("Use PDF como entrada e Markdown dentro de corpus_md/ como saída, sem substituir INDEX.md.")
        jobs.append((pdf, target))
    if len({t for _, t in jobs}) != len(jobs):
        parser.error("Mais de um PDF produziria o mesmo Markdown. Renomeie as fontes.")
    ok = True
    for pdf, target in jobs:
        try:
            ok = process(pdf, target, args) and ok
        except Exception as exc:
            print(f"Falha em {pdf.name}: {exc}")
            ok = False
        finally:
            try:
                update_index()
            except (ValueError, OSError) as exc:
                print(f"Índice não atualizado: {exc}. As extrações continuam; corrija o catálogo e atualize o índice depois.")
                ok = False
    if not jobs:
        update_index()
        print("Nenhum PDF encontrado. Índice atualizado.")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as exc:
        print(f"Não foi possível concluir: {exc}")
        raise SystemExit(1)
