// by Vance. Скорость себе + блинк на 5 метров
using UnityEngine;
using BepInEx.Configuration;

namespace HowToFish.SDK
{
    public class SpeedTeleport : MonoBehaviour
    {
        public static ConfigEntry<float> Sprint;
        public static ConfigEntry<KeyCode> BlinkKey;

        Player _me;

        void Update()
        {
            if (_me == null || !_me.IsOwner)
            {
                _me = null;
                foreach (var p in PlayerManager.Players)
                    if (p != null && p.IsOwner) { _me = p; break; }
                if (_me == null) return;
            }

            var mv = _me.GetComponent<PlayerMovement>();
            if (mv == null) return;

            mv._walkSpeed = MinimalPlugin.WalkSpeed.Value;
            if (Sprint != null)
                mv._sprintSpeed = Sprint.Value;

            if (BlinkKey != null && Input.GetKeyDown(BlinkKey.Value))
                _me.LocalTeleport(_me.transform.position + _me.transform.forward * 5f);
        }
    }
}
