# Aurora — 双界灵兔 / Twin-Realm Hare

一个给 **Terraria tModLoader 1.4.4** 的城镇 NPC mod：有点不正经的法师，能从物质领域与精神领域的交叠处"取出"东西，再把方块按一块一个铜板卖给你。

> 仓库名是 Aurora，但 **mod 内部名保持 `Starlight`**（tModLoader 用文件夹名作为内部 ID）。
> 改名会让存档里已有的 mod 引用失效，所以对外显示名（`displayName`）是 Aurora，内部 ID 不变。
> 克隆时把目录命名为 `Starlight` 即可，见下方安装步骤。

## 内容

| 内容 | 说明 |
|---|---|
| 城镇 NPC「双界灵兔 Aurora」 | 骷髅王之后、且服装商曾入住过才会搬进来 |
| 对话 | 首次见面 + 5 条常态 + 雨/血月场景 + 服装商邻居评论，中英双语 |
| 商店 | 10 种木材 + 石块 / 沙 / 雪块 / 雪砖 / 淤泥 / 泥块 / 沙漠化石，**全部 1 铜** |
| 攻击 | 魔法型，发射「月光新月」：穿透 6、每次命中炸开 70px 月光 |
| 掉落 | 死亡必掉「阿罗拉的魔杖」（玩家可用，伤害 22 / 耗魔 8） |
| 贴图 | 25 帧规范（40×56 / 帧），行走与攻击帧为手绘 |

## 安装

```bash
cd "%USERPROFILE%\Documents\My Games\Terraria\tModLoader\ModSources"
git clone https://github.com/ZenithOliver/Aurora.git Starlight
```

然后在 tModLoader 里 `Workshop → Develop Mods` 找到 `Starlight` → **Build + Reload**。

需要 **.NET 8.0 SDK**（不是运行时）。命令行编译：

```bash
dotnet build Starlight.csproj
```

## 目录

```
.
├─ build.txt / description.txt / icon.png
├─ Starlight.cs                 mod 入口
├─ Common/Systems/              世界存档标记（服装商来访）
├─ Content/
│  ├─ NPCs/Aurora.cs            对话、商店、出生条件、掉落
│  ├─ NPCs/Aurora.png           25 帧贴图
│  ├─ Projectiles/MoonCrescent  月光新月弹幕（NPC 与魔杖共用）
│  └─ Items/AuroraWand.cs       玩家的魔杖
├─ Localization/                中英双语（hjson）
├─ tools/                       贴图生成、识别、校验脚本（不参与打包）
├─ 设计说明.md                   内容设计方法论
└─ 画法指南.md                   像素画与 25 帧规范
```

## 美术与脚本

角色设计与立绘：**ZenithOliver**。像素合成、贴图管线、全部代码由本仓库的脚本生成／维护：

```bash
python tools/build_placeholder.py   # 从立绘合成 25 帧贴图
python tools/make_wand.py           # 魔杖与弹幕贴图
python tools/sheet_check.py         # 校验 25 帧规范
```

需要 Python 3 + Pillow。

## 许可

MIT，见 `LICENSE`。
