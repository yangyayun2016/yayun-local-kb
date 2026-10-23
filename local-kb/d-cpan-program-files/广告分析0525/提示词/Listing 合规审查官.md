【角色】

你是一名亚马逊 Listing 合规审查官，熟悉 Seller Central 政策、社区最佳实践和 2024–2025年 新规。任务是逐条检查 Listing 内容，找出潜在违规与风险点，并给出修改建议。



【输入】

- 标题: {title}

- 主图与附图（Product Images）: {images_info}关键词

- 五点要点 : {bullet_points}

- 产品描述 : {a_plus_content}



【任务】

逐项对照官方政策和最佳实践，输出合规检查结果。检查范围包含：

1. **标题（Title）**

   - 是否 ≤200 字符，推荐 ≤150 字符。

   - 是否有特殊字符 (!, $, ?, { }, _, ^, ¬)。

   - 是否有重复词堆砌（同词 >2 次）。

   - 是否包含促销语（Best, Free Shipping, Cheapest 等）。

   - 是否误导性或包含竞品品牌 / 商家名。

   - 结构是否符合：品牌 + 核心产品名 + 关键属性（颜色/规格/材质等）。

   - 是否存在 “Review Listing Updates” 风险提示因子。



2. **主图 / 附图（Images）**

   - 主图是否纯白背景（RGB 255,255,255）。

   - 是否占画布 ≥85%。

   - 像素是否合规（500px–10,000px，推荐≥1000px）。

   - 格式是否为 jpg/jpeg/png/tif。

   - 是否有水印 / Logo / 边框 / 促销标签 / 文案（违规）。

   - 辅助图是否包含多角度、使用场景、细节、尺寸示意、信息图（加分项）。

   - 风格是否一致，是否符合移动端优化。



3. **五点要点（Bullet Points）**

   - 数量是否为 3–5 条。

   - 单条字符是否在 10–255 范围内。

   - 是否包含 ASIN、品牌名、促销、保修/退款/折扣等违规内容。

   - 是否有特殊字符或 Emoji。

   - 是否突出核心卖点（每条一个重点）。

   - 是否数字/单位表述清晰（如 17"-21" 高度调节）。



4. **产品描述（Description）**

   - 是否 ≤2000 字符。

   - 是否包含外部链接、联系方式、价格/促销/运输信息。

   - 是否包含未验证奖项、虚假/过度承诺。

   - HTML 是否仅使用允许的标签 (<b>, <strong>, <em>, <p>)。

   - 是否与标题 / 五点互补（避免冗余）。



5. **后台关键词（Search Terms）**

   - 是否重复（不同字段重复关键词）。

   - 是否包含品牌名/竞品名/商标。

   - 是否包含价格/促销类词。

   - 长度是否合理（避免被截断）。



6. **A+ 内容（A+ Enhanced Content）**

   - 是否已品牌备案（Brand Registered）。

   - 是否包含促销、外链、无根据声明。

   - 模块设计是否平衡图文，移动端可读性良好。

   - 是否上传高质量图片（≥970px）。

   - 是否包含 alt-text（关键词）。

   - 是否做对比模块 / 技术规格表 / 品牌故事 / 使用场景。

   - 是否与标准 Detail 描述重复过多。



7. **整体合规性**

   - 是否存在冲突或误导

   - 是否有 AI 自动修正风险（不当标点、字符、违规词）

   - 是否有类目特殊限制（如医疗/儿童/食品额外要求）



【输出】

以表格形式输出：

| 模块 | 检查点 | 状态 (合规/风险/违规) | 问题说明 | 修改建议 |



【目标】

帮助卖家快速发现 Listing 中的违规与潜在风险点，提供清晰可执行的修改建议。

































【背景】
- Rufus 是亚马逊用于购物问答与推荐的系统。
- Rufus 不会猜测商品能力，也不会使用 Listing 之外的隐含常识。强grounding,事实校验，有证据，不胡说八道
- 只有当 Listing 中存在明确、可引用的信息时，Rufus 才能给出确定回答并推荐商品。
- 本任务用于验证：当前 Listing 是否具备“无需猜测即可回答买家问题”的能力。

【角色】
你是一名 亚马逊 Listing 质检官（Rufus 视角），
职责是 模拟真实买家提问，并验证当前 Listing 是否提供了足够的信息，让 Rufus 能“直接回答、而不是猜”。
你的判断标准不是“回答是否好看”，而是：
Rufus 能否仅基于 Listing 中的明确文本或属性，给出确定、不含推断的回答

【输入】
- 产品标题:  {title}
- 五点描述:  {bullet_points}
- 产品描述: . {description}
- Search Terms &   {keywords_terms}

- 后台属性:{backend_terms}
{"detailPageListingResponse":{"supplier_declared_dg_hz_regulation#1.value":{"displayLabel":"危险商品规管","value":"not_applicable"},"item_name#1.value":{"displayLabel":"商品名称","value":"MOVA Air Purifier for Bedroom Home - True H13 HEPA Air Purifier for Smoke,Dust,Pollen,Pet Dander & Odor,(20dB) Quiet Air Purifiers with 3 Light,3 Speeds,Timer & Aroma Function"},"ships_globally#1.value":{"displayLabel":"全球发货","value":"false"},"item_weight#1.value":{"displayLabel":"商品重量","value":"3.53"},"model_number#1.value":{"displayLabel":"型号","value":"R0007US"},"detail_page_primary_image_url":{"displayLabel":"","value":"https://m.media-amazon.com/images/I/714GO9KgqWL.jpg"},"bullet_point#1.value":{"displayLabel":"要点","value":"HEPA Air purifier 3-LAYER H13 HEPA FILTRATION:Equipped with an advanced three-layer HEPA filtration system, the MOVA 100AP AIR effectively captures dust, Allergies,pet dander, pollen, smoke, unwanted odors, and fine hair — helping you create a cleaner,comfortable healthier living environment.Powerful 3-Stage H13 HEPA Air Filter – The MOVA air purifier combines a pre-filter, H13 True HEPA layer, and activated carbon air filter to capture up to 99.97% of dust, pollen, smoke, and pet dander;"},"wattage#1.unit":{"displayLabel":"额定功率单位","value":"watts"},"supplemental_condition_information#1.functional_condition":{"displayLabel":"功能状况","value":"fully_functional"},"control_method#1.value":{"displayLabel":"控制方法","value":"touch"},"pesticide_marking#1.marking_type":{"displayLabel":"农药标识","value":"epa_registration_number"},"item_package_weight#1.value":{"displayLabel":"包装重量","value":"3.53"},"batteries_required#1.value":{"displayLabel":"需要电池吗？","value":"false"},"product_site_launch_date#1.value":{"displayLabel":"产品网站发布日期","value":"2025-08-25T03:30:57.333Z"},"particle_retention_size#1.value":{"displayLabel":"滞留颗粒尺寸","value":"0.3"},"item_package_dimensions#1.width.value":{"displayLabel":"包装宽度","value":"7.28"},"legal_compliance_certifications#1.regulatory_organization_name":{"displayLabel":"Regulatory Organization Name","value":"California Environmental Protection Agency - Air Resources Board"},"pesticide_marking#1.certification_number":{"displayLabel":"农药认证编号","value":"102445-CHN-1"},"model_name#1.value":{"displayLabel":"型号名称","value":"R0007US"},"item_package_dimensions#1.width.unit":{"displayLabel":"包装宽度单位","value":"inches"},"supplemental_condition_information#1.features#1":{"displayLabel":"功能","value":"parts_replaced"},"special_feature#1.value":{"displayLabel":"专有特征","value":"Manual"},"pesticide_marking#1.registration_status":{"displayLabel":"农药登记状况","value":"fifra_not_considered_pesticide"},"batteries_included#1.value":{"displayLabel":"是否附带电池","value":"false"},"item_depth_width_height#1.width.value":{"displayLabel":"商品左右宽度","value":"7.28"},"item_depth_width_height#1.height.unit":{"displayLabel":"商品高度单位","value":"inches"},"supplemental_condition_information#1.accessories":{"displayLabel":"配件","value":"generic"},"legal_compliance_certifications#1.certification_status":{"displayLabel":"合规认证状态","value":"Compliant"},"manufacture_year#1.value":{"displayLabel":"制造年份","value":"2025"},"noise_level#1.unit":{"displayLabel":"噪声级单位","value":"decibels"},"legal_compliance_certifications#1.value":{"displayLabel":"Compliance Certification Value","value":"G-24-242"},"item_depth_width_height#1.width.unit":{"displayLabel":"商品宽度单位","value":"inches"},"color#1.standardized_values#1":{"displayLabel":"色彩地图","value":"White"},"item_depth_width_height#1.height.value":{"displayLabel":"底部到顶部的高度","value":"7.28"},"contaminant_filtration_capability#1.value":{"displayLabel":"污染物过滤能力","value":"Cigarette Smoke"},"noise_level#1.value":{"displayLabel":"噪声级","value":"20.0"},"filter_type#1.value":{"displayLabel":"过滤器类型","value":"HEPA"},"warranty_description#1.value":{"displayLabel":"保修说明","value":"2 Year Manufacturer"},"brand#1.value":{"displayLabel":"品牌名","value":"MOVA BETTER TOOLS FOR BETTER LIFE"},"has_replaceable_battery#1.value":{"displayLabel":"有可更换电池","value":"false"},"item_depth_width_height#1.depth.value":{"displayLabel":"商品从前到后的深度","value":"12.6"},"item_package_weight#1.unit":{"displayLabel":"包装重量单位","value":"pounds"},"number_of_items#1.value":{"displayLabel":"产品数量","value":"1"},"product_type#1.value":{"displayLabel":"产品类型","value":"AIR_PURIFIER"},"color#1.value":{"displayLabel":"颜色","value":"White"},"controller_type#1.value":{"displayLabel":"控制器类型","value":"Hand Control"},"item_package_dimensions#1.height.unit":{"displayLabel":"包装高度单位","value":"inches"},"item_package_dimensions#1.height.value":{"displayLabel":"包装高度","value":"7.28"},"size#1.value":{"displayLabel":"尺码","value":"one size"},"is_this_product_subject_to_buyer_age_restrictions#1.value":{"displayLabel":"该产品是否有买家年龄限制","value":"false"},"item_package_dimensions#1.length.value":{"displayLabel":"包装长度","value":"12.6"},"part_number#1.value":{"displayLabel":"零件编号","value":"R0007US"},"regulatory_compliance_certification#1.value":{"displayLabel":"监管标识","value":"102445-CHN-1"},"included_components#1.value":{"displayLabel":"所包含组件","value":"1 X Air purifier(H13 HEPA,Aroma,night light,timer)"},"item_depth_width_height#1.depth.unit":{"displayLabel":"商品深度单位","value":"inches"},"required_product_compliance_certificate#1.value":{"displayLabel":"产品合规证书","value":"California Air Review Board (CARB)"},"particle_retention_size#1.unit":{"displayLabel":"滞留颗粒尺寸单位","value":"micron"},"floor_area#1.unit":{"displayLabel":"占地面积的单位","value":"square_inches"},"product_description#1.value":{"displayLabel":"产品描述","value":"HEPA Air purifier MOVA Air Purifier for Bedroom Home - True H13 HEPA Air Purifier for Smoke,Dust,Pollen,Pet Dander & Odor,Quiet Air Purifiers with 3 Night Light,3 Speeds,Timer & Aroma Function MOVA Air Purifier for Bedroom Home - True H13 HEPA Air Purifier for Smoke,Dust,Pollen,Pet Dander & Odor,(20dB)Quiet Air Purifiers with 3 Light,3 Speeds,Timer & Aroma Function \uD835\uDFD1-\uD835\uDC0B\uD835\uDC00\uD835\uDC18\uD835\uDC04\uD835\uDC11 \uD835\uDC07\uD835\uDC04\uD835\uDC0F\uD835\uDC00 \uD835\uDC05\uD835\uDC08\uD835\uDC0B\uD835\uDC13\uD835\uDC11\uD835\uDC00\uD835\uDC13\uD835\uDC08\uD835\uDC0E\uD835\uDC0D:Equipped with an advanced three-layer HEPA filtration system, the MOVA 100AP effectively captures dust, Allergies,pet dander, pollen, smoke, unwanted odors, and fine hair — helping you create a cleaner,comfortable healthier living environment.Powerful 3-Stage H13 HEPA Air Filter – The MOVA air purifier combines a pre-filter, H13 True HEPA layer, and activated carbon air filter to capture up to 99.97% of dust, pollen, smoke, and pet dander; this compact H13 HEPA air purifier helps improve everyday indoor air quality for your family. high-efficiency particle filtration:Filtration system & efficiency True H13 HEPA filters:3-stage,Removes up to 99.97% of airborne particles as small as 0.3 microns"},"manufacturer#1.value":{"displayLabel":"制造商","value":"MOVA"},"has_automatic_shutoff#1.value":{"displayLabel":"自动关机","value":"true"},"power_source_type#1.value":{"displayLabel":"动力来源","value":"dc"},"is_assembly_required#1.value":{"displayLabel":"需要组装","value":"true"},"item_package_quantity#1.value":{"displayLabel":"成套产品数量","value":"1"},"floor_area#1.value":{"displayLabel":"占地面积","value":"62.0"},"item_type_keyword#1.value":{"displayLabel":"产品类型关键字","value":"hepa-filter-air-purifiers"},"item_package_dimensions#1.length.unit":{"displayLabel":"包装长度单位","value":"inches"},"regulatory_compliance_certification#1.regulation_type":{"displayLabel":"合规监管类型","value":"certificate_of_conformity"},"specification_met#1.value":{"displayLabel":"符合的规范","value":"CE Certified"},"wattage#1.value":{"displayLabel":"功率","value":"10.0"},"item_weight#1.unit":{"displayLabel":"商品重量单位","value":"pounds"},"list_price#1.value":{"displayLabel":"不含税价目表","value":"99.99"}},"detailPageListingResponseImsv3":"{\"batteries_included\":[{\"value\":\"false\"}],\"batteries_required\":[{\"value\":\"false\"}],\"brand\":[{\"value\":\"MOVA BETTER TOOLS FOR BETTER LIFE\"}],\"bullet_point\":[{\"value\":\"HEPA Air purifier 3-LAYER H13 HEPA FILTRATION:Equipped with an advanced three-layer HEPA filtration system, the MOVA 100AP AIR effectively captures dust, Allergies,pet dander, pollen, smoke, unwanted odors, and fine hair — helping you create a cleaner,comfortable healthier living environment.Powerful 3-Stage H13 HEPA Air Filter – The MOVA air purifier combines a pre-filter, H13 True HEPA layer, and activated carbon air filter to capture up to 99.97% of dust, pollen, smoke, and pet dander;\"}],\"color\":[{\"standardized_values\":[\"White\"],\"value\":\"White\"}],\"contaminant_filtration_capability\":[{\"value\":\"Cigarette Smoke\"}],\"control_method\":[{\"value\":\"touch\"}],\"controller_type\":[{\"value\":\"Hand Control\"}],\"detail_page_primary_image_url\":\"https://m.media-amazon.com/images/I/714GO9KgqWL.jpg\",\"filter_type\":[{\"value\":\"HEPA\"}],\"floor_area\":[{\"unit\":\"square_inches\",\"value\":\"62.0\"}],\"has_automatic_shutoff\":[{\"value\":\"true\"}],\"has_replaceable_battery\":[{\"value\":\"false\"}],\"included_components\":[{\"value\":\"1 X Air purifier(H13 HEPA,Aroma,night light,timer)\"}],\"is_assembly_required\":[{\"value\":\"true\"}],\"is_this_product_subject_to_buyer_age_restrictions\":[{\"value\":\"false\"}],\"item_depth_width_height\":[{\"depth\":{\"unit\":\"inches\",\"value\":\"12.6\"},\"height\":{\"unit\":\"inches\",\"value\":\"7.28\"},\"width\":{\"unit\":\"inches\",\"value\":\"7.28\"}}],\"item_name\":[{\"value\":\"MOVA Air Purifier for Bedroom Home - True H13 HEPA Air Purifier for Smoke,Dust,Pollen,Pet Dander & Odor,(20dB) Quiet Air Purifiers with 3 Light,3 Speeds,Timer & Aroma Function\"}],\"item_package_dimensions\":[{\"height\":{\"unit\":\"inches\",\"value\":\"7.28\"},\"length\":{\"unit\":\"inches\",\"value\":\"12.6\"},\"width\":{\"unit\":\"inches\",\"value\":\"7.28\"}}],\"item_package_quantity\":[{\"value\":\"1\"}],\"item_package_weight\":[{\"unit\":\"pounds\",\"value\":\"3.53\"}],\"item_type_keyword\":[{\"value\":\"hepa-filter-air-purifiers\"}],\"item_weight\":[{\"unit\":\"pounds\",\"value\":\"3.53\"}],\"legal_compliance_certifications\":[{\"certification_status\":\"Compliant\",\"regulatory_organization_name\":\"California Environmental Protection Agency - Air Resources Board\",\"value\":\"G-24-242\"}],\"list_price\":[{\"value\":\"99.99\"}],\"manufacture_year\":[{\"value\":\"2025\"}],\"manufacturer\":[{\"value\":\"MOVA\"}],\"model_name\":[{\"value\":\"R0007US\"}],\"model_number\":[{\"value\":\"R0007US\"}],\"noise_level\":[{\"unit\":\"decibels\",\"value\":\"20.0\"}],\"number_of_items\":[{\"value\":\"1\"}],\"part_number\":[{\"value\":\"R0007US\"}],\"particle_retention_size\":[{\"unit\":\"micron\",\"value\":\"0.3\"}],\"pesticide_marking\":[{\"certification_number\":\"102445-CHN-1\",\"marking_type\":\"epa_registration_number\",\"registration_status\":\"fifra_not_considered_pesticide\"}],\"power_source_type\":[{\"value\":\"dc\"}],\"product_description\":[{\"value\":\"HEPA Air purifier MOVA Air Purifier for Bedroom Home - True H13 HEPA Air Purifier for Smoke,Dust,Pollen,Pet Dander & Odor,Quiet Air Purifiers with 3 Night Light,3 Speeds,Timer & Aroma Function MOVA Air Purifier for Bedroom Home - True H13 HEPA Air Purifier for Smoke,Dust,Pollen,Pet Dander & Odor,(20dB)Quiet Air Purifiers with 3 Light,3 Speeds,Timer & Aroma Function \uD835\uDFD1-\uD835\uDC0B\uD835\uDC00\uD835\uDC18\uD835\uDC04\uD835\uDC11 \uD835\uDC07\uD835\uDC04\uD835\uDC0F\uD835\uDC00 \uD835\uDC05\uD835\uDC08\uD835\uDC0B\uD835\uDC13\uD835\uDC11\uD835\uDC00\uD835\uDC13\uD835\uDC08\uD835\uDC0E\uD835\uDC0D:Equipped with an advanced three-layer HEPA filtration system, the MOVA 100AP effectively captures dust, Allergies,pet dander, pollen, smoke, unwanted odors, and fine hair — helping you create a cleaner,comfortable healthier living environment.Powerful 3-Stage H13 HEPA Air Filter – The MOVA air purifier combines a pre-filter, H13 True HEPA layer, and activated carbon air filter to capture up to 99.97% of dust, pollen, smoke, and pet dander; this compact H13 HEPA air purifier helps improve everyday indoor air quality for your family. high-efficiency particle filtration:Filtration system & efficiency True H13 HEPA filters:3-stage,Removes up to 99.97% of airborne particles as small as 0.3 microns\"}],\"product_site_launch_date\":[{\"value\":\"2025-08-25T03:30:57.333Z\"}],\"product_type\":[{\"value\":\"AIR_PURIFIER\"}],\"regulatory_compliance_certification\":[{\"regulation_type\":\"certificate_of_conformity\",\"value\":\"102445-CHN-1\"}],\"required_product_compliance_certificate\":[{\"value\":\"California Air Review Board (CARB)\"}],\"ships_globally\":[{\"value\":\"false\"}],\"size\":[{\"value\":\"one size\"}],\"special_feature\":[{\"value\":\"Manual\"}],\"specification_met\":[{\"value\":\"CE Certified\"}],\"supplemental_condition_information\":[{\"accessories\":\"generic\",\"features\":[\"parts_replaced\"],\"functional_condition\":\"fully_functional\"}],\"supplier_declared_dg_hz_regulation\":[{\"value\":\"not_applicable\"}],\"warranty_description\":[{\"value\":\"2 Year Manufacturer\"}],\"wattage\":[{\"unit\":\"watts\",\"value\":\"10.0\"}]}","reconciledDataSummary":null,"debug":null} {backend_terms}


- 卖点与规格:MOVA HEPA H13空气净化器，白色外观，带HEPA H13过滤芯，有定时器2H/4H/8H，3档风速，童锁，一键启动，睡眠模式，香薰功能，适合面积375ft2,3层过滤系统 20分贝， {usps_specs}
后台关键词，埋词：air purifier air purifiers for home air filter air purifiers for bedroom air purifiers for HOME air purifiers  air purifiers for home pets hepa filter hepa air purifiers for home air filter air purifier SMALL hepa air purifier home air purifiers purificador de aire para casa









【任务】
1. 请基于真实购物场景，生成 不少于 20 条“买家可能在 Rufus 中直接询问的问题”，要求“
- 问题必须是完整自然语言（不是关键词）
- 问题应体现买家在下单前的真实犹豫点
- 覆盖以下维度（可交叉）：
   -- 功能与效果（怎么用、效果如何）
   -- 适配与兼容（适合谁 / 不适合谁 / 使用场景）
   -- 安装 / 组装 / 使用门槛
   -- 清洁/维护
   -- 安全性（材质、安全限制、承重、风险）
   -- 对比与差异（与常见替代方案或版本的区别）
   -- 售后/保修/退换
2. 模拟 Rufus 作答：让AI仅基于输入的Listing内容（前台+后台文本与属性）进行回答，
只允许引用或复述 Listing 中“明确存在”的信息如果 Listing 中没有明确支持信息，必须如实反映“无法确定”

3. 对每个问题输出：
   - Question: [问题]  
   - Answer: [基于Listing文本生成的回答]  
   - Confidence: 可直接回答 / 部分可回答 / 无法回答  
   - Missing Info: [若无法或部分回答，指出具体缺失的字段、参数或措辞]  

【输出格式】
以表格形式输出：
| # | Question | Answer | Confidence | Missing Info |totally output做最终总结

产品开发信息：品牌名 MOVA   整体外观，颜色，白色  配件包含一个H13 HEPA滤芯，一个说明书（5个国家语言），包装盒，充电器1.2米，参数 12V / 功率10W
电源信息 ：INPUT :100-240V  /  50-60Hz
OUTPUT:12V / 1A
型号：OLD120100AUS1D
线长：1.2米
插脚类型： US
插头类型：Type-C
主机风机信息：无刷电机：低功耗 低噪音
型号USTF 1207012HW
参数值:
额定电压：12V
额定电流：0.45-0.84A
额定转速：2400±10%rpm
PCBA: 型号FR4
面板控制信息：1、ON/OFF开关
2、模式：睡眠模式（1档风速）、 中（2档风速）、 高（3档风速）
3、定时：2h/4h/8h
4、灯光：三色（午夜蓝/柔光橙/活力绿）
（开机默认：睡眠-柔光橙，中档-活力绿，高档-午夜蓝）
5、Lock/Unlock  童锁
CADR  ≥70m³/h ,就=375平方英尺/小时噪音 睡眠档位：≤20dB(A) 
滤芯配件，3合1（初效滤网+HEPA H13+活性炭滤网）(密封包装）1个适配器1.2米， 3个香薰垫片，产品认证包含 不限于    ETL
    CARB
    DOE
    FDA
    EPA
    FCC
    CE


以下是挑词逻辑，
新增分析字段（算法计算）
    广告投放方案（智能决策）
    计算方式：基于5个指标综合评分（商业价值、广告选词、点击转化率， 分类级别（按优先级 为5档）：1.最高优先级），2.高优先级），（3.正常投放），（4.值得测试），（5.小额测试）
    核心投放：综合得分≥80，日预算25-35%（最高优先级）
    重点投放：得分65-79，日预算15-25%（高优先级）
    标准投放：得分50-64，日预算10-15%（正常投放）
    测试投放：得分35-49，日预算5-10%（值得测试）
    低价测试：得分20-34，日预算<5%（小额测试）
    暂不投放：得分<20，不建议投放  不设置预算，预算为0
    否定词屏蔽：基础分类为否定词，需添加到否定词列表
    数据不足：缺少广告选词或商业价值数据
     使用建议：直接根据此列分配广告预算，无需复杂判断,

整个工作流程是从反查竞品ASIN，（20个竞品ASIN）导出关键词，通过算法分几个维度给关键词打分。通过分数划分出适合广告投放的分类，考虑的是广告效率。再划分出适合文案的分类，考虑的是相关性。关键词的流量得分，机会指数

在广告结构中做出挑词逻辑，来源于算法选词的算法分类，不需要在广告结构中再新增指标了




做一个亚马逊广告运营助手，从算法选词，到广告结构，到批量上传广告数据    ，全流程打通

算法选词，选词逻辑 {挑词逻辑如下}   ，词库文案

广告结构，截图1，截图2














关键词分析

在类目里面找到最相近或同款竞品ASIN 10-20个（至少3个ASIN以上，最多10个ASIN） 在SIF 多产品对比 对比流量，下载数据，给AI分析， chatGPTo3
流量分级	   关键词相关性分级    周搜索量	      搜索量排名	在售商品数	流量垄断占比	竞争程度
组合统计指标 包含 流量分级，词相关性，关键词个数	总周搜索量	中位周搜索量	平均周搜索量	平均流量垄断度	流量垄断情况	平均在售商品	搜索量份额	加权流量垄断度

卖家精灵 20个竞品ASIN 拓展流量，分析  关键词词库追踪 分析
SIF SIF相似竞品拓词法   相似竞品拓词和筛查   50-100个   1.1 竞品拓词法 （至少10个 100个）删选，最相关那个  竞品拓词导出_2025-08-07 竞品拓词导出_   自然位前N 占位符  4-8-16-32-48 周搜索趋势 相关性   搜索量  ABA排名  相关性-手动  流量大小  相关性手动
修饰词类型    搜索转化率   搜索转化率   360天内 商品搜索量大小 商机探测器数据          1.1 竞品拓词法 （至少10个） 1.0 竞品拓词法 （至少48个）
 

词频统计   1个单词词根      2个单词词根     3个单词词根    搜索量加权词频(亚马逊官方方法)
品类拓词导出    SIF 品类拓词&筛查 选细分品类  下载， v #	关键词	搜索量	排名	相关性-手动    {品类拓词导出 }
1.2 以词拓词（词根法）  以词拓词&筛查 

AI分析， 关键词	流量分级	关键词相关性分级	周搜索量	搜索量排名	在售商品数	流量垄断占比	竞争程度



2025.8.14就加上SIF 广告点击转化率 盈亏平衡，





关键词优化路径： 
①选取10个竞品ASIN  SIF多产品对比，流量布局， 
②选取20个ASIN竞品  在卖家精灵（关键词优化 - 拓展流量词） 流量拓展=关键词优化 - 拓展流量词 按照畅销变体 拓展，下载数据，做关键词词库追踪，需要要AI智能体打标和分类，做关键词词库追踪数据
③ 用核心关键词搜索，去亚马逊前台抓取50-100类目相关竞品做SIF关键词收集 放关键词收集蓝 做相关性筛查，关键词词库+消费者洞察  
④ 要在后台商机探测器 关键词 份额，确定大词有哪些 做大词，   
⑤查看 SIF关键词中竞争格局-- 自然流量份额分布， 在售产品 自然流量分布  ⑥关键词广告点击转化率 ACOS  CPA 利润率
⑦ 关键词CPC情况（具体看是 在哪个类目下）


亚马逊关键词搭建随想，会用到卖家精灵，SIF， chatGPT o3模型

①在类目里面找到最相近或同款竞品ASIN 10-20个（至少3个ASIN以上，最多10个ASIN） 在SIF 多产品对比 对比流量，下载数据，给AI分析， chatGPT o3模型
流量分级	   关键词相关性分级    周搜索量	      搜索量排名	在售商品数	流量垄断占比	竞争程度
组合统计指标 包含 流量分级，词相关性，关键词个数	总周搜索量	中位周搜索量	平均周搜索量	平均流量垄断度	流量垄断情况	平均在售商品	搜索量份额	加权流量垄断度

②卖家精灵 20个竞品ASIN 拓展流量，分析  关键词词库追踪 分析
③SIF SIF相似竞品拓词法   相似竞品拓词和筛查   50-100个   1.1 竞品拓词法 （至少10个 100个）删选，最相关那个  竞品拓词导出_2025-08-07 竞品拓词导出_   自然位前N 占位符  4-8-16-32-48 周搜索趋势 相关性   搜索量  ABA排名  相关性-手动  流量大小  相关性手动
修饰词类型    搜索转化率   搜索转化率   360天内 商品搜索量大小 商机探测器数据          1.1 竞品拓词法 （至少10个） 1.0 竞品拓词法 （至少48个）

④词频统计   1个单词词根      2个单词词根     3个单词词根    搜索量加权词频(亚马逊官方方法)
⑤品类拓词导出    SIF 品类拓词&筛查 选细分品类  下载， v #	关键词	搜索量	排名	相关性-手动    {品类拓词导出 }
⑥1.2 以词拓词（词根法）  以词拓词&筛查 

⑦AI分析， 关键词	流量分级	关键词相关性分级	周搜索量	搜索量排名	在售商品数	流量垄断占比	竞争程度

--

chatGPT o3模型  模型 指令

要求按照之前的格式稳定输出，
请帮我分出表格全部关键词分类，一级，二级，三级流量词，然后再分出强中弱不相关。排列组合一级，二级，三级的强中弱，不相关关键词子表,具体需要生成以下格式的表格字段：1.流量分级：关键词按流量划分等级，分为一级二级三级。
关键词相关性分级： 按相关性对流量进行分类统计，比如划分强中弱，不相关。
 关键词个数：相关关键词的数量 
总周搜索量：一周内的总搜索次数。
中位周搜索量： 中位搜索量情况
平均周搜索量：平均周搜索量情况。
平均流量垄断度：流量垄断的平均垄断情况 
流量垄断情况 ：关键词流量垄断情况。 平均在售商品： 平均在售商品的分布情况。
搜索量份额：搜索量占整体的比例。
加权流量垄断度：衡量流量被垄断的程度。
模型 指令，：



关键词优化路径： 
①选取10个竞品ASIN  SIF多产品对比，流量布局， 
②选取20个ASIN竞品  在卖家精灵（关键词优化 - 拓展流量词） 流量拓展=关键词优化 - 拓展流量词 按照畅销变体 拓展，下载数据，做关键词词库追踪，需要要AI智能体打标和分类，做关键词词库追踪数据
③ 用核心关键词搜索，去亚马逊前台抓取50-100类目相关竞品做SIF关键词收集 放关键词收集蓝 做相关性筛查，关键词词库+消费者洞察  
④ 要在后台商机探测器 关键词 份额，确定大词有哪些 做大词，   
⑤查看 SIF关键词中竞争格局-- 自然流量份额分布， 在售产品 自然流量分布  ⑥关键词广告点击转化率 ACOS  CPA 利润率
⑦ 关键词CPC情况（具体看是 在哪个类目下）



以下是挑词逻辑，
新增分析字段（算法计算）
    广告投放方案（智能决策）
    计算方式：基于5个指标综合评分（商业价值、广告选词、点击转化率， 分类级别（按优先级 为5档）：1.最高优先级），2.高优先级），（3.正常投放），（4.值得测试），（5.小额测试）
    核心投放：综合得分≥80，日预算25-35%（最高优先级）
    重点投放：得分65-79，日预算15-25%（高优先级）
    标准投放：得分50-64，日预算10-15%（正常投放）
    测试投放：得分35-49，日预算5-10%（值得测试）
    低价测试：得分20-34，日预算<5%（小额测试）
    暂不投放：得分<20，不建议投放  不设置预算，预算为0
    否定词屏蔽：基础分类为否定词，需添加到否定词列表
    数据不足：缺少广告选词或商业价值数据
     使用建议：直接根据此列分配广告预算，无需复杂判断,

整个工作流程是从反查竞品ASIN，（20个竞品ASIN）导出关键词，通过算法分几个维度给关键词打分。通过分数划分出适合广告投放的分类，考虑的是广告效率。再划分出适合文案的分类，考虑的是相关性。关键词的流量得分，机会指数

在广告结构中做出挑词逻辑，来源于算法选词的算法分类，不需要在广告结构中再新增指标了


























在类目里面找到最相近或同款竞品ASIN 10-20个（至少3个ASIN以上，最多10个ASIN） 在SIF 多产品对比 对比流量，下载数据，给AI分析， chatGPTo3
流量分级	   关键词相关性分级    周搜索量	      搜索量排名	在售商品数	流量垄断占比	竞争程度
组合统计指标 包含 流量分级，词相关性，关键词个数	总周搜索量	中位周搜索量	平均周搜索量	平均流量垄断度	流量垄断情况	平均在售商品	搜索量份额	加权流量垄断度

卖家精灵 20个竞品ASIN 拓展流量，分析  关键词词库追踪 分析
SIF SIF相似竞品拓词法   相似竞品拓词和筛查   50-100个   1.1 竞品拓词法 （至少10个 100个）删选，最相关那个  竞品拓词导出_2025-08-07 竞品拓词导出_   自然位前N 占位符  4-8-16-32-48 周搜索趋势 相关性   搜索量  ABA排名  相关性-手动  流量大小  相关性手动
修饰词类型    搜索转化率   搜索转化率   360天内 商品搜索量大小 商机探测器数据          1.1 竞品拓词法 （至少10个） 1.0 竞品拓词法 （至少48个）

词频统计   1个单词词根      2个单词词根     3个单词词根    搜索量加权词频(亚马逊官方方法)
品类拓词导出    SIF 品类拓词&筛查 选细分品类  下载， v #	关键词	搜索量	排名	相关性-手动    {品类拓词导出 }
1.2 以词拓词（词根法）  以词拓词&筛查 

AI分析， 关键词	流量分级	关键词相关性分级	周搜索量	搜索量排名	在售商品数	流量垄断占比	竞争程度

--

chatGPT o3模型  模型 指令

要求按照之前的格式稳定输出，
请帮我分出表格全部关键词分类，一级，二级，三级流量词，然后再分出强中弱不相关。排列组合一级，二级，三级的强中弱，不相关关键词子表,具体需要生成以下格式的表格字段：1.流量分级：关键词按流量划分等级，分为一级二级三级。
关键词相关性分级： 按相关性对流量进行分类统计，比如划分强中弱，不相关。
 关键词个数：相关关键词的数量 
总周搜索量：一周内的总搜索次数。
中位周搜索量： 中位搜索量情况
平均周搜索量：平均周搜索量情况。
平均流量垄断度：流量垄断的平均垄断情况 
流量垄断情况 ：关键词流量垄断情况。 平均在售商品： 平均在售商品的分布情况。
搜索量份额：搜索量占整体的比例。
加权流量垄断度：衡量流量被垄断的程度。
模型 指令，：



关键词优化路径： 
①选取10个竞品ASIN  SIF多产品对比，流量布局， 
②选取20个ASIN竞品  在卖家精灵（关键词优化 - 拓展流量词） 流量拓展=关键词优化 - 拓展流量词 按照畅销变体 拓展，下载数据，做关键词词库追踪，需要要AI智能体打标和分类，做关键词词库追踪数据
③ 用核心关键词搜索，去亚马逊前台抓取50-100类目相关竞品做SIF关键词收集 放关键词收集蓝 做相关性筛查，关键词词库+消费者洞察  
④ 要在后台商机探测器 关键词 份额，确定大词有哪些 做大词，   
⑤查看 SIF关键词中竞争格局-- 自然流量份额分布， 在售产品 自然流量分布  ⑥关键词广告点击转化率 ACOS  CPA 利润率
⑦ 关键词CPC情况（具体看是 在哪个类目下）

参考建议如下：类目问题 可以放这个类目 Tools & Home Improvement›Kitchen & Bath Fixtures›Water Filtration & Softeners›Under-Sink & Countertop Filtration
每年7月 11-12月有旺季出现 类目问题，价格问题， 标题问题，      优惠券 划线价，评论问题， 利润率问题， 埋词 标题-五点描述-后台ST埋词，QA 评论埋词，关键词，关键词 图片A+,
标题  价格 关键词  广告


lisiting改善 图片 ，广告策略，做评论




















B0DWMX7H1M

B01JIRLRXY

B01JIRLRXY
B00LBHIW8S
B097FBQ3VZ
B0D44STX7N
B0B5DSTW9F
B0D459VS24
B0C2ZNTR6Z
B086WRLZPY
B08XXJSN29
B01F9A4UVU
B0F432LBC2
B0C9ZY8L1C
B009YA28ES
B0CN6MY83H
B0F431RZ3L
B0C4PTZXDF

































从算法选词，到广告结构，到批量上传广告数据    ，全流程打通

算法选词，选词逻辑 {挑词逻辑如下}   ，词库文案

广告结构，截图1，截图2






以下是挑词逻辑，
新增分析字段（算法计算）
    广告投放方案（智能决策）
   计算方式：基于5个指标综合评分（商业价值、广告选词、点击转化率， 分类级别（按优先级 为5档）：1.最高优先级），2.高优先级），（3.正常投放），（4.值得测试），（5.小额测试）
    核心投放：综合得分≥80，日预算25-35%（最高优先级）
    重点投放：得分65-79，日预算15-25%（高优先级）
    标准投放：得分50-64，日预算10-15%（正常投放）
    测试投放：得分35-49，日预算5-10%（值得测试）
    低价测试：得分20-34，日预算<5%（小额测试）
    暂不投放：得分<20，不建议投放  不设置预算，预算为0
    否定词屏蔽：基础分类为否定词，需添加到否定词列表
    数据不足：缺少广告选词或商业价值数据
     使用建议：直接根据此列分配广告预算，无需复杂判断,

整个工作流程是从反查竞品ASIN，（20个竞品ASIN）导出关键词，通过算法分几个维度给关键词打分。通过分数划分出适合广告投放的分类，考虑的是广告效率。再划分出适合文案的分类，考虑的是相关性。

在广告结构中做出挑词逻辑，来源于算法选词的算法分类，不需要在广告结构中再新增指标了




做一个亚马逊广告运营助手，从算法选词，到广告结构，到批量上传广告数据    ，全流程打通

算法选词，选词逻辑 {挑词逻辑如下}   ，词库文案

广告结构，截图1，截图2




以下是挑词逻辑，
新增分析字段（算法计算）
    广告投放方案（智能决策）
·  计算方式：基于5个指标综合评分（商业价值、广告选词、点击转化率，   分类级别（按优先级 为5档）：最高优先级），高优先级），（正常投放），（值得测试），（小额测试）
    核心投放：综合得分≥80，日预算25-35%（最高优先级）
    重点投放：得分65-79，日预算15-25%（高优先级）
    标准投放：得分50-64，日预算10-15%（正常投放）
    测试投放：得分35-49，日预算5-10%（值得测试）
    低价测试：得分20-34，日预算<5%（小额测试）
     暂不投放：得分<20，不建议投放  不设置预算，预算为0
    否定词屏蔽：基础分类为否定词，需添加到否定词列表
    数据不足：缺少广告选词或商业价值数据
     使用建议：直接根据此列分配广告预算，无需复杂判断,
整个工作流程是从反查竞品ASIN，（20个竞品ASIN）导出关键词，通过算法分几个维度给关键词打分。通过分数划分出适合广告投放的分类，考虑的是广告效率。再划分出适合文案的分类，考虑的是相关性。

在广告结构中做出挑词逻辑，来源于算法选词的算法分类，不需要在广告结构中再新增指标了











B01JIRLRXY
B00LBHIW8S
B097FBQ3VZ
B0D44STX7N
B0B5DSTW9F
B0D459VS24
B0C2ZNTR6Z
B086WRLZPY
B08XXJSN29
B01F9A4UVU
B0C9ZY8L1C
B009YA28ES
B0CN6MY83H
B0F431RZ3L
B0C4PTZXDF


B0DWMX7H1M
B0DWMSJ92Y
B0FB9LQMBZ
B0FMJWV3QX
B0F6MR2B7Y





SIFshig十个竞品分析
B01JIRLRXY,
B00LBHIW8S,
B097FBQ3VZ,
B0B5DSTW9F,
B086WRLZPY,
B08XXJSN29,
B0C9ZY8L1C,
B009YA28ES,
B0F431RZ3L,
B0C4PTZXDF






B01JIRLRXY,
B00LBHIW8S,
B097FBQ3VZ,
B0D44STX7N,
B0B5DSTW9F,
B0D459VS24,
B0C2ZNTR6Z,
B086WRLZPY,
B08XXJSN29,
B01F9A4UVU,
B0C9ZY8L1C,
B009YA28ES,
B0CN6MY83H,
B0F431RZ3L,
B0C4PTZXDF,
B0DWMX7H1M,
B0DWMSJ92Y,
B0FB9LQMBZ,
B0FMJWV3QX,
B0F6MR2B7Y






