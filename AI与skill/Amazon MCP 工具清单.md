# Amazon MCP 工具清单

更新时间：2026-09-11

数据来源：通过 Dinzee Gateway 实时执行 `list-tools`。本清单记录当前对外开放的工具，不等同于 Amazon 官方 API 的全部端点。

## 先看懂几个词

- **商城 / Marketplace**：美国站、德国站、日本站等 Amazon 销售站点。
- **Listing**：卖家后台中的商品页面和商品资料。
- **FBA 入库**：卖家把货发到 Amazon 仓库。
- **入库计划 / Inbound Plan**：一次备货计划，说明准备发哪些商品、多少件、从哪里发。
- **货件 / Shipment**：Amazon 把入库计划拆成的实际发货批次，一次计划可能有多个货件。
- **箱子 / Box**：货件中的纸箱，以及每箱装了哪些商品。
- **托盘 / Pallet**：多个纸箱码放并固定在一个托盘上，常见于大批量卡车或海运入仓。
- **装箱组 / Packing Group**：Amazon 要求放在一起装箱的一组商品。
- **FBA 出库 / Outbound**：Amazon 从仓库拣货、打包并寄给买家或寄到卖家指定地址。
- **Data Kiosk**：Amazon 提供的数据查询中心，可以查询销售、流量、库存和费用等经营数据。

## 总览

| Provider | 当前开放数量 | 单次点数 | 写操作 |
| --- | ---: | ---: | --- |
| `amazon_sp_api_mcp` | 59 | 3 | 无业务数据写入；`create_report` 和 `create_data_kiosk_query` 只创建只读任务 |
| `amazon-ads` | 35 | 5 | 22 个广告业务写工具，调用时必须通过广告修改二次授权和参数校验 |

## SP-API：店铺与商城（2）

| 工具 | 小白说明 |
| --- | --- |
| `list_stores` | 看这个登录凭证已经绑定了哪些 Amazon 店铺，以及可以操作哪些店铺。 |
| `get_marketplace_participations` | 看某个店铺开通了哪些站点，例如美国站、加拿大站、德国站，以及这些站点目前是否正常。 |

## SP-API：订单与销售（4）

| 工具 | 小白说明 |
| --- | --- |
| `get_orders` | 按时间查看一批订单，可以筛选待付款、已发货、已取消等状态。订单太多时可以一页一页继续查。 |
| `get_order` | 输入 Amazon 订单号，查看这一笔订单的时间、金额、配送状态等详细信息。 |
| `get_order_items` | 输入订单号，查看买家在这笔订单里买了哪些 SKU、买了几件和对应价格。 |
| `get_order_metrics` | 查看一段时间内有多少订单、卖出多少件、销售额是多少，适合做日报和趋势统计。 |

## SP-API：目录、Listing、价格与费用（13）

| 工具 | 小白说明 |
| --- | --- |
| `get_catalog_item` | 输入 ASIN，查看 Amazon 商品目录里的标题、图片、品牌、类目、尺寸和排名等资料。 |
| `search_catalog_items` | 不知道 ASIN 时，用关键词、品牌、UPC/EAN 或类目搜索 Amazon 商品。 |
| `get_listing_item` | 输入自己店铺的 SKU，查看商品是否在售、资料是否完整、有没有违规或无法销售的问题。 |
| `search_listing_items` | 在自己店铺里批量查找商品，可按 SKU、状态、问题或更新时间筛选。 |
| `get_competitive_pricing` | 查看某个 ASIN 或 SKU 当前有多少卖家报价，以及主要竞争价格。 |
| `get_competitive_summary` | 一次查看多个 ASIN 的购物车报价、最低价和主要竞争报价，适合批量比价。 |
| `get_featured_offer_expected_price_batch` | 估算商品大约要卖到什么价格才更有机会获得购物车，只提供建议，不会自动改价。 |
| `get_item_offers` | 输入 ASIN，查看其他卖家对这个商品的价格、配送方式和商品状态。 |
| `get_listing_offers` | 输入自己店铺的 SKU，查看它在市场上的竞争报价和购物车情况。 |
| `get_pricing` | 查看商品在指定站点的当前售价和报价状态。 |
| `get_fee_estimate_for_asin` | 输入 ASIN 和预计售价，估算销售佣金、FBA 配送费等 Amazon 费用。 |
| `get_fee_estimate_for_sku` | 输入自己店铺的 SKU 和预计售价，估算 Amazon 费用。 |
| `get_fee_estimates` | 一次给多个 ASIN 或 SKU 估算 Amazon 费用，适合批量核算利润。 |

## SP-API：库存、FBA 出库与退货（8）

| 工具 | 小白说明 |
| --- | --- |
| `get_inventory_summaries` | 查看每个 SKU 在 Amazon 仓库有多少可售、预留、调拨中、处理中和不可售库存，用来判断缺货和补货。 |
| `get_feature_inventory` | 查看有多少 FBA 库存可以用于指定的特殊配送服务，例如多渠道配送。 |
| `get_feature_sku` | 检查某个 SKU 能不能使用指定的 FBA 特殊配送服务，以及当前可用数量。 |
| `get_fulfillment_features` | 查看某个站点支持哪些 FBA 出库服务，先确认可以使用什么配送能力。 |
| `get_fulfillment_order` | 查看一笔由 Amazon 仓库代为拣货和发货的订单详情及处理进度。 |
| `list_fulfillment_orders` | 查看一批由 Amazon 仓库代发的订单，例如多渠道配送订单。 |
| `get_package_tracking_details` | 输入包裹编号，查看 Amazon 仓库发出的包裹走到哪里、是否签收。 |
| `list_return_reason_codes` | 查看某个 SKU 创建 FBA 退货时可以选择哪些退货原因。 |

## SP-API：FBA 入库与运输（22）

| 工具 | 小白说明 |
| --- | --- |
| `get_inbound_plan` | 查看一次 FBA 备货计划的完整情况，包括准备发什么货、多少件，以及被分成了哪些货件。 |
| `list_inbound_plans` | 查看近期创建过的所有 FBA 备货计划，以及每个计划正在创建、运输中还是已完成。 |
| `get_inbound_shipment` | 查看某一票实际发往 Amazon 仓库的货，包括目的仓、运输状态和货件编号。 |
| `get_inbound_operation_status` | 某个入库操作需要后台处理时，用它查看处理完成了、还在等待，还是失败了。 |
| `get_delivery_challan_document` | 获取部分站点入仓时需要随货携带的交货单文件信息，主要用于印度站等有此要求的场景。 |
| `get_self_ship_appointment_slots` | 自己安排车辆送仓时，查看 Amazon 仓库还有哪些可以预约的送货时间。 |
| `get_shipment_content_update_preview` | 正式修改货件装了什么商品之前，先看 Amazon 预计会接受哪些变化、会报什么错误。此工具只看预览，不提交修改。 |
| `list_shipment_content_update_previews` | 查看某个货件以前生成过的内容修改预览及处理结果。 |
| `list_delivery_window_options` | 查看 Amazon 允许这票货在哪些日期送到仓库，用来选择预计送达时间。 |
| `list_inbound_plan_boxes` | 查看整个备货计划登记了哪些纸箱，以及每个箱子的编号、重量和尺寸等信息。 |
| `list_inbound_plan_items` | 查看整个备货计划准备发送哪些 SKU、每个 SKU 发多少件。 |
| `list_inbound_plan_pallets` | 查看整个备货计划登记了哪些托盘。托盘就是把多个纸箱码放并固定在一个底座上，适合大批量运输。 |
| `list_inbound_shipment_boxes` | 查看某一票具体货件包含哪些纸箱，以及每箱装了什么。 |
| `list_inbound_shipment_items` | 查看某一票具体货件包含哪些 SKU、每个 SKU 发多少件。 |
| `list_inbound_shipment_pallets` | 查看某一票具体货件用了几个托盘及托盘信息，主要用于整托送仓；普通小包裹货件通常没有托盘。 |
| `list_item_compliance_details` | 查看商品入仓前是否需要提供危险品、电池、保质期或其他合规资料。 |
| `list_packing_group_boxes` | 查看某一组必须一起装箱的商品最终被放进了哪些纸箱。 |
| `list_packing_group_items` | 查看 Amazon 要求放在同一装箱组里的 SKU 和数量。 |
| `list_packing_options` | 查看 Amazon 给出的装箱方案，例如哪些商品可以混装、需要分成哪些箱组。 |
| `list_placement_options` | 查看 Amazon 给出的分仓方案，例如全部发到一个仓，还是拆到多个仓，以及可能产生的入库配置费。 |
| `list_prep_details` | 查看商品入仓前是否需要贴标、套袋、气泡膜包装等预处理，以及由谁负责。 |
| `list_transportation_options` | 查看这票货可以选择哪些承运商、运输方式和报价，例如小包裹、零担或整车。 |

## SP-API：报告与 Data Kiosk（10）

| 工具 | 小白说明 |
| --- | --- |
| `create_report` | 向 Amazon 申请生成一份经营报表，例如订单、库存、退货或品牌分析报表；它不会修改店铺数据。 |
| `get_report` | 用报告任务编号查看报表生成到哪一步，完成后可以拿到文档编号。 |
| `get_report_document` | 报表完成后获取临时下载地址和解压方式，用来真正读取报表文件。 |
| `list_reports` | 查看近期申请过哪些报表，以及每份报表正在处理、已完成还是已失败。 |
| `get_report_schedule` | 查看某一种报表是否设置了自动定时生成，以及生成频率。 |
| `list_report_schedules` | 查看店铺当前有哪些报表设置了自动定时生成。 |
| `create_data_kiosk_query` | 向 Data Kiosk 提交一次经营数据查询，例如按日期查询销量、流量或费用；不会修改店铺。 |
| `get_data_kiosk_query` | 查看 Data Kiosk 查询是否完成，完成后取得结果文档编号。 |
| `get_data_kiosk_document` | 获取 Data Kiosk 查询结果的临时下载地址，用来读取实际数据。 |
| `list_data_kiosk_queries` | 查看近期提交过哪些 Data Kiosk 查询及各自状态。 |

## Amazon Ads：账户、资格与只读查询（8）

| 工具 | 类型 | 小白说明 |
| --- | --- | --- |
| `ads_accounts-list_ads_accounts` | 只读 | 查看这个 Amazon 广告授权下面有哪些广告账户、站点和币种，通常是调用其他广告工具的第一步。 |
| `advertiser_product_group_eligibility-create` | 资格请求 | 向 Amazon 发起资格检查，确认广告账户能不能使用某类广告产品；不会新建或修改广告活动。 |
| `campaign_management-check_product_eligibility` | 只读 | 检查某个 ASIN 能不能投放指定类型的广告，并查看不能投放的原因。 |
| `campaign_management-query_campaign` | 只读 | 查看广告活动列表及名称、状态、预算、类型等信息。SP 是商品推广，SB 是品牌推广，SD 是展示型推广。 |
| `campaign_management-query_ad_group` | 只读 | 查看广告活动下面有哪些广告组，以及广告组状态和默认竞价。 |
| `campaign_management-query_ad` | 只读 | 查看广告组里具体推广了哪些商品或创意，以及是否启用。 |
| `campaign_management-query_ad_association` | 只读 | 查看某个广告被放在哪个广告组里，用于核对广告和广告组的对应关系。 |
| `campaign_management-query_target` | 只读 | 查看广告组正在投放哪些关键词、ASIN、类目或受众，以及对应竞价和状态。 |

## Amazon Ads：报告（5）

| 工具 | 类型 | 小白说明 |
| --- | --- | --- |
| `reporting-create_report` | 只读任务 | 自己指定字段和日期，申请生成一份通用广告报表，不会修改广告。 |
| `reporting-create_campaign_report` | 只读任务 | 申请生成广告活动表现报表，可查看曝光、点击、花费、订单、销售额、ROAS 等数据。 |
| `reporting-create_inventory_report` | 只读任务 | 申请生成广告库存报表，用于查看可投放库存和库存相关表现。 |
| `reporting-create_product_report` | 只读任务 | 申请生成商品维度广告报表，用于比较每个推广商品的花费和销售表现。 |
| `reporting-retrieve_report` | 只读 | 用报告编号查看生成进度；完成后获取并下载真正的广告数据文件。 |

## Amazon Ads：创建类写工具（9）

以下工具会改变 Amazon Ads 业务数据，必须经过广告修改二次授权。

| 工具 | 小白说明 |
| --- | --- |
| `campaign_management-create_campaign` | 新建一个广告活动，并设置广告类型、名称、预算、日期和初始状态。会真实影响广告账户。 |
| `campaign_management-create_singleshot_sp_campaign` | 一次把商品推广活动、广告组、商品广告和关键词或自动定向全部建好，适合完整创建一套 SP 广告。 |
| `campaign_management-add_country_campaign` | 给现有商品推广活动增加投放国家，并给各国家设置预算上限。 |
| `campaign_management-create_ad_group` | 在广告活动下面新建广告组，用来放广告商品和定向。 |
| `campaign_management-create_ad` | 在广告组里加入要推广的商品或广告创意。 |
| `campaign_management-create_ad_association` | 把已经存在的广告关联到指定广告组。 |
| `campaign_management-create_target` | 给广告组新增关键词、竞品 ASIN、类目或受众定向，并设置竞价。 |
| `campaign_management-create_bid_adjustment_rule` | 为 DSP 广告组创建自动调高或调低竞价的规则。 |
| `campaign_management-dsp_create_conversion_tracking_products` | 把商品加入 DSP 活动的转化追踪清单，之后可以统计这些商品带来的转化。 |

## Amazon Ads：修改类写工具（8）

| 工具 | 小白说明 |
| --- | --- |
| `campaign_management-update_campaign` | 修改现有广告活动的名称、开关状态、预算或其他设置。 |
| `campaign_management-update_campaign_budget` | 只调整广告活动预算，例如把每日预算从 20 改成 30。 |
| `campaign_management-update_campaign_state` | 启用或暂停广告活动，不修改预算和其他设置。 |
| `campaign_management-update_ad_group` | 修改广告组名称、启停状态或默认竞价。 |
| `campaign_management-update_ad` | 启用、暂停或修改具体广告。 |
| `campaign_management-update_ad_association` | 调整广告与广告组之间的关联设置。 |
| `campaign_management-update_target` | 修改关键词、商品、类目或受众定向的竞价、状态或其他参数。 |
| `campaign_management-update_target_bid` | 只修改某个关键词或商品定向的出价。 |

## Amazon Ads：删除类写工具（5）

| 工具 | 小白说明 |
| --- | --- |
| `campaign_management-delete_campaign` | 永久删除广告活动及下面的广告组、广告和定向。删除前必须认真核对活动 ID。 |
| `campaign_management-delete_ad_group` | 永久删除广告组及其关联广告。删除前必须核对广告组 ID。 |
| `campaign_management-delete_ad` | 永久删除某个具体广告。 |
| `campaign_management-delete_ad_association` | 解除广告与广告组的关联，不一定删除广告本身。 |
| `campaign_management-delete_target` | 永久删除某个关键词、商品、类目或受众定向。 |

## 权限和计费说明

- `amazon_sp_api_mcp` 当前 59 个工具全部为读取、搜索、估算或创建只读查询任务；每次成功调用 3 点。
- `amazon-ads` 当前 35 个工具全部为每次成功调用 5 点。
- Amazon Ads 中 22 个业务写工具包括 9 个创建、8 个修改、5 个删除。
- 广告写工具应同时满足：客户已明确开启广告修改授权、调用 Token 属于该客户、目标店铺已授权 Ads、请求参数通过网关校验。
- 未开启广告修改授权时，扣费网关应在 `tools/list` 隐藏这 22 个写工具，并在直接调用时再次拒绝，不能只依赖前端隐藏。
- `create_report`、`create_data_kiosk_query` 和 `reporting-create_*` 名称虽然包含 `create`，只创建查询或报告任务，不修改 Listing、库存、订单或广告投放状态。
