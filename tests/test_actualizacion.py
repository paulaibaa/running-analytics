"""Pruebas locales del flujo CSV -> HTML; no conectan con Garmin."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from actualizar_running import extraer_carreras, guardar_preparado, preparar_carreras
from generar_dashboard import generar_dashboard
from actualizar_running import copiar_a_docs, guardar_metadatos, leer_opciones, main


class ActualizacionTests(unittest.TestCase):
    def test_copia_es_opcional_y_reemplaza_solo_destino(self):
        self.assertFalse(leer_opciones([]).copiar_a_docs)
        self.assertTrue(leer_opciones(["--copiar-a-docs"]).copiar_a_docs)
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            html = folder / "dashboard.html"
            html.write_text("<html>nuevo</html>", encoding="utf-8")
            docs = folder / "docs"
            docs.mkdir()
            (docs / "index.html").write_text("anterior", encoding="utf-8")
            destino = copiar_a_docs(html, docs)
            self.assertEqual(destino.read_bytes(), html.read_bytes())
            self.assertTrue((docs / ".nojekyll").is_file())
            self.assertFalse((docs / "index.html.tmp").exists())

    def test_main_solo_copia_con_opcion(self):
        import actualizar_running as modulo
        with patch.multiple(modulo, conectar_garmin=unittest.mock.DEFAULT,
                            extraer_carreras=unittest.mock.DEFAULT,
                            guardar_original=unittest.mock.DEFAULT,
                            preparar_carreras=unittest.mock.DEFAULT,
                            guardar_preparado=unittest.mock.DEFAULT,
                            guardar_metadatos=unittest.mock.DEFAULT,
                            generar_dashboard=unittest.mock.DEFAULT,
                            copiar_a_docs=unittest.mock.DEFAULT) as mocks:
            main([])
            mocks["copiar_a_docs"].assert_not_called()
            main(["--copiar-a-docs"])
            mocks["copiar_a_docs"].assert_called_once()

    def test_paginacion_avanza_y_termina(self):
        class Cliente:
            posiciones = []

            def get_activities(self, start, limit, activitytype):
                self.posiciones.append(start)
                return [{"activityId": i} for i in range(25)][start:start + limit]

        cliente = Cliente()
        carreras = extraer_carreras(cliente)
        self.assertEqual(len(carreras), 25)
        self.assertEqual(cliente.posiciones, [0, 20, 25])

    def test_csv_y_dashboard_reflejan_los_mismos_datos(self):
        # Datos mínimos de prueba, no se mezclan con el historial real.
        columnas = ["activityId", "activityName", "activityType", "startTimeLocal", "distance", "duration", "steps"]
        carreras = [{
            "activityId": 1, "activityName": " Prueba ",
            "activityType": {"typeKey": "running"},
            "startTimeLocal": "2026-01-01 10:00:00", "distance": 5000., "duration": 1800., "steps": 9000.
        }]
        df = preparar_carreras(carreras, columnas)
        self.assertEqual(df.loc[0, "pace_min_km"], 6.)
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            csv = guardar_preparado(df, folder)
            html = generar_dashboard(csv, folder / "running_dashboard.html")
            text = html.read_text(encoding="utf-8")
            payload = json.loads(re.search(
                r'<script id="running-data" type="application/json">(.*?)</script>', text, re.S
            ).group(1))
            self.assertEqual(payload["meta"]["rows"], len(pd.read_csv(csv)))
            self.assertEqual(payload["activities"][0]["steps"], 9000.)
            self.assertEqual(payload["activities"][0]["distance_km"], 5.)
            self.assertIn("generatedAt", payload["meta"])
            self.assertIn("sourceModifiedAt", payload["meta"])
            self.assertIsNone(payload["meta"]["extractionFinishedAt"])
            instante = datetime(2026, 1, 2, tzinfo=timezone.utc)
            guardar_metadatos(csv, folder / "original.json", instante, instante, 1)
            generar_dashboard(csv, html)
            def meta_actual():
                return json.loads(re.search(
                    r'<script id="running-data" type="application/json">(.*?)</script>',
                    html.read_text(encoding="utf-8"), re.S
                ).group(1))["meta"]
            self.assertEqual(meta_actual()["extractionFinishedAt"], instante.isoformat())
            csv.write_text(csv.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            generar_dashboard(csv, html)
            self.assertIsNone(meta_actual()["extractionFinishedAt"])
            self.assertFalse((folder / "running_dashboard_v4.html").exists())
            self.assertFalse((folder / "running_preparado_temporal.csv").exists())

    def test_datos_invalidos_se_detienen_antes_del_guardado(self):
        with self.assertRaises(ValueError):
            preparar_carreras([], [])
        carreras = [{"activityId": 1}, {"activityId": 1}]
        with self.assertRaisesRegex(ValueError, "repetidos"):
            preparar_carreras(carreras, ["activityId"])


if __name__ == "__main__":
    unittest.main()
