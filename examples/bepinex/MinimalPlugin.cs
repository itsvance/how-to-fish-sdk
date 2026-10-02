// by Vance. Стартовый плагин
// game 1.1.3 / Unity 6000.4.4f1 / BepInEx 5.4.23.5
using BepInEx;
using BepInEx.Configuration;
using HarmonyLib;
using UnityEngine;

namespace HowToFish.SDK
{
    [BepInPlugin("com.vance.sdk", "HowToFish SDK by Vance", "0.2.0")]
    public class MinimalPlugin : BaseUnityPlugin
    {
        internal static ConfigEntry<KeyCode> MenuKey;
        internal static ConfigEntry<float> WalkSpeed;

        void Awake()
        {
            MenuKey = Config.Bind("General", "MenuKey", KeyCode.Insert);
            WalkSpeed = Config.Bind("Movement", "WalkSpeed", 12f);

            new Harmony("com.vance.sdk").PatchAll();
            Logger.LogInfo("vance sdk loaded");
        }
    }
}
