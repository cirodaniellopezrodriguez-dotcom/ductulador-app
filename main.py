import datetime
import json
import math
import os
import sqlite3
import flet as ft

DB_NAME = "ductulador_persist.db"


# --- BASE DE DATOS ---
def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS estado (id INTEGER PRIMARY KEY, data TEXT)"
  )
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            cliente TEXT,
            fecha TEXT,
            data TEXT
        )
    """)
  conn.commit()
  conn.close()


def db_save_draft(data_dict):
  try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    raw = json.dumps(data_dict)
    cursor.execute("INSERT OR REPLACE INTO estado (id, data) VALUES (1, ?)", (raw,))
    conn.commit()
    conn.close()
  except:
    pass


def db_load_draft():
  try:
    if not os.path.exists(DB_NAME):
      return None
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM estado WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None
  except:
    return None


def db_clear_draft():
  try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estado WHERE id = 1")
    conn.commit()
    conn.close()
  except:
    pass


def db_save_project(nombre, cliente, fecha, data_dict):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  raw = json.dumps(data_dict)
  cursor.execute("SELECT id FROM proyectos WHERE nombre = ?", (nombre,))
  row = cursor.fetchone()
  if row:
    cursor.execute(
        "UPDATE proyectos SET cliente=?, fecha=?, data=? WHERE id=?",
        (cliente, fecha, raw, row[0]),
    )
  else:
    cursor.execute(
        "INSERT INTO proyectos (nombre, cliente, fecha, data) VALUES (?, ?, ?,"
        " ?)",
        (nombre, cliente, fecha, raw),
    )
  conn.commit()
  conn.close()


def db_get_projects():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, nombre, cliente, fecha, data FROM proyectos ORDER BY id DESC"
  )
  rows = cursor.fetchall()
  conn.close()
  return rows


def db_delete_project(p_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM proyectos WHERE id = ?", (p_id,))
  conn.commit()
  conn.close()


# --- LÓGICA PRINCIPAL ---
def main(page: ft.Page):
  init_db()
  page.title = "DUCTULADOR PRO"
  page.scroll = ft.ScrollMode.AUTO
  page.theme_mode = ft.ThemeMode.DARK
  page.padding = 6

  BG_CARD, BG_DARK = "#1e293b", "#0f172a"
  BORDER_COLOR = "#334155"
  ACCENT_YELLOW, ACCENT_GREEN, ACCENT_CYAN, ACCENT_ORANGE, ACCENT_PURPLE, ACCENT_PINK, ACCENT_TEAL, ACCENT_AMBER, ACCENT_BLUE = (
      "#facc15",
      "#22c55e",
      "#38bdf8",
      "#fb923c",
      "#a855f7",
      "#ec4899",
      "#14b8a6",
      "#f59e0b",
      "#3b82f6",
  )
  TEXT_MUTED = "#94a3b8"

  state = {"h1_val": "0", "h2_val": "0", "h3_val": "0"}
  areas_list = []
  col_areas = ft.Column()

  card_resultado = ft.Container(
      visible=False,
      bgcolor=BG_CARD,
      padding=12,
      border_radius=10,
      border=ft.Border.all(width=1, color=BORDER_COLOR),
  )
  col_proyectos_lista = ft.Column(spacing=10)

  def on_focus_clear(e):
    if e.control.value in ["0", "0.0", "3.0"]:
      e.control.value = ""
      e.control.update()

  def calc_diam(cfm, p):
    return (0.109136 * (cfm**1.9) / p) ** (1 / 5.02) if cfm > 0 else 0

  def lado_cuadrado(d):
    return math.ceil(d / 1.094) if d > 0 else 0

  def ancho_rect(d, a):
    if a <= 0 or d <= 0:
      return 0
    low, high = 1, 200
    for _ in range(80):
      b = (low + high) / 2
      de = 1.30 * ((a * b) ** 0.625) / ((a + b) ** 0.25)
      if de < d:
        low = b
      else:
        high = b
    return math.ceil(low)

  def obtener_payload():
    datos_areas = []
    for item in areas_list:
      datos_areas.append({
          "modo": item["modo"],
          "nom": item["nom"].value or "",
          "largo": item["largo"].value or "",
          "ancho": item["ancho"].value or "",
          "m2_directo": item["m2_directo"].value or "",
          "alto": item["alto"].value or "",
          "h_ducto": item["h_ducto"].value or "",
          "ramal": item["ramal"].value or "PRINCIPAL",
      })
    return {
        "proyecto": txt_proyecto.value or "",
        "cliente": txt_cliente.value or "",
        "telefono": txt_telefono.value or "",
        "direccion": txt_direccion.value or "",
        "fecha": txt_fecha.value or "",
        "tipo": dd_tipo.value or "18",
        "caida": dd_caida.value or "0.10",
        "areas": datos_areas,
        "hosp_ductos": state,
    }

  def auto_guardar(e=None):
    db_save_draft(obtener_payload())

  txt_proyecto = ft.TextField(
      label="PROYECTO",
      hint_text="Ej: Casa Habitación",
      border_color=BORDER_COLOR,
      text_size=13,
      on_change=auto_guardar,
  )
  txt_cliente = ft.TextField(
      label="CLIENTE",
      hint_text="Cliente",
      border_color=BORDER_COLOR,
      expand=True,
      text_size=13,
      on_change=auto_guardar,
  )
  txt_telefono = ft.TextField(
      label="TELÉFONO",
      hint_text="618-123-4567",
      border_color=BORDER_COLOR,
      expand=True,
      text_size=13,
      on_change=auto_guardar,
  )
  txt_direccion = ft.TextField(
      label="DIRECCIÓN",
      hint_text="Ubicación",
      border_color=BORDER_COLOR,
      expand=True,
      text_size=13,
      on_change=auto_guardar,
  )
  txt_fecha = ft.TextField(
      label="FECHA",
      value=datetime.date.today().strftime("%d-%m-%Y"),
      border_color=BORDER_COLOR,
      expand=True,
      text_size=13,
      on_change=auto_guardar,
  )

  dd_tipo = ft.Dropdown(
      label="TIPO / APLICACIÓN",
      options=[
          ft.dropdown.Option("18", "Casa"),
          ft.dropdown.Option("15", "Comercio"),
          ft.dropdown.Option("12", "Caliente"),
          ft.dropdown.Option("QUIROFANO", "Quirófano / Hospitalario"),
      ],
      value="18",
      expand=True,
  )
  dd_tipo.on_change = auto_guardar

  dd_caida = ft.Dropdown(
      label="CAÍDA DE PRESIÓN",
      options=[
          ft.dropdown.Option("0.08", "0.08"),
          ft.dropdown.Option("0.10", "0.10"),
          ft.dropdown.Option("0.15", "0.15"),
      ],
      value="0.10",
      expand=True,
  )
  dd_caida.on_change = auto_guardar

  def alternar_modo(item, modo):
    item["modo"] = modo
    item["box_medidas"].visible = modo == "medidas"
    item["box_m2"].visible = modo == "m2"
    item["btn_medidas"].bgcolor = ACCENT_YELLOW if modo == "medidas" else BG_CARD
    item["txt_btn_med"].color = "black" if modo == "medidas" else TEXT_MUTED
    item["btn_m2"].bgcolor = ACCENT_YELLOW if modo == "m2" else BG_CARD
    item["txt_btn_m2"].color = "black" if modo == "m2" else TEXT_MUTED
    auto_guardar()
    page.update()

  def borrar_area(item):
    if item in areas_list:
      areas_list.remove(item)
      col_areas.controls.remove(item["card"])
      auto_guardar()
      page.update()

  def agregar_area(data_prev=None):
    if len(areas_list) >= 20:
      return
    idx = len(areas_list) + 1

    val_nom = data_prev["nom"] if data_prev else f"Área {idx}"
    val_largo = data_prev["largo"] if data_prev else "0"
    val_ancho = data_prev["ancho"] if data_prev else "0"
    val_m2_dir = data_prev["m2_directo"] if data_prev else ""
    val_alto = data_prev["alto"] if data_prev else "3.0"
    val_h_ducto = data_prev["h_ducto"] if data_prev else "0"
    val_ramal = data_prev["ramal"] if data_prev else "PRINCIPAL"
    modo_init = data_prev["modo"] if data_prev else "medidas"

    txt_nom = ft.TextField(
        value=val_nom,
        border_color=BORDER_COLOR,
        text_size=13,
        on_change=auto_guardar,
    )
    txt_largo = ft.TextField(
        label="LARGO (m)",
        value=val_largo,
        hint_text="0",
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        border_color=BORDER_COLOR,
        text_size=13,
        on_change=auto_guardar,
        on_focus=on_focus_clear,
    )
    txt_ancho = ft.TextField(
        label="ANCHO (m)",
        value=val_ancho,
        hint_text="0",
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        border_color=BORDER_COLOR,
        text_size=13,
        on_change=auto_guardar,
        on_focus=on_focus_clear,
    )
    txt_m2_directo = ft.TextField(
        label="M² DIRECTOS",
        value=val_m2_dir,
        hint_text="0",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=BORDER_COLOR,
        text_size=13,
        on_change=auto_guardar,
        on_focus=on_focus_clear,
    )
    txt_alto = ft.TextField(
        label="ALTURA ÁREA (m)",
        value=val_alto,
        hint_text="3.0",
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        border_color=BORDER_COLOR,
        text_size=13,
        on_change=auto_guardar,
        on_focus=on_focus_clear,
    )
    txt_h_ducto = ft.TextField(
        label="ALTURA DUCTO (0=cuadrado)",
        value=val_h_ducto,
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        border_color=ACCENT_YELLOW,
        text_size=13,
        on_change=auto_guardar,
        on_focus=on_focus_clear,
    )

    dd_ramal = ft.Dropdown(
        label="LÍNEA / RAMAL",
        options=[
            ft.dropdown.Option("PRINCIPAL", "Principal (Tronco)"),
            ft.dropdown.Option("RAMAL_A", "Ramal A"),
            ft.dropdown.Option("RAMAL_B", "Ramal B"),
            ft.dropdown.Option("RAMAL_C", "Ramal C"),
            ft.dropdown.Option("RAMAL_D", "Ramal D"),
            ft.dropdown.Option("RAMAL_E", "Ramal E"),
        ],
        value=val_ramal,
        expand=True,
    )
    dd_ramal.on_change = auto_guardar

    lbl_res_area = ft.Text(
        "",
        size=12,
        color=ACCENT_CYAN,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )
    box_medidas = ft.Row([txt_largo, txt_ancho], visible=(modo_init == "medidas"))
    box_m2 = ft.Column([txt_m2_directo], visible=(modo_init == "m2"))

    txt_b_med = ft.Text(
        "POR MEDIDAS",
        color="black" if modo_init == "medidas" else TEXT_MUTED,
        weight=ft.FontWeight.BOLD,
        size=11,
        text_align=ft.TextAlign.CENTER,
    )
    txt_b_m2 = ft.Text(
        "M² DIRECTO",
        color="black" if modo_init == "m2" else TEXT_MUTED,
        weight=ft.FontWeight.BOLD,
        size=11,
        text_align=ft.TextAlign.CENTER,
    )

    btn_medidas = ft.Container(
        content=ft.Row([txt_b_med], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ACCENT_YELLOW if modo_init == "medidas" else BG_CARD,
        padding=8,
        border_radius=6,
        expand=True,
        border=ft.Border.all(width=1, color="#475569"),
    )
    btn_m2 = ft.Container(
        content=ft.Row([txt_b_m2], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ACCENT_YELLOW if modo_init == "m2" else BG_CARD,
        padding=8,
        border_radius=6,
        expand=True,
        border=ft.Border.all(width=1, color="#475569"),
    )

    item = {
        "modo": modo_init,
        "nom": txt_nom,
        "largo": txt_largo,
        "ancho": txt_ancho,
        "m2_directo": txt_m2_directo,
        "alto": txt_alto,
        "h_ducto": txt_h_ducto,
        "ramal": dd_ramal,
        "box_medidas": box_medidas,
        "box_m2": box_m2,
        "btn_medidas": btn_medidas,
        "btn_m2": btn_m2,
        "txt_btn_med": txt_b_med,
        "txt_btn_m2": txt_b_m2,
        "res_area": lbl_res_area,
        "card": None,
    }

    btn_medidas.on_click = lambda _: alternar_modo(item, "medidas")
    btn_m2.on_click = lambda _: alternar_modo(item, "m2")

    btn_borrar = ft.Container(
        content=ft.Text(
            "X BORRAR", color="#ef4444", size=11, weight=ft.FontWeight.BOLD
        ),
        on_click=lambda _: borrar_area(item),
    )

    card_area = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"ÁREA {idx}",
                            weight=ft.FontWeight.BOLD,
                            color="white",
                            size=13,
                        ),
                        btn_borrar,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                txt_nom,
                ft.Row([btn_medidas, btn_m2]),
                box_medidas,
                box_m2,
                ft.Row([txt_alto, txt_h_ducto]),
                dd_ramal,
                ft.Row([lbl_res_area], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=8,
        ),
        bgcolor=BG_DARK,
        padding=14,
        border_radius=10,
        border=ft.Border.all(width=1, color="#475569"),
    )

    item["card"] = card_area
    areas_list.append(item)
    col_areas.controls.append(card_area)
    if not data_prev:
      auto_guardar()
    page.update()

  def cargar_datos_en_formulario(data):
    col_areas.controls.clear()
    areas_list.clear()
    state.update(data.get("hosp_ductos", {"h1": "0", "h2": "0", "h3": "0"}))

    txt_proyecto.value = data.get("proyecto", "")
    txt_cliente.value = data.get("cliente", "")
    txt_telefono.value = data.get("telefono", "")
    txt_direccion.value = data.get("direccion", "")
    txt_fecha.value = data.get(
        "fecha", datetime.date.today().strftime("%d-%m-%Y")
    )
    dd_tipo.value = data.get("tipo", "18")
    dd_caida.value = data.get("caida", "0.10")

    areas_saved = data.get("areas", [])
    for a in areas_saved:
      agregar_area(data_prev=a)
    page.update()

  def actualizar_medida_tramo(
      txt_h_custom,
      lbl_medida,
      lbl_detalles,
      d_remanente,
      cfm_rem,
      item_ref=None,
  ):
    try:
      h_val = float(txt_h_custom.value or 0)
    except ValueError:
      h_val = 0

    if item_ref:
      item_ref["h_ducto"].value = txt_h_custom.value or "0"

    d_tramo_redondo = f"{d_remanente:.1f}"
    if h_val <= 0:
      lado = lado_cuadrado(d_remanente)
      lbl_medida.value = f'{lado}"x{lado}"  |  {d_tramo_redondo}" Ø'
      lbl_detalles.value = f"{lado*lado} pulg² | {int(cfm_rem)} CFM"
    else:
      ancho = ancho_rect(d_remanente, h_val)
      lbl_medida.value = f'{int(h_val)}"x{ancho}"  |  {d_tramo_redondo}" Ø'
      lbl_detalles.value = f"{int(h_val)*ancho} pulg² | {int(cfm_rem)} CFM"

    auto_guardar()
    page.update()

  def calcular_todo(e=None):
    auto_guardar()
    tipo_val = dd_tipo.value
    caida = float(dd_caida.value or 0.10)

    proy = (txt_proyecto.value or "SIN NOMBRE").upper()
    cli = txt_cliente.value or "---"
    tel = txt_telefono.value or "---"
    dir_txt = txt_direccion.value or "---"
    fec = txt_fecha.value or ""

    total_cfm = 0
    total_m2 = 0
    total_m3 = 0
    total_tr = 0
    total_cfm_aire_nuevo = 0

    items_calculados = []
    for item in areas_list:
      m2 = 0
      try:
        if item["modo"] == "medidas":
          l = float(item["largo"].value or 0)
          an = float(item["ancho"].value or 0)
          m2 = l * an
        else:
          m2 = float(item["m2_directo"].value or 0)
      except ValueError:
        continue

      if m2 <= 0:
        continue

      try:
        alto = float(item["alto"].value or 3.0)
        h_d = float(item["h_ducto"].value or 0)
      except ValueError:
        alto, h_d = 3.0, 0

      m3 = m2 * alto
      nome = item["nom"].value or "Área"
      ramal_sel = item["ramal"].value or "PRINCIPAL"

      if tipo_val == "QUIROFANO":
        cfm = (m3 * 20) / 60 * 35.315
        tons_exact = cfm / 400
        cfm_aire_nuevo = (m3 * 4) / 60 * 35.315
      else:
        tipo_num = float(tipo_val or 18)
        tons_exact = (m2 / tipo_num) * (alto / 2.7 if alto > 2.7 else 1)
        cfm = tons_exact * 400
        cfm_aire_nuevo = cfm * 0.20

      total_cfm += cfm
      total_m2 += m2
      total_m3 += m3
      total_tr += tons_exact
      total_cfm_aire_nuevo += cfm_aire_nuevo
      d = calc_diam(cfm, caida)

      items_calculados.append({
          "item_ref": item,
          "nome": nome,
          "m2": m2,
          "m3": m3,
          "tons": tons_exact,
          "cfm": cfm,
          "cfm_aire_nuevo": cfm_aire_nuevo,
          "d": d,
          "h_d": h_d,
          "ramal": ramal_sel,
      })

    if total_cfm == 0:
      return

    columnas_tabla = [
        ft.DataColumn(
            ft.Text(
                "ÁREA",
                color=ACCENT_YELLOW,
                weight=ft.FontWeight.BOLD,
                size=11,
            )
        ),
        ft.DataColumn(
            ft.Text("M²", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11)
        ),
        ft.DataColumn(
            ft.Text("TR", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11)
        ),
        ft.DataColumn(
            ft.Text(
                "CFM / AIRE NUEVO",
                color=ACCENT_YELLOW,
                weight=ft.FontWeight.BOLD,
                size=11,
            )
        ),
        ft.DataColumn(
            ft.Text(
                "TRAMO DUCTO (EDITABLE)",
                color=ACCENT_GREEN,
                weight=ft.FontWeight.BOLD,
                size=11,
            )
        ),
    ]

    if tipo_val == "QUIROFANO":
      columnas_tabla.append(
          ft.DataColumn(
              ft.Text(
                  "SALIDA Y CAJA (PLENUM)",
                  color=ACCENT_YELLOW,
                  weight=ft.FontWeight.BOLD,
                  size=11,
              )
          )
      )

    dt = ft.DataTable(
        column_spacing=14,
        data_row_min_height=52,
        border=ft.Border.all(width=1, color=ACCENT_BLUE),
        vertical_lines=ft.BorderSide(1.5, ACCENT_CYAN),
        horizontal_lines=ft.BorderSide(1, "#334155"),
        columns=columnas_tabla,
        rows=[],
    )

    cfm_ramales = {
        "RAMAL_A": sum(
            x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_A"
        ),
        "RAMAL_B": sum(
            x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_B"
        ),
        "RAMAL_C": sum(
            x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_C"
        ),
        "RAMAL_D": sum(
            x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_D"
        ),
        "RAMAL_E": sum(
            x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_E"
        ),
    }

    cfm_principal_activo = total_cfm
    cfm_ramal_activo = cfm_ramales.copy()
    primer_ingreso_ramal = {key: True for key in cfm_ramales}

    for item in items_calculados:
      r = item["ramal"]
      if r == "PRINCIPAL":
        cfm_para_tramo = cfm_principal_activo
        cfm_principal_activo -= item["cfm"]
      else:
        if primer_ingreso_ramal[r]:
          cfm_principal_activo -= cfm_ramales[r]
          primer_ingreso_ramal[r] = False
        cfm_para_tramo = cfm_ramal_activo[r]
        cfm_ramal_activo[r] -= item["cfm"]

      d_salida_redondo = f"{item['d']:.1f}"
      if item["h_d"] == 0:
        lado = lado_cuadrado(item["d"])
        propuesta_salida = f'{lado}"x{lado}"  |  {d_salida_redondo}" Ø'
        pulg2_salida = lado * lado
      else:
        ancho = ancho_rect(item["d"], item["h_d"])
        propuesta_salida = f'{int(item["h_d"])}"x{ancho}"  |  {d_salida_redondo}" Ø'
        pulg2_salida = int(item["h_d"]) * ancho

      cuello_plenum_diam = math.sqrt((item["cfm"] / 500.0) * 183.35)
      cuello_lado = lado_cuadrado(cuello_plenum_diam)

      radio_cuello = cuello_plenum_diam / 2.0
      pulg2_cuello_redondo = math.pi * (radio_cuello**2)

      lado_caja_plenum = cuello_lado + 4
      caja_plenum_str = (
          f'Caja Plenum: {lado_caja_plenum}"x{lado_caja_plenum}" | Cuello'
          f' {cuello_lado}"Ø ({pulg2_cuello_redondo:.1f} pulg²)'
      )

      d_remanente = calc_diam(cfm_para_tramo, caida)
      d_tramo_redondo = f"{d_remanente:.1f}"

      if item["h_d"] == 0:
        lado_p = lado_cuadrado(d_remanente)
        init_medida_tramo = f'{lado_p}"x{lado_p}"  |  {d_tramo_redondo}" Ø'
        init_detalles_tramo = f"{lado_p*lado_p} pulg² | {int(cfm_para_tramo)} CFM"
        init_h_val = "0"
      else:
        ancho_p = ancho_rect(d_remanente, item["h_d"])
        init_medida_tramo = (
            f'{int(item["h_d"])}"x{ancho_p}"  |  {d_tramo_redondo}" Ø'
        )
        init_detalles_tramo = (
            f"{int(item["h_d"])*ancho_p} pulg² | {int(cfm_para_tramo)} CFM"
        )
        init_h_val = str(int(item["h_d"]))

      color_map = {
          "PRINCIPAL": ACCENT_GREEN,
          "RAMAL_A": ACCENT_ORANGE,
          "RAMAL_B": ACCENT_PURPLE,
          "RAMAL_C": ACCENT_PINK,
          "RAMAL_D": ACCENT_TEAL,
          "RAMAL_E": ACCENT_AMBER,
      }
      lbl_color = color_map.get(r, ACCENT_GREEN)
      tag = "TRONCO" if r == "PRINCIPAL" else r

      lbl_medida_tramo = ft.Text(
          init_medida_tramo,
          color=lbl_color,
          weight=ft.FontWeight.BOLD,
          size=12,
      )
      lbl_detalles_tramo = ft.Text(
          f"{init_detalles_tramo} [{tag}]", size=9, color=TEXT_MUTED
      )

      txt_h_tramo_custom = ft.TextField(
          value=init_h_val,
          width=42,
          height=32,
          content_padding=3,
          text_size=11,
          keyboard_type=ft.KeyboardType.NUMBER,
          border_color=lbl_color,
          text_align=ft.TextAlign.CENTER,
          on_focus=on_focus_clear,
      )
      txt_h_tramo_custom.on_change = lambda e, txt=txt_h_tramo_custom, lbl_m=lbl_medida_tramo, lbl_d=lbl_detalles_tramo, d_r=d_remanente, cfm_r=cfm_para_tramo, ref=item[
          "item_ref"
      ]: actualizar_medida_tramo(
          txt, lbl_m, lbl_d, d_r, cfm_r, ref
      )

      nombre_con_tag = (
          f"{item['nome']} [{tag}]" if r != "PRINCIPAL" else item["nome"]
      )
      celdas_fila = [
          ft.DataCell(
              ft.Text(
                  nombre_con_tag,
                  color=lbl_color if r != "PRINCIPAL" else "white",
                  size=11,
                  weight=ft.FontWeight.BOLD,
              )
          ),
          ft.DataCell(ft.Text(f"{item['m2']:.1f}", size=11)),
          ft.DataCell(
              ft.Text(
                  f"{item['tons']:.2f}",
                  color=ACCENT_CYAN,
                  weight=ft.FontWeight.BOLD,
                  size=11,
              )
          ),
          ft.DataCell(
              ft.Column(
                  [
                      ft.Text(
                          f"{int(item['cfm'])} CFM Total",
                          size=11,
                          weight=ft.FontWeight.BOLD,
                          color="white",
                      ),
                      ft.Text(
                          f"Aire Nuevo: {int(item['cfm_aire_nuevo'])} CFM",
                          size=9,
                          color=ACCENT_CYAN,
                      ),
                  ],
                  spacing=1,
              )
          ),
          ft.DataCell(
              ft.Row(
                  [
                      ft.Column(
                          [ft.Text("Alt:", size=8, color=TEXT_MUTED), txt_h_tramo_custom],
                          spacing=1,
                      ),
                      ft.Column([lbl_medida_tramo, lbl_detalles_tramo], spacing=1),
                  ],
                  alignment=ft.MainAxisAlignment.START,
                  vertical_alignment=ft.CrossAxisAlignment.CENTER,
              )
          ),
      ]

      if tipo_val == "QUIROFANO":
        celdas_fila.append(
            ft.DataCell(
                ft.Column(
                    [
                        ft.Text(
                            propuesta_salida,
                            color=ACCENT_YELLOW,
                            weight=ft.FontWeight.BOLD,
                            size=11,
                        ),
                        ft.Text(f"{pulg2_salida} pulg²", size=9, color=TEXT_MUTED),
                        ft.Text(
                            caja_plenum_str,
                            size=9,
                            color=ACCENT_PINK,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=1,
                )
            )
        )

      dt.rows.append(ft.DataRow(cells=celdas_fila))

    total_btu = total_tr * 12000
    celdas_totales = [
        ft.DataCell(
            ft.Text(
                "TOTALES",
                color=ACCENT_YELLOW,
                weight=ft.FontWeight.BOLD,
                size=11,
            )
        ),
        ft.DataCell(
            ft.Text(
                f"{total_m2:.1f} m² / {total_m3:.1f} m³",
                color="white",
                weight=ft.FontWeight.BOLD,
                size=10,
            )
        ),
        ft.DataCell(
            ft.Text(
                f"{total_tr:.2f} TR",
                color=ACCENT_CYAN,
                weight=ft.FontWeight.BOLD,
                size=11,
            )
        ),
        ft.DataCell(
            ft.Column(
                [
                    ft.Text(
                        f"{int(total_cfm)} CFM Tot.",
                        color=ACCENT_GREEN,
                        weight=ft.FontWeight.BOLD,
                        size=10,
                    ),
                    ft.Text(
                        f"A. Nuevo: {int(total_cfm_aire_nuevo)} CFM",
                        color=ACCENT_CYAN,
                        weight=ft.FontWeight.BOLD,
                        size=9,
                    ),
                ],
                spacing=1,
            )
        ),
        ft.DataCell(
            ft.Text(
                f"CAPACIDAD: {total_btu:,.0f} BTU/h",
                color=ACCENT_YELLOW,
                weight=ft.FontWeight.BOLD,
                size=10,
            )
        ),
    ]
    if tipo_val == "QUIROFANO":
      celdas_totales.append(
          ft.DataCell(
              ft.Text(
                  "SISTEMA HOSPITALARIO",
                  color=ACCENT_PINK,
                  weight=ft.FontWeight.BOLD,
                  size=10,
              )
          )
      )

    dt.rows.append(ft.DataRow(color="#0f172a", cells=celdas_totales))
    state["last_total_cfm"] = total_cfm
    state["last_diam_tot"] = calc_diam(total_cfm, caida)

    if tipo_val == "QUIROFANO":
      diam_tot = state["last_diam_tot"]
      lado_tot = lado_cuadrado(diam_tot)
      cfm_16 = total_cfm * (16.0 / 20.0)
      diam_16 = calc_diam(cfm_16, caida)
      cfm_4 = total_cfm_aire_nuevo
      diam_4 = calc_diam(cfm_4, caida)

      def actualizar_hosp_bloque(
          txt_h, lbl_m, lbl_det, cfm_val, diam_val, key_id
      ):
        try:
          h_val = float(txt_h.value or 0)
        except ValueError:
          h_val = 0
        state[key_id] = txt_h.value or "0"
        d_red_str = f"{diam_val:.1f}"
        if h_val <= 0:
          l_sq = lado_cuadrado(diam_val)
          lbl_m.value = f'{l_sq}"x{l_sq}"  |  {d_red_str}" Ø'
          lbl_det.value = f"{l_sq*l_sq} pulg² | {int(cfm_val)} CFM"
        else:
          w_rect = ancho_rect(diam_val, h_val)
          lbl_m.value = f'{int(h_val)}"x{w_rect}"  |  {d_red_str}" Ø'
          lbl_det.value = f"{int(h_val)*w_rect} pulg² | {int(cfm_val)} CFM"
        auto_guardar()
        page.update()

      def crear_caja_hospital_ajustable(
          titulo_bloque, cfm_val, diam_val, color_res, area_inicial_sq, key_id
      ):
        val_inicial = state.get(key_id, "0")
        lbl_m = ft.Text("", size=13, color=color_res, weight=ft.FontWeight.BOLD)
        lbl_det = ft.Text("", size=10, color="white")

        txt_h_box = ft.TextField(
            value=val_inicial,
            width=45,
            height=32,
            content_padding=3,
            text_size=11,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=color_res,
            text_align=ft.TextAlign.CENTER,
            on_focus=on_focus_clear,
        )
        txt_h_box.on_change = lambda e, t=txt_h_box, lm=lbl_m, ld=lbl_det, c=cfm_val, d=diam_val, kid=key_id: actualizar_hosp_bloque(
            t, lm, ld, c, d, kid
        )

        actualizar_hosp_bloque(
            txt_h_box, lbl_m, lbl_det, cfm_val, diam_val, key_id
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        titulo_bloque,
                        size=10,
                        color=TEXT_MUTED,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [ft.Text("Alt:", size=8, color=TEXT_MUTED), txt_h_box],
                                spacing=1,
                            ),
                            ft.Column([lbl_m, lbl_det], spacing=1),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=BG_CARD,
            padding=8,
            border_radius=6,
            border=ft.Border.all(width=1, color="#334155"),
        )

      # Aviso fijo de Presión Positiva bien visible
      aviso_presion_positiva = ft.Container(
          content=ft.Row(
              [
                  ft.Text(
                      "ℹ️ PRESIÓN POSITIVA: Mantener inyección de aire 10% a"
                      " 20% superior al caudal de extracción.",
                      size=11,
                      color=ACCENT_CYAN,
                      weight=ft.FontWeight.BOLD,
                  )
              ],
              alignment=ft.MainAxisAlignment.CENTER,
          ),
          bgcolor=BG_CARD,
          padding=10,
          border_radius=6,
          border=ft.Border.all(width=1, color=ACCENT_CYAN),
      )

      box_principal = ft.Container(
          content=ft.Column(
              [
                  ft.Text(
                      "DUCTO PRINCIPAL INICIAL (SALIDA DEL EQUIPO) - DESGLOSE"
                      " HOSPITALARIO (EDITABLE)",
                      color=ACCENT_YELLOW,
                      weight=ft.FontWeight.BOLD,
                      size=11,
                  ),
                  aviso_presion_positiva,
                  crear_caja_hospital_ajustable(
                      "1. DUCTO GENERAL TOTAL (20 Cambios):",
                      total_cfm,
                      diam_tot,
                      ACCENT_GREEN,
                      lado_tot * lado_tot,
                      "h1",
                  ),
                  crear_caja_hospital_ajustable(
                      "2. DUCTO PARA 16 CAMBIOS DE AIRE:",
                      cfm_16,
                      calc_diam(cfm_16, caida),
                      ACCENT_CYAN,
                      lado_cuadrado(calc_diam(cfm_16, caida)) ** 2,
                      "h2",
                  ),
                  crear_caja_hospital_ajustable(
                      "3. DUCTO PARA 4 CAMBIOS RESTANTES (AIRE NUEVO):",
                      cfm_4,
                      calc_diam(cfm_4, caida),
                      ACCENT_PINK,
                      lado_cuadrado(calc_diam(cfm_4, caida)) ** 2,
                      "h3",
                  ),
              ],
              spacing=8,
          ),
          bgcolor=BG_DARK,
          padding=12,
          border_radius=8,
          border=ft.Border.all(width=1, color=ACCENT_YELLOW),
      )
    else:
      diam_tot = state["last_diam_tot"]
      lado_tot = lado_cuadrado(diam_tot)
      box_principal = ft.Container(
          content=ft.Column(
              [
                  ft.Text(
                      "DUCTO PRINCIPAL INICIAL (SALIDA DEL EQUIPO)",
                      color=ACCENT_YELLOW,
                      weight=ft.FontWeight.BOLD,
                      size=11,
                  ),
                  ft.Text(
                      f'{lado_tot}"x{lado_tot}"  |  {diam_tot:.1f}" Ø',
                      size=14,
                      color=ACCENT_GREEN,
                      weight=ft.FontWeight.BOLD,
                  ),
                  ft.Text(
                      f"{lado_tot*lado_tot} pulg² | {total_cfm:.0f} CFM",
                      size=10,
                      color="white",
                  ),
              ],
              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
          ),
          bgcolor=BG_DARK,
          padding=12,
          border_radius=8,
          border=ft.Border.all(width=1, color=ACCENT_YELLOW),
      )

    header_resumen = ft.Container(
        content=ft.Column([
            ft.Text(
                f"PROYECTO: {proy}",
                weight=ft.FontWeight.BOLD,
                color="black",
                size=13,
            ),
            ft.Text(
                f"Cliente: {cli} | Tel: {tel}\n{dir_txt} | {fec}",
                size=11,
                color="black",
            ),
        ]),
        bgcolor=ACCENT_YELLOW,
        padding=10,
        border_radius=6,
    )

    card_resultado.content = ft.Column(
        [
            header_resumen,
            ft.Row([dt], scroll=ft.ScrollMode.ALWAYS),
            box_principal,
        ],
        spacing=10,
    )
    card_resultado.visible = True
    page.update()

  def guardar_proyecto_click(e=None):
    p_nombre = txt_proyecto.value.strip()
    if not p_nombre:
      txt_proyecto.border_color = "#ef4444"
      page.update()
      return
    txt_proyecto.border_color = BORDER_COLOR
    db_save_project(
        p_nombre,
        txt_cliente.value or "---",
        txt_fecha.value or "",
        obtener_payload(),
    )
    refrescar_lista_proyectos()
    cambiar_vista("historial")

  def refrescar_lista_proyectos():
    col_proyectos_lista.controls.clear()
    for p_id, p_nom, p_cli, p_fec, p_data_str in db_get_projects():
      p_data = json.loads(p_data_str) if p_data_str else {}

      card_p = ft.Container(
          content=ft.Column(
              [
                  ft.Row(
                      [
                          ft.Text(
                              p_nom.upper(),
                              weight=ft.FontWeight.BOLD,
                              color=ACCENT_CYAN,
                              size=14,
                          ),
                          ft.Text(p_fec, size=11, color=TEXT_MUTED),
                      ],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  ),
                  ft.Text(f"Cliente: {p_cli}", size=12, color="white"),
                  ft.Row(
                      [
                          ft.Container(
                              content=ft.Text(
                                  "ABRIR / CORREGIR",
                                  color="black",
                                  weight=ft.FontWeight.BOLD,
                                  size=11,
                              ),
                              bgcolor=ACCENT_YELLOW,
                              padding=8,
                              border_radius=6,
                              on_click=lambda _, d=p_data: (
                                  cargar_datos_en_formulario(d),
                                  calcular_todo(),
                                  cambiar_vista("calculadora"),
                              ),
                          ),
                          ft.Container(
                              content=ft.Text(
                                  "ELIMINAR",
                                  color="#ef4444",
                                  weight=ft.FontWeight.BOLD,
                                  size=11,
                              ),
                              padding=8,
                              on_click=lambda _, pid=p_id: (
                                  db_delete_project(pid),
                                  refrescar_lista_proyectos(),
                              ),
                          ),
                      ],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  ),
              ],
              spacing=6,
          ),
          bgcolor=BG_DARK,
          padding=16,
          border_radius=8,
          border=ft.Border.all(width=1, color=BORDER_COLOR),
      )
      col_proyectos_lista.controls.append(card_p)
    page.update()

  def limpiar(e=None):
    col_areas.controls.clear()
    areas_list.clear()
    card_resultado.visible = False
    txt_proyecto.value = (
        txt_cliente.value
    ) = txt_telefono.value = txt_direccion.value = ""
    txt_fecha.value = datetime.date.today().strftime("%d-%m-%Y")
    dd_tipo.value = "18"
    db_clear_draft()
    state.update({"h1": "0", "h2": "0", "h3": "0"})
    page.update()

  txt_tab_calc = ft.Text(
      "CALCULADORA",
      color="black",
      weight=ft.FontWeight.BOLD,
      size=12,
  )
  txt_tab_hist = ft.Text(
      "HISTORIAL", color="white", weight=ft.FontWeight.BOLD, size=12
  )

  btn_tab_calc = ft.Container(
      content=ft.Row([txt_tab_calc], alignment=ft.MainAxisAlignment.CENTER),
      bgcolor=ACCENT_YELLOW,
      padding=18,
      border_radius=8,
      expand=True,
  )
  btn_tab_hist = ft.Container(
      content=ft.Row([txt_tab_hist], alignment=ft.MainAxisAlignment.CENTER),
      bgcolor=BG_CARD,
      padding=18,
      border_radius=8,
      expand=True,
  )

  def cambiar_vista(v):
    vista_calculadora.visible = v == "calculadora"
    vista_historial.visible = v == "historial"

    if v == "calculadora":
      btn_tab_calc.bgcolor = ACCENT_YELLOW
      txt_tab_calc.color = "black"
      btn_tab_hist.bgcolor = BG_CARD
      txt_tab_hist.color = "white"
    else:
      btn_tab_calc.bgcolor = BG_CARD
      txt_tab_calc.color = "white"
      btn_tab_hist.bgcolor = ACCENT_YELLOW
      txt_tab_hist.color = "black"

    if v == "historial":
      refrescar_lista_proyectos()
    page.update()

  btn_tab_calc.on_click = lambda _: cambiar_vista("calculadora")
  btn_tab_hist.on_click = lambda _: cambiar_vista("historial")

  vista_calculadora = ft.Column(
      [
          ft.Container(
              content=ft.Column(
                  [
                      ft.Text(
                          "DATOS DEL PROYECTO",
                          color=ACCENT_YELLOW,
                          weight=ft.FontWeight.BOLD,
                          size=12,
                      ),
                      txt_proyecto,
                      ft.Row([txt_cliente, txt_telefono]),
                      ft.Row([txt_direccion, txt_fecha]),
                      ft.Row([dd_tipo, dd_caida]),
                  ],
                  spacing=8,
              ),
              bgcolor=BG_CARD,
              padding=14,
              border_radius=10,
              border=ft.Border.all(width=1, color=ACCENT_YELLOW),
          ),
          col_areas,
          ft.Container(
              content=ft.Column(
                  [
                      ft.Container(
                          content=ft.Row(
                              [
                                  ft.Text(
                                      "+ AGREGAR ÁREA",
                                      color="black",
                                      weight=ft.FontWeight.BOLD,
                                      size=12,
                                  )
                              ],
                              alignment=ft.MainAxisAlignment.CENTER,
                          ),
                          bgcolor=ACCENT_YELLOW,
                          padding=12,
                          border_radius=8,
                          on_click=lambda e: agregar_area(),
                      ),
                      ft.Container(
                          content=ft.Row(
                              [
                                  ft.Text(
                                      "CALCULAR TODO",
                                      color="black",
                                      weight=ft.FontWeight.BOLD,
                                      size=12,
                                  )
                              ],
                              alignment=ft.MainAxisAlignment.CENTER,
                          ),
                          bgcolor=ACCENT_GREEN,
                          padding=12,
                          border_radius=8,
                          on_click=calcular_todo,
                      ),
                      ft.Container(
                          content=ft.Row(
                              [
                                  ft.Text(
                                      "GUARDAR PROYECTO",
                                      color="black",
                                      weight=ft.FontWeight.BOLD,
                                      size=12,
                                  )
                              ],
                              alignment=ft.MainAxisAlignment.CENTER,
                          ),
                          bgcolor=ACCENT_CYAN,
                          padding=12,
                          border_radius=8,
                          on_click=guardar_proyecto_click,
                      ),
                      ft.Container(
                          content=ft.Row(
                              [
                                  ft.Text(
                                      "NUEVO / LIMPIAR TODO",
                                      color="white",
                                      weight=ft.FontWeight.BOLD,
                                      size=12,
                                  )
                              ],
                              alignment=ft.MainAxisAlignment.CENTER,
                          ),
                          bgcolor=ACCENT_BLUE,
                          padding=12,
                          border_radius=8,
                          on_click=limpiar,
                      ),
                  ],
                  spacing=8,
              ),
              bgcolor=BG_CARD,
              padding=14,
              border_radius=10,
              border=ft.Border.all(width=1, color=BORDER_COLOR),
          ),
          card_resultado,
      ],
      spacing=10,
  )

  vista_historial = ft.Column(
      [
          ft.Text(
              "PROYECTOS Y CÁLCULOS GUARDADOS",
              size=14,
              weight=ft.FontWeight.BOLD,
              color=ACCENT_YELLOW,
          ),
          col_proyectos_lista,
      ],
      spacing=10,
      visible=False,
  )

  page.add(
      ft.Column(
          [ft.Row([btn_tab_calc, btn_tab_hist]), vista_calculadora, vista_historial],
          spacing=10,
      )
  )

  draft = db_load_draft()
  if draft:
    cargar_datos_en_formulario(draft)


if __name__ == "__main__":
  ft.app(target=main)
