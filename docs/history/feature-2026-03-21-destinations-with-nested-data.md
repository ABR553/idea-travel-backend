# Feature: Accommodations y experiences anidados en cada destino

- **Fecha**: 2026-03-21
- **Solicitado como**: "en el endpoint de obtener un pack por slug anade que cada destino lleva una lista de accomodations y una lista de experiencias"

## Descripcion
En GET /api/v1/packs/{slug}, cada destino ahora incluye sus accommodations y experiences anidados. Se mantienen tambien aplanados a nivel de pack para retrocompatibilidad.

## Archivos modificados
- `app/schemas/destination.py` - Nuevo schema `DestinationDetailResponse` que hereda de `DestinationResponse` y anade `accommodations[]` y `experiences[]`
- `app/schemas/pack.py` - `PackResponse.destinations` ahora usa `DestinationDetailResponse` en vez de `DestinationResponse`
- `app/services/pack_service.py` - Nueva funcion `_build_destination_detail_response` que construye destinos con sus accommodations y experiences. Se usa en `_pack_to_full_response`

## Estructura de respuesta
```json
{
  "destinations": [
    {
      "name": "Paris",
      "country": "Francia",
      "description": "...",
      "image": "...",
      "accommodations": [
        { "id": "...", "name": "Generator Paris", "tier": "budget", ... }
      ],
      "experiences": [
        { "id": "...", "title": "Torre Eiffel: visita guiada", ... }
      ]
    }
  ],
  "accommodations": [...],
  "experiences": [...]
}
```

## Decisiones tecnicas
- Se creo `DestinationDetailResponse` como subclase de `DestinationResponse` para no romper el listado de packs (que sigue usando `DestinationResponse` sin datos anidados)
- Los arrays aplanados `accommodations` y `experiences` a nivel de pack se mantienen para retrocompatibilidad con el frontend actual
