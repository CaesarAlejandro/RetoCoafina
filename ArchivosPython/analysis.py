
import sys
import os
import json
import time
import numpy as np
import uproot
import awkward as ak
import vector
import atlasopenmagic as atom
import re

# --- Configuración del Análisis ---
atom.set_release('2025e-13tev-beta')
fraction = 0.2 # Usar una fracción de los datos para acelerar la ejecución
skim = "exactly4lep"
GeV = 1.0

# --- Definiciones de Samples y Funciones ---
defs = {
    r'Background $Z,t\bar{t},t\bar{t}+V,VVV$':{'dids': [410470,410155,410218,410219,412043,364243,364242,364246,364248,700320,700321,700322,700323,700324,700325], 'color': "#6b59d3" },
    r'Background $ZZ^{*}$': {'dids': [700600],'color': "#ff0000" },
    r'Signal ($m_H$ = 125 GeV)':  {'dids': [345060, 346228, 346310, 346311, 346312, 346340, 346341, 346342],'color': "#00cdff" },
}

def cut_lep_type(lep_type):
    sum_lep_type = ak.sum(lep_type, axis=1)
    return (sum_lep_type != 44) & (sum_lep_type != 48) & (sum_lep_type != 52)

def cut_lep_charge(lep_charge):
    return ak.sum(lep_charge, axis=1) != 0

def calc_mass(lep_pt, lep_eta, lep_phi, lep_e):
    p4 = vector.zip({"pt": lep_pt, "eta": lep_eta, "phi": lep_phi, "E": lep_e})
    return (p4[:, 0] + p4[:, 1] + p4[:, 2] + p4[:, 3]).m

def cut_trig_match(lep_trigmatch):
    return ak.sum(lep_trigmatch, axis=1) >= 1

def cut_trig(trigE, trigM):
    return trigE | trigM

def ID_iso_cut(IDel, IDmu, isoel, isomu, pid):
    return (ak.sum(((pid == 13) & IDmu & isomu) | ((pid == 11) & IDel & isoel), axis=1) == 4)

def calc_weight(lumi, weight_variables, events):
    total_weight = (lumi * 1000) / events["sum_of_weights"]
    for variable in weight_variables:
        total_weight = total_weight * abs(events[variable])
    return total_weight


# --- Configuración del Histograma ---
m_min = 80      # GeV
m_max = 170     # GeV
step_size = 2   # GeV
bin_edges = np.arange(start=m_min, stop=m_max, step=step_size)

# ## 6. Bucle Principal de Análisis por Período (con filtrado por RunYear)
#
# Estrategia: Cargar todos los datos y simulaciones una vez, y luego filtrar por
# la variable 'RunYear' para generar los JSONs para cada período.

# --- 1. Carga y procesamiento inicial de todos los datos ---

# Variables a leer, AHORA SIN 'RunYear' directametne del tree para los datos
variables = ['lep_pt', 'lep_eta', 'lep_phi', 'lep_e', 'lep_charge', 'lep_type', 'lep_isTrigMatched', 'lep_isLooseID', 'lep_isMediumID', 'lep_isTightID', 'lep_isLooseIso', 'lep_isTightIso', 'trigE', 'trigM']
weight_variables = ['mcWeight', 'scaleFactor_PILEUP', 'scaleFactor_ELE', 'scaleFactor_MUON', 'scaleFactor_LepTRIGGER']

# Usamos 'defs' y añadimos 'Data' con el atajo 'data' que agrupa todos los años
defs_total = { 'Data': {'dids': ['data']} }
for key, value in defs.items():
    defs_total[key] = value

print("Cargando y procesando todos los samples (esto puede tardar)...")
samples_total = atom.build_dataset(defs_total, skim=skim, protocol='https')
all_data_unfiltered = {}

for s in samples_total:
    print('Procesando sample: ' + s)
    frames = []
    for val in samples_total[s]['list']:
        start = time.time()
        try:
            tree = uproot.open(val + ":analysis")
            print(f"\tArchivo: {val.split('/')[-1]}")

            # Leemos todas las variables necesarias. 'RunYear' se añadirá manualmente para Data.
            iter_vars = variables + weight_variables + ["sum_of_weights"] if 'data' not in s.lower() else variables + ["sum_of_weights"]

            # Iterate and process data
            for data in tree.iterate(iter_vars, library="ak", entry_stop=tree.num_entries * fraction):
                # Para los datos, extraemos el RunYear del nombre del archivo
                if 'data' in s.lower():
                    match = re.search(r'data(\d{2})', val)
                    if match:
                        year_suffix = int(match.group(1))
                        run_year = 2000 + year_suffix # Asumiendo años 20xx
                        # Añadimos RunYear al array de awkward
                        data['RunYear'] = ak.Array([run_year] * len(data))
                    else:
                        print(f"Warning: No se pudo extraer RunYear del nombre del archivo: {val}. Saltando este chunk.")
                        continue # Saltar este chunk si no se puede determinar el año

                # Aplicamos todos los cortes comunes
                data = data[cut_trig(data.trigE, data.trigM)]
                data = data[cut_trig_match(data.lep_isTrigMatched)]
                data = data[ak.all(data.lep_pt > 10, axis=1)]
                data = data[data.lep_pt[:,0] > 20]
                data = data[data.lep_pt[:,1] > 15]
                data = data[ID_iso_cut(data.lep_isLooseID, data.lep_isMediumID, data.lep_isLooseIso, data.lep_isLooseIso, data.lep_type)]
                data = data[~cut_lep_type(data.lep_type)]
                data = data[~cut_lep_charge(data.lep_charge)]

                if len(data) > 0:
                    frames.append(data)

            elapsed = time.time() - start
            print(f"\t...hecho en {round(elapsed,1)}s")

        except Exception as e:
            print(f"\tError procesando archivo {val}: {e}. Saltando este archivo.")
            continue

    if frames:
        all_data_unfiltered[s] = ak.concatenate(frames)

print("\n--- ¡Carga completa! Ahora generando JSON por período... ---")

# --- 2. Bucle por período para filtrar, calcular y guardar ---
periodos = {
    '2015-2016': {'years': [2015, 2016], 'lumi': 36.2},
    '2017': {'years': [2017], 'lumi': 44.3},
    '2018': {'years': [2018], 'lumi': 59.5},
    'Total': {'years': [2015, 2016, 2017, 2018], 'lumi': 139.0}
}

for nombre_periodo, info_periodo in periodos.items():
    print(f"\n{'='*60}\n========== FILTRANDO PARA PERÍODO: {nombre_periodo} ==========\n{'='*60}")
    lumi = info_periodo['lumi']

    all_data_periodo = {}
    for s, data in all_data_unfiltered.items():
        if not len(data): continue

        # Filtramos los datos reales por año. La simulación (MC) se usa completa.
        if s == 'Data':
            # Asegurarse de que 'RunYear' existe en los datos, que ahora es inyectado
            if 'RunYear' in data.fields:
                mask = (data.RunYear == info_periodo['years'][0])
                for year in info_periodo['years'][1:]:
                    mask = mask | (data.RunYear == year)
                filtered_data = data[mask]
            else:
                print(f"Warning: 'RunYear' no encontrado en el sample de Data para el período {nombre_periodo}. Saltando.")
                filtered_data = ak.Array([]) # Vaciar si no hay RunYear
        else:
            filtered_data = data # Usamos toda la simulación

        # Calculamos masa y pesos DESPUÉS de filtrar
        if len(filtered_data) > 0:
            filtered_data['mass'] = calc_mass(filtered_data.lep_pt, filtered_data.lep_eta, filtered_data.lep_phi, filtered_data.lep_e)
            if 'data' not in s.lower():
                filtered_data['totalWeight'] = calc_weight(lumi, weight_variables, filtered_data)

        all_data_periodo[s] = filtered_data

    # --- 3. PREPARACIÓN PARA EXPORTACIÓN A JSON ---
    # (El resto del código es igual, pero usa 'all_data_periodo')
    if 'Data' in all_data_periodo and 'mass' in all_data_periodo['Data'].fields:
        data_x, _ = np.histogram(ak.to_numpy(all_data_periodo['Data']['mass']), bins=bin_edges)
    else:
        data_x = np.zeros(len(bin_edges) - 1)
    data_x_errors = np.sqrt(data_x)

    signal_key = r'Signal ($m_H$ = 125 GeV)'
    if signal_key in all_data_periodo and 'mass' in all_data_periodo[signal_key].fields:
        signal_x = ak.to_numpy(all_data_periodo[signal_key]['mass'])
        signal_weights = ak.to_numpy(all_data_periodo[signal_key].totalWeight)
    else:
        signal_x, signal_weights = [], []
    signal_color = samples_total[signal_key]['color']
    signal_counts, _ = np.histogram(signal_x, bins=bin_edges, weights=signal_weights)

    background_hists = []
    for s in samples_total:
        if s not in ['Data', signal_key]:
            if s in all_data_periodo and 'mass' in all_data_periodo[s].fields:
                mc_mass = ak.to_numpy(all_data_periodo[s]['mass'])
                mc_weights = ak.to_numpy(all_data_periodo[s].totalWeight)
                mc_counts, _ = np.histogram(mc_mass, bins=bin_edges, weights=mc_weights)
            else:
                mc_counts = np.zeros(len(bin_edges) - 1)
            background_hists.append({
                "label": s,
                "counts": mc_counts.tolist(),
                "color": samples_total[s]['color']
            })

    # --- 4. CREAR Y GUARDAR EL ARCHIVO JSON ---
    final_plot_data = {
        "period": nombre_periodo,
        "lumi": lumi,
        "data": {"counts": data_x.tolist(), "errors": data_x_errors.tolist(), "label": "Data"},
        "signal": {"counts": signal_counts.tolist(), "label": signal_key, "color": signal_color},
        "backgrounds": background_hists,
        "bins": bin_edges.tolist(),
        "x_axis_label": "Masa Invariante 4l (GeV)",
        "y_axis_label": f"Eventos / {step_size} GeV"
    }

    output_filename = f"datos_analisis_{nombre_periodo.replace('-', '_')}.json"
    with open(output_filename, 'w') as f:
        json.dump(final_plot_data, f, indent=4)

    print(f"\n--- ¡Éxito! Datos para el período {nombre_periodo} guardados en {output_filename} ---\n")

print("¡TODOS LOS PERÍODOS HAN SIDO PROCESADOS!")