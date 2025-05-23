from nicegui import ui, app
from datetime import datetime
from stores.store import AppState


async def base_layout(content_function, store: AppState):
    """Layout base simplificado porque el menú está en main_view"""
    ui.query("body").style("background-color: #f5f5f5")

    # Header
    with ui.header().classes("bg-primary text-white justify-between px-4"):
        ui.label("Siscont - ERPNext").classes("text-h5")
        if store.connected:
            with ui.row().classes('items-center'):
                ui.icon('check_circle').classes('text-green-300')
                if hasattr(store, 'db_params') and store.db_params:
                    ui.label(f"Conectado: {store.db_params.db_name}").classes('ml-2 text-caption')

    # Contenido principal
    try:
        await content_function()
    except Exception as e:
        ui.notify(f"Error cargando contenido: {str(e)}", type='negative')
        print(f"Content Error: {str(e)}")

    # Footer
    with ui.footer().classes("bg-primary text-white"):
        ui.label(f"Tecnomática © {datetime.now().year}").classes("text-center w-full")


async def on_module_change(e, store: AppState):
    if e.value == "Salir":
        store.reset()
        # Limpiar storage de usuario
        app.storage.user.clear()  # Esto borrará todos los datos de sesión
        ui.notify("Sesión cerrada", type="info")
        ui.navigate.to('/')
    else:
        store.selected_module = e.value
        app.storage.user['selected_module'] = e.value
        app.storage.user['last_activity'] = datetime.now().isoformat()
        ui.navigate.to(f"/modulo/{e.value}")