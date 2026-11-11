"""Genera el dashboard local posterior al notebook 03, sin conectar a Garmin."""
import argparse
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TEXT = {
    'activityId', 'activityName', 'startTimeLocal', 'startTimeGMT',
    'fecha_local', 'modalidad', 'trainingEffectLabel',
    'aerobicTrainingEffectMessage', 'anaerobicTrainingEffectMessage', 'isPR',
}
RUNNING = {'running', 'treadmill_running', 'trail_running', 'track_running',
           'indoor_running', 'ultra_run', 'virtual_run', 'street_running'}


def numeric(series):
    """El CSV preparado usa punto; también admite coma decimal y --."""
    text = series.astype('string').str.strip().replace({'--': pd.NA, '': pd.NA})
    return pd.to_numeric(text.str.replace(',', '.', regex=False), errors='coerce')


def prepare(path):
    df = pd.read_csv(path, dtype={'activityId': 'string'}, na_values=['--', ''])
    required = {'activityId', 'activityName', 'fecha_local', 'modalidad', 'distance', 'duration'}
    if missing := required - set(df.columns):
        raise ValueError(f'Faltan columnas del CSV preparado: {sorted(missing)}')
    before = len(df)
    unknown = sorted(set(df.modalidad.dropna()) - RUNNING)
    df = df[df.modalidad.isin(RUNNING)].copy()
    if df.empty:
        raise ValueError('No hay actividades de running reconocidas.')
    if df.activityId.isna().any() or df.activityId.duplicated().any():
        raise ValueError('Identificadores ausentes o duplicados: revisa la fuente.')
    df['fecha_local'] = pd.to_datetime(df.fecha_local, errors='raise')
    if df.fecha_local.isna().any():
        raise ValueError('Hay fechas ausentes.')
    for col in df.columns:
        if col not in TEXT:
            df[col] = numeric(df[col])
    # Los campos originales están ya en metros y segundos, según notebooks 01–03.
    for col in ('distance', 'duration'):
        if (df[col].isna() | (df[col] <= 0)).any():
            raise ValueError(f'{col}: existen valores ausentes o no positivos.')
    df['distance_km'] = df.distance / 1000
    df['pace_sec_km'] = df.duration / df.distance_km
    df['duration_min'] = df.duration / 60
    df['pace_min_km'] = df.pace_sec_km / 60
    # Cero es legítimo en desnivel/Training Effect/zonas, pero no en FC o zancada.
    for col in ('averageHR', 'maxHR', 'averageRunningCadenceInStepsPerMinute', 'avgStrideLength'):
        if col in df:
            df.loc[df[col] <= 0, col] = float('nan')
    df['fecha_local'] = df.fecha_local.dt.strftime('%Y-%m-%dT%H:%M:%S')
    df = df.sort_values('fecha_local')
    # Pandas serializa NaN como null. No se rellena ningún nulo con cero.
    records = json.loads(df.to_json(orient='records', force_ascii=False, double_precision=10))
    return records, {
        'source': path.name, 'rows': len(records), 'excluded': before - len(records),
        'unknownTypes': unknown, 'columns': list(df.columns),
        'missing': {c: int(df[c].isna().sum()) for c in df},
        'from': records[0]['fecha_local'], 'to': records[-1]['fecha_local'],
    }


def generar_dashboard(entrada=None, salida=None):
    """Genera una única salida; también se puede llamar desde el actualizador."""
    entrada = Path(entrada) if entrada is not None else ROOT / 'data/processed/running_preparado.csv'
    salida = Path(salida) if salida is not None else ROOT / 'dashboard/running_dashboard.html'
    records, meta = prepare(entrada)
    meta['generatedAt'] = datetime.now(timezone.utc).isoformat()
    meta['sourceModifiedAt'] = datetime.fromtimestamp(entrada.stat().st_mtime, timezone.utc).isoformat()
    # Solo usamos fechas de extracción si los metadatos pertenecen a este CSV.
    meta['extractionStartedAt'] = None
    meta['extractionFinishedAt'] = None
    ruta_metadatos = entrada.with_suffix('.metadata.json')
    if ruta_metadatos.is_file():
        datos = json.loads(ruta_metadatos.read_text(encoding='utf-8'))
        if datos.get('csv_sha256') == hashlib.sha256(entrada.read_bytes()).hexdigest():
            meta['extractionStartedAt'] = datos.get('extraction_started_at')
            meta['extractionFinishedAt'] = datos.get('extraction_finished_at')
    template = (ROOT / 'src/dashboard_template.html').read_text(encoding='utf-8')
    # Impide que un nombre de actividad cierre el bloque <script> incrustado.
    payload = json.dumps({'meta': meta, 'activities': records}, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c')
    html = template.replace('__RUNNING_DATA__', payload)
    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = salida.with_name(salida.name + '.tmp')
    temporal.write_text(html, encoding='utf-8')
    temporal.replace(salida)
    print(f'Dashboard: {salida.resolve()} ({len(records)} actividades)')
    return salida


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'data/processed/running_preparado.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'dashboard/running_dashboard.html')
    args = parser.parse_args()
    generar_dashboard(args.input, args.output)


if __name__ == '__main__':
    main()
