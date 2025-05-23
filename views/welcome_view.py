# views/welcome_view.py

from nicegui import ui
from datetime import datetime

async def welcome_view():
    with ui.column().classes('w-full min-h-screen'):
        # Usamos ui.element('div') para definir las columnas
        with ui.element('div').classes('columns-2 w-full p-0 m-0'):
            
            # Columna de la imagen (ocupa el 50% en pantallas grandes)
            with ui.element('div').classes('w-full h-full p-0 m-0'):
                ui.image('static/siscont-2018.jpg').classes(
                    'w-full h-full object-cover'
                ).style('min-height: 400px; max-height: 100vh;')

            # Columna del texto (ocupa el 50% en pantallas grandes)
            with ui.element('div').classes('w-full h-full p-10 bg-white overflow-y-auto'):
                ui.label('Siscont - ERPNext').classes('text-4xl font-bold mb-6 text-primary')

                ui.html('''
                    <div class="text-body1">
                        Sistema integral de gestión empresarial que incluye:
                        <ul class="list-disc pl-5 mt-4 space-y-2">
                            <li>Módulo de Administración</li>
                            <li>Módulo General</li>
                            <li>Contabilidad General</li>
                            <li>Contabilidad de Costo (incluye consolidación)</li>
                            <li>Estados Financieros (incluye consolidación)</li>
                            <li>Activos fijos</li>
                            <li>Cobros y pagos</li>
                            <li>Inventarios y Útiles y herramientas</li>
                            <li>Control de Almacén (interno y externo)</li>
                            <li>Nómina y Sistemas de Pagos</li>
                            <li>Ventas y Compras (Web)</li>
                            <li>Gestión de Inversiones</li>
                            <li>Módulo Gerencial</li>
                            <li>Presupuestos</li>
                            <li>Consolidación de Inventarios</li>
                        </ul>
                    </div>
                ''').classes('text-gray-700 text-lg')

                ui.label(f'Versión 2.1 - Desarrollado por Tecnomática © {datetime.now().year}').classes(
                    'text-sm text-right mt-8 text-gray-500'
                )
