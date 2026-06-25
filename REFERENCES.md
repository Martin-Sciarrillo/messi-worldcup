# 📚 Referencias y atribución

Este experimento es **no comercial y educativo** (data-viz / R&D). Todos los datos e
imágenes pertenecen a sus respectivos dueños y se usan con fines de comentario y análisis.

## 📊 Datos de partidos

- **FBref — Sports Reference LLC.** Estadísticas de Copa del Mundo por edición (1966–2022).
  - Fuente: `https://fbref.com/en/comps/1/{año}/stats/{año}-World-Cup-Stats`
  - Scrapeado con `fetch_fbref.py`, parseado a `worldcup_all.csv` con `build_data.py`.
- **Mundial 2026 (en curso):** los minutos/goles/asistencias se sumaron **a mano** desde
  prensa deportiva, porque FBref aún no publica la edición. Están marcados en el código
  (bloque `WC2026`) y en toda la comunicación como **datos parciales / provisionales**.

## 📷 Retratos de jugadores

Descargados con `fetch_photos.py` vía la API REST de Wikipedia (imagen principal del
artículo). Cada imagen está bajo su **propia licencia** en Wikimedia Commons y pertenece a
su autor/a original. No se versionan en este repo (ver `.gitignore`); se regeneran con el
script. Artículos fuente:

| Jugador | Artículo de Wikipedia |
|---------|-----------------------|
| Lionel Messi | https://en.wikipedia.org/wiki/Lionel_Messi |
| Cristiano Ronaldo | https://en.wikipedia.org/wiki/Cristiano_Ronaldo |
| Kylian Mbappé | https://en.wikipedia.org/wiki/Kylian_Mbappé |
| Pelé | https://en.wikipedia.org/wiki/Pelé |
| Diego Maradona | https://en.wikipedia.org/wiki/Diego_Maradona |
| Miroslav Klose | https://en.wikipedia.org/wiki/Miroslav_Klose |
| Ronaldo (R9) | https://en.wikipedia.org/wiki/Ronaldo_(Brazilian_footballer) |
| Gerd Müller | https://en.wikipedia.org/wiki/Gerd_Müller |
| Just Fontaine | https://en.wikipedia.org/wiki/Just_Fontaine |
| Sándor Kocsis | https://en.wikipedia.org/wiki/Sándor_Kocsis |
| Gabriel Batistuta | https://en.wikipedia.org/wiki/Gabriel_Batistuta |
| Ivan Perišić | https://en.wikipedia.org/wiki/Ivan_Perišić |
| Klaas-Jan Huntelaar | https://en.wikipedia.org/wiki/Klaas-Jan_Huntelaar |

## 🏴 Banderas

Banderas nacionales circulares en `flags/` (ar, br, de, fr, hr, hu, nl, pt). Insignias
nacionales — generalmente **dominio público** / Wikimedia Commons.

## 🔢 Leyendas pre-Opta (nota metodológica)

Para Kocsis (1954), Fontaine (1958) y Pelé (1958–70), las **asistencias no se registraban**
de forma confiable en su era. Sus puntos usan un ratio **solo-goles** y se grafican aparte
(diamantes dorados), para no comparar peras con manzanas contra los datos modernos de G+A.

| Leyenda | Minutos | Goles | Ratio (solo-G/90) | Edición |
|---------|--------:|------:|------------------:|---------|
| Just Fontaine | 540 | 13 | 2.17 | 1958 🇫🇷 (récord de un torneo) |
| Sándor Kocsis | 450 | 11 | 2.20 | 1954 🇭🇺 |
| Pelé | 1215 | 12 | 0.89 | 1958–70 🇧🇷 (3 títulos) |

## ⚖️ Licencia

El **código** de este repo está bajo licencia MIT (`LICENSE`). Los datos, fotos y banderas
**no** están cubiertos por esa licencia y permanecen bajo los términos de sus fuentes.
