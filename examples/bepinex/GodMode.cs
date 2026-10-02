// by Vance. Годмод через TakeDamage
// в соло и на своем хосте работает, гостем сервер может перетереть
using HarmonyLib;

namespace HowToFish.SDK
{
    [HarmonyPatch(typeof(PlayerVitals), "TakeDamage")]
    static class GodMode
    {
        static bool Prefix() => false;
    }
}
