from nicegui import ui, Client, app
from db.models import ConexionParams
from stores.store import AppState
from datetime import datetime
from db.database import create_db_manager
from config import get_settings

ui.add_head_html('''
    <style>
        .list-disc { list-style-type: disc; }
        .pl-5 { padding-left: 1.25rem; }
        .mt-2 { margin-top: 0.5rem; }
        .space-y-2 > * + * { margin-top: 0.5rem; }
    </style>
''')


def main_view(client: Client):
    store: AppState = app.state.store

    ui.query('body').style('background-color: #f5f5f5')

    with ui.header().classes('bg-primary text-white'):
        ui.label('Siscont - ERPNext').classes('text-h5')
        ui.space()
        if store.connected:
            # ui.select(
            #     options=get_module_choices() + [{'label': 'Salir', 'value': 'salir'}],
            #     on_change=lambda e: on_module_change(e, store)
            # ).props('filled label="Módulos"')

            ui.select(
                options=[(m['label'], m['value']) for m in get_module_choices()] + [('Salir', 'salir')],
                on_change=lambda e: on_module_change(e, store)
            ).props('filled label="Módulos"')

    with ui.page_sticky(position='top'):
        if not store.connected:
            connection_form(store)
        elif store.selected_module in modules:
            modules[store.selected_module].render()
        else:
            welcome_view()

    with ui.footer().classes('bg-primary text-white'):
        ui.label(f'Tecnomática © {datetime.now().year}').classes('text-center w-full')


def on_module_change(e, store: AppState):
    if e.value == 'salir':
        store.reset()
        ui.notify('Sesión cerrada')
        ui.navigate.to('/')
    else:
        store.selected_module = e.value
        ui.navigate.to('/')


def connection_form(store: AppState):
    settings = get_settings()  # Obteniendo los valores del .env
    
    with ui.column().classes('items-center justify-center min-h-screen'):
        with ui.card().classes('w-full max-w-md p-4'):
            ui.label('Teclee las credenciales').classes('text-h6 mb-4 text-center')

            ip_input = ui.input('IP del servidor SQL Server').classes('w-full')
            # user_input = ui.input('Usuario').classes('w-full')
            database_input = ui.input('Base de datos').classes('w-full')
            password_input = ui.input('Contraseña', password=True, password_toggle_button=True).classes('w-full')
            # port_input = ui.input('Puerto', value='1433').classes('w-full')

            error_label = ui.label('').classes('text-red text-sm')

            async def connect():
                if not ip_input.value:
                    error_label.text = 'La IP del servidor es requerida'
                    return
                # if not user_input.value:
                #     error_label.text = 'El usuario es requerido'
                #     return
                if not password_input.value:
                    error_label.text = 'La contraseña es requerida'
                    return
                if not database_input.value:
                    error_label.text = 'La base de datos es requerida'
                    return
                try:
                    params = ConexionParams(
                        host=ip_input.value,
                        user=settings.SQL_USER,
                        password=password_input.value,
                        database=database_input.value or 'master',
                        port=str(settings.SQL_PORT)
                    )
                    # Guardamos los parámetros como dict si los necesitas después
                    store.db_params = params.dict()
                    store.ip_server = ip_input.value

                    # Creamos el manager con los datos correctos
                    db_manager = create_db_manager(params)
                    
                    with db_manager.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        if cursor.fetchone()[0] == 1:
                            store.connected = True
                            store.db_manager = db_manager
                            store.ip_server = ip_input.value
                            ui.notify('Conexión exitosa!', type='positive')
                            ui.navigate.to('/')
                except Exception as e:
                    error_label.text = f'Error de conexión: {str(e)}'
                    store.reset()
                    ui.notify('Error al conectar', type='negative')

            ui.button('Conectar', on_click=connect).classes('mt-4 w-full')



def welcome_view():
    with ui.column().classes('items-center justify-center p-6 w-full'):
        with ui.card().classes('max-w-6xl w-full shadow-md'):
            with ui.row().classes('w-full items-stretch'):
                # Imagen
                with ui.column().classes('w-1/2'):
                    ui.image('static/siscont-2018.jpg').classes(
                        'w-full h-full object-cover rounded-l'
                    ).style('min-height: 350px; max-height: 500px;')

                # Contenido
                with ui.column().classes('p-6 w-1/2'):
                    ui.label('Siscont - ERPNext').classes('overflow-y-auto').style('max-height:400px')

                    ui.html('''
                        <div class="text-body1">
                            Sistema integral de gestión empresarial que incluye:
                            <ul class="list-disc pl-5 mt-2 space-y-2">
                                <li>Módulo de Administración</li>
                                <li>Módulo General</li>
                                <li>Contabilidad General</li>
                                <li>Contabilidad de Costo (incluye consolidación)</li>
                                <li>Estados Financieros (incluye consolidación)</li>
                                <li>Activos fijos</li>
                                <li>Cobros y pagos</li>
                                <li>Inventarios y Útiles y herramientas.</li>
                                <li>Control de Almacén (escenarios internos y externos)</li>
                                <li>Nómina y Cálculo de Sistemas de Pagos</li>
                                <li>Gestión Comercial. Ventas de Productos y Servicios. (Plataforma WEB)</li>
                                <li>Gestión Comercial. Compras. (Plataforma WEB)</li>
                                <li>Gestión de Inversiones (Plataforma WEB)</li>
                                <li>Módulo Gerencial (Plataforma WEB)</li>
                                <li>Módulo Presupuesto (Plataforma WEB)</li>
                                <li>Herramienta de Consolidación de inventarios (Plataforma WEB)</li>
                            </ul>
                        </div>
                    ''').classes('w-full')

                    ui.label(f'Versión 2.1 - Desarrollado por Tecnomática © {datetime.now().year}').classes(
                        'text-caption text-right mt-6'
                    )


def get_module_choices():
    return [
        {'label': 'Contabilidad', 'value': 'contabilidad'},
        {'label': 'Inventario', 'value': 'inventario'},
        {'label': 'Ventas', 'value': 'ventas'},
    ]


modules = {
    'mod1': type('', (), {'render': lambda: ui.label('Módulo 1')}),
    'mod2': type('', (), {'render': lambda: ui.label('Módulo 2')})
}
