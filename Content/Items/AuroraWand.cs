using Microsoft.Xna.Framework;
using Terraria;
using Terraria.DataStructures;
using Terraria.ID;
using Terraria.ModLoader;
using Starlight.Content.Projectiles;

namespace Starlight.Content.Items
{
	// 阿罗拉死后掉落的魔杖。和她的攻击同款月光新月，但威力低一档。
	public class AuroraWand : ModItem
	{
		public override void SetDefaults() {
			Item.width = 32;
			Item.height = 32;
			Item.useStyle = ItemUseStyleID.Shoot;
			Item.useTime = 18;
			Item.useAnimation = 18;
			Item.autoReuse = true;
			Item.noMelee = true;

			Item.DamageType = DamageClass.Magic;
			Item.damage = 22;
			Item.knockBack = 3f;
			Item.mana = 8;
			Item.shoot = ModContent.ProjectileType<MoonCrescent>();
			Item.shootSpeed = 9.5f;

			Item.value = Item.sellPrice(gold: 2);
			Item.rare = ItemRarityID.Blue;
			Item.UseSound = SoundID.Item43;
		}

		// 玩家版：用 ai[0] = 1 告诉弹幕"我是玩家用的"，它会把穿透和爆炸范围调低
		public override bool Shoot(Player player, EntitySource_ItemUse_WithAmmo source,
			Vector2 position, Vector2 velocity, int type, int damage, float knockback) {
			Projectile.NewProjectile(source, position, velocity, type, damage, knockback,
				player.whoAmI, 1f);
			return false;
		}
	}
}
