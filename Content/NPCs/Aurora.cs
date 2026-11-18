using System.Collections.Generic;
using Terraria;
using Terraria.GameContent.Bestiary;
using Terraria.GameContent.ItemDropRules;
using Terraria.GameContent.Personalities;
using Terraria.ID;
using Terraria.Localization;
using Terraria.ModLoader;
using Terraria.ModLoader.IO;
using Terraria.Utilities;
using Starlight.Common.Systems;
using Starlight.Content.Projectiles;
using Starlight.Content.Items;

namespace Starlight.Content.NPCs
{
	// 阿罗拉：有点不正经的法师，用法术变出方块跟玩家交易。
	[AutoloadHead]
	public class Aurora : ModNPC
	{
		public const string ShopName = "Shop";

		private int timesTalked;

		public override LocalizedText DeathMessage => this.GetLocalization("DeathMessage");

		public override void SetStaticDefaults() {
			// 25 帧：0 站 / 1 跳 / 2-15 走 / 16-17 抬手 / 18 坐 / 19 说话 / 20 眨眼 / 21-24 攻击
			Main.npcFrameCount[Type] = 25;

			NPCID.Sets.ExtraFramesCount[Type] = 9;
			NPCID.Sets.AttackFrameCount[Type] = 2;    // 魔法型只用 2 帧
			NPCID.Sets.DangerDetectRange[Type] = 600;
			NPCID.Sets.AttackType[Type] = 2;          // 2 = 魔法
			NPCID.Sets.AttackTime[Type] = 40;
			NPCID.Sets.AttackAverageChance[Type] = 20;// 比一般人更爱出手
			NPCID.Sets.HatOffsetY[Type] = 2;

			// 喜欢的群系：雪原（爱）、森林（喜欢）；讨厌：丛林、海洋；蘑菇地（恨）
			NPC.Happiness
				.SetBiomeAffection<SnowBiome>(AffectionLevel.Love)
				.SetBiomeAffection<ForestBiome>(AffectionLevel.Like)
				.SetBiomeAffection<JungleBiome>(AffectionLevel.Dislike)
				.SetBiomeAffection<OceanBiome>(AffectionLevel.Dislike)
				.SetBiomeAffection<MushroomBiome>(AffectionLevel.Hate)
				.SetNPCAffection(NPCID.Clothier, AffectionLevel.Love)
				.SetNPCAffection(NPCID.Wizard, AffectionLevel.Like)
				.SetNPCAffection(NPCID.Guide, AffectionLevel.Like)
				.SetNPCAffection(NPCID.TaxCollector, AffectionLevel.Hate);
		}

		public override void SetDefaults() {
			NPC.townNPC = true;
			NPC.friendly = true;
			NPC.width = 18;
			NPC.height = 40;
			NPC.aiStyle = NPCAIStyleID.Passive;
			NPC.damage = 12;
			NPC.defense = 15;
			NPC.lifeMax = 250;
			NPC.HitSound = SoundID.NPCHit1;
			NPC.DeathSound = SoundID.NPCDeath1;
			NPC.knockBackResist = 0.5f;

			AnimationType = NPCID.Guide;
		}

		public override bool CanTownNPCSpawn(int numTownNPCs) {
			// 骷髅王之后，且服装商曾经入住过（见过他就算，之后他搬走也不影响）
			return Terraria.NPC.downedBoss3 && ClothierHousedSystem.ClothierHasMovedIn;
		}

		public override List<string> SetNPCNameList() {
			return new List<string> { "Aurora" };
		}

		public override void SetBestiary(BestiaryDatabase database, BestiaryEntry bestiaryEntry) {
			bestiaryEntry.Info.AddRange(new IBestiaryInfoElement[] {
				BestiaryDatabaseNPCsPopulator.CommonTags.SpawnConditions.Biomes.Surface,
				new FlavorTextBestiaryInfoElement("Mods.Starlight.NPCs.Aurora.Bestiary")
			});
		}

		public override string GetChat() {
			WeightedRandom<string> chat = new WeightedRandom<string>();

			// 场景台词：下雨 / 血月（灵物暴走）
			if (Main.raining || Main.bloodMoon)
				chat.Add(Language.GetTextValue("Mods.Starlight.NPCs.Aurora.Dialogue.WeirdWeather"), 3.0);

			// 邻居台词：服装商在场
			int clothier = NPC.FindFirstNPC(NPCID.Clothier);
			if (clothier >= 0 && Main.rand.NextBool(3)) {
				chat.Add(Language.GetTextValue("Mods.Starlight.NPCs.Aurora.Dialogue.AboutClothier",
					Main.npc[clothier].GivenName), 1.5);
			}

			chat.Add(Language.GetTextValue("Mods.Starlight.NPCs.Aurora.Dialogue.Standard1"));
			chat.Add(Language.GetTextValue("Mods.Starlight.NPCs.Aurora.Dialogue.Standard2"));
			chat.Add(Language.GetTextValue("Mods.Starlight.NPCs.Aurora.Dialogue.Standard3"));
			chat.Add(Language.GetTextValue("Mods.Starlight.NPCs.Aurora.Dialogue.Standard4"));
			chat.Add(Language.GetTextValue("Mods.Starlight.NPCs.Aurora.Dialogue.Standard5"));

			timesTalked++;
			if (timesTalked == 1)
				chat.Add(Language.GetTextValue("Mods.Starlight.NPCs.Aurora.Dialogue.FirstMeeting"), 10.0);

			return chat;
		}

		public override void SetChatButtons(ref string button, ref string button2) {
			button = Language.GetTextValue("LegacyInterface.28"); // 原版“商店”
		}

		public override void OnChatButtonClicked(bool firstButton, ref string shop) {
			if (firstButton)
				shop = ShopName;
		}

		public override void AddShops() {
			var shop = new NPCShop(Type, ShopName);

			// 全部木材（含 1.4.4 的灰烬木）
			int[] woods = {
				ItemID.Wood, ItemID.BorealWood, ItemID.RichMahogany, ItemID.Ebonwood,
				ItemID.Shadewood, ItemID.Pearlwood, ItemID.DynastyWood, ItemID.PalmWood,
				ItemID.SpookyWood, ItemID.AshWood
			};
			foreach (int wood in woods)
				shop.Add(new Item(wood) { shopCustomPrice = Item.buyPrice(copper: 1) });

			// 基础建材
			shop.Add(new Item(ItemID.StoneBlock) { shopCustomPrice = Item.buyPrice(copper: 1) });
			shop.Add(new Item(ItemID.SandBlock) { shopCustomPrice = Item.buyPrice(copper: 1) });
			shop.Add(new Item(ItemID.SnowBlock) { shopCustomPrice = Item.buyPrice(copper: 1) });
			shop.Add(new Item(ItemID.SnowBrick) { shopCustomPrice = Item.buyPrice(copper: 1) });
			shop.Add(new Item(ItemID.SiltBlock) { shopCustomPrice = Item.buyPrice(copper: 1) });
			shop.Add(new Item(ItemID.MudBlock) { shopCustomPrice = Item.buyPrice(copper: 1) });
			shop.Add(new Item(ItemID.DesertFossil) { shopCustomPrice = Item.buyPrice(copper: 1) });

			shop.Register();
		}

		// ---- 战斗：一根魔杖，甩出纯白亮光弹，可穿透、可群伤 ----

		public override void TownNPCAttackStrength(ref int damage, ref float knockback) {
			// 因为弹幕每次命中都会炸一次，单体伤害从 15 降到 10 来平衡
			damage = 10;
			knockback = 3f;
		}

		public override void TownNPCAttackCooldown(ref int cooldown, ref int randExtraCooldown) {
			cooldown = 50;
			randExtraCooldown = 30;
		}

		public override void TownNPCAttackProj(ref int projType, ref int attackDelay) {
			projType = ModContent.ProjectileType<MoonCrescent>();
			attackDelay = 12;
		}

		public override void TownNPCAttackProjSpeed(ref float multiplier, ref float gravityCorrection, ref float randomOffset) {
			multiplier = 9f;
			randomOffset = 1f;
		}

		public override void TownNPCAttackMagic(ref float auraLightMultiplier) {
			auraLightMultiplier = 0.8f;
		}

		// 她死后必掉「阿罗拉的魔杖」（玩家可用版本）
		public override void ModifyNPCLoot(NPCLoot npcLoot) {
			npcLoot.Add(ItemDropRule.Common(ModContent.ItemType<AuroraWand>(), 1));
		}

		// ---- 存档 ----

		public override void SaveData(TagCompound tag) {
			tag["timesTalked"] = timesTalked;
		}

		public override void LoadData(TagCompound tag) {
			timesTalked = tag.GetInt("timesTalked");
		}
	}
}
