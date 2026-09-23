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

Przykładowa jedna automatyzacja HA znajduje się w
`examples/neuro_rooms_apply_desired.yaml`. Zawiera jawne, testowe mapowanie
pokoi na encje światła. W tej wersji obsługuje jedynie `lighting`; HVAC i media
pozostają danymi wyjściowymi do późniejszego podłączenia.

Neuro Modes w aktualnym kodzie wystawia globalny wybór jako encję `select`.
Dlatego kontekst globalny zawiera jej bieżący stan. Nie ma osobnego, gotowego
strumienia aktywnych modyfikatorów globalnych, więc `global_modifiers` jest na
razie puste. Zmiana trybu globalnego powoduje ponowne wyliczenie wyniku.
