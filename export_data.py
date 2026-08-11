#!/usr/bin/env python3
"""
Script para exportar datos de Modelo de Madurez Territorios STEM a JSON
Uso: python3 export_data.py <ruta_excel> <ruta_salida_json>
"""

import pandas as pd
import json
import sys
from datetime import datetime

def export_to_json(excel_path, output_path):
    """
    Exporta datos del Excel a formato JSON para el visualizador
    """
    try:
        # Leer hojas necesarias
        print(f"Leyendo archivo: {excel_path}")
        
        df_total_dim = pd.read_excel(excel_path, sheet_name='Total_Dim')
        df_dict = pd.read_excel(excel_path, sheet_name='Diccionario')
        df_sheet1 = pd.read_excel(excel_path, sheet_name='Sheet1')
        
        # Estructura de datos a exportar
        data = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0",
                "model_version": "Modelo de Madurez Territorios STEM+ 2025"
            },
            "dimensions": {
                "1. Visión": {
                    "id": 1,
                    "name": "Visión",
                    "color": "#FF6B6B",
                    "domains": []
                },
                "2. Trabajo en Red": {
                    "id": 2,
                    "name": "Trabajo en Red",
                    "color": "#4ECDC4",
                    "domains": []
                },
                "3. Aprendizaje Colectivo": {
                    "id": 3,
                    "name": "Aprendizaje Colectivo",
                    "color": "#FFD93D",
                    "domains": []
                },
                "4. Impacto": {
                    "id": 4,
                    "name": "Impacto",
                    "color": "#6BCB77",
                    "domains": []
                }
            },
            "maturity_levels": {
                "Temprana": {
                    "level": 1,
                    "range": [0, 25],
                    "color": "#FFDDC1"
                },
                "Crecimiento": {
                    "level": 2,
                    "range": [26, 50],
                    "color": "#FFB88C"
                },
                "Consolidación": {
                    "level": 3,
                    "range": [51, 75],
                    "color": "#90EE90"
                },
                "Expansión": {
                    "level": 4,
                    "range": [76, 100],
                    "color": "#00CED1"
                }
            },
            "territories": []
        }
        
        # Mapear dominios a dimensiones
        domain_to_dimension = {}
        for _, row in df_dict.iterrows():
            domain = row['Dominio']
            dimension = row['Dimension']
            if domain and dimension:
                domain_to_dimension[str(domain).strip()] = str(dimension).strip()
        
        # Agregar dominios únicos a las dimensiones
        for domain, dimension_key in domain_to_dimension.items():
            for dim_key, dim_data in data['dimensions'].items():
                if dim_key.split('. ', 1)[1] == dimension_key.split('. ', 1)[1]:
                    if domain not in dim_data['domains']:
                        dim_data['domains'].append(domain)
                    break
        
        # Procesar datos de territorios
        territories_set = set()
        if 'Territorio STEM+ que realiza el auto-diagnóstico' in df_sheet1.columns:
            territories_set = set(df_sheet1['Territorio STEM+ que realiza el auto-diagnóstico'].dropna())
        
        # Crear registro para cada territorio y aplicación
        for idx, row in df_total_dim.iterrows():
            territory_id = row['Id']
            
            # Extraer valores por dimensión
            dimension_scores = {}
            for dim_key in ['1. Visión', '2. Trabajo en Red', '3. Aprendizaje Colectivo', '4. Impacto']:
                if dim_key in row:
                    score = row[dim_key]
                    if pd.notna(score):
                        try:
                            dimension_scores[dim_key] = float(score)
                        except:
                            dimension_scores[dim_key] = 0
                    else:
                        dimension_scores[dim_key] = 0
            
            # Determinar nivel general
            if all(v in dimension_scores for v in ['1. Visión', '2. Trabajo en Red', '3. Aprendizaje Colectivo', '4. Impacto']):
                avg_score = sum(dimension_scores.values()) / 4
            else:
                avg_score = 0
            
            # Determinar nivel de madurez
            maturity_level = "Temprana"
            if avg_score <= 25:
                maturity_level = "Temprana"
            elif avg_score <= 50:
                maturity_level = "Crecimiento"
            elif avg_score <= 75:
                maturity_level = "Consolidación"
            else:
                maturity_level = "Expansión"
            
            # Obtener territorio y organización de Sheet1
            territory_name = "Territorio"
            organization = "Organización"
            if territory_id - 1 < len(df_sheet1):
                sheet_row = df_sheet1.iloc[territory_id - 1]
                if 'Territorio STEM+ que realiza el auto-diagnóstico' in df_sheet1.columns:
                    territory_name = sheet_row.get('Territorio STEM+ que realiza el auto-diagnóstico', f'Territorio {territory_id}')
                if 'Organización a la que pertenece' in df_sheet1.columns:
                    organization = sheet_row.get('Organización a la que pertenece', 'Organización')
            
            territory_record = {
                "id": int(territory_id),
                "name": str(territory_name) if pd.notna(territory_name) else f"Territorio {territory_id}",
                "organization": str(organization) if pd.notna(organization) else "Organización",
                "dimension_scores": dimension_scores,
                "general_score": round(avg_score, 2),
                "maturity_level": maturity_level,
                "timestamp": datetime.now().isoformat()
            }
            
            data['territories'].append(territory_record)
        
        # Guardar JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Exportación exitosa!")
        print(f"  - Territorios procesados: {len(data['territories'])}")
        print(f"  - Dimensiones: {len(data['dimensions'])}")
        print(f"  - Archivo guardado: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error durante la exportación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 export_data.py <ruta_excel> [ruta_salida.json]")
        print("\nEjemplo:")
        print("  python3 export_data.py 'datos.xlsx' 'dashboard_data.json'")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'dashboard_data.json'
    
    export_to_json(excel_path, output_path)
