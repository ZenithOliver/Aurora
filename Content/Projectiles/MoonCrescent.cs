using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Terraria;
using Terraria.DataStructures;
using Terraria.GameContent;
using Terraria.ID;
using Terraria.ModLoader;

namespace Starlight.Content.Projectiles
{
	// 阿罗拉的攻击弹幕：月光新月。穿透多个目标，每次命中炸开一片月光。
	public class MoonCrescent : ModProjectile
	{
		public override void SetStaticDefaults() {
			ProjectileID.Sets.TrailCacheLength[Type] = 8;
			ProjectileID.Sets.TrailingMode[Type] = 2;
		}

		public override void SetDefaults() {
			Projectile.width = 22;
			Projectile.height = 22;
			Projectile.friendly = true;
			Projectile.hostile = false;
			Projectile.tileCollide = false;
			Projectile.ignoreWater = true;
			Projectile.penetrate = 6;
			Projectile.timeLeft = 90;
			Projectile.DamageType = DamageClass.Magic;

			Projectile.usesLocalNPCImmunity = true;
			Projectile.localNPCHitCooldown = 12;
		}

		// 玩家版（ai[0] == 1）：穿透和爆炸范围都降一档
		public override void OnSpawn(IEntitySource source) {
			if (Projectile.ai[0] == 1f)
				Projectile.penetrate = 3;
		}

		public override void AI() {
			// 月光是淡紫色，不是纯白
			Lighting.AddLight(Projectile.Center, 0.95f, 0.88f, 1.15f);

			// 月牙的开口朝右，直接对齐飞行方向
			Projectile.rotation = Projectile.velocity.ToRotation();

			// 缓慢自转，让轨迹有点"飘"的感觉
			Projectile.rotation += MathHelper.ToRadians(4f);

			if (Main.rand.NextBool(3)) {
				Dust dust = Dust.NewDustPerfect(
					Projectile.Center + Main.rand.NextVector2Circular(8f, 8f),
					DustID.GemDiamond, Vector2.Zero, 0, new Color(226, 212, 250), 0.85f);
				dust.noGravity = true;
				dust.velocity *= 0.15f;
			}
		}

		public override bool PreDraw(ref Color lightColor) {
			Texture2D texture = TextureAssets.Projectile[Type].Value;
			Vector2 origin = new Vector2(texture.Width, texture.Height) / 2f;

			for (int i = 1; i < Projectile.oldPos.Length; i++) {
				if (Projectile.oldPos[i] == Vector2.Zero)
					continue;

				float fade = (1f - i / (float)Projectile.oldPos.Length) * 0.5f;
				Main.EntitySpriteDraw(texture,
					Projectile.oldPos[i] + Projectile.Size / 2f - Main.screenPosition,
					null, new Color(226, 212, 250) * fade, Projectile.rotation, origin,
					Projectile.scale * (1f - i * 0.06f), SpriteEffects.None, 0);
			}

			return true;
		}

		public override void OnHitNPC(NPC target, NPC.HitInfo hit, int damageDone) {
			Explode(target.Center, target.whoAmI);
		}

		public override void OnKill(int timeLeft) {
			Explode(Projectile.Center, -1);
		}

		private void Explode(Vector2 center, int ignoreNpcIndex) {
			for (int i = 0; i < 18; i++) {
				Vector2 speed = Main.rand.NextVector2Circular(5f, 5f);
				Dust dust = Dust.NewDustPerfect(center, DustID.GemDiamond,
					speed, 0, new Color(232, 220, 252), 1.25f);
				dust.noGravity = true;
			}
			Lighting.AddLight(center, 1.1f, 1.05f, 1.35f);

			if (Projectile.owner != Main.myPlayer)
				return;

			float radius = Projectile.ai[0] == 1f ? 55f : 70f;
			int explosionDamage = (int)(Projectile.damage * 0.5f);
			if (explosionDamage < 1)
				explosionDamage = 1;

			for (int i = 0; i < Main.maxNPCs; i++) {
				if (i == ignoreNpcIndex)
					continue;

				NPC npc = Main.npc[i];
				if (!npc.active || npc.friendly || npc.dontTakeDamage)
					continue;
				if (Vector2.Distance(npc.Center, center) > radius + npc.width * 0.5f)
					continue;

				int direction = npc.Center.X > center.X ? 1 : -1;
				npc.SimpleStrikeNPC(explosionDamage, direction, false, 2f);
			}
		}
	}
}
