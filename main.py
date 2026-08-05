import flet as ft
import math
import datetime
import json

def main(page: ft.Page):
    page.title = "DUCTULADOR V8"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 6

    BG_CARD = "#1e293b"
    BG_DARK = "#0f172a"
    BORDER_COLOR = "#334155"
    ACCENT_YELLOW = "#facc15"
    ACCENT_BLUE = "#3b82f6"
    ACCENT_GREEN = "#22c55e"
    ACCENT_CYAN = "#38bdf8"
    ACCENT_ORANGE = "#fb923c"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_PINK = "#ec4899"
    ACCENT_TEAL = "#14b8a6"
    ACCENT_AMBER = "#f59e0b"
    TEXT_MUTED = "#94a3b8"

    def calc_diam(cfm, p):
        if cfm <= 0: return 0
        return (0.109136 * (cfm ** 1.9) / p) ** (1 / 5.02)

    def lado_cuadrado(d):
        if d <= 0: return 0
        return math.ceil(d / 1.094)

    def ancho_rect(d, a):
        if a <= 0 or d <= 0: return 0
        low, high = 1, 200
        for _ in range(80):
            b = (low + high) / 2
            de = 1.30 * ((a * b) ** 0.625) / ((a + b) ** 0.25)
            if de < d:
                low = b
            else:
                high = b
        return math.ceil(low)

    # Campos header
    txt_proyecto = ft.TextField(label="PROYECTO", hint_text="Ej: Restaurante", border_color=BORDER_COLOR, text_size=13, on_change=lambda e: guardar_estado())
    txt_cliente = ft.TextField(label="CLIENTE", hint_text="Cliente", border_color=BORDER_COLOR, expand=True, text_size=13, on_change=lambda e: guardar_estado())
    txt_telefono = ft.TextField(label="TELÉFONO", hint_text="618-123-4567", border_color=BORDER_COLOR, expand=True, text_size=13, on_change=lambda e: guardar_estado())
    txt_direccion = ft.TextField(label="DIRECCIÓN", hint_text="Punto Guadiana", border_color=BORDER_COLOR, expand=True, text_size=13, on_change=lambda e: guardar_estado())
    txt_fecha = ft.TextField(label="FECHA", value=datetime.date.today().strftime("%Y-%m-%d"), border_color=BORDER_COLOR, expand=True, text_size=13, on_change=lambda e: guardar_estado())

    dd_tipo = ft.Dropdown(
        label="TIPO",
        options=[
            ft.dropdown.Option("18", "Casa 18m²/T"),
            ft.dropdown.Option("15", "Comercio 15m²/T"),
            ft.dropdown.Option("12", "Caliente 12m²/T"),
        ],
        value="15",
        expand=True
    )
    dd_tipo.on_change = lambda e: guardar_estado()

    dd_caida = ft.Dropdown(
        label="CAÍDA",
        options=[
            ft.dropdown.Option("0.08", "0.08"),
            ft.dropdown.Option("0.10", "0.10"),
            ft.dropdown.Option("0.15", "0.15"),
        ],
        value="0.10",
        expand=True
    )
    dd_caida.on_change = lambda e: guardar_estado()

    col_areas = ft.Column()
    card_resultado = ft.Container(visible=False, bgcolor=BG_CARD, padding=8, border_radius=10, border=ft.Border.all(1, BORDER_COLOR))
    
    state = {"last_total_cfm": 0, "last_diam_tot": 0}
    areas_list = []

    def guardar_estado():
        try:
            datos_areas = []
            for item in areas_list:
                datos_areas.append({
                    "modo": item["modo"],
                    "nom": item["nom"].value,
                    "largo": item["largo"].value,
                    "ancho": item["ancho"].value,
                    "m2_directo": item["m2_directo"].value,
                    "alto": item["alto"].value,
                    "h_ducto": item["h_ducto"].value,
                    "ramal": item["ramal"].value,
                })
            
            payload = {
                "proyecto": txt_proyecto.value,
                "cliente": txt_cliente.value,
                "telefono": txt_telefono.value,
                "direccion": txt_direccion.value,
                "fecha": txt_fecha.value,
                "tipo": dd_tipo.value,
                "caida": dd_caida.value,
                "areas": datos_areas
            }
            page.client_storage.set("ductulador_draft", json.dumps(payload))
        except Exception:
            pass

    def alternar_modo(item, modo):
        item["modo"] = modo
        item["box_medidas"].visible = (modo == "medidas")
        item["box_m2"].visible = (modo == "m2")
        item["btn_medidas"].bgcolor = ACCENT_YELLOW if modo == "medidas" else BG_CARD
        item["txt_btn_med"].color = "black" if modo == "medidas" else TEXT_MUTED
        item["btn_m2"].bgcolor = ACCENT_YELLOW if modo == "m2" else BG_CARD
        item["txt_btn_m2"].color = "black" if modo == "m2" else TEXT_MUTED
        guardar_estado()
        page.update()

    def borrar_area(item):
        if item in areas_list:
            areas_list.remove(item)
            col_areas.controls.remove(item["card"])
            guardar_estado()
            page.update()

    def agregar_area(data_prev=None, e=None):
        if len(areas_list) >= 20:
            return

        idx = len(areas_list) + 1
        
        val_nom = data_prev["nom"] if data_prev else f"Area {idx}"
        val_largo = data_prev["largo"] if data_prev else ""
        val_ancho = data_prev["ancho"] if data_prev else ""
        val_m2_dir = data_prev["m2_directo"] if data_prev else ""
        val_alto = data_prev["alto"] if data_prev else "2.5"
        val_h_ducto = data_prev["h_ducto"] if data_prev else "0"
        val_ramal = data_prev["ramal"] if data_prev else "PRINCIPAL"
        modo_init = data_prev["modo"] if data_prev else "medidas"

        txt_nom = ft.TextField(value=val_nom, border_color=BORDER_COLOR, text_size=13, on_change=lambda e: guardar_estado())
        txt_largo = ft.TextField(label="LARGO (m)", value=val_largo, hint_text="4", keyboard_type=ft.KeyboardType.NUMBER, expand=True, border_color=BORDER_COLOR, text_size=13, on_change=lambda e: guardar_estado())
        txt_ancho = ft.TextField(label="ANCHO (m)", value=val_ancho, hint_text="4", keyboard_type=ft.KeyboardType.NUMBER, expand=True, border_color=BORDER_COLOR, text_size=13, on_change=lambda e: guardar_estado())
        txt_m2_directo = ft.TextField(label="M² DIRECTOS", value=val_m2_dir, hint_text="16", keyboard_type=ft.KeyboardType.NUMBER, border_color=BORDER_COLOR, text_size=13, on_change=lambda e: guardar_estado())
        txt_alto = ft.TextField(label="ALTURA ÁREA (m)", value=val_alto, keyboard_type=ft.KeyboardType.NUMBER, expand=True, border_color=BORDER_COLOR, text_size=13, on_change=lambda e: guardar_estado())
        txt_h_ducto = ft.TextField(label="ALTURA DUCTO (0=cuadrado)", value=val_h_ducto, keyboard_type=ft.KeyboardType.NUMBER, expand=True, border_color=ACCENT_YELLOW, text_size=13, on_change=lambda e: guardar_estado())

        dd_ramal = ft.Dropdown(
            label="LÍNEA / RAMAL",
            options=[
                ft.dropdown.Option("PRINCIPAL", "Principal (Tronco)"),
                ft.dropdown.Option("RAMAL_A", "Ramal Brazo A"),
                ft.dropdown.Option("RAMAL_B", "Ramal Brazo B"),
                ft.dropdown.Option("RAMAL_C", "Ramal Brazo C"),
                ft.dropdown.Option("RAMAL_D", "Ramal Brazo D"),
                ft.dropdown.Option("RAMAL_E", "Ramal Brazo E"),
            ],
            value=val_ramal,
            expand=True
        )
        dd_ramal.on_change = lambda e: guardar_estado()

        lbl_res_area = ft.Text("", size=12, color=ACCENT_CYAN, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

        box_medidas = ft.Row([txt_largo, txt_ancho], visible=(modo_init == "medidas"))
        box_m2 = ft.Column([txt_m2_directo], visible=(modo_init == "m2"))

        txt_b_med = ft.Text("POR MEDIDAS", color="black" if modo_init == "medidas" else TEXT_MUTED, weight=ft.FontWeight.BOLD, size=11, text_align=ft.TextAlign.CENTER)
        txt_b_m2 = ft.Text("M² DIRECTO", color="black" if modo_init == "m2" else TEXT_MUTED, weight=ft.FontWeight.BOLD, size=11, text_align=ft.TextAlign.CENTER)

        btn_medidas = ft.Container(
            content=ft.Row([txt_b_med], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ACCENT_YELLOW if modo_init == "medidas" else BG_CARD, padding=6, border_radius=6, expand=True, border=ft.Border.all(1, "#475569")
        )
        btn_m2 = ft.Container(
            content=ft.Row([txt_b_m2], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ACCENT_YELLOW if modo_init == "m2" else BG_CARD, padding=6, border_radius=6, expand=True, border=ft.Border.all(1, "#475569")
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
            "cfm": 0, "diam": 0, "tons": 0
        }

        btn_medidas.on_click = lambda _: alternar_modo(item, "medidas")
        btn_m2.on_click = lambda _: alternar_modo(item, "m2")

        btn_borrar = ft.Container(
            content=ft.Text("X BORRAR", color="#ef4444", size=11, weight=ft.FontWeight.BOLD),
            on_click=lambda _: borrar_area(item)
        )

        header_area = ft.Row([
            ft.Text(f"ÁREA {idx}", weight=ft.FontWeight.BOLD, color="white", size=13),
            btn_borrar
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        card_area = ft.Container(
            content=ft.Column([
                header_area,
                txt_nom,
                ft.Row([btn_medidas, btn_m2]),
                box_medidas,
                box_m2,
                ft.Row([txt_alto, txt_h_ducto]),
                dd_ramal,
                ft.Row([lbl_res_area], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=8),
            bgcolor=BG_DARK, padding=10, border_radius=10, border=ft.Border.all(1, "#475569")
        )

        item["card"] = card_area
        areas_list.append(item)
        col_areas.controls.append(card_area)
        
        if not data_prev:
            guardar_estado()
        page.update()

    def cargar_estado_guardado():
        try:
            raw = page.client_storage.get("ductulador_draft")
            if raw:
                data = json.loads(raw)
                txt_proyecto.value = data.get("proyecto", "")
                txt_cliente.value = data.get("cliente", "")
                txt_telefono.value = data.get("telefono", "")
                txt_direccion.value = data.get("direccion", "")
                txt_fecha.value = data.get("fecha", datetime.date.today().strftime("%Y-%m-%d"))
                dd_tipo.value = data.get("tipo", "15")
                dd_caida.value = data.get("caida", "0.10")

                areas_saved = data.get("areas", [])
                if areas_saved:
                    for a in areas_saved:
                        agregar_area(data_prev=a)
                    return True
        except Exception:
            pass
        return False

    def actualizar_medida_tramo(txt_h_custom, lbl_medida, lbl_detalles, d_remanente, cfm_rem):
        try:
            h_val = float(txt_h_custom.value or 0)
        except ValueError:
            h_val = 0

        d_tramo_redondo = math.ceil(d_remanente)

        if h_val <= 0:
            lado = lado_cuadrado(d_remanente)
            lbl_medida.value = f'{lado}"x{lado}"  |  {d_tramo_redondo}" Ø'
            lbl_detalles.value = f'{lado*lado} pulg² | {int(cfm_rem)} CFM'
        else:
            ancho = ancho_rect(d_remanente, h_val)
            lbl_medida.value = f'{int(h_val)}"x{ancho}"  |  {d_tramo_redondo}" Ø'
            lbl_detalles.value = f'{int(h_val)*ancho} pulg² | {int(cfm_rem)} CFM'
        page.update()

    def calcular_todo(e):
        guardar_estado()
        tipo = float(dd_tipo.value)
        caida = float(dd_caida.value)

        proy = (txt_proyecto.value or "SIN NOMBRE").upper()
        cli = txt_cliente.value or "---"
        tel = txt_telefono.value or "---"
        dir_txt = txt_direccion.value or "---"
        fec = txt_fecha.value or ""

        total_cfm = 0
        total_m2 = 0
        total_m3 = 0
        total_tr = 0

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

            if m2 <= 0: continue

            try:
                alto = float(item["alto"].value or 2.5)
                h_d = float(item["h_ducto"].value or 0)
            except ValueError:
                alto, h_d = 2.5, 0

            m3 = m2 * alto
            nome = item["nom"].value or "Área"
            ramal_sel = item["ramal"].value or "PRINCIPAL"
            tons_exact = (m2 / tipo) * (alto / 2.7 if alto > 2.7 else 1)
            cfm = tons_exact * 400

            total_cfm += cfm
            total_m2 += m2
            total_m3 += m3
            total_tr += tons_exact

            d = calc_diam(cfm, caida)

            items_calculados.append({
                "nome": nome,
                "m2": m2,
                "m3": m3,
                "tons": tons_exact,
                "cfm": cfm,
                "d": d,
                "h_d": h_d,
                "ramal": ramal_sel
            })

        if total_cfm == 0:
            return

        dt = ft.DataTable(
            column_spacing=14,
            data_row_min_height=46,
            border=ft.Border.all(1, ACCENT_BLUE),
            vertical_lines=ft.BorderSide(1.5, ACCENT_CYAN),
            horizontal_lines=ft.BorderSide(1, "#334155"),
            columns=[
                ft.DataColumn(ft.Text("ÁREA", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("M²", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("TR", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("CFM", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("SALIDA (RECT / Ø)", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("TRAMO DUCTO (EDITABLE)", color=ACCENT_GREEN, weight=ft.FontWeight.BOLD, size=11)),
            ],
            rows=[]
        )

        cfm_ramales = {
            "RAMAL_A": sum(x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_A"),
            "RAMAL_B": sum(x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_B"),
            "RAMAL_C": sum(x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_C"),
            "RAMAL_D": sum(x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_D"),
            "RAMAL_E": sum(x["cfm"] for x in items_calculados if x["ramal"] == "RAMAL_E"),
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

            # Salida Individual
            d_salida_redondo = math.ceil(item["d"])
            if item["h_d"] == 0:
                lado = lado_cuadrado(item["d"])
                propuesta_salida = f'{lado}"x{lado}"  |  {d_salida_redondo}" Ø'
                pulg2_salida = lado * lado
            else:
                ancho = ancho_rect(item["d"], item["h_d"])
                propuesta_salida = f'{int(item["h_d"])}"x{ancho}"  |  {d_salida_redondo}" Ø'
                pulg2_salida = int(item["h_d"]) * ancho

            # Ducto del Tramo
            d_remanente = calc_diam(cfm_para_tramo, caida)
            d_tramo_redondo = math.ceil(d_remanente)
            
            if item["h_d"] == 0:
                lado_p = lado_cuadrado(d_remanente)
                init_medida_tramo = f'{lado_p}"x{lado_p}"  |  {d_tramo_redondo}" Ø'
                init_detalles_tramo = f'{lado_p*lado_p} pulg² | {int(cfm_para_tramo)} CFM'
                init_h_val = "0"
            else:
                ancho_p = ancho_rect(d_remanente, item["h_d"])
                init_medida_tramo = f'{int(item["h_d"])}"x{ancho_p}"  |  {d_tramo_redondo}" Ø'
                init_detalles_tramo = f'{int(item["h_d"])*ancho_p} pulg² | {int(cfm_para_tramo)} CFM'
                init_h_val = str(int(item["h_d"]))

            color_map = {
                "PRINCIPAL": ACCENT_GREEN,
                "RAMAL_A": ACCENT_ORANGE,
                "RAMAL_B": ACCENT_PURPLE,
                "RAMAL_C": ACCENT_PINK,
                "RAMAL_D": ACCENT_TEAL,
                "RAMAL_E": ACCENT_AMBER
            }

            lbl_color = color_map.get(r, ACCENT_GREEN)
            tag = "TRONCO" if r == "PRINCIPAL" else r

            lbl_medida_tramo = ft.Text(init_medida_tramo, color=lbl_color, weight=ft.FontWeight.BOLD, size=12)
            lbl_detalles_tramo = ft.Text(f"{init_detalles_tramo} [{tag}]", size=9, color=TEXT_MUTED)
            
            txt_h_tramo_custom = ft.TextField(
                value=init_h_val,
                width=42,
                height=32,
                content_padding=3,
                text_size=11,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_color=lbl_color,
                text_align=ft.TextAlign.CENTER
            )

            txt_h_tramo_custom.on_change = lambda e, txt=txt_h_tramo_custom, lbl_m=lbl_medida_tramo, lbl_d=lbl_detalles_tramo, d_r=d_remanente, cfm_r=cfm_para_tramo: actualizar_medida_tramo(txt, lbl_m, lbl_d, d_r, cfm_r)

            nombre_con_tag = f"{item['nome']} [{tag}]" if r != "PRINCIPAL" else item['nome']

            dt.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(nombre_con_tag, color=lbl_color if r != "PRINCIPAL" else "white", size=11, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(f"{item['m2']:.1f}", size=11)),
                    ft.DataCell(ft.Text(f"{item['tons']:.2f}", color=ACCENT_CYAN, weight=ft.FontWeight.BOLD, size=11)),
                    ft.DataCell(ft.Text(str(int(item["cfm"])), size=11)),
                    ft.DataCell(ft.Column([
                        ft.Text(propuesta_salida, color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11),
                        ft.Text(f"{pulg2_salida} pulg²", size=9, color=TEXT_MUTED)
                    ], spacing=1)),
                    ft.DataCell(ft.Row([
                        ft.Column([ft.Text("Alt:", size=8, color=TEXT_MUTED), txt_h_tramo_custom], spacing=1),
                        ft.Column([lbl_medida_tramo, lbl_detalles_tramo], spacing=1)
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)),
                ])
            )

        state["last_total_cfm"] = total_cfm
        state["last_diam_tot"] = calc_diam(total_cfm, caida)
        lado_prin = lado_cuadrado(state["last_diam_tot"])
        d_principal_redondo = math.ceil(state["last_diam_tot"])

        box_principal = ft.Container(
            content=ft.Column([
                ft.Text("DUCTO PRINCIPAL INICIAL (SALIDA DEL EQUIPO)", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f'{lado_prin}"x{lado_prin}"  |  {d_principal_redondo}" Ø', size=16, color=ACCENT_GREEN, weight=ft.FontWeight.BOLD),
                        ft.Text(f'{lado_prin*lado_prin} pulg² | {total_cfm:.0f} CFM TOTALES', size=10, color=TEXT_MUTED)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=BG_CARD, padding=8, border_radius=6
                ),
            ]),
            bgcolor=BG_DARK, padding=10, border_radius=8, border=ft.Border.all(1, ACCENT_YELLOW)
        )

        header_resumen = ft.Container(
            content=ft.Column([
                ft.Text(f"PROYECTO: {proy}", weight=ft.FontWeight.BOLD, color="black", size=13),
                ft.Text(f"Cliente: {cli} | Tel: {tel}\n{dir_txt} | {fec}", size=11, color="black")
            ]),
            bgcolor=ACCENT_YELLOW, padding=8, border_radius=6
        )

        total_btu = total_tr * 12000

        barra_totales = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"TOTAL: {total_m2:.1f} m² / {total_m3:.1f} m³", weight=ft.FontWeight.BOLD, size=11),
                    ft.Text(f"{total_tr:.2f} TR", color=ACCENT_CYAN, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{int(total_cfm)} CFM", color=ACCENT_GREEN, weight=ft.FontWeight.BOLD, size=11)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                ft.Row([
                    ft.Text(f"CAPACIDAD TÉRMICA: {total_btu:,.0f} BTU/h", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=11)
                ], alignment=ft.MainAxisAlignment.CENTER)
            ]),
            bgcolor=BG_CARD, padding=8, border_radius=6
        )

        tabla_scrollable = ft.Row(
            [dt],
            scroll=ft.ScrollMode.ALWAYS
        )

        card_resultado.content = ft.Column([
            header_resumen,
            tabla_scrollable,
            barra_totales,
            box_principal
        ], spacing=10)
        card_resultado.visible = True
        page.update()

    def limpiar(e=None):
        col_areas.controls.clear()
        areas_list.clear()
        card_resultado.visible = False
        txt_proyecto.value = ""
        txt_cliente.value = ""
        txt_telefono.value = ""
        txt_direccion.value = ""
        try:
            page.client_storage.remove("ductulador_draft")
        except Exception:
            pass
        agregar_area()
        page.update()

    btn_add = ft.Container(
        content=ft.Row([ft.Text("+ AGREGAR ÁREA", color="black", weight=ft.FontWeight.BOLD, size=12)], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ACCENT_YELLOW, padding=10, border_radius=8, on_click=lambda e: agregar_area()
    )
    btn_calc = ft.Container(
        content=ft.Row([ft.Text("CALCULAR TODO", color="black", weight=ft.FontWeight.BOLD, size=12)], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ACCENT_GREEN, padding=10, border_radius=8, on_click=calcular_todo
    )
    btn_clean = ft.Container(
        content=ft.Row([ft.Text("LIMPIAR TODO", color="white", weight=ft.FontWeight.BOLD, size=12)], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ACCENT_BLUE, padding=10, border_radius=8, on_click=limpiar
    )

    page.add(
        ft.Column([
            ft.Text("DUCTULADOR V8", size=18, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("FLUJO ACUMULATIVO Y RAMIFICACIONES", size=10, color=ACCENT_GREEN, weight=ft.FontWeight.BOLD)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        
        ft.Container(
            content=ft.Column([
                ft.Text("DATOS DEL PROYECTO", color=ACCENT_YELLOW, weight=ft.FontWeight.BOLD, size=12),
                txt_proyecto,
                ft.Row([txt_cliente, txt_telefono]),
                ft.Row([txt_direccion, txt_fecha]),
                ft.Row([dd_tipo, dd_caida])
            ], spacing=8),
            bgcolor=BG_CARD, padding=10, border_radius=10, border=ft.Border.all(1, ACCENT_YELLOW)
        ),
        
        col_areas,
        
        ft.Container(
            content=ft.Column([btn_add, btn_calc, btn_clean], spacing=8),
            bgcolor=BG_CARD, padding=10, border_radius=10, border=ft.Border.all(1, BORDER_COLOR)
        ),
        
        card_resultado
    )

    if not cargar_estado_guardado():
        agregar_area()

ft.app(target=main)
