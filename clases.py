import sys
from pathlib import Path
import pandas as pd

# GitHub Copilot
# archivo: D:/UEX/ControlAsistencia/clases.py
# Script: combinar CSV de clases y mostrar estadísticas de ocupación de aulas
# Uso: python clases.py
# Requisitos: pandas, openpyxl
# Instalar: pip install pandas openpyxl


# Lista de archivos esperados (coloque los CSV en el mismo directorio que este script
# o modifique las rutas)
FILES = [
    "clases_informatica.csv",
    "clases_telematica.csv",
    "clases_diseño.csv",
    "clases_enfermeria.csv",
    "clases_geomatica.csv",
]

OUT_CSV = "horarios_cume.csv"
OUT_XLSX = "horarios_cume.xlsx"

# columnas esperadas estándar (✅ AÑADIDO cuatrimestre)
EXPECTED_COLS = {"asignatura", "dia", "hora", "aula", "carrera", "cuatrimestre"}


def normalize_columns(df):
    """Normaliza nombres de columnas a minúsculas sin espacios extras y mapea variantes comunes."""
    mapping = {}
    for c in df.columns:
        c0 = c.strip().lower()
        c0 = c0.replace(" ", "_")
        # mapeos comunes
        c0 = c0.replace("asignatura", "asignatura")
        c0 = c0.replace("día", "dia").replace("dia", "dia")
        c0 = c0.replace("horario", "hora").replace("hora", "hora")
        c0 = c0.replace("aula", "aula")
        c0 = c0.replace("carrera", "carrera")
        c0 = c0.replace("cuatrimestre", "cuatrimestre")
        mapping[c] = c0
    df = df.rename(columns=mapping)
    return df


def read_and_validate(path: Path):
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")
    df = normalize_columns(df)
    present = set(df.columns)
    missing = EXPECTED_COLS - present
    if missing:
        raise ValueError(f"El archivo {path.name} no tiene las columnas esperadas: faltan {missing}")
    # asegurar solo columnas relevantes
    return df[list(EXPECTED_COLS)]


def main():
    base = Path(".")
    dfs = []
    
    print("🔍 Buscando archivos CSV...")
    print(f"📁 Directorio de trabajo: {base.absolute()}\n")
    
    for fname in FILES:
        p = base / fname
        print(f"   Buscando: {fname}...", end=" ")
        
        if not p.exists():
            print(f"❌ NO ENCONTRADO (ruta completa: {p.absolute()})")
            continue
        
        print(f"✓ Encontrado")
        
        try:
            df = read_and_validate(p)
            df["origen"] = fname
            dfs.append(df)
            print(f"      ✅ Leído correctamente: {len(df)} filas")
            print(f"      📊 Columnas: {list(df.columns)}")
            if 'carrera' in df.columns:
                print(f"      🎓 Carreras únicas: {df['carrera'].unique().tolist()}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📦 Total de archivos cargados: {len(dfs)}/{len(FILES)}\n")
    if not dfs:
        print("No se cargaron archivos. Coloque los CSV en el directorio y vuelva a ejecutar.")
        sys.exit(1)

    all_df = pd.concat(dfs, ignore_index=True)

    # Guardar combinados
    all_df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    all_df.to_excel(OUT_XLSX, index=False, engine="openpyxl")
    print(f"\nGuardado: {OUT_CSV} y {OUT_XLSX} (total registros: {len(all_df)})\n")

    # Estadísticas sobre ocupación de aulas
    # 1) Conteo por aula
    aulas_count = all_df["aula"].value_counts().rename_axis("aula").reset_index(name="clases")
    aulas_count["pct"] = (aulas_count["clases"] / len(all_df) * 100).round(2)
    aulas_count.to_csv("estad_ocupacion_aulas.csv", index=False, encoding="utf-8")
    print("Ocupación por aula (top 10):")
    print(aulas_count.head(10).to_string(index=False))

    # 2) Pivot día x hora (número de clases en cada franja)
    pivot = pd.pivot_table(all_df, index="dia", columns="hora", values="asignatura", aggfunc="count", fill_value=0)
    pivot.to_csv("pivot_dia_hora.csv", encoding="utf-8")
    print("\nTop franjas día/hora más ocupadas (lista de las 10 combinaciones con más clases):")
    pivot_long = pivot.stack().reset_index()
    pivot_long.columns = ["dia", "hora", "clases"]
    top_slots = pivot_long.sort_values("clases", ascending=False).head(10)
    print(top_slots.to_string(index=False))

    # 3) Aula más ocupada
    top_aula = aulas_count.iloc[0]
    print(f"\nAula más ocupada: {top_aula['aula']} con {top_aula['clases']} clases ({top_aula['pct']}%)")

    # 4) Ocupación por día
    dias = all_df["dia"].value_counts().rename_axis("dia").reset_index(name="clases")
    dias["pct"] = (dias["clases"] / len(all_df) * 100).round(2)
    dias.to_csv("estad_ocupacion_dia.csv", index=False, encoding="utf-8")
    print("\nClases por día:")
    print(dias.to_string(index=False))

    # 5) Ocupación por carrera
    carreras = all_df["carrera"].value_counts().rename_axis("carrera").reset_index(name="clases")
    carreras["pct"] = (carreras["clases"] / len(all_df) * 100).round(2)
    carreras.to_csv("estad_ocupacion_carrera.csv", index=False, encoding="utf-8")
    print("\n🎓 Clases por carrera:")
    print(carreras.to_string(index=False))

    # 6) Ocupación por cuatrimestre
    cuatrimestres = all_df["cuatrimestre"].value_counts().rename_axis("cuatrimestre").reset_index(name="clases")
    cuatrimestres = cuatrimestres.sort_values("cuatrimestre")  # Ordenar por cuatrimestre
    cuatrimestres["pct"] = (cuatrimestres["clases"] / len(all_df) * 100).round(2)
    cuatrimestres.to_csv("estad_ocupacion_cuatrimestre.csv", index=False, encoding="utf-8")
    print("\n📆 Clases por cuatrimestre:")
    print(cuatrimestres.to_string(index=False))

    # 7) Ocupación por carrera y cuatrimestre (tabla cruzada)
    pivot_carrera_cuatri = pd.pivot_table(
        all_df, 
        index="carrera", 
        columns="cuatrimestre", 
        values="asignatura", 
        aggfunc="count", 
        fill_value=0
    )
    pivot_carrera_cuatri.to_csv("estad_carrera_por_cuatrimestre.csv", encoding="utf-8")
    print("\n🎓📆 Distribución de clases por carrera y cuatrimestre:")
    print(pivot_carrera_cuatri.to_string())

    # 8) Aulas más ocupadas por cuatrimestre
    print("\n🏫📆 Top 5 aulas más ocupadas por cuatrimestre:")
    for cuatri in sorted(all_df["cuatrimestre"].unique()):
        df_cuatri = all_df[all_df["cuatrimestre"] == cuatri]
        top_aulas_cuatri = df_cuatri["aula"].value_counts().head(5)
        print(f"\n  Cuatrimestre {cuatri}:")
        for aula, count in top_aulas_cuatri.items():
            pct = (count / len(df_cuatri) * 100)
            print(f"    • {aula}: {count} clases ({pct:.1f}%)")

    # 9) Resumen: número de asignaturas distintas, aulas y franjas
    resumen = {
        "total_registros": len(all_df),
        "asignaturas_distintas": all_df["asignatura"].nunique(),
        "aulas_distintas": all_df["aula"].nunique(),
        "dias_distintos": all_df["dia"].nunique(),
        "franjas_hora_distintas": all_df["hora"].nunique(),
        "carreras_totales": len(dfs),
        "cuatrimestres_distintos": all_df["cuatrimestre"].nunique(),
    }
    print("\n📊 Resumen General:")
    for k, v in resumen.items():
        print(f"   • {k.replace('_', ' ').title()}: {v}")

    # Guardar resumen sencillo
    pd.Series(resumen).to_frame("valor").to_csv("resumen_general.csv", encoding="utf-8")

    print("\n📂 Archivos generados:")
    print("   ✅ horarios_cume.csv")
    print("   ✅ horarios_cume.xlsx")
    print("   ✅ estad_ocupacion_aulas.csv")
    print("   ✅ pivot_dia_hora.csv")
    print("   ✅ estad_ocupacion_dia.csv")
    print("   ✅ estad_ocupacion_carrera.csv")
    print("   ✅ estad_ocupacion_cuatrimestre.csv")
    print("   ✅ estad_carrera_por_cuatrimestre.csv")
    print("   ✅ resumen_general.csv")
    print("\n✅ Proceso completado sin errores.\n")


if __name__ == "__main__":
    main()