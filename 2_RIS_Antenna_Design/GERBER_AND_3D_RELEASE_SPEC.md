# Gerber 与 3D 模型发布规范

> **本文档定义 PCB 可制造文件的导出格式、命名规范与发布前检查清单。**
> 真实 Gerber / 3D 文件需在完成 KiCad（或等效 EDA）布局布线后导出，
> 仓库中的 `gerber/` 与 `3d/` 目录按本规范归档对应版本。

---

## 1. 文件命名规范

统一采用 Protel 风格后缀命名（各家板厂通用），文件置于 `gerber/` 目录：

| 文件 | 名称 | 层说明 |
|-----|------|--------|
| 顶层铜 | `PLFM-RIS.GTL` | Top Copper (Layer 1) |
| 内层 1 | `PLFM-RIS.G1` | Inner Layer 1 (Layer 2, GND) |
| 内层 2 | `PLFM-RIS.G2` | Inner Layer 2 (Layer 3, DC) |
| 内层 3 | `PLFM-RIS.G3` | Inner Layer 3 (Layer 4, DC) |
| 内层 4 | `PLFM-RIS.G4` | Inner Layer 4 (Layer 5, GND) |
| 底层铜 | `PLFM-RIS.GBL` | Bottom Copper (Layer 6) |
| 顶层阻焊 | `PLFM-RIS.GTS` | Top Soldermask |
| 底层阻焊 | `PLFM-RIS.GBS` | Bottom Soldermask |
| 顶层锡膏 | `PLFM-RIS.GTP` | Top Solderpaste |
| 底层锡膏 | `PLFM-RIS.GBP` | Bottom Solderpaste |
| 顶层丝印 | `PLFM-RIS.GTO` | Top Silkscreen |
| 底层丝印 | `PLFM-RIS.GBO` | Bottom Silkscreen |
| 板框 | `PLFM-RIS.GKO` | Board Outline (Edge.Cuts) |
| 钻孔 | `PLFM-RIS.TXT` | Drill File (Excellon) |

**格式要求**: Gerber RS-274X (Gerber X2)，单位 mm，坐标精度 4.6，
前导零抑制；钻孔文件为 Excellon，同时输出 Drill Map (PDF)。
**IPC 网表比对**: 导出的网表与原理图网表应通过 IPC-D-356 比对（KiCad: 生成 `.net` 后与板厂确认）。

---

## 2. 叠层与阻抗要求

6 层 Rogers 4350B 混合叠层（自上而下）：

| 层 | 功能 | 介质 | 厚度 |
|----|------|------|------|
| L1 | RF 辐射贴片/微带 | — | 1 oz (35 μm) |
| 介质 | 微带介质 | Rogers 4350B | 0.254 mm (10 mil) |
| L2 | GND 参考层 | — | 1 oz |
| 介质 | 芯板 | FR4 或 Rogers | 0.5 mm |
| L3 | DC 控制线 | — | 1 oz |
| L4 | DC 控制线 | — | 1 oz |
| 介质 | 芯板 | FR4 或 Rogers | 0.5 mm |
| L5 | GND 参考层 | — | 1 oz |
| 介质 | 微带介质 | Rogers 4350B | 0.254 mm (10 mil) |
| L6 | 馈电网络微带 | — | 1 oz |

**阻抗控制**: 50 Ω 单端，公差 ±10%；L1/L6 微带按 εr=3.48 计算，
阻抗计算表（如 KiCad PCB Calculator 或 Polar SI9000）随设计归档。
表面处理 ENIG；最小线宽/间距 0.15 mm；最小钻孔 0.3 mm。

---

## 3. 3D 模型导出规范（STEP）

1. KiCad: `File → Export → STEP`，选择含铜板体（board with copper）。
2. **格式**: STEP AP214，单位 mm；3D 模型原点 = 板框左下角（与 Gerber 原点一致），PCB 顶面朝 +Z。
3. 元件必须含 3D 封装模型：优先使用 KiCad 标准库 STEP 模型，
   定制封装（RIS 单元、SMA 馈电）须自建并随仓库归档于 `3d/models/`。
4. 导出后使用 FreeCAD / KiCad 3D Viewer 目检：丝印朝向、元件高度冲突、连接器出板方向。
5. 归档：`3d/PLFM-RIS_vX.Y_step.zip`（含 STEP + 模型引用清单）。

---

## 4. 发布前检查清单（Checklist）

- [ ] DRC: 0 error（按板厂工艺规则文件配置后复跑）
- [ ] ERC: 0 error（原理图电气规则）
- [ ] IPC 网表比对通过（PCB 与原理图一致）
- [ ] 阻抗: 50 Ω ±10%，与叠层计算表一致
- [ ] Gerber 预览（gerbv / 板厂在线预览）目检无缺层、无镜像
- [ ] 钻孔文件与焊盘对齐，孔位无偏移
- [ ] 板框尺寸 100 × 100 mm ±0.2 mm，与 STEP 3D 模型一致
- [ ] 丝印: 元件位号清晰，无重叠，无反向
- [ ] BOM 与位号一一对应（本目录 `BOM.csv`）
- [ ] 坐标文件（Pick-and-Place, Centroid）已导出归档 `production/`
- [ ] 装配图（Assembly Drawing, PDF）已导出归档 `production/`

---

## 5. 目录归档约定

```
2_RIS_Antenna_Design/
├── BOM.csv                         # 物料清单（含位号/封装/供应商）
├── PCB_DESIGN_GUIDE.md             # PCB 设计指南
├── GERBER_MANUFACTURING_GUIDE.md   # Gerber 导出与下单指南
├── GERBER_AND_3D_RELEASE_SPEC.md   # 本文档
├── gerber/                         # 可制造文件（按 §1 命名，随版本归档）
│   └── PLFM-RIS_vX.Y_gerber.zip    # 打板打包文件 + SHA256 校验和
├── 3d/                             # 3D 模型
│   ├── PLFM-RIS_vX.Y_step.zip      # STEP AP214 归档
│   └── models/                     # 自建元件 3D 模型
└── production/                     # 生产辅助文件
    ├── PLFM-RIS_vX.Y_centroid.csv  # 贴片坐标
    └── PLFM-RIS_vX.Y_assembly.pdf  # 装配图
```

---

## 6. 版本与变更管理

- 每次打板版本在 `gerber/`、`3d/` 中以 `vX.Y` 命名归档，压缩包附 SHA256 校验和文件。
- 打板版本在 git 中打标签（如 `fab-v1.0`），与 `BOM.csv` 版本对应。
- Gerber 一经投板即视为发布，后续修改必须升版本号，禁止原位覆盖已打板文件。

---

## 📚 参考

- [Gerber 文件格式标准 (Ucamco)](https://www.ucamco.com/gerber-file-format/)
- [KiCad 制造输出文档](https://docs.kicad.org/7.0/en/pcbnew/pcbnew_fabrication_outputs.html)
- [IPC-2581 / ODB++ 说明](https://www.ipc.org/)
