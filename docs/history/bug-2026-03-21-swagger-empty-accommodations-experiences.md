# Bug: Swagger muestra listas vacias para accommodations y experiences en destinations

- **Fecha**: 2026-03-21
- **Tipo**: API / Documentacion OpenAPI
- **Reportado como**: El Swagger en los listados de accommodations y experiences dentro de destinations no tiene las props, solo sale la lista vacia. Front necesita ver los campos para integrarlo.

## Causa raiz
`DestinationDetailResponse` tenia `accommodations` y `experiences` definidos con default `= []`:

```python
accommodations: list[AccommodationResponse] = []
experiences: list[ExperienceResponse] = []
```

En Pydantic v2, cuando un campo tiene `default: []`, el JSON Schema generado incluye `"default": []` y el campo NO aparece en el array `required`. Swagger UI usa el valor por defecto como ejemplo, mostrando arrays vacios sin expandir el schema de los items (`AccommodationResponse`, `ExperienceResponse`).

## Archivos modificados
- `app/schemas/destination.py` - Eliminado `= []` de `accommodations` y `experiences` en `DestinationDetailResponse`

## Solucion aplicada
Se removieron los valores por defecto `= []` de ambos campos, haciendolos requeridos:

```python
accommodations: list[AccommodationResponse]
experiences: list[ExperienceResponse]
```

Esto es semanticamente correcto: la API siempre devuelve estos campos (aunque sea lista vacia). El servicio (`pack_service.py`) siempre los proporciona explicitamente.

## Verificacion
1. Se verifico el OpenAPI spec (`/openapi.json`): `accommodations` y `experiences` ahora aparecen en `required` y sin `"default": []`
2. Se verifico que el endpoint `GET /api/v1/packs/{slug}` sigue devolviendo datos correctos con accommodations y experiences poblados
3. Se verifico que el endpoint `GET /api/v1/packs` (listado) sigue funcionando correctamente
