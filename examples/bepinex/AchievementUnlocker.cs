// by Vance. Открывает все 31 ачивку A01..A31
// на основе не гоняй, тести на втором акке
namespace HowToFish.SDK
{
    public static class AchievementUnlocker
    {
        public static void UnlockAll()
        {
            var mgr = AchievementManager.Instance;
            if (mgr == null) return;

            for (int i = 1; i <= 31; i++)
            {
                try { mgr.UnlockAchievement($"A{i:00}"); } catch { }
            }
        }
    }
}
