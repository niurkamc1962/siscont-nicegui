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
            tab2 = ui.tab('Exportar de sqlserver a JSON')
            tab3 = ui.tab('Ver los archivos JSON generados')

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

            # Tab 2 - Mostrar los JSON a crear
            with ui.tab_panel(tab2):
                ui.label('Json a crear a partir de SQLServer').classes('text-lg font-bold mb-2')


            # Tab 3 - Generar los JSON
            with ui.tab_panel(tab3):
                ui.label('Mostrar proceso de los archivos que se van creando').classes('text-lg font-bold').style(
                    'flex-grow: 1')