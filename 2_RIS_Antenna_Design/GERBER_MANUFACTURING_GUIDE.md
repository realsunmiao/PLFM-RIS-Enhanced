# Gerber 制造文件生成指南

> **本文档说明如何从 KiCad/Altium 导出 Gerber 文件并下单打板**

---

## 📋 Gerber 文件清单

### 必需文件 (6 层 PCB)

| 文件名 | 层说明 | 用途 |
|-------|--------|------|
| `F_Cu.gbr` | Top Copper (Layer 1) | 辐射贴片铜箔 |
| `In1_Cu.gbr` | Inner Layer 1 (Layer 2) | 接地层 1 |
| `In2_Cu.gbr` | Inner Layer 2 (Layer 3) | DC 控制线 1 |
| `In3_Cu.gbr` | Inner Layer 3 (Layer 4) | DC 控制线 2 |
| `In4_Cu.gbr` | Inner Layer 4 (Layer 5) | 接地层 2 |
| `B_Cu.gbr` | Bottom Copper (Layer 6) | 馈电网络铜箔 |
| `F_Mask.gbr` | Top Soldermask | 顶层阻焊 |
| `B_Mask.gbr` | Bottom Soldermask | 底层阻焊 |
| `F_Paste.gbr` | Top Solderpaste | 顶层锡膏 |
| `B_Paste.gbr` | Bottom Solderpaste | 底层锡膏 |
| `F_Silk.gbr` | Top Silkscreen | 顶层丝印 |
| `B_Silk.gbr` | Bottom Silkscreen | 底层丝印 |
| `Edge_Cuts.gbr` | Board Outline | 板框轮廓 |
| `Drill.drl` | Drill File | 钻孔文件 (Excellon 格式) |
| `Drill_Map.pdf` | Drill Map | 钻孔示意图 (可选) |

---

## 🔧 KiCad 导出步骤

### 1. 打开 PCB 编辑器

```
File → Open → 选择 RIS_Antenna.kicad_pcb
```

### 2. 配置 Gerber 输出

```
File → Fabrication Outputs → Gerbers (.gbr)...
```

**设置参数**:
- **Plot format**: Gerber X2
- **Use extended X2 attributes**: ✓
- **Coordinate format**: 4.6 (单位 mm)
- **Zero suppression**: Leading zeros

### 3. 选择要输出的层

在 "Layers" 标签页勾选:
- ✅ F.Cu (Top Copper)
- ✅ In1.Cu, In2.Cu, In3.Cu, In4.Cu (Inner Layers)
- ✅ B.Cu (Bottom Copper)
- ✅ F.Mask, B.Mask (Soldermask)
- ✅ F.Paste, B.Paste (Solderpaste)
- ✅ F.SilkS, B.SilkS (Silkscreen)
- ✅ Edge.Cuts (Board Outline)

### 4. 生成钻孔文件

```
File → Fabrication Outputs → Drill Files (.drl)...
```

**设置参数**:
- **Drill file format**: Excellon
- **Map file format**: PDF
- **Units**: Millimeters
- **Zero suppression**: Leading zeros
- **Plated holes**: ✓
- **NPTH holes**: ✓

### 5. 打包文件

导出的文件位于项目目录的 `gerber/` 文件夹,打包为 ZIP:

```bash
cd gerber
zip -r RIS_Antenna_Gerber.zip *.gbr *.drl *.pdf
```

---

## 🏭 下单打板

### 推荐厂家

#### 国内厂家
1. **嘉立创 (JLCPCB)**
   - 网址: https://jlcpcb.com/
   - 优势: 价格低,交期快 (3-5天)
   - 支持 Rogers 板材: 是 (需特殊备注)

2. **捷配 (NextPCB)**
   - 网址: https://www.nextpcb.com/
   - 优势: 高频板材经验丰富
   - 支持 Rogers 板材: 是

#### 国际厂家
1. **PCBWay**
   - 网址: https://www.pcbway.com/
   - 优势: 英文界面,全球配送
   - 支持 Rogers 板材: 是

2. **AllPCB**
   - 网址: https://www.allpcb.com/
   - 优势: 性价比高
   - 支持 Rogers 板材: 是

### 下单参数

**嘉立创示例**:

```
基本参数:
  - 层数: 6 层
  - 板材: Rogers 4350B (需在备注中说明)
  - 尺寸: 100 × 100 mm
  - 数量: 10 pcs

工艺参数:
  - 铜厚: 1 oz (35 μm)
  - 最小线宽/间距: 0.15 mm / 0.15 mm
  - 最小过孔: 0.3 mm (钻孔)
  - 表面处理: ENIG (化学镍金)
  - 阻抗控制: 是 (50 Ω ±10%)
  - 测试: 100% 电气测试

特殊要求:
  - 板材: Rogers 4350B + 4003C 混合叠层
  - 介电常数: εr = 3.48 ±0.05
  - 提供阻抗测试报告
```

### 上传文件

1. 登录厂家网站
2. 点击 "Quick Order" 或 "Instant Quote"
3. 上传 `RIS_Antenna_Gerber.zip`
4. 系统自动解析层数和尺寸
5. 确认参数无误后下单

---

## 💰 费用估算

### 小批量 (10 pcs)

| 项目 | 费用 (USD) | 说明 |
|-----|-----------|------|
| PCB 打板 | $150-200 | Rogers 板材, 6层, ENIG |
| 运费 | $30-50 | DHL/FedEx |
| **合计** | **$180-250** | 约 ¥1300-1800 |

### 中批量 (50 pcs)

| 项目 | 费用 (USD) | 说明 |
|-----|-----------|------|
| PCB 打板 | $500-700 | 单价降低 |
| 运费 | $50-80 | 海运更便宜 |
| **合计** | **$550-780** | 约 ¥4000-5600 |

---

## 🔍 收货检验

### 外观检查

1. **板框尺寸**: 用卡尺测量 (应为 100×100 mm ±0.2 mm)
2. **铜箔颜色**: 应均匀,无氧化斑点
3. **丝印清晰度**: 文字应清晰可读
4. **过孔质量**: 无毛刺,孔壁光滑

### 电气测试

1. **开路/短路测试**
   ```
   - 使用万用表蜂鸣档
   - 测量相邻走线应不通 (电阻 > 1 MΩ)
   - 测量同一网络应导通 (电阻 < 1 Ω)
   ```

2. **阻抗测试**
   ```
   - 厂家应提供阻抗测试报告
   - 微带线阻抗: 50 Ω ±10%
   - 如有偏差,联系厂家返工
   ```

---

## 📞 常见问题

### Q1: Rogers 板材比普通 FR4 贵多少?

**A**: 约 3-5 倍。FR4 六层板 10 pcs 约 $30-50,Rogers 约 $150-200。但高频性能差异巨大,不可替换。

### Q2: 能否先用 FR4 打样验证布局?

**A**: 可以,但不推荐。FR4 在 10 GHz 损耗极大 (tanδ ≈ 0.02 vs Rogers 0.0037),会导致性能严重下降。建议直接上 Rogers。

### Q3: ENIG 表面处理有必要吗?

**A**: 强烈建议。ENIG (化学镍金) 平整度好,适合高频应用和细间距焊接。HASL (喷锡) 表面不平,会影响 RF 性能。

### Q4: 打板周期多久?

**A**: 
- 嘉立创: 3-5 天 (加急 24-48 小时,费用翻倍)
- PCBWay: 5-7 天
- 运费: DHL 3-5 天,海运 15-30 天

---

## 📚 参考资源

- [Gerber 文件格式标准](https://www.ucamco.com/gerber-file-format/)
- [KiCad Gerber 导出教程](https://docs.kicad.org/7.0/en/pcbnew/pcbnew_fabrication_outputs.html)
- [Rogers 板材选型指南](https://rogerscorp.com/resources/)

---

**准备好打板了吗?** 
按照上述步骤导出 Gerber 文件,上传到厂家网站,即可开始生产!
