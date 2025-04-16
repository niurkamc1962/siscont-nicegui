from nicegui import ui, Client, app
from stores.store import AppState
from datetime import datetime
from db.db_manager import create_db_manager


def main_view(client: Client):
    store: AppState = app.state.store

    ui.query('body').style('background-color: #f5f5f5')

    with ui.header().classes('bg-primary text-white'):
        ui.label('Siscont - ERPNext').classes('text-h5')
        ui.space()
        if store.connected:
            ui.select(
                options=get_module_choices() + [{'label': 'Salir', 'value': 'salir'}],
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
        ui.open('/')
    else:
        store.selected_module = e.value
        ui.open('/')


def connection_form(store: AppState):
    with ui.card().classes('absolute-center w-96'):
        ui.label('Conectar con servidor ERP').classes('text-h6')
        
        ip_input = ui.input('IP del servidor ERP').classes('w-full')
        user_input = ui.input('Usuario').classes('w-full')
        password_input = ui.input('Contraseña', password=True, password_toggle_button=True).classes('w-full')
        database_input = ui.input('Base de datos', value='master').classes('w-full')
        port_input = ui.input('Puerto', value='1433').classes('w-full')
        
        error_label = ui.label('').classes('text-red')

        async def connect():
            try:
                if not ip_input.value:
                    error_label.text = 'La IP del servidor es requerida'
                    return
                if not user_input.value:
                    error_label.text = 'El usuario es requerido'
                    return
                if not password_input.value:
                    error_label.text = 'La contraseña es requerida'
                    return

                store.db_params = {
                    'host': ip_input.value,
                    'user': user_input.value,
                    'password': password_input.value,
                    'database': database_input.value or 'master',
                    'port': port_input.value or '1433'
                }

                db_manager = create_db_manager(store.db_params)
                with db_manager.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    if cursor.fetchone()[0] == 1:
                        store.connected = True
                        store.db_manager = db_manager
                        store.ip_server = ip_input.value
                        ui.notify('Conexión exitosa!', type='positive')
                        ui.open('/')

            except Exception as e:
                error_label.text = f'Error de conexión: {str(e)}'
                store.reset()
                ui.notify('Error al conectar', type='negative')

        ui.button('Conectar', on_click=connect).classes('mt-2 w-full')


def welcome_view():
    ui.label('Bienvenido al sistema Siscont').classes('text-h4 mt-4 text-center')


def get_module_choices():
    return [{'label': 'Módulo 1', 'value': 'mod1'}, {'label': 'Módulo 2', 'value': 'mod2'}]


modules = {
    'mod1': type('', (), {'render': lambda: ui.label('Módulo 1')}),
    'mod2': type('', (), {'render': lambda: ui.label('Módulo 2')})
}
