# TODO / 待办

## 已完成

- [x] **阿罗拉的魔杖**（玩家可用，她死亡时 100% 掉落）
  - `Content/Items/AuroraWand.cs`：伤害 22 / 使用时间 18 / 耗魔 8 / 击退 3 / 弹速 9.5 / 稀有度蓝 / 自动连发
  - `Content/Projectiles/AuroraWandBolt.cs`：穿透 3、命中爆炸（半径 55、50% 伤害）、白色星芒拖尾
  - 贴图：`Content/Items/AuroraWand.png`（32×32）、`Content/Projectiles/AuroraWandBolt.png`（16×16）
  - 掉落：`Aurora.cs` 的 `ModifyNPCLoot`

## 待办

- [ ] 阿罗拉专属表情气泡（`ModEmoteBubble`，需要一张 32×32 表情图）
- [ ] `PickEmote()` 差异化：对服装商冒爱心、对税收官冒愤怒
- [ ] 用真图替换占位行走帧（现在只有 2 个侧身姿势循环）
