# how-to-fish-sdk by Vance

[![game 1.1.3](https://img.shields.io/badge/game-1.1.3-blue)](https://store.steampowered.com/app/4001890/)
[![unity](https://img.shields.io/badge/unity-6000.4.4f1-black)](https://unity.com)
[![bepinex](https://img.shields.io/badge/BepInEx-5.4.23.5-green)](https://github.com/BepInEx/BepInEx)
[![by Vance](https://img.shields.io/badge/by-Vance-orange)](https://github.com/itsvance)

Привет, я Vance. Все по How to Fish в двух файлах: тут коротко, в [DOCS.md](DOCS.md) подробно

Сижу на: Steam `4001890`, игра `1.1.3`, dll `E3EC0BEF...F84B1`, Unity `6000.4.4f1` Mono. Античита нет, сеть FishNet через стим-лобби, кто создал лобби тот и хост

```
DOCS.md               - вся документалка
examples/save-editor  - правка сейвов питоном
examples/bepinex      - плагины, Harmony
examples/cheat-engine - табличка .CT
tools/                - дампер типов
```

```powershell
# глянуть миры
python examples\save-editor\edit_save.py --list

# насыпать денег и отхилиться, игра закрыта
python examples\save-editor\edit_save.py --world "MyWorld" --money 999999 --heal

# собрать плагин
dotnet build examples\bepinex\HowToFish.SDK.csproj -c Release
# dll в BepInEx\plugins\, меню на Insert
```

CE: Money и HP это `4 Bytes`, число из своего `<World>.txt`, у меня было `Money=99247`, `HP=50`

Хост или гость:

- соло или ты хост - можно все
- чужое лобби - только себя: хил, скорость, ESP, скины

Детали в [DOCS.md](DOCS.md). Нашел новое - кидай PR, только SHA dll сверяй

by Vance, тг - @vance_hub
