# Vista de NOMINA
from nicegui import ui
from db.db_nomina import construir_tree_trabajadores
from services.nomina_services import fetch_relaciones_trabajadores, fetch_trabajadores
import asyncio


async def nomina_view():
    try:
        # Precarga de datos con manejo de errores
        with ui.linear_progress(show_value=False) as progress:
            relaciones, trabajadores = await asyncio.gather(
                fetch_relaciones_trabajadores(),
                fetch_trabajadores()
            )
            tree_data = construir_tree_trabajadores(relaciones)

        # Contenido principal
        with ui.column().classes('p-6 w-full'):
            # Header del módulo
            with ui.row().classes('w-full items-center mb-6'):
                ui.icon('payments').classes('text-3xl text-primary')
                ui.label('Módulo de Nómina').classes('text-2xl text-primary ml-2')

            # Pestañas
            with ui.tabs().classes('w-full') as tabs:
                tab_relaciones = ui.tab('Relaciones', icon='account_tree')
                tab_exportar = ui.tab('Exportar JSON', icon='cloud_upload')
                tab_archivos = ui.tab('Archivos', icon='folder')

            with ui.tab_panels(tabs, value=tab_relaciones).classes('w-full mt-2'):
                # Pestaña Relaciones
                with ui.tab_panel(tab_relaciones):
                    with ui.card().classes('w-full'):
                        ui.label('Estructura de relaciones').classes('text-lg font-bold mb-4')
                        ui.tree(
                            tree_data,
                            label_key='id',
                            node_key='id',
                            children_key='children',
                            on_select=lambda e: ui.notify(f'Seleccionado: {e.value}')
                        ).classes('w-full')

                # Pestaña Exportar
                with ui.tab_panel(tab_exportar):
                    with ui.card().classes('w-full'):
                        ui.label('Exportar datos').classes('text-lg font-bold mb-4')
                        # Aquí iría el contenido de exportación

                # Pestaña Archivos
                with ui.tab_panel(tab_archivos):
                    with ui.card().classes('w-full'):
                        ui.label('Archivos generados').classes('text-lg font-bold mb-4')
                        # Aquí iría el listado de archivos

    except Exception as e:
        ui.notify(f"Error en módulo nómina: {str(e)}", type='negative')
        print(f"Nómina Error: {str(e)}")
        raise


