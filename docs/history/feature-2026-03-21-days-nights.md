# Feature: Dias por destino y noches por alojamiento

- **Fecha**: 2026-03-21
- **Solicitado como**: "cada destino deberia tener la duracion del viaje total y cada accomodation los dias en cada lugar"

## Descripcion
Cada destino ahora indica cuantos dias se pasa alli (campo `days`), y cada alojamiento cuantas noches corresponden (campo `nights`, igual a los dias del destino).

## Archivos modificados
- `app/domain/models/destination.py` - Nuevo campo `days: int` (default 1)
- `app/domain/models/accommodation.py` - Nuevo campo `nights: int` (default 1)
- `app/schemas/destination.py` - Anadido `days: int` a DestinationResponse
- `app/schemas/accommodation.py` - Anadido `nights: int` a AccommodationResponse
- `app/services/pack_service.py` - Pasar days y nights en los builders
- `app/seeds/seed_data.py` - Dias correctos por destino y noches por alojamiento en los 8 packs

## Archivos creados
- `alembic/versions/003_add_days_and_nights.py` - Migracion ADD COLUMN
- `scripts/patch_days.py` - Script auxiliar para patchear el seed

## Migraciones
- `003_add_days_and_nights` - ADD COLUMN days (destinations), ADD COLUMN nights (accommodations)

## Datos por pack
| Pack | Destinos (dias) | Total |
|------|----------------|-------|
| Paris | Paris(5) | 5 |
| Italia | Roma(3), Florencia(3), Venecia(2), Amalfi(2) | 10 |
| Espana | Madrid(3), Barcelona(4) | 7 |
| Eslovenia-Croacia | Ljubljana(2), Bled(1), Plitvice(1), Dubrovnik(3) | 7+1 traslado |
| Japon | Tokyo(5), Kyoto(4), Osaka(3) | 12 |
| Londres | London(5) | 5 |
| Noruega | Bergen(2), Geiranger(2), Flam(1), Stavanger(2) | 7 |
| Kenia | Nairobi(1), Masai Mara(3), Nakuru(1), Amboseli(2) | 7+1 regreso |
