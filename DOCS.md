# DOCS by Vance

Вся документалка по How to Fish в одном месте. Игра `1.1.3`, dll `E3EC0BEF...F84B1`, Unity `6000.4.4f1` Mono

Содержание:

- [1. Сетап](#1-сетап)
- [2. Сейвы](#2-сейвы)
- [3. Классы](#3-классы)
- [4. Сеть](#4-сеть)
- [5. BepInEx](#5-bepinex)
- [6. CE](#6-ce)
- [7. Ачивки](#7-ачивки)
- [8. Вопросы](#8-вопросы)

## 1. Сетап

- сама игра `How to Fish\How to Fish.exe`
- python 3.10+ если правишь сейвы скриптом
- CE 7.5+ если лезешь в память
- для dll: .NET SDK + BepInEx 5.4.23.5 + Harmony

Если версия другая - сначала сверь SHA

Сейвы:

```powershell
Get-ChildItem "$env:USERPROFILE\AppData\LocalLow\Dazed Games\How to Fish\Saves" -Recurse -Filter *.txt

Copy-Item "<World>.txt" "<World>.txt.mybackup"

python examples\save-editor\edit_save.py --list
python examples\save-editor\edit_save.py --world "ИмяМира" --money 999999 --heal
```

Игра закрыта, Cloud выключен. В сейве смотри `UseSteam:true` и `steam_autocloud.vdf` рядом

BepInEx:

1. Кидаешь BepInEx рядом с exe: `winhttp.dll`, `doorstop_config.ini`, папка `BepInEx/`
2. Запускаешь разок, появляются `config/`, `plugins/`
3. Собираешь:
   ```
   dotnet build examples/bepinex/HowToFish.SDK.csproj -c Release
   copy bin\Release\*.dll "E:\SteamLibrary\steamapps\common\How to Fish\How to Fish\BepInEx\plugins\"
   ```
4. Меню на `Insert`, аим на `ё`. Не нравится - поменяй в конфиге

CE:

1. Цепляешься к exe
2. Money ищешь как `4 bytes`, цифру бери из своего мира, у меня было 99247
3. Купил-продал, next scan, осталось 1-3 адреса
4. Указатель строй от `MoneyManager.Instance`, абсолюты после рестарта сдохнут
5. Хп так же, у меня было 50, сытость 21

## 2. Сейвы

Оба файла голый JSON в UTF-8, шифрования нет

Лежат в `%USERPROFILE%\AppData\LocalLow\Dazed Games\How to Fish\Saves\<SteamID>\`

- `local.txt` - личное: шмотки, скины, бестиарий
- `<WorldName>.txt` - мир: бабки, игроки, шмотки на земле. Имя файла = имя мира. С кириллицей в проводнике бывает `??????.txt`, реальное имя через `dir /x` или скриптом
- рядом `*.backup` и `steam_autocloud.vdf`

local.txt:

```jsonc
{
  "UnlockedItemSkins": [],
  "UnlockedBoatSkins": [],
  "CreaturesToList": []
  // Hat, Outfit, Accessory - внешность
  // CreaturesToList: [{ ID, BeenKilled, KilledDrip }]
}
```

Скины открываются допиской id в `UnlockedItemSkins`, бестиарий через `BeenKilled=true, KilledDrip=true`. В коде `SaveManager.UnlockSkin`, `PlayerSkin.SetServerColors`

Мир, ServerSaveObject:

```jsonc
{
  "Name": "ИмяМира",
  "Money": 99247,
  "Euro": 0,
  "Difficulty": 0,
  "MaxIsland": 0,
  "UseSteam": true,
  "Players": [
    {
      "SteamID": 7656...,
      "Health": 50,
      "Fullness": 21,
      "HeldItem": { "Exists": false },
      "InventoryItems": [],
      "OwnedBaits": [],
      "ExtraSlots": 0
    }
  ],
  "WorldItems": []
}
```

`ItemID` у меня были `63/66/61/68/43`, 43 с `IsDeadCreature:true` это туша

Поля шмотки: `Exists, InventorySlot, ItemID, Cookness, BettingMultiplier, Weight, KillScoreMultiplier, IsDripCreature, SkinIndex, Sharpness, Quiver, Sight, BarrelAttachment, AmmoType, ExtendedMag, LaserSight`

В коде: `SaveManager.SaveServer/LoadAllServers`, `SaveWorldItems/LoadWorldItems`

Как правлю:

1. Закрываю игру
2. Копирую мир в `.bak`
3. Открываю как UTF-8
4. Меняю числа, сохраняю, запускаю. Откатило - вырубаю Cloud и по новой

Скрипт `examples/save-editor/edit_save.py` делает то же самое

## 3. Классы

Вытащил из `Assembly-CSharp.dll`, там 426 типов в глобале. Оставил нужное, остальное через `tools/dump_types.py`

MoneyManager:

```csharp
static class MoneyManager {
  static int Money; static int Euro;          // у меня было 99247/0
  static int _money, _euro, _cheatMoney, _cheatEuro;
  static MoneyManager Instance;
  static void AddMoney(int n);
  static void RemoveMoney(int n);
  static bool CanAfford(int n);
}
```

Хост вызывает `AddMoney` напрямую, гостю только CE заморозка

Хил и годмод:

```csharp
class PlayerVitals {
  int _syncedHealth, _syncedFullness;
  int _localHp; bool _localIsDead;
  void TakeDamage(int n);
  void LocalHit(int n);
  void Heal(int n);
  void ServerResetVitals();
}
static class PlayerManager {
  static List<Player> Players, AlivePlayers, OtherPlayers;
  static bool InGodMode;
  static void ToggleGodMode();
}
```

Пример в `GodMode.cs`

Инвентарь:

```csharp
class PlayerInventory {
  void PutItemInInventory(SavedItem it);
  void SpawnNewItem(int itemId);
  void DespawnItemOnServer(...);
}
// чужой лут сервер отбивает через TargetReconcileRejectedItemPickup
```

Мобы, урон, аим:

```csharp
class Creature {
  int _hp, _maxHp;
  int _localHp; bool _localIsDead;
  void LocalHit(int dmg);
  void ServerChangeHp(int n);
  void OnDeath();
}
class PlayerAimAssist {
  Player FindBestTarget();
  float _maxTargetDistance;
}
```

Конфиг образца `com.howtofish.cheat.cfg`, там `[Aimbot] MaxDistance/SmoothSpeed`, `[ESP] MaxDistance`

Движение:

```csharp
class PlayerMovement {
  float _walkSpeed, _sprintSpeed, _jumpForce;
}
class Player {
  void LocalTeleport(Vector3 pos);
  void TeleportPlayer(Vector3 pos);
  void RPCTeleport(Vector3 pos);
}
class OtherPlayer {
  void SetReceivedPosRot(Vector3 p, Quaternion r);
}
```

Баннихоп в cfg на `Space`, пример в `SpeedTeleport.cs`

Мир, магаз, финал - только хост: `SaveManager.CurServerSave`, `SaveServer/LoadAllServers`, `IslandSpawner.TpToNextIsland`, `SendFinishGame`, `EruptVolcano`, `PlaceBet`, `BuyItem`

Консоль разрабов: `DazedCommands`, гейт `IsServerCommand() => true`, команды `AddMoney/RemoveMoney/GodMode/OneShot/Spawn/Give/KillBoss/NextIsland/FinishGame/UnlockAllSkins`. Токены строчными: `addmoney`, `removemoney`, `unlockachievements`

Какой клавишей открывается - не нашел, в строках только токены. Найдешь - кидай в issues

Ачивки: `AchievementManager.UnlockAchievement("A01")`, всего `A01..A31`. Пример в `AchievementUnlocker.cs`

Копаешь сам:

```powershell
python tools/dump_types.py --dll "E:\...\Assembly-CSharp.dll" --grep "Money|Teleport|Achiev"
# в CE нашел Money, жми Find what accesses
# в Player.log ищи Harmony patches applied successfully
```

## 4. Сеть

FishNet через стим-лобби, отдельного сервера нет, только `How to Fish.exe`. Кто создал лобби тот и сервер

- хост - у него мир, бабки, мобы, лут, острова, магаз, финал
- гость - ему шлют снапшоты, он шлет запросы

Хост или нет: смотри `IsServerInitialized`. True - хост, false - гость

В коде 111 штук `RpcLogic___*`:

- `ServerRpc` просишь: `SendFinishGame`, `TeleportPlayer`, `BuyItem`, `SetDriver`
- `ObserversRpc` хост раздает: `ObserverAddProjectile`, `ObserverHit`, `ObserverMoneySound`
- `TargetRpc` в одного: `RPCTeleport`, `RPCKnockback`
- отказы: `TargetReconcileRejectedItemPickup`, `Player spawn rejected`

| Хочу | Гость | Хост |
|---|---|---|
| Бабки через CE | видно только у себя | да |
| `AddMoney` вызовом | нет | да |
| Годмод себе | да | да |
| Скорость / блинк себе | да | да |
| ESP / аим | да | да |
| Спавн / магаз всем | нет | да |
| Телепорт другого | нет | да |
| Острова / финал / вулкан / рулетка | нет | да |
| Ачивки себе | да | да |
| Скины себе | да, через local.txt | да |

Хочешь рулить миром - хости сам

## 5. BepInEx

BepInEx 5.4.23.5 + Doorstop, Harmony цепляет `Creature.LocalHit`

Проект: `.NET Framework 4.7.2`, x64. Референсы: `Assembly-CSharp.dll`, `BepInEx.dll`, `0Harmony.dll`, `UnityEngine.dll`. Старт с `MinimalPlugin.cs`

Кусочки:

```csharp
// годмод
[HarmonyPatch(typeof(PlayerVitals), "TakeDamage")]
class GodPatch {
  static bool Prefix(PlayerVitals __instance) {
    if (__instance.GetComponent<Player>()?.IsOwner == true) return false;
    return true;
  }
}

// ваншот 9999
[HarmonyPatch(typeof(Creature), "LocalHit")]
class OneShot {
  static void Prefix(ref int damage) { damage = 9999; }
}

// скорость
void Update() {
  var me = PlayerManager.Players?.FirstOrDefault(p => p.IsOwner);
  if (me != null)
    me.GetComponent<PlayerMovement>()._walkSpeed = 12f;
}

// ESP
foreach (var op in PlayerManager.OtherPlayers)
  DrawBox(Camera.main.WorldToScreenPoint(op.transform.position));
```

Логи: `BepInEx/LogOutput.log` и `Player.log`, ищи `Harmony patches applied successfully`

Конфиг:

```csharp
MenuKey = Config.Bind("General", "MenuKey", KeyCode.Insert);
AimKey = Config.Bind("Aimbot", "AimbotKey", KeyCode.BackQuote);
```

Правится при закрытой игре: `BepInEx/config/com.howtofish.cheat.cfg`

Ошибки:

- `MissingMethodException` - игра обновилась, сверь SHA `E3EC0BEF...F84B1`
- Патч молчит - опечатка в имени или перегрузка, лечится `[HarmonyPatch(typeof(X), "M", new Type[]{typeof(int)})]`
- Краш в сетке - вызвал серверный метод гостем, проверяй `IsServerInitialized`

## 6. CE

Цепляемся к `How to Fish.exe`, mono-модуль `mono-2.0-bdwgc.dll`. Включи `Mono -> Activate mono features`

Бабки:

1. Attach, тип `4 Bytes`, exact
2. Цифру бери из своего мира, у меня было 99247
3. Купил-продал, next scan, осталось 1-3 адреса
4. Указатель: `Mono -> Assembly-CSharp -> MoneyManager -> Instance -> _money`
5. `Find what accesses` покажет `AddMoney/RemoveMoney/OnChangeMoney`

Евро так же, сначала заработай хоть 1

ХП: у меня было `Health=50`, `Fullness=21`. Сканишь exact int, получаешь урон, жмешь next scan. Методы `TakeDamage/Heal/LocalHit`, поля `_localHp`. Годмод в CE - брейк на `TakeDamage` и NOP, либо заморозь `_localHp`. Гостем это визуал

Скорость: `PlayerMovement._walkSpeed` это float. Сканишь float, вкл/выкл спринт через Changed/Unchanged. Сохрани в `.CT`, пример в `examples/cheat-engine/HowToFish.CT`

Ачивки не сканируй. Дергай метод через mono invoker или правь `local.txt`

Напоминалка:

- Все классы в `Assembly-CSharp.dll`, имена выше
- Абсолюты после рестарта дохнут, храни указатели

## 7. Ачивки, 31 штука

`A01_FirstCreature .. A31_MoneyInABottle`. Менеджер `AchievementManager.UnlockAchievement`, плюс стим `SetAchievement/StoreStats`

- `A01` - первая рыба
- `A02..A30` - середина: бестиарий, острова, гриль, лодка, рулетка, босс. Точные условия смотри в `ObserverFastBossAchievement`
- `A31_MoneyInABottle` - бутылка с бабками

Где смотреть список:

```powershell
python tools/dump_types.py --grep Achievement
# или строки A01..A31 в dll
```

Как открываю, код в `examples/bepinex/AchievementUnlocker.cs`:

```csharp
for (int i = 1; i <= 31; i++)
  AchievementManager.Instance.UnlockAchievement($"A{i:00}");
```

Либо консоль хоста `unlockachievements`

Стим ставит всем 31 один таймстамп, это палится. Тести на втором акке

## 8. Вопросы

**Надо ставить IDA?**
Нет. Все нужное выше + примеры

**Тут есть античит?**
Не нашел. Риск только кик и клауд

**Почему правка бабок не видна всем?**
Ты гость, мир у хоста. Хочешь чтобы видели все - хости сам

**Сейв откатило, что делать?**
Выруби Cloud, правь на закрытой игре, бэкап держи. В сейве `UseSteam:true` это метка клауда

**Где кнопка консоли addmoney?**
Не нашел. Токены есть, гейт на хоста есть, кнопки нет. Найдешь - кидай в issues

**ESP только хосту?**
Нет, всем. Позиции всем летят через `OtherPlayer.SetReceivedPosRot`

**Других телепортить можно?**
Хосту да, гостю нет. Себя - всем через `LocalTeleport`

**Адреса слетают?**
Да, после рестарта. Строй указатели от `MoneyManager.Instance`

**Игра обновилась, все сломалось?**
1. Сверь SHA с `E3EC0BEF...F84B1` (это 1.1.3)
2. Прогони `dump_types.py` и сравни с разделом 3

by Vance
