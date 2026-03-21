# Feature: Booking URL en alojamientos

- **Fecha**: 2026-03-21
- **Solicitado como**: "los accomodations tiene que tener link de booking tambien, y ademas busca alojamientos reales de cada lugar para popular ese nuevo campo"

## Descripcion
Se anadio un campo `booking_url` a los alojamientos para enlazar directamente a la pagina de reserva en Booking.com. Se investigaron y anadieron URLs reales de Booking.com para los 24 alojamientos existentes (3 por cada uno de los 8 packs).

## Archivos modificados
- `app/domain/models/accommodation.py` - Nuevo campo `booking_url: str | None` (nullable)
- `app/schemas/accommodation.py` - Nuevo campo `bookingUrl` con alias `booking_url`
- `app/services/pack_service.py` - Incluido `booking_url` en la construccion de AccommodationResponse
- `app/seeds/seed_data.py` - Anadido `booking_url=` a las 24 llamadas `_make_accommodation` con URLs reales
- `app/seeds/add_pack.py` - Soporte para `booking_url` en el JSON de importacion

## Archivos creados
- `alembic/versions/002_add_booking_url_to_accommodations.py` - Migracion ALTER TABLE

## Migraciones
- `002_add_booking_url_to_accommodations` - ADD COLUMN booking_url VARCHAR(500) NULLABLE

## URLs de Booking reales anadidas

| Pack | Alojamiento | URL |
|------|-------------|-----|
| Paris | Generator Paris | booking.com/hotel/fr/generator-paris.html |
| Paris | Hotel de la Bretonnerie | booking.com/hotel/fr/de-la-bretonnerie.html |
| Paris | Le Pavillon de la Reine | booking.com/hotel/fr/le-pavillon-de-la-reine.html |
| Italia | Generator Rome | booking.com/hotel/it/generator-rome.html |
| Italia | Hotel Davanzati | booking.com/hotel/it/davanzati.html |
| Italia | Hotel Danieli | booking.com/hotel/it/hoteldanielivenice.html |
| Espana | Bastardo Hostel | booking.com/hotel/es/bastardo-hostel.html |
| Espana | Hotel Preciados | booking.com/hotel/es/hoprevippreciados.html |
| Espana | Mandarin Oriental Ritz | booking.com/hotel/es/ritz-madrid.html |
| Eslovenia | Hostel Celica | booking.com/hotel/si/hostel-celica.html |
| Eslovenia | Hotel Cubo | booking.com/hotel/si/cubo.html |
| Eslovenia | InterContinental Ljubljana | booking.com/hotel/si/intercontinental-ljubljana.html |
| Japon | 9h Nine Hours Shinjuku | booking.com/hotel/jp/nainawazuumanxin-su.html |
| Japon | Shinjuku Granbell Hotel | booking.com/hotel/jp/shinjuku-granbell.html |
| Japon | Park Hyatt Tokyo | booking.com/hotel/jp/park-hyatt-tokyo.html |
| Londres | Generator London | booking.com/hotel/gb/thegenerator.html |
| Londres | citizenM Tower of London | booking.com/hotel/gb/citizenm-tower-of-london-london.html |
| Londres | The Savoy | booking.com/hotel/gb/the-savoy.html |
| Noruega | HI Bergen Montana | booking.com/hotel/no/bergen-hostel-montana.html |
| Noruega | Scandic Torget Bergen | booking.com/hotel/no/scandic-torget.html |
| Noruega | Opus XVI | booking.com/hotel/no/opus-xvi.html |
| Kenia | Miti Mingi Eco Camp | booking.com/hotel/ke/miti-mingi-eco-camp-nairagie-ngare.html |
| Kenia | Sarova Mara Game Camp | booking.com/hotel/ke/sarova-mara-game-camp.html |
| Kenia | Angama Mara | angama.com/stay/angama-mara/ (no esta en Booking) |

## Verificacion
- Migracion 002 aplicada correctamente
- 24 alojamientos con booking_url en la respuesta de la API
- Campo visible en GET /api/v1/packs/{slug} dentro de cada accommodation
