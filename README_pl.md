# Profile zachowania i `desired`

Neuro Rooms łączy stan pokoju (`idle / occupied / night / away`), istniejące
`mode` i `modifier` pokoju oraz bieżący wybór z `select` Neuro Modes. Nie tworzy
drugich pól typu `room_mode` ani `room_modifier`.

Sensor pokoju publikuje `context`, `selected_profile` i `desired`. Profile można
edytować w opcjach integracji: **profiles**. Reguła profilu ma postać:

```json
{
  "id": "skupienie",
  "when": {"state": "occupied", "mode": "office", "modifier": "focus"},
  "desired": {"lighting": "work", "hvac": "comfort", "media": "off"}
}
```

Dopasowanie wybiera regułę o największej liczbie warunków; przy remisie wygrywa
pierwsza na liście. Domyślne profile są przykładowe i można je zastąpić.
`desired` opisuje wynik, ale integracja nie wykonuje na jego podstawie działań.

Przykładowa generyczna automatyzacja HA znajduje się w
`examples/neuro_rooms_apply_desired.yaml`. Nie zawiera ręcznej listy pokoi ani
urządzeń: wykrywa sensor Neuro Rooms, obszar HA pokoju i przypisane do niego
encje. Obsługuje oświetlenie, HVAC przez wspierane presety lub tryby grzania,
oraz wyłączenie/włączenie odtwarzaczy. Dla termostatów bez presetów przykładowa
automatyzacja mapuje `comfort` na 20°C, a `eco` i `sleep` na 18°C; te wartości są
testowe i można je zmienić w automatyzacji. `hvac: off` jest stosowane tylko
przy obsługiwanym trybie `off`.

Neuro Modes w aktualnym kodzie wystawia globalny wybór jako encję `select`.
Dlatego kontekst globalny zawiera jej bieżący stan. Nie ma osobnego, gotowego
strumienia aktywnych modyfikatorów globalnych, więc `global_modifiers` jest na
razie puste. Zmiana trybu globalnego powoduje ponowne wyliczenie wyniku.

## Urządzenia i konfiguracja pomieszczeń

Urządzenie silnika jest nadrzędne wobec urządzeń poszczególnych pomieszczeń.
Na stronie urządzenia pokoju dostępne są konfiguracyjne encje wyboru trybu i
modyfikatora; zmiana zapisuje się w konfiguracji i od razu przelicza profil.
Menu silnika służy do ustawień wspólnych oraz dodawania, wykrywania i usuwania
pokoi.
