from views.modules.nomina_view import nomina_view
from views.modules.contabilidad_view import contabilidad_view
from views.modules.activos_fijos_view import activos_fijos_view
from views.modules.cobros_pagos_view import cobros_pagos_view
from views.modules.control_almacen_view import control_almacen_view
from views.modules.inventario_view import inventarios_view

# Definiendo los modulos a mostrar en el menu para seleccionar la vista
modules = {
    "Nomina": nomina_view,
    "Contabilidad": contabilidad_view,
    "Activos Fijos": activos_fijos_view,
    "Cobros y Pagos": cobros_pagos_view,
    "Control de Almacen": control_almacen_view,
    "Inventarios": inventarios_view,
}
