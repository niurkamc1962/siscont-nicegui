from nicegui import ui
from db.db_nomina import construir_tree_trabajadores
from services.nomina_services import fetch_relaciones_trabajadores, fetch_trabajadores
import json


async def nomina_view():
    relaciones = await fetch_relaciones_trabajadores()
    tree_data = construir_tree_trabajadores(relaciones)

    trabajadores = await fetch_trabajadores()

    with ui.column().classes('p-6 w-full'):
        ui.label('Módulo de Nómina').classes('text-2xl text-primary mb-4')

        with ui.tabs().classes('w-full') as tabs:
            tab1 = ui.tab('Relaciones entre Tablas')
            tab2 = ui.tab('Datos de Trabajadores')
            tab3 = ui.tab('Exportar JSON')
            tab4 = ui.tab('Importar JSON a Doctype')

        with ui.tab_panels(tabs, value=tab1).classes('w-full'):
            # Tab 1 - Relaciones entre Tablas
            with ui.tab_panel(tab1):
                ui.label('Relaciones entre Tablas').classes('text-lg font-bold mb-2')
                tree = ui.tree(
                    tree_data,
                    label_key='id',
                    node_key='id',
                    children_key='children',
                    on_select=lambda e: ui.notify(f'Seleccionado: {e.value}')
                )
                tree.add_slot('default-header', '''
                    <span :props="props">� <strong>{{ props.node.id }}</strong></span>
                ''')
                tree.add_slot('default-body', '''
                    <span :props="props">{{ props.node.description }}</span>
                ''')

            # Tab 2 - Datos de Trabajadores
            with ui.tab_panel(tab2):
                ui.label('Datos de Trabajadores').classes('text-lg font-bold mb-2')
                for t in trabajadores:
                    with ui.expansion(f"{t['CPTrabNombre']} {t['CPTrabPriApellido']} {t['CPTrabSegApellido']}").classes('w-full'):
                        for key, value in t.items():
                            ui.label(f"{key}: {value}")

            # Tab 3 - Exportar JSON
            with ui.tab_panel(tab3):
                # Fila para título y botón
                with ui.row().classes('items-center justify-between mb-4 w-full'):
                    # Título a la izquierda
                    ui.label('Exportar JSON').classes('text-lg font-bold').style('flex-grow: 1')

                    # Botón alineado a la derecha
                    ui.button('Guardar JSON en archivo', on_click=lambda: ui.download(json.dumps(trabajadores, indent=2, ensure_ascii=False), 'trabajadores.json')).classes('ml-4')

                # Área de texto debajo del título y botón
                json_str = json.dumps(trabajadores, indent=2, ensure_ascii=False)
                ui.textarea(value=json_str).classes('w-full h-96').style('overflow-y:auto')

            # Tab 4 - Importar JSON a formato Doctype
            with ui.tab_panel(tab4):
                # Fila para título y botón
                with ui.row().classes('items-center justify-between mb-4 w-full'):
                    # Título a la izquierda
                    ui.label('Importar JSON a formato Doctype').classes('text-lg font-bold').style('flex-grow: 1')

                    # Botón alineado a la derecha
                    ui.button('Procesar JSON como Doctype', on_click=lambda: ui.notify('JSON procesado a Doctype')).classes('ml-4')

                # Fila para la carga de archivo
                file = ui.upload(on_upload=lambda e: ui.notify('Archivo cargado')).props('accept=.json')
