# Feature: Mostrar tabla LinkClick en el panel de admin

- **Fecha**: 2026-03-21
- **Solicitado como**: en el admin no se muestra la nueva tabla de llevar el conteo y las horas a las que se accedio a los links

## Descripcion
El modelo `LinkClick` ya existia pero no tenia un `ModelView` registrado en SQLAdmin, por lo que no aparecia en el panel de administracion. Se agrego la vista `LinkClickAdmin` con las columnas relevantes.

## Archivos modificados
- `app/admin/views.py` - Se agrego `LinkClickAdmin` (solo lectura) y se registro en `ALL_VIEWS`

## Decisiones tecnicas
- Vista configurada como **solo lectura** (`can_create=False`, `can_edit=False`, `can_delete=False`) ya que los clicks se registran automaticamente via API
- Ordenacion por defecto: `clicked_at` descendente (mas recientes primero)
- `page_size=50` para facilitar la revision de volumenes altos de clicks
- Icono `fa-chart-line` para diferenciarla visualmente como tabla de analytics

## Verificacion
- Se verifico que el import de `LinkClick` y la clase `LinkClickAdmin` estan correctamente definidos
- La vista se registra en `ALL_VIEWS` que `setup.py` itera para montar en el admin
