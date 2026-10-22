# economics 集成补丁（安装到 amazon-ppc-profit-diagnosis/references/）

> 将本文件放入 `amazon-ppc-profit-diagnosis/references/economics-integration.md`，
> 并在其 SKILL.md 的"参考资料"或"配置"章节追加下方【SKILL.md 追加段落】。
> 协议全文与 economics 侧一致：Schema v1.0，见 economics 的 integration-contract.md。

---

## 【SKILL.md 追加段落】（复制到 diagnosis 的 SKILL.md）

### 与 amazon-ppc-economics 的接口（诊断 ↔ 算账）

参数来源优先级（高→低）：
1. 会话中存在 `ppc_config.json`（或用户说"用刚才算的参数"）→ **直接消费，跳过参数问询**
2. 用户手动提供参数 → 正常流程
3. 都没有 → 提示："建议先用 amazon-ppc-economics 跑 export 生成配置（平本ACOS/CPC上限/分区锚线会自动对齐），也可以现在手动提供客单价/毛利率/目标ACOS/CVR"

消费规则：
- `pre_ad_margin` / `breakeven_acos` / `target_acos` / `cpc_cap` / `cpa_cap` **一律不重算**，economics 是唯一权威；本 skill 只做分区判定和动作输出
- `acos_tiers` 覆盖内置五档分区默认阈值（优质/健康/预警/承压/亏损的边界）
- `clicks_per_order_threshold` 覆盖词级 0 单止损的点击数阈值
- `config_warnings` 非空 → 原样置于诊断报告头部（如"可承受CPC低于类目均价"类结构性警告）
- `target_acos_mode = "sacrifice"` → 报告标注"新品期亏本换排名模式（牺牲比例 r），档位锚线整体锚在等效目标ACOS（毛利率×r）上，超出即止损；`accounting_loss_above`（=平本ACOS）到等效目标之间标记为有意亏损带"

诊断完成后的回传义务：
从 result.json 按账户或 ASIN 聚合，导出 `actuals.json`：

```json
{
  "schema_version": "1.0",
  "period": "30d",
  "actual_cvr": <广告订单/广告点击>,
  "actual_cpc": <花费/点击>,
  "actual_acos": <花费/广告销售额>,
  "ad_orders": <广告订单数>,
  "organic_orders": <总订单-广告订单>,
  "total_sales": <总销售额, 可选>
}
```

并提示用户："实际数据已导出，可用 economics 的 calibrate 校准参数；若 CVR 漂移超 ±15% 会建议重锚分区。"

字段容错：config 缺字段 → 回退参数问询；schema_version 不一致 → 提示更新较旧一方。

---

## 五档分区锚线的来源（供 diagnosis 理解，不供其修改）

```
premium_max  = target_acos × 0.7          ← 系数0.7为 engineering_assumption
healthy_max  = target_acos                 ← "自己想赚多少"
warning_max  = target + (breakeven−target)/2
pressure_max = breakeven_acos (= pre_ad_margin)  ← "数学上还没亏"
loss         : ACOS > breakeven_acos
```

经济学含义：目标ACOS 或毛利率一变，五档整体自动平移。diagnosis 的档位判断因此永远锚在最新的账上，不会出现"分区还是上个月的毛利结构"这类漂移。
