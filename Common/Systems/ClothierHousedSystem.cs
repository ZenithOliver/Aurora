using Terraria;
using Terraria.ID;
using Terraria.ModLoader;
using Terraria.ModLoader.IO;

namespace Starlight.Common.Systems
{
	// NPC 只能查“现在在不在”，查不到“以前来过没有”。
	// 所以用一个世界存档里的 bool 记住：服装商是否曾经入住过。
	public class ClothierHousedSystem : ModSystem
	{
		public static bool ClothierHasMovedIn { get; private set; }

		public override void PostUpdateEverything() {
			if (!ClothierHasMovedIn && NPC.AnyNPCs(NPCID.Clothier))
				ClothierHasMovedIn = true;
		}

		public override void SaveWorldData(TagCompound tag) {
			if (ClothierHasMovedIn)
				tag["clothierHoused"] = true;
		}

		public override void LoadWorldData(TagCompound tag) {
			ClothierHasMovedIn = tag.GetBool("clothierHoused");
		}
	}
}
