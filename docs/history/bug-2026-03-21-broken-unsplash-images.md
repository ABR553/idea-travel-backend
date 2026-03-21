# Bug: Imagenes Unsplash rotas (404) en seed y BD

- **Fecha**: 2026-03-21
- **Tipo**: datos/seed
- **Reportado como**: imagenes de Roma, Florencia, Venecia, Costa Amalfitana siguen rotas

## Causa raiz
14 URLs de imagenes de Unsplash en `app/seeds/seed_data.py` devolvian 404 porque las fotos fueron eliminadas o movidas en Unsplash. Las imagenes rotas afectaban destinos, experiencias, productos y covers de packs.

## Imagenes reemplazadas

| Contexto | ID roto | ID nuevo |
|---|---|---|
| Cover Fiordos Noruegos | photo-1508943723464-9ce9a30de2f4 | photo-1638140020886-587476d1e6d9 |
| Cover Londres | photo-1513635269975-59855b1a1d38 | photo-1522358461163-fcc21d170a26 |
| Cover Ruta Italia | photo-1515542622106-078bda359ba1 | photo-1607027187704-5ee3f9bc8854 |
| Costa Amalfitana | photo-1533606688076-b6683a1c9c10 | photo-1558629173-2b20b2a72ef3 |
| Stavanger | photo-1535083783855-aaab6e994a56 | photo-1554844428-1c9b6199f1be |
| Florencia | photo-1541370976299-4d24be63db28 | photo-1640077433514-8bb81960846b |
| Exp Torre Eiffel | photo-1543349689-9a4d426bee8e | photo-1570097703229-b195d6dd291f |
| Plitvice | photo-1555990538-1a0849cae100 | photo-1598384545086-62262b88111f |
| Dubrovnik | photo-1555990538-70a4e3040b8c | photo-1515679523025-8d02a8dd20ed |
| Adaptador enchufe | photo-1558618666-fcd25c85f82e | photo-1625465588028-458f59e19ee6 |
| Exp Coliseo Roma | photo-1568797629192-789acf8e4df3 | photo-1626435001540-5ab7bdb97254 |
| Ljubljana | photo-1569347204803-972aa3e72e46 | photo-1568497092899-a4c3e9af9d4c |
| Lake Bled / Cover Eslovenia | photo-1583425423320-1a5ef1f05be6 | photo-1600983918330-01182b1372d6 |
| Producto Kindle | photo-1594980596870-8aa52a78d8a4 | photo-1532104041590-1046d1a28c64 |

## Archivos modificados
- `app/seeds/seed_data.py` - Reemplazadas 14 URLs de imagenes Unsplash rotas (404) por nuevas verificadas (200)

## Solucion aplicada
1. Se extrajeron todas las URLs unicas de Unsplash del seed
2. Se verificaron con curl (HTTP status code)
3. Se buscaron reemplazos tematicos via la API interna de Unsplash
4. Se verificaron los reemplazos (todos 200)
5. Se limpio la BD y se re-ejecuto el seed
6. Se verifico la API (`/api/v1/packs` y `/api/v1/packs/ruta-por-italia`) - todas las imagenes 200

## Verificacion
- `curl` a cada imagen unica del seed: 0 rotas
- `curl` a cada imagen en la BD: 0 rotas
- API endpoint `/api/v1/packs`: todas las imagenes responden 200
- API endpoint `/api/v1/packs/ruta-por-italia` (detalle con alojamientos y experiencias): todas 200
