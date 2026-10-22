"""Verificacoes de integracao; PDFs sinteticos ficam em pastas temporarias."""
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
import pymupdf

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/extrair_pdf.py"
spec = importlib.util.spec_from_file_location("extracao", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
TEXT = "This research document contains readable text for checking extraction. " * 8


class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old_root, self.old_corpus = m.ROOT, m.CORPUS
        m.ROOT, m.CORPUS = self.root, self.root / "corpus_md"
        self.addCleanup(self.restore)
        self.source = self.root / "sample.pdf"
        self.target = m.CORPUS / "sample.md"
        self.args = SimpleNamespace(idiomas="eng", ocr=False, sobrescrever=False, tessdata=None)

    def restore(self):
        m.ROOT, m.CORPUS = self.old_root, self.old_corpus

    def make_pdf(self, scan=False, blank=False):
        with pymupdf.open() as doc:
            page = doc.new_page()
            if not blank:
                page.insert_textbox(pymupdf.Rect(50, 50, 540, 700), TEXT, fontsize=14)
            if scan:
                pix = page.get_pixmap(dpi=200)
                with pymupdf.open() as image_doc:
                    image_doc.new_page().insert_image(page.rect, stream=pix.tobytes("png"))
                    image_doc.save(self.source)
            else:
                doc.save(self.source)

    def test_native_cache_and_index_preserve_notes(self):
        self.make_pdf()
        self.assertTrue(m.process(self.source, self.target, self.args))
        meta = m.metadata(self.target)
        self.assertEqual(meta["paginas_ocr"], [])
        self.assertEqual(meta["status"], "pendente_de_revisao")
        with self.target.open("a", encoding="utf-8") as f:
            f.write("\nNota manual preservada.\n")
        before = self.target.read_bytes()
        self.assertTrue(m.process(self.source, self.target, self.args))
        self.assertEqual(before, self.target.read_bytes())
        index = m.CORPUS / "INDEX.md"
        index.write_text("# Notas\n\nMinha referencia.\n", encoding="utf-8")
        m.update_index()
        before = index.read_bytes()
        m.update_index()
        self.assertEqual(before, index.read_bytes())
        self.assertIn("Minha referencia.", index.read_text(encoding="utf-8"))
        self.assertEqual(index.read_text(encoding="utf-8").count("| sample.pdf |"), 1)

    def test_editorial_catalog_survives_refresh_and_missing_local_files(self):
        self.make_pdf()
        m.process(self.source, self.target, self.args)
        m.update_index()
        catalog_path = m.CORPUS / "catalogo.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["sample.md"].update({"referencia": "Obra conferida", "resumo": "Resumo autoral | com separador",
                                   "palavras_chave": ["tema"], "url": "https://example.org/artigo",
                                   "status_metadados": "conferido", "fichamento": "fichamento-sample.md"})
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        m.update_index()
        self.target.unlink()
        self.source.unlink()
        m.update_index()
        text = (m.CORPUS / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Obra conferida", text)
        self.assertIn("Resumo autoral &#124; com separador", text)
        self.assertIn("https://example.org/artigo", text)
        self.assertIn("markdown_local_ausente", text)
        self.assertIn("fonte_ausente", text)
        self.assertEqual(json.loads(catalog_path.read_text(encoding="utf-8"))["sample.md"]["referencia"], "Obra conferida")

    def test_catalog_only_entry_does_not_claim_extraction_or_reading(self):
        m.CORPUS.mkdir()
        (m.CORPUS / "catalogo.json").write_text(json.dumps({"future.md": {
            "referencia": "Leitura sugerida", "resumo": "Contribuicao para a discussao",
            "status_metadados": "conferido", "status_leitura": "nao_iniciada"}}), encoding="utf-8")
        m.update_index()
        index = (m.CORPUS / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Com extração registrada: **0**", index)
        self.assertIn("Leitura concluída: **0**", index)
        self.assertIn("nao_extraido", index)
        before = (m.CORPUS / "INDEX.md").read_bytes()
        m.update_index()
        self.assertEqual(before, (m.CORPUS / "INDEX.md").read_bytes())

    def test_changed_source_does_not_overwrite(self):
        self.make_pdf()
        m.process(self.source, self.target, self.args)
        before = self.target.read_bytes()
        self.source.write_bytes(self.source.read_bytes() + b"\n% changed\n")
        self.assertFalse(m.process(self.source, self.target, self.args))
        self.assertEqual(before, self.target.read_bytes())
        m.update_index()
        self.assertIn("fonte_alterada_reextrair", (m.CORPUS / "INDEX.md").read_text(encoding="utf-8"))

    def test_scanned_page_uses_real_ocr(self):
        try:
            folder = m.tessdata(None, "eng")
        except RuntimeError:
            self.skipTest("Dados Tesseract eng indisponiveis")
        self.args.tessdata = folder
        self.make_pdf(scan=True)
        self.assertTrue(m.process(self.source, self.target, self.args))
        meta = m.metadata(self.target)
        self.assertEqual(meta["paginas_ocr"], [1])
        self.assertEqual(meta["extrator"], "pymupdf+tesseract")
        self.assertIn("research", self.target.read_text(encoding="utf-8").lower())

    def test_selectable_header_does_not_hide_scanned_body(self):
        try:
            self.args.tessdata = m.tessdata(None, "eng")
        except RuntimeError:
            self.skipTest("Dados Tesseract eng indisponiveis")
        with pymupdf.open() as original:
            page = original.new_page()
            page.insert_textbox(pymupdf.Rect(40, 50, 540, 700), TEXT, fontsize=14)
            image = page.get_pixmap(dpi=180).tobytes("png")
        with pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_text((20, 25), "Research journal on digital platforms volume one demonstration article", fontsize=10)
            page.insert_image(pymupdf.Rect(0, 50, 595, 842), stream=image)
            self.assertFalse(m.quality(page.get_text()))
            doc.save(self.source)
        self.assertFalse(m.process(self.source, self.target, self.args))
        self.assertEqual(m.metadata(self.target)["paginas_ocr"], [1])
        self.assertEqual(m.metadata(self.target)["paginas_ocr_alternativo"], [1])
        self.assertIn("readable text", self.target.read_text(encoding="utf-8").lower())

    def test_tiled_scan_triggers_ocr(self):
        try:
            self.args.tessdata = m.tessdata(None, "eng")
        except RuntimeError:
            self.skipTest("Dados Tesseract eng indisponiveis")
        with pymupdf.open() as original:
            source = original.new_page(width=595, height=792)
            source.insert_textbox(pymupdf.Rect(40, 40, 550, 730), TEXT, fontsize=14)
            with pymupdf.open() as doc:
                page = doc.new_page(width=595, height=842)
                page.insert_text((10, 20), "Research journal with selectable header for platform article", fontsize=8)
                for y in (0, 1):
                    for x in (0, 1):
                        rect = pymupdf.Rect(x * 297.5, y * 396, (x + 1) * 297.5, (y + 1) * 396)
                        page.insert_image(pymupdf.Rect(rect.x0, rect.y0 + 50, rect.x1, rect.y1 + 50), stream=source.get_pixmap(dpi=180, clip=rect).tobytes("png"), keep_proportion=False)
                self.assertGreater(m.image_coverage(page), .9)
                doc.save(self.source)
        self.assertFalse(m.process(self.source, self.target, self.args))
        self.assertEqual(m.metadata(self.target)["paginas_ocr"], [1])
        self.assertEqual(m.metadata(self.target)["paginas_ocr_alternativo"], [1])
        self.assertIn("readable text", self.target.read_text(encoding="utf-8").lower())

    def test_overlapping_images_are_not_counted_twice(self):
        with pymupdf.open() as source:
            source.new_page().insert_text((20, 30), "Logo")
            image = source[0].get_pixmap().tobytes("png")
        with pymupdf.open() as doc:
            page = doc.new_page(width=100, height=100)
            for _ in range(3):
                page.insert_image(pymupdf.Rect(0, 0, 40, 100), stream=image, keep_proportion=False)
            self.assertAlmostEqual(m.image_coverage(page), .4, places=3)

    def test_null_metadata_and_keywords(self):
        m.CORPUS.mkdir()
        path = m.CORPUS / "catalogo.json"
        path.write_text(json.dumps({"future.md": {"extracao": None, "palavras_chave": None, "referencia": "Leitura futura"}}), encoding="utf-8")
        m.update_index()
        self.assertIn("nao_extraido", (m.CORPUS / "INDEX.md").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["future.md"]["referencia"], "Leitura futura")

    def test_invalid_catalog_is_reported_without_overwriting(self):
        m.CORPUS.mkdir()
        path = m.CORPUS / "catalogo.json"
        path.write_text(json.dumps({"bad.md": {"palavras_chave": 42}}), encoding="utf-8")
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "bad.md.palavras_chave"):
            m.update_index()
        self.assertEqual(before, path.read_bytes())
        self.assertFalse((m.CORPUS / "INDEX.md").exists())

    def test_invalid_technical_fields_preserve_catalog(self):
        m.CORPUS.mkdir()
        path = m.CORPUS / "catalogo.json"
        for field in ("sha256", "fonte", "verificacao_tecnica", "status", "extrator"):
            with self.subTest(field=field):
                path.write_text(json.dumps({"bad.md": {"extracao": {field: ["invalid"]}}}), encoding="utf-8")
                before = path.read_bytes()
                with self.assertRaisesRegex(ValueError, "bad.md.extracao." + field):
                    m.update_index()
                self.assertEqual(before, path.read_bytes())
                self.assertFalse((m.CORPUS / "INDEX.md").exists())

    def test_page_rotation_does_not_hide_scanned_body(self):
        try:
            self.args.tessdata = m.tessdata(None, "eng")
        except RuntimeError:
            self.skipTest("Dados Tesseract eng indisponiveis")
        with pymupdf.open() as original:
            p = original.new_page(width=300, height=1000)
            p.insert_textbox(pymupdf.Rect(20, 50, 280, 950), TEXT, fontsize=12)
            image = p.get_pixmap(dpi=160).tobytes("png")
        with pymupdf.open() as doc:
            p = doc.new_page(width=300, height=1000)
            p.insert_image(p.rect, stream=image)
            p.insert_text((20, 25), "Selectable document header for research collection", fontsize=9)
            p.set_rotation(90)
            self.assertGreater(m.image_coverage(p), .99)
            doc.save(self.source)
        self.args.rotacao_ocr = 270
        self.assertFalse(m.process(self.source, self.target, self.args))
        self.assertEqual(m.metadata(self.target)["paginas_ocr"], [1])
        self.assertEqual(m.metadata(self.target)["paginas_ocr_alternativo"], [1])
        self.assertIn("readable text", self.target.read_text(encoding="utf-8").lower())

    def test_explicit_rotation_preserves_source(self):
        self.check_rotated_scan(90)

    def test_explicit_upside_down_correction(self):
        self.check_rotated_scan(180)

    def check_rotated_scan(self, angle):
        try:
            self.args.tessdata = m.tessdata(None, "eng")
        except RuntimeError:
            self.skipTest("Dados Tesseract eng indisponiveis")
        with pymupdf.open() as original:
            page = original.new_page(width=595, height=842)
            page.insert_textbox(pymupdf.Rect(40, 50, 550, 750), TEXT * 2, fontsize=14)
            page.set_rotation(angle)
            pix = page.get_pixmap(dpi=160)
            with pymupdf.open() as doc:
                page = doc.new_page(width=original[0].rect.width, height=original[0].rect.height)
                page.insert_image(page.rect, stream=pix.tobytes("png"))
                doc.save(self.source)
        before = self.source.read_bytes()
        self.args.rotacao_ocr = (-angle) % 360
        self.assertTrue(m.process(self.source, self.target, self.args))
        self.assertIn("readable text", self.target.read_text(encoding="utf-8").lower())
        self.assertTrue(m.metadata(self.target)["rotacoes_ocr"])
        self.assertEqual(before, self.source.read_bytes())

    def test_longer_ocr_never_replaces_native_text(self):
        self.make_pdf()
        with pymupdf.open(self.source) as doc:
            native = doc[0].get_text("text", sort=True).strip()
        self.args.ocr = True
        with patch.object(m, "tessdata", return_value="unused"), patch.object(m, "ocr_page", return_value="Incorrect OCR content. " * 100):
            self.assertFalse(m.process(self.source, self.target, self.args))
        body = self.target.read_text(encoding="utf-8").split("<!-- extrator: pymupdf -->", 1)[1]
        self.assertTrue(body.lstrip().startswith(native))
        self.assertIn("Alternativa OCR", body)
        self.assertEqual(m.metadata(self.target)["paginas_pendentes"], [1])

    def test_short_native_text_does_not_trigger_ocr(self):
        with pymupdf.open() as doc:
            doc.new_page().insert_text((30, 40), "a b c x y z 1 2 3")
            doc.save(self.source)
        with patch.object(m, "ocr_page", side_effect=AssertionError("OCR desnecessario")) as ocr:
            self.assertFalse(m.process(self.source, self.target, self.args))
        ocr.assert_not_called()
        self.assertEqual(m.metadata(self.target)["paginas_ocr"], [])
        self.assertIn("a b c x y z", self.target.read_text(encoding="utf-8"))

    def test_invalid_catalog_does_not_stop_remaining_extractions(self):
        self.make_pdf()
        (self.root / "other.pdf").write_bytes(self.source.read_bytes())
        m.CORPUS.mkdir()
        path = m.CORPUS / "catalogo.json"
        path.write_text('{"bad.md":{"palavras_chave":42}}', encoding="utf-8")
        before = path.read_bytes()
        with patch("sys.argv", ["extrair_pdf.py", str(self.root)]):
            self.assertEqual(m.main(), 1)
        self.assertTrue(self.target.exists())
        self.assertTrue((m.CORPUS / "other.md").exists())
        self.assertEqual(path.read_bytes(), before)

    def test_small_illustration_does_not_force_ocr(self):
        with pymupdf.open() as original:
            original.new_page().insert_text((30, 40), "Illustration")
            image = original[0].get_pixmap().tobytes("png")
        with pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_textbox(pymupdf.Rect(30, 30, 540, 500), TEXT, fontsize=12)
            page.insert_image(pymupdf.Rect(20, 600, 100, 680), stream=image)
            self.assertFalse(m.image_text_suspect(page, page.get_text()))

    def test_duplicate_hash_is_flagged_without_erasing_metadata(self):
        self.make_pdf()
        m.process(self.source, self.target, self.args)
        other = m.CORPUS / "other.md"
        other.write_bytes(self.target.read_bytes())
        m.update_index()
        index = (m.CORPUS / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("conteudo_duplicado", index)
        self.assertIn("Conteúdos extraídos distintos (SHA-256): **1**", index)
        self.assertEqual(len(json.loads((m.CORPUS / "catalogo.json").read_text(encoding="utf-8"))), 2)
        self.assertTrue(self.target.exists() and other.exists())

    def test_missing_language_records_failure_in_index(self):
        self.make_pdf(scan=True)
        self.args.idiomas = "idioma_inexistente"
        self.assertFalse(m.process(self.source, self.target, self.args))
        self.assertEqual(m.metadata(self.target)["paginas_pendentes"], [1])
        m.update_index()
        self.assertIn("revisao_necessaria", (m.CORPUS / "INDEX.md").read_text(encoding="utf-8"))

    def test_corrupt_pdf_records_failure(self):
        self.source.write_bytes(b"not a PDF")
        self.assertFalse(m.process(self.source, self.target, self.args))
        self.assertTrue(m.metadata(self.target)["avisos"])
        m.update_index()
        self.assertIn("sample.pdf", (m.CORPUS / "INDEX.md").read_text(encoding="utf-8"))

    def test_blank_page_is_not_silently_accepted(self):
        self.make_pdf(blank=True)
        self.assertFalse(m.process(self.source, self.target, self.args))
        self.assertEqual(m.metadata(self.target)["paginas_pendentes"], [1])


if __name__ == "__main__":
    unittest.main()
